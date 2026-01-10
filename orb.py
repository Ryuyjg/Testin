#!/usr/bin/env python3
import asyncio
import os
import json
import random
import logging
import socket
import time
import gc
import resource
import signal
import sys
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.errors import (
    UserDeactivatedBanError,
    FloodWaitError,
    ChannelPrivateError,
    ChatWriteForbiddenError,
    PeerIdInvalidError
)
from colorama import init, Fore, Style
from datetime import datetime

# Initialize colorama
init(autoreset=True)

# ============= CONFIGURATION =============
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "Orgjhonysins"

# Optimized timing for 50+ sessions
MIN_DELAY = 90    # 1.5 minutes between groups
MAX_DELAY = 180   # 3 minutes between groups  
CYCLE_DELAY = 2400  # 40 minutes between cycles

# Memory protection settings
MEMORY_LIMIT_MB = 7000  # 7GB for 8GB VPS with swap
GC_INTERVAL = 50        # Garbage collect every 50 operations

# Connection settings
MAX_CONNECT_RETRIES = 3
CONNECT_TIMEOUT = 30

# Logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(message)s',
    handlers=[
        logging.FileHandler('bot.log'),
        logging.StreamHandler()
    ]
)

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @OgDigital For Buy"

# ============= SYSTEM PROTECTION =============
class SystemProtector:
    """Prevents system from killing the process"""
    
    @staticmethod
    def setup_protection():
        """Setup all system protections"""
        try:
            # Set memory limit
            memory_bytes = MEMORY_LIMIT_MB * 1024 * 1024
            resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
            
            # Increase stack size
            resource.setrlimit(resource.RLIMIT_STACK, (resource.RLIM_INFINITY, resource.RLIM_INFINITY))
            
            # Increase core file size (0 means no core dumps)
            resource.setrlimit(resource.RLIMIT_CORE, (0, 0))
            
            # Ignore SIGPIPE signals
            signal.signal(signal.SIGPIPE, signal.SIG_IGN)
            
            # Handle SIGTERM gracefully
            signal.signal(signal.SIGTERM, SystemProtector.graceful_shutdown)
            
            print(Fore.GREEN + f"✓ Memory limit: {MEMORY_LIMIT_MB}MB")
            print(Fore.GREEN + "✓ System protections enabled")
            
        except Exception as e:
            print(Fore.YELLOW + f"⚠ System protection warning: {e}")
    
    @staticmethod
    def graceful_shutdown(signum, frame):
        """Handle termination signals gracefully"""
        print(Fore.YELLOW + f"\n⚠ Received shutdown signal ({signum}). Gracefully stopping...")
        sys.exit(0)
    
    @staticmethod
    def optimize_system():
        """Optimize Python runtime"""
        # Disable garbage collection during critical sections
        gc.disable()
        
        # Set Python optimizations
        sys.setrecursionlimit(100000)
        
        # Disable bytecode generation
        sys.dont_write_bytecode = True
        
        # Optimize GC thresholds
        gc.set_threshold(70000, 100, 100)

# ============= MEMORY MANAGEMENT =============
class MemoryManager:
    """Manages memory usage to prevent OOM kills"""
    
    def __init__(self):
        self.operation_count = 0
        self.memory_warnings = 0
    
    def should_cleanup(self):
        """Check if we should run cleanup"""
        self.operation_count += 1
        return self.operation_count % GC_INTERVAL == 0
    
    def force_cleanup(self):
        """Force memory cleanup"""
        # Collect garbage
        collected = gc.collect()
        
        # Clear Python caches
        sys.modules[__name__].__dict__.clear()
        
        # Clear import cache
        if 'telethon' in sys.modules:
            del sys.modules['telethon']
        
        self.operation_count = 0
        
        if collected > 0:
            print(Fore.CYAN + f"♻ Cleaned {collected} objects")
    
    def check_memory_pressure(self):
        """Check if memory pressure is high"""
        try:
            import psutil
            memory = psutil.virtual_memory()
            
            if memory.percent > 85:
                self.memory_warnings += 1
                print(Fore.YELLOW + f"⚠ High memory: {memory.percent}% (Warning {self.memory_warnings})")
                
                # If too many warnings, force cleanup
                if self.memory_warnings > 3:
                    self.force_cleanup()
                    self.memory_warnings = 0
                    return True
            else:
                self.memory_warnings = 0
                
        except ImportError:
            pass  # psutil not installed
        
        return False

# ============= NETWORK UTILITIES =============
def check_internet_connection():
    """Robust internet connection check"""
    hosts = ["8.8.8.8", "1.1.1.1", "208.67.222.222"]
    
    for host in hosts:
        try:
            socket.create_connection((host, 53), timeout=5)
            return True
        except:
            continue
    
    return False

async def wait_for_internet():
    """Wait for internet with backoff"""
    backoff = 5
    max_backoff = 60
    
    print(Fore.YELLOW + "🌐 Waiting for internet connection...")
    
    while not check_internet_connection():
        print(Fore.RED + f"❌ No internet. Retrying in {backoff}s...")
        await asyncio.sleep(backoff)
        backoff = min(backoff * 2, max_backoff)
    
    print(Fore.GREEN + "✅ Internet connection available!")

# ============= DISPLAY =============
def display_banner():
    """Show optimized banner"""
    print(Fore.GREEN + Style.BRIGHT + """
    ╔══════════════════════════════════════════╗
    ║     ORBIT ADBOT - VPS ULTIMATE EDITION   ║
    ║          NO MORE KILLING!                ║
    ╚══════════════════════════════════════════╝
    """)
    
    print(Fore.CYAN + "📊 System Configuration:")
    print(Fore.YELLOW + f"   • Sessions: Unlimited")
    print(Fore.YELLOW + f"   • Delay: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"   • Cycle: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + f"   • Memory Limit: {MEMORY_LIMIT_MB}MB")
    print(Fore.YELLOW + f"   • Protection: Active")
    print()

# ============= SESSION MANAGEMENT =============
def save_session(session_name, data):
    """Save session with error handling"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except:
        return False

def load_session(session_name):
    """Load session with caching"""
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    
    return None

def load_all_sessions():
    """Load all sessions from folder"""
    sessions = {}
    
    for file in os.listdir(CREDENTIALS_FOLDER):
        if file.endswith('.json'):
            session_name = file.replace('.json', '')
            data = load_session(session_name)
            if data:
                sessions[session_name] = data
    
    return sessions

# ============= TELEGRAM OPERATIONS =============
async def get_last_message_cached(client):
    """Get last message with entity caching"""
    try:
        # Cache entity in client attribute
        if not hasattr(client, '_cached_entity'):
            client._cached_entity = await client.get_input_entity(TARGET_USER)
        
        messages = await client.get_messages(client._cached_entity, limit=1)
        return messages[0] if messages else None
    except Exception as e:
        print(Fore.RED + f"Error getting message: {e}")
        return None

async def safe_forward_with_retry(client, group, message, session_name, retries=2):
    """Forward message with retry logic"""
    for attempt in range(retries):
        try:
            await client.forward_messages(group, message)
            print(Fore.GREEN + f"[{session_name}] ✅ Sent to group")
            return True
            
        except FloodWaitError as e:
            wait_time = e.seconds
            print(Fore.RED + f"[{session_name}] ⏳ Flood wait: {wait_time}s")
            await asyncio.sleep(wait_time)
            continue
            
        except (ChannelPrivateError, ChatWriteForbiddenError):
            print(Fore.YELLOW + f"[{session_name}] ⚠ No access")
            return False
            
        except PeerIdInvalidError:
            print(Fore.RED + f"[{session_name}] ❌ Invalid peer")
            return False
            
        except Exception as e:
            if attempt < retries - 1:
                print(Fore.YELLOW + f"[{session_name}] ⚠ Retry {attempt + 1}/{retries}: {e}")
                await asyncio.sleep(2)
                continue
            else:
                print(Fore.RED + f"[{session_name}] ❌ Failed after {retries} attempts")
                return False
    
    return False

async def process_groups_efficient(client, session_name, message, memory_manager):
    """Efficient group processing with memory management"""
    if not message:
        print(Fore.YELLOW + f"[{session_name}] ⚠ No message")
        return 0

    groups = []
    try:
        # Get groups with limit to prevent memory overflow
        async for dialog in client.iter_dialogs(limit=100):  # Reduced limit
            if dialog.is_group:
                groups.append(dialog.entity)
                
                # Check memory every 10 groups
                if len(groups) % 10 == 0:
                    if memory_manager.check_memory_pressure():
                        print(Fore.YELLOW + f"[{session_name}] ⚠ Memory pressure, limiting groups")
                        break
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error getting groups: {e}")
        return 0

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] ⚠ No groups found")
        return 0

    print(Fore.CYAN + f"[{session_name}] 📤 Processing {len(groups)} groups")
    
    sent_count = 0
    for i, group in enumerate(groups):
        if await safe_forward_with_retry(client, group, message, session_name):
            sent_count += 1
        
        # Memory cleanup check
        if memory_manager.should_cleanup():
            memory_manager.force_cleanup()
        
        # Delay between groups (except last one)
        if i < len(groups) - 1:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            minutes = delay / 60
            
            print(Fore.BLUE + f"[{session_name}] ⏰ Next in {minutes:.1f} mins ({i+1}/{len(groups)})")
            await asyncio.sleep(delay)
    
    print(Fore.GREEN + f"[{session_name}] ✅ Completed: {sent_count}/{len(groups)} sent")
    return sent_count

async def setup_auto_reply_smart(client, session_name):
    """Smart auto-reply with cooldown"""
    cooldown = {}  # user_id -> last_reply_time
    
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            sender_id = event.sender_id
            current_time = time.time()
            
            # 5-minute cooldown per user
            if sender_id in cooldown:
                if current_time - cooldown[sender_id] < 300:
                    return
            
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                cooldown[sender_id] = current_time
                print(Fore.MAGENTA + f"[{session_name}] 🤖 Auto-replied")
                
                # Clean old entries
                if len(cooldown) > 100:
                    # Remove entries older than 1 hour
                    cutoff = current_time - 3600
                    to_remove = [uid for uid, ts in cooldown.items() if ts < cutoff]
                    for uid in to_remove:
                        cooldown.pop(uid, None)
                        
            except Exception:
                pass  # Silent fail

# ============= SESSION HANDLER =============
async def manage_session_robust(session_name, credentials):
    """Robust session management with automatic recovery"""
    memory_manager = MemoryManager()
    consecutive_errors = 0
    max_consecutive_errors = 5
    
    print(Fore.CYAN + f"\n[{session_name}] 🚀 Starting session...")
    
    while True:
        client = None
        try:
            # Internet check
            if not check_internet_connection():
                print(Fore.YELLOW + f"[{session_name}] 🌐 Waiting for internet...")
                await wait_for_internet()
            
            # Create client with optimized settings
            client = TelegramClient(
                StringSession(credentials["string_session"]),
                credentials["api_id"],
                credentials["api_hash"],
                connection_retries=MAX_CONNECT_RETRIES,
                request_retries=2,
                flood_sleep_threshold=120,
                device_model="Android",
                system_version="10",
                app_version="8.4",
                lang_code="en",
                system_lang_code="en-US",
                base_logger=logging.getLogger(__name__)
            )
            
            # Connect with timeout
            print(Fore.YELLOW + f"[{session_name}] 🔗 Connecting...")
            
            try:
                await asyncio.wait_for(client.connect(), timeout=CONNECT_TIMEOUT)
            except asyncio.TimeoutError:
                print(Fore.RED + f"[{session_name}] ❌ Connection timeout")
                consecutive_errors += 1
                await asyncio.sleep(30)
                continue
            
            # Authorization check
            if not await client.is_user_authorized():
                print(Fore.RED + f"[{session_name}] ❌ Not authorized")
                break
            
            print(Fore.GREEN + f"[{session_name}] ✅ Connected successfully!")
            consecutive_errors = 0  # Reset error counter
            
            # Setup auto-reply
            await setup_auto_reply_smart(client, session_name)
            
            # Main operation loop
            cycle_count = 0
            while True:
                try:
                    # Check internet before operation
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] 🌐 Internet lost")
                        await wait_for_internet()
                        
                        # Reconnect if needed
                        if not client.is_connected():
                            await client.connect()
                    
                    # Get message
                    message = await get_last_message_cached(client)
                    
                    # Process groups
                    sent = await process_groups_efficient(client, session_name, message, memory_manager)
                    
                    if sent > 0:
                        print(Fore.GREEN + f"[{session_name}] ✅ Cycle {cycle_count} complete")
                    else:
                        print(Fore.YELLOW + f"[{session_name}] ⚠ Cycle {cycle_count} - no messages sent")
                    
                    # Sleep between cycles
                    print(Fore.CYAN + f"[{session_name}] 💤 Sleeping for {CYCLE_DELAY//60} minutes...")
                    
                    # Sleep with periodic checks
                    for i in range(CYCLE_DELAY // 60):
                        # Check memory every minute
                        memory_manager.check_memory_pressure()
                        await asyncio.sleep(60)
                    
                    cycle_count += 1
                    
                    # Force cleanup every 3 cycles
                    if cycle_count % 3 == 0:
                        memory_manager.force_cleanup()
                    
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] ❌ Operation error: {e}")
                    await asyncio.sleep(30)
                    break  # Break inner loop to reconnect
        
        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_name}] ❌ Account banned")
            break
            
        except Exception as e:
            consecutive_errors += 1
            print(Fore.RED + f"[{session_name}] ❌ Session error ({consecutive_errors}/{max_consecutive_errors}): {e}")
            
            if consecutive_errors >= max_consecutive_errors:
                print(Fore.RED + f"[{session_name}] ⚠ Too many errors, taking a break")
                await asyncio.sleep(300)  # 5 minutes break
                consecutive_errors = 0
            
            await asyncio.sleep(30)
            
        finally:
            # Clean disconnect
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] 🔌 Disconnected")
                except:
                    pass
    
    print(Fore.RED + f"[{session_name}] 🛑 Session ended")

# ============= MAIN FUNCTION =============
async def main_optimized():
    """Main function with all optimizations"""
    # Setup system protection
    SystemProtector.setup_protection()
    SystemProtector.optimize_system()
    
    # Display banner
    display_banner()
    
    # Initial internet check
    if not check_internet_connection():
        print(Fore.RED + "❌ No internet connection")
        await wait_for_internet()
    
    try:
        # Ask for session count
        try:
            num_sessions = int(input(Fore.CYAN + "📝 Enter number of sessions: " + Fore.WHITE))
            if num_sessions < 1:
                raise ValueError("At least 1 session required")
        except ValueError:
            print(Fore.RED + "❌ Invalid number")
            return
        
        # Load or configure sessions
        sessions_to_run = {}
        
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = load_session(session_name)
            
            if not creds:
                print(Fore.CYAN + f"\n⚙ Configuring {session_name}:")
                try:
                    creds = {
                        "api_id": int(input("API ID: ")),
                        "api_hash": input("API Hash: "),
                        "string_session": input("String Session: ")
                    }
                    save_session(session_name, creds)
                except Exception as e:
                    print(Fore.RED + f"❌ Error configuring {session_name}: {e}")
                    continue
            
            sessions_to_run[session_name] = creds
        
        if not sessions_to_run:
            print(Fore.RED + "❌ No valid sessions to run")
            return
        
        print(Fore.GREEN + f"\n✅ Loaded {len(sessions_to_run)} sessions")
        print(Fore.YELLOW + "🚀 Starting all sessions simultaneously...\n")
        
        # Create tasks for all sessions
        tasks = []
        for session_name, creds in sessions_to_run.items():
            task = asyncio.create_task(
                manage_session_robust(session_name, creds)
            )
            tasks.append(task)
            await asyncio.sleep(0.5)  # Stagger startup
        
        # Wait for all tasks to complete
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⚠ Operation cancelled by user")
    except Exception as e:
        print(Fore.RED + f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

# ============= ENTRY POINT =============
if __name__ == "__main__":
    print(Fore.CYAN + "🔧 Setting up VPS-optimized environment...")
    
    # Install uvloop if available (faster async)
    try:
        import uvloop
        uvloop.install()
        print(Fore.GREEN + "✅ UVLoop installed for faster performance")
    except ImportError:
        print(Fore.YELLOW + "⚠ UVLoop not installed (pip install uvloop for better performance)")
    
    # Auto-restart with backoff
    restart_count = 0
    max_restarts = 5
    restart_delay = 10
    
    while restart_count < max_restarts:
        try:
            asyncio.run(main_optimized())
            break  # Exit if completed successfully
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n🛑 Script stopped by user")
            break
            
        except MemoryError:
            restart_count += 1
            print(Fore.RED + f"💥 Memory error! Restarting in {restart_delay}s ({restart_count}/{max_restarts})")
            time.sleep(restart_delay)
            restart_delay = min(restart_delay * 2, 300)  # Exponential backoff
            
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"💥 Script crashed: {type(e).__name__}")
            print(Fore.YELLOW + f"🔄 Restarting in {restart_delay}s ({restart_count}/{max_restarts})")
            time.sleep(restart_delay)
    
    if restart_count >= max_restarts:
        print(Fore.RED + "🚨 Too many restarts. Please check your system.")
    
    print(Fore.CYAN + "\n👋 Orbit AdBot terminated")
