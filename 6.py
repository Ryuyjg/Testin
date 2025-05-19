import asyncio
import os
import json
import random
import logging
import gc
from datetime import datetime
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
from telethon.errors import (
    UserDeactivatedBanError,
    FloodWaitError,
    ChannelPrivateError,
    ChatWriteForbiddenError,
    ChannelInvalidError,
    PeerIdInvalidError
)
from colorama import init, Fore, Style
import pyfiglet

# Initialize colorama
init(autoreset=True)

# Try to import psutil with fallback
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False

# Configuration
CREDENTIALS_FOLDER = 'sessions'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "OrbitService"  # Target username for DM forwarding

# Timing Settings
MIN_DELAY = 15  # Minimum delay between groups (seconds)
MAX_DELAY = 30  # Maximum delay between groups (seconds)
CYCLE_DELAY = 900  # 15 minutes between full cycles (seconds)

# Enhanced Memory Configuration
MEMORY_CHECK_INTERVAL = 15  # Check memory every 15 operations
FORCE_CLEAN_THRESHOLD = 70  # Force cleanup when memory exceeds 70%
AGGRESSIVE_CLEAN_THRESHOLD = 80  # Emergency cleanup threshold
MAX_MEMORY_RETRIES = 3  # Max retries if memory remains high

# Forwarding Mode
FORWARD_MODE = 1  # 1 = Forward from OrbitService DM, 2 = Forward from public post link
POST_LINK = None  # Will store the shared post link

# Set up logging
logging.basicConfig(
    filename='orbit_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @OrbitService"

def clear_memory(session_name=None, aggressive=False):
    """Enhanced memory cleanup with multiple strategies"""
    mem_before = None
    mem_after = None
    
    if PSUTIL_AVAILABLE:
        process = psutil.Process(os.getpid())
        mem_before = process.memory_percent()
        if mem_before >= AGGRESSIVE_CLEAN_THRESHOLD:
            aggressive = True
    
    # Level 1: Standard cleanup
    gc.collect()
    
    # Level 2: Aggressive cleanup
    if aggressive:
        display_status("Performing aggressive memory cleanup", "warning", session_name)
        for i in range(3):  # Triple collection pass
            gc.collect()
            gc.collect(2)  # Collect older generations
            if hasattr(gc, 'mem_free'):  # If available (PyPy)
                gc.mem_free()
    
    if PSUTIL_AVAILABLE:
        mem_after = process.memory_percent()
        log_msg = f"[Memory] {mem_before:.2f}% → {mem_after:.2f}%"
        if aggressive:
            log_msg += " (aggressive)"
        if session_name:
            log_msg = f"[{session_name}] {log_msg}"
        logging.info(log_msg)
        return mem_after
    return None

def display_status(message, status_type="info", session_name=None):
    """Prints colored status messages with optional session prefix"""
    timestamp = datetime.now().strftime("%H:%M:%S")
    prefix = f"[{session_name}] " if session_name else ""
    
    status_colors = {
        "success": Fore.GREEN,
        "error": Fore.RED,
        "warning": Fore.YELLOW,
        "info": Fore.CYAN
    }
    
    color = status_colors.get(status_type.lower(), Fore.CYAN)
    print(f"{color}{timestamp} {prefix}{message}{Style.RESET_ALL}")
    
    # Also log to file
    log_level = getattr(logging, status_type.upper(), logging.INFO)
    logging.log(log_level, f"{prefix}{message}")

def display_memory_status(session_name=None):
    """Display current memory status if psutil is available"""
    if not PSUTIL_AVAILABLE:
        return
        
    process = psutil.Process(os.getpid())
    mem_info = process.memory_percent()
    status = f"Memory usage: {mem_info:.2f}%"
    
    if mem_info > AGGRESSIVE_CLEAN_THRESHOLD:
        display_status(status, "error", session_name)
    elif mem_info > FORCE_CLEAN_THRESHOLD:
        display_status(status, "warning", session_name)
    else:
        display_status(status, "info", session_name)
    
    return mem_info

def display_banner():
    """Display the banner"""
    print(Fore.RED + pyfiglet.figlet_format("ORBIT ADBOT"))
    display_status("By @OrbitService", "success")
    
    # Show memory capabilities in banner
    if PSUTIL_AVAILABLE:
        display_status(f"Advanced memory monitoring (Clean at {FORCE_CLEAN_THRESHOLD}%/{AGGRESSIVE_CLEAN_THRESHOLD}%)", "success")
    else:
        display_status("Basic memory management (install psutil for advanced monitoring)", "warning")

def save_credentials(session_name, credentials):
    """Save session credentials"""
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    with open(path, "w") as f:
        json.dump(credentials, f)
    display_status(f"Credentials saved for {session_name}", "success")

def load_credentials(session_name):
    """Load session credentials"""
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return None

async def memory_safety_check(session_name, operation_count):
    """Enhanced memory monitoring with recovery strategies"""
    if not PSUTIL_AVAILABLE:
        if operation_count % 50 == 0:  # Basic fallback
            clear_memory(session_name)
        return True
    
    process = psutil.Process(os.getpid())
    mem_info = process.memory_percent()
    
    # Emergency check
    if mem_info >= AGGRESSIVE_CLEAN_THRESHOLD:
        display_status(f"CRITICAL MEMORY: {mem_info:.2f}% - Emergency cleanup", "error", session_name)
        clear_memory(session_name, aggressive=True)
        await asyncio.sleep(2)  # Recovery pause
        return False if process.memory_percent() >= AGGRESSIVE_CLEAN_THRESHOLD else True
    
    # Regular threshold check
    if mem_info >= FORCE_CLEAN_THRESHOLD or operation_count % MEMORY_CHECK_INTERVAL == 0:
        display_status(f"Memory threshold: {mem_info:.2f}%", "warning", session_name)
        clear_memory(session_name)
        await asyncio.sleep(1)  # Short pause after cleanup
    
    return True

async def get_last_dm_message(client, session_name):
    """Get last message from target user's DM"""
    try:
        entity = await client.get_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=10)
        
        for msg in messages:
            # Skip service messages and empty messages
            if not isinstance(msg, types.MessageService) and msg.message:
                return msg
                
        display_status("No forwardable messages in DM", "warning", session_name)
        return None
        
    except PeerIdInvalidError:
        display_status(f"Not in DM with @{TARGET_USER}", "error", session_name)
        return None
    except Exception as e:
        display_status(f"DM error: {str(e)}", "error", session_name)
        return None

async def get_post_from_link(client, session_name):
    """Get a post from the shared public link and forward to Saved Messages"""
    global POST_LINK
    try:
        if not POST_LINK:
            return None
            
        # Parse the link to get channel and post ID
        if "t.me/" not in POST_LINK:
            display_status("Invalid Telegram link", "error", session_name)
            return None
            
        parts = POST_LINK.split("/")
        if len(parts) < 2:
            display_status("Invalid link format", "error", session_name)
            return None
            
        channel = parts[-2]
        post_id = int(parts[-1])
        
        # Get the entity and message
        entity = await client.get_entity(channel)
        msg = await client.get_messages(entity, ids=post_id)
        
        if not msg:
            display_status("Post not found", "error", session_name)
            return None
            
        # Forward to Saved Messages
        saved = await client.get_entity("me")
        forwarded_msg = await client.forward_messages(saved, msg)
        display_status("Post forwarded to Saved Messages", "success", session_name)
        return forwarded_msg
        
    except ValueError:
        display_status("Invalid post ID in link", "error", session_name)
    except ChannelInvalidError:
        display_status("Channel is private or inaccessible", "error", session_name)
    except Exception as e:
        display_status(f"Post link error: {str(e)}", "error", session_name)
    return None

async def forward_to_group(client, group, message, session_name, operation_count):
    """Reliable message forwarding with retries and memory management"""
    try:
        # Memory check before each forward
        if not await memory_safety_check(session_name, operation_count):
            raise MemoryError("Memory too high to continue")
            
        await client.forward_messages(group, message)
        display_status(f"Sent to {getattr(group, 'title', 'UNKNOWN')}", "success", session_name)
        return True
    except FloodWaitError as e:
        wait = min(e.seconds, 30)  # Cap at 30 seconds
        display_status(f"Flood wait: {wait}s", "warning", session_name)
        await asyncio.sleep(wait)
        return await forward_to_group(client, group, message, session_name, operation_count)
    except (ChannelPrivateError, ChatWriteForbiddenError):
        display_status("No access to group", "warning", session_name)
        return False
    except Exception as e:
        display_status(f"Forward error: {str(e)}", "error", session_name)
        return False

async def process_groups(client, session_name, message):
    """Process all groups with strict timing control and memory management"""
    try:
        dialogs = await client.get_dialogs()
        groups = [d.entity for d in dialogs if d.is_group]
        
        if not groups:
            display_status("No groups found", "warning", session_name)
            return

        display_status(f"Processing {len(groups)} groups", "info", session_name)
        
        operation_count = 0
        for group in groups:
            start_time = asyncio.get_event_loop().time()
            
            success = await forward_to_group(client, group, message, session_name, operation_count)
            if success:
                operation_count += 1
            
            # Calculate remaining delay time
            elapsed = asyncio.get_event_loop().time() - start_time
            remaining_delay = max(0, random.randint(MIN_DELAY, MAX_DELAY) - elapsed)
            
            if remaining_delay > 0:
                display_status(f"Waiting {remaining_delay:.1f}s", "info", session_name)
                await asyncio.sleep(remaining_delay)
                
    except Exception as e:
        display_status(f"Group error: {str(e)}", "error", session_name)
    finally:
        # Force cleanup after processing all groups
        clear_memory(session_name, aggressive=True)

async def setup_auto_reply(client, session_name):
    """Efficient auto-reply setup with memory management"""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private and event.sender_id != (await client.get_me()).id:
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                display_status("Replied to DM", "success", session_name)
                clear_memory(session_name)
            except FloodWaitError as e:
                await asyncio.sleep(min(e.seconds, 30))
                await event.reply(AUTO_REPLY_MESSAGE)
            except Exception as e:
                display_status(f"Auto-reply error: {str(e)}", "error", session_name)

async def run_session(session_name, credentials):
    """Enhanced session runner with better memory management"""
    client = None
    retry_count = 0
    
    while retry_count < MAX_MEMORY_RETRIES:
        try:
            client = TelegramClient(
                StringSession(credentials["string_session"]),
                credentials["api_id"],
                credentials["api_hash"],
                device_model=f"OrbitBot-{random.randint(1000,9999)}",
                system_version="4.16.30-vxCustom",
                connection_retries=2,
                request_retries=2,
                auto_reconnect=True
            )
            
            await client.start()
            display_status("Session started", "success", session_name)
            
            operation_count = 0
            await setup_auto_reply(client, session_name)
            
            while True:
                try:
                    # Memory check before each major operation
                    if not await memory_safety_check(session_name, operation_count):
                        retry_count += 1
                        raise MemoryError("High memory persists after cleanup")
                    
                    if FORWARD_MODE == 1:
                        # Mode 1: Forward from OrbitService DM
                        message = await get_last_dm_message(client, session_name)
                    else:
                        # Mode 2: Forward from public post link
                        message = await get_post_from_link(client, session_name)
                    
                    if message:
                        await process_groups(client, session_name, message)
                        operation_count += 1
                    
                    # Between-cycle cleanup
                    mem_status = ""
                    if PSUTIL_AVAILABLE:
                        mem_status = f" (Mem: {psutil.Process(os.getpid()).memory_percent():.2f}%)"
                    display_status(f"Cycle complete{mem_status}", "info", session_name)
                    clear_memory(session_name, aggressive=True)
                    await asyncio.sleep(CYCLE_DELAY)
                    
                except MemoryError:
                    if retry_count >= MAX_MEMORY_RETRIES:
                        display_status("Max memory retries exceeded", "error", session_name)
                        break
                    await asyncio.sleep(10 * retry_count)  # Exponential backoff
                except Exception as e:
                    display_status(f"Operation error: {str(e)}", "error", session_name)
                    await asyncio.sleep(300)
            
        except UserDeactivatedBanError:
            display_status("Account banned", "error", session_name)
            break
        except Exception as e:
            display_status(f"Session crash: {str(e)}", "error", session_name)
            retry_count += 1
            if retry_count >= MAX_MEMORY_RETRIES:
                display_status("Max retries exceeded", "error", session_name)
                break
            await asyncio.sleep(30 * retry_count)  # Exponential backoff
        finally:
            if client:
                await client.disconnect()
            clear_memory(session_name, aggressive=True)
    
    display_status("Session ended", "warning", session_name)

async def main():
    """Main execution with unlimited concurrent sessions"""
    global POST_LINK, FORWARD_MODE
    
    display_banner()
    
    try:
        # Select forwarding mode
        print("\nSelect forwarding mode:")
        print("1. Forward from @OrbitService DM (default)")
        print("2. Forward from public post link")
        mode_choice = input("Enter choice (1/2): ").strip()
        if mode_choice == "2":
            FORWARD_MODE = 2
            POST_LINK = input("Enter the public post link (t.me/...) to forward: ").strip()
    
        num_sessions = int(input("Enter number of sessions: "))
        if num_sessions <= 0:
            raise ValueError("Positive number required")
                
        # Prepare all sessions
        sessions = []
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = load_credentials(session_name)
            
            if not creds:
                display_status(f"Enter details for {session_name}:", "info")
                creds = {
                    "api_id": int(input("API ID: ")),
                    "api_hash": input("API Hash: "),
                    "string_session": input("String Session: ")
                }
                save_credentials(session_name, creds)
                
            sessions.append((session_name, creds))

        # Process all sessions without concurrency limit
        display_status(f"Starting {len(sessions)} sessions", "success")
        
        # Run all sessions concurrently
        await asyncio.gather(*[run_session(name, creds) for name, creds in sessions])
        
    except ValueError as e:
        display_status(f"Input error: {str(e)}", "error")
    except KeyboardInterrupt:
        display_status("Stopped by user", "warning")
    except Exception as e:
        display_status(f"Fatal: {str(e)}", "error")
    finally:
        # Final memory cleanup
        clear_memory("MAIN", aggressive=True)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        display_status("Script stopped", "warning")
    finally:
        clear_memory("MAIN", aggressive=True)