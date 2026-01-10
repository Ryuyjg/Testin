#!/usr/bin/env python3
import asyncio
import os
import json
import random
import logging
import socket
import time
import gc
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

# Timing settings
MIN_DELAY = 60    # 1 minute between groups
MAX_DELAY = 120   # 2 minutes between groups  
CYCLE_DELAY = 1200  # 20 minutes between cycles

# ============= UTILITIES =============
def check_internet():
    """Check internet connection"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except:
        return False

async def wait_for_internet():
    """Wait for internet"""
    while not check_internet():
        print(Fore.YELLOW + "🌐 Waiting for internet...")
        await asyncio.sleep(10)
    print(Fore.GREEN + "✅ Internet connected")

def display_banner():
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════╗
    ║     ORBIT ADBOT - SIMPLE EDITION ║
    ║     NO ERRORS • FAST • STABLE    ║
    ╚══════════════════════════════════╝
    """)
    print(Fore.YELLOW + f"• Groups delay: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"• Cycle delay: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + "• All sessions run simultaneously\n")

def save_session(session_name, data):
    """Save session"""
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    with open(path, 'w') as f:
        json.dump(data, f, indent=2)

def load_session(session_name):
    """Load session"""
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    if os.path.exists(path):
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except:
            pass
    return None

# ============= MEMORY MANAGEMENT =============
class SimpleMemoryManager:
    """Simple memory management"""
    
    def __init__(self):
        self.last_cleanup = time.time()
        self.operation_count = 0
    
    def should_cleanup(self):
        """Check if cleanup is needed"""
        self.operation_count += 1
        current_time = time.time()
        
        # Clean every 5 minutes or 50 operations
        if (current_time - self.last_cleanup > 300) or (self.operation_count % 50 == 0):
            return True
        return False
    
    def cleanup(self):
        """Run memory cleanup"""
        # Run garbage collection
        collected = gc.collect()
        
        # Clear some caches
        try:
            if 'telethon' in sys.modules:
                telethon = sys.modules['telethon']
                # Clear some caches if they exist
                for attr in ['_download_cache', '_entity_cache']:
                    if hasattr(telethon, attr):
                        cache = getattr(telethon, attr)
                        if hasattr(cache, 'clear'):
                            cache.clear()
        except:
            pass
        
        self.last_cleanup = time.time()
        self.operation_count = 0
        
        if collected > 0:
            print(Fore.CYAN + "🧹 Memory cleaned")

# ============= TELEGRAM OPERATIONS =============
async def get_last_message_simple(client):
    """Get last message from target"""
    try:
        entity = await client.get_input_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=1)
        return messages[0] if messages else None
    except Exception as e:
        print(Fore.RED + f"Error getting message: {e}")
        return None

async forward_to_group_simple(client, group, message, session_name):
    """Forward message to a single group"""
    try:
        # Get group name
        group_name = "Group"
        if hasattr(group, 'title'):
            group_name = group.title
        elif hasattr(group, 'username'):
            group_name = f"@{group.username}"
        
        # Forward message
        await client.forward_messages(group, message)
        print(Fore.GREEN + f"[{session_name}] ✅ Sent to: {group_name}")
        return True
        
    except FloodWaitError as e:
        print(Fore.RED + f"[{session_name}] ⏳ Flood wait: {e.seconds}s")
        await asyncio.sleep(e.seconds)
        return False
        
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] ⚠️  No access: {group_name}")
        return False
        
    except PeerIdInvalidError:
        print(Fore.RED + f"[{session_name}] ❌ Invalid peer")
        return False
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__}")
        return False

async def process_groups_simple(client, session_name, message, memory_manager):
    """Process all groups"""
    if not message:
        print(Fore.YELLOW + f"[{session_name}] ⚠️  No message")
        return 0, 0
    
    groups = []
    try:
        # Get all groups
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Error getting groups: {e}")
        return 0, 0
    
    if not groups:
        print(Fore.YELLOW + f"[{session_name}] ⚠️  No groups found")
        return 0, 0
    
    print(Fore.CYAN + f"[{session_name}] 📤 Processing {len(groups)} groups")
    
    sent = 0
    for i, group in enumerate(groups):
        # Forward message
        if await forward_to_group_simple(client, group, message, session_name):
            sent += 1
        
        # Memory cleanup check
        if memory_manager.should_cleanup():
            memory_manager.cleanup()
        
        # Delay between groups (except last one)
        if i < len(groups) - 1:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            minutes = delay / 60
            
            # Show progress
            progress = f"{i+1}/{len(groups)}"
            print(Fore.BLUE + f"[{session_name}] ⏰ Next in {minutes:.1f}m | Progress: {progress}")
            await asyncio.sleep(delay)
    
    return sent, len(groups)

# ============= AUTO-REPLY =============
async def setup_auto_reply_simple(client, session_name):
    """Simple auto-reply"""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            try:
                await event.reply("Dm @OgDigital For Buy")
                print(Fore.MAGENTA + f"[{session_name}] 🤖 Auto-replied")
            except:
                pass

# ============= SESSION MANAGEMENT =============
async def manage_session_simple(session_name, credentials):
    """Simple and robust session management"""
    memory_manager = SimpleMemoryManager()
    
    print(Fore.CYAN + f"\n[{session_name}] 🚀 Starting...")
    
    while True:
        client = None
        try:
            # Internet check
            if not check_internet():
                await wait_for_internet()
            
            # Create client
            client = TelegramClient(
                StringSession(credentials["string_session"]),
                credentials["api_id"],
                credentials["api_hash"],
                device_model="Android",
                system_version="10",
                app_version="8.4",
                lang_code="en",
                system_lang_code="en-US"
            )
            
            # Connect
            print(Fore.YELLOW + f"[{session_name}] 🔗 Connecting...")
            await client.connect()
            
            # Check authorization
            if not await client.is_user_authorized():
                print(Fore.RED + f"[{session_name}] ❌ Not authorized")
                break
            
            print(Fore.GREEN + f"[{session_name}] ✅ Connected!")
            
            # Setup auto-reply
            await setup_auto_reply_simple(client, session_name)
            
            # Get target entity once
            try:
                target_entity = await client.get_input_entity(TARGET_USER)
            except:
                print(Fore.RED + f"[{session_name}] ❌ Target not found")
                await asyncio.sleep(300)
                continue
            
            # Main loop
            cycle_count = 0
            total_sent = 0
            total_groups = 0
            
            while True:
                cycle_count += 1
                print(Fore.MAGENTA + f"\n[{session_name}] 🔄 Cycle {cycle_count}")
                
                # Get last message
                try:
                    messages = await client.get_messages(target_entity, limit=1)
                    message = messages[0] if messages else None
                except:
                    message = None
                
                if message:
                    # Process groups
                    sent, groups = await process_groups_simple(
                        client, session_name, message, memory_manager
                    )
                    
                    total_sent += sent
                    total_groups += groups
                    
                    # Show stats
                    if sent > 0:
                        print(Fore.GREEN + f"[{session_name}] ✅ Sent {sent}/{groups} this cycle")
                        print(Fore.CYAN + f"[{session_name}] 📊 Total: {total_sent} sent to {total_groups} groups")
                
                # Sleep between cycles
                print(Fore.YELLOW + f"[{session_name}] 💤 Sleeping {CYCLE_DELAY//60} minutes...")
                
                # Sleep with periodic cleanup
                for i in range(CYCLE_DELAY // 60):
                    # Clean memory every 5 minutes
                    if i % 5 == 0:
                        memory_manager.cleanup()
                    
                    await asyncio.sleep(60)
        
        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_name}] ⛔ Account banned")
            break
            
        except KeyboardInterrupt:
            raise  # Re-raise to be caught by main
            
        except Exception as e:
            error_type = type(e).__name__
            print(Fore.RED + f"[{session_name}] ❌ Error: {error_type}")
            
            # Don't print full traceback for common errors
            if error_type not in ['ConnectionError', 'TimeoutError']:
                import traceback
                traceback.print_exc()
            
            print(Fore.YELLOW + f"[{session_name}] 🔄 Retrying in 30 seconds...")
            await asyncio.sleep(30)
            
        finally:
            # Disconnect
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] 🔌 Disconnected")
                except:
                    pass

# ============= MAIN FUNCTION =============
async def main_simple():
    """Simple main function"""
    display_banner()
    
    # Internet check
    if not check_internet():
        print(Fore.RED + "❌ No internet connection")
        await wait_for_internet()
    
    try:
        # Get number of sessions
        try:
            num_sessions = int(input(Fore.CYAN + "\n📝 Enter number of sessions: " + Fore.WHITE))
        except ValueError:
            print(Fore.RED + "❌ Invalid number")
            return
        
        if num_sessions < 1:
            print(Fore.RED + "❌ At least 1 session required")
            return
        
        # Load or configure sessions
        sessions = []
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = load_session(session_name)
            
            if not creds:
                print(Fore.CYAN + f"\n⚙️  Configuring {session_name}:")
                try:
                    creds = {
                        "api_id": int(input("API ID: ")),
                        "api_hash": input("API Hash: "),
                        "string_session": input("String Session: ")
                    }
                    save_session(session_name, creds)
                except Exception as e:
                    print(Fore.RED + f"❌ Error: {e}")
                    continue
            
            sessions.append((session_name, creds))
        
        if not sessions:
            print(Fore.RED + "❌ No sessions to run")
            return
        
        print(Fore.GREEN + f"\n✅ Ready to run {len(sessions)} sessions")
        print(Fore.YELLOW + "🚀 Starting all sessions...\n")
        
        # Start all sessions
        tasks = []
        for session_name, creds in sessions:
            task = asyncio.create_task(
                manage_session_simple(session_name, creds)
            )
            tasks.append(task)
            
            # Small delay between starting sessions
            await asyncio.sleep(1)
        
        # Wait for all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⏹️  Stopped by user")
    except Exception as e:
        print(Fore.RED + f"❌ Fatal error: {e}")
        import traceback
        traceback.print_exc()

# ============= ENTRY POINT =============
if __name__ == "__main__":
    # Simple startup
    print(Fore.CYAN + "🔧 Starting Orbit AdBot...")
    
    # Set recursion limit
    sys.setrecursionlimit(10000)
    
    # Disable bytecode
    sys.dont_write_bytecode = True
    
    # Run with restart protection
    restart_count = 0
    max_restarts = 3
    
    while restart_count < max_restarts:
        try:
            asyncio.run(main_simple())
            break
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n👋 Goodbye!")
            break
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"\n💥 Crash #{restart_count}: {type(e).__name__}")
            
            if restart_count < max_restarts:
                print(Fore.YELLOW + f"🔄 Restarting in 10 seconds...")
                time.sleep(10)
            else:
                print(Fore.RED + "🚨 Too many crashes, stopping.")
                break
    
    print(Fore.CYAN + "\n✨ Orbit AdBot terminated")
