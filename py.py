#!/usr/bin/env python3
import asyncio
import os
import json
import random
import logging
import socket
import time
import gc
import psutil
import traceback
import weakref
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from telethon.errors import (
    UserDeactivatedBanError,
    FloodWaitError,
    ChannelPrivateError,
    ChatWriteForbiddenError,
    PeerIdInvalidError
)
from colorama import init, Fore, Style
from datetime import datetime, timedelta
import signal
import sys

# Initialize colorama
init(autoreset=True)

# Enhanced Configuration
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "Orgjhonysins"

# Timing Settings
MIN_DELAY = 60   # 1 minute
MAX_DELAY = 120  # 2 minutes
CYCLE_DELAY = 1200  # 20 minutes
MAX_RETRIES = 3

# Performance Optimization
MEMORY_CLEAN_INTERVAL = 50  # Clear memory every 50 operations
HEARTBEAT_INTERVAL = 300  # Send heartbeat every 5 minutes
BATCH_SIZE = 5  # Process groups in batches
MAX_MEMORY_MB = 150  # Maximum allowed memory in MB

# Enhanced logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orbot_operations.log'),
        logging.StreamHandler()
    ]
)

AUTO_REPLY_MESSAGE = "Dm @OgDigital For Buy"

class MemoryOptimizer:
    """Memory optimization and monitoring"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.session_refs = []  # Store session references
        self.operation_counter = 0
        self.last_cleanup = datetime.now()
        
    def get_memory_usage(self):
        """Get current memory usage in MB"""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except:
            return 0
    
    def should_cleanup(self):
        """Check if cleanup is needed"""
        memory_usage = self.get_memory_usage()
        
        # Cleanup conditions
        conditions = [
            memory_usage > MAX_MEMORY_MB,
            self.operation_counter >= MEMORY_CLEAN_INTERVAL,
            (datetime.now() - self.last_cleanup).seconds > 600  # 10 minutes
        ]
        
        return any(conditions)
    
    def perform_cleanup(self, force=False):
        """Perform memory cleanup"""
        memory_before = self.get_memory_usage()
        
        # Count objects before cleanup
        objects_before = len(gc.get_objects())
        
        # Force garbage collection
        gc.collect()
        
        # Clear session references
        self.session_refs = [ref for ref in self.session_refs if ref() is not None]
        
        # Clear Python caches
        sys.modules[__name__].__dict__.clear()
        
        memory_after = self.get_memory_usage()
        objects_after = len(gc.get_objects())
        
        self.operation_counter = 0
        self.last_cleanup = datetime.now()
        
        print(Fore.CYAN + f"🔄 Memory cleanup: {memory_before:.1f}MB → {memory_after:.1f}MB "
              f"| Objects: {objects_before:,} → {objects_after:,}")
        
        return memory_after
    
    def register_session(self, session_object):
        """Register a session for monitoring - FIXED VERSION"""
        # Don't create weakrefs of weakrefs
        if isinstance(session_object, weakref.ref):
            return
            
        try:
            # Create a weak reference to the session
            ref = weakref.ref(session_object)
            self.session_refs.append(ref)
        except TypeError:
            # If weakref fails, just store the ID
            self.session_refs.append(id(session_object))
    
    def track_operation(self):
        """Track an operation for cleanup scheduling"""
        self.operation_counter += 1

# Global memory optimizer
memory_optimizer = MemoryOptimizer()

def check_internet_connection(host="8.8.8.8", port=53, timeout=5):
    """Check internet connection"""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.error, OSError):
        return False

async def wait_for_internet(max_wait=300):
    """Wait for internet connection"""
    print(Fore.YELLOW + "🔌 Checking internet connection...")
    start_time = time.time()
    
    while time.time() - start_time < max_wait:
        if check_internet_connection():
            print(Fore.GREEN + "✅ Internet connected!")
            return True
        print(Fore.YELLOW + "🌐 Waiting for internet...")
        await asyncio.sleep(10)
    
    return False

def display_banner():
    """Display optimized banner"""
    print(Fore.GREEN + """
    ╔══════════════════════════════════════╗
    ║       ORBIT ADBOT - 24/7 EDITION     ║
    ║      Advanced Memory Management      ║
    ╚══════════════════════════════════════╝
    """)
    print(Fore.CYAN + "📊 Features:")
    print(Fore.CYAN + "• Smart Memory Optimization")
    print(Fore.CYAN + "• Auto-Crash Recovery")
    print(Fore.CYAN + "• Connection Stability")
    print(Fore.CYAN + "• Resource Monitoring")
    print(Fore.GREEN + "=" * 40)
    print(Fore.YELLOW + f"⏰ Delays: {MIN_DELAY//60}-{MAX_DELAY//60} min | Cycle: {CYCLE_DELAY//60} min")
    print(Fore.YELLOW + f"💾 Memory Limit: {MAX_MEMORY_MB}MB | Cleanup every: {MEMORY_CLEAN_INTERVAL} ops")
    print()

def save_session(session_name, data):
    """Save session data"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
        print(Fore.GREEN + f"💾 Saved session: {session_name}")
    except Exception as e:
        print(Fore.RED + f"❌ Failed to save session: {e}")

def load_session(session_name):
    """Load session data"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception as e:
        print(Fore.RED + f"❌ Failed to load session: {e}")
    return None

async def get_last_message(client):
    """Get last message with error handling"""
    try:
        entity = await client.get_input_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=1)
        return messages[0] if messages else None
    except Exception as e:
        print(Fore.RED + f"❌ Error getting message: {e}")
        return None

async def safe_forward(client, group, message, session_name):
    """Safe message forwarding"""
    try:
        # Quick memory check
        if memory_optimizer.should_cleanup():
            memory_optimizer.perform_cleanup()
        
        await client.forward_messages(group, message)
        print(Fore.GREEN + f"[{session_name}] ✅ Sent to {getattr(group, 'title', 'GROUP')}")
        memory_optimizer.track_operation()
        return True
    except FloodWaitError as e:
        wait_time = e.seconds
        print(Fore.YELLOW + f"[{session_name}] ⏳ Flood wait: {wait_time}s")
        await asyncio.sleep(wait_time + 5)
        return False
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] 🔒 No access")
        return False
    except Exception as e:
        error_type = type(e).__name__
        print(Fore.RED + f"[{session_name}] ❌ Error: {error_type}")
        return False

async def process_groups_optimized(client, session_name, message):
    """Optimized group processing with memory management"""
    if not message:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No message to forward")
        return 0, 0
    
    groups = []
    try:
        # Limit groups to reduce memory
        async for dialog in client.iter_dialogs(limit=100):
            if dialog.is_group:
                groups.append(dialog.entity)
                
                # Check memory periodically while fetching
                if len(groups) % 20 == 0 and memory_optimizer.should_cleanup():
                    memory_optimizer.perform_cleanup()
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error getting groups: {e}")
        return 0, 0
    
    if not groups:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No groups found")
        return 0, 0
    
    total = len(groups)
    print(Fore.CYAN + f"[{session_name}] 📊 Processing {total} groups")
    
    processed = 0
    failed = 0
    
    # Process in batches
    for i in range(0, total, BATCH_SIZE):
        batch = groups[i:i + BATCH_SIZE]
        
        for group in batch:
            success = await safe_forward(client, group, message, session_name)
            if success:
                processed += 1
            else:
                failed += 1
            
            # Random delay between sends
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            if i + 1 < total:  # Not the last one
                minutes = delay / 60
                print(Fore.BLUE + f"[{session_name}] ⏰ Next in {minutes:.1f} min")
                await asyncio.sleep(delay)
        
        # Memory cleanup after each batch
        if memory_optimizer.should_cleanup():
            memory_optimizer.perform_cleanup()
    
    print(Fore.CYAN + f"[{session_name}] 📈 Summary: {processed}/{total} sent | {failed} failed")
    return processed, failed

async def setup_auto_reply(client, session_name):
    """Setup auto-reply handler"""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                print(Fore.MAGENTA + f"[{session_name}] 🤖 Auto-replied")
            except Exception:
                pass

async def manage_session_optimized(session_name, credentials):
    """Optimized session management with memory fixes"""
    session_start = datetime.now()
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        client = None
        try:
            print(Fore.CYAN + f"[{session_name}] 🚀 Starting session...")
            
            # Wait for internet
            if not await wait_for_internet():
                print(Fore.RED + f"[{session_name}] ❌ No internet, skipping...")
                break
            
            # Create client with optimized settings
            client = TelegramClient(
                StringSession(credentials["string_session"]),
                credentials["api_id"],
                credentials["api_hash"],
                device_model="Android",
                system_version="10",
                app_version="8.4",
                lang_code="en",
                system_lang_code="en-US",
                connection_retries=3,
                retry_delay=2,
                timeout=20
            )
            
            print(Fore.YELLOW + f"[{session_name}] 🔗 Connecting...")
            await client.connect()
            
            if not await client.is_user_authorized():
                print(Fore.RED + f"[{session_name}] ❌ Not authorized")
                break
            
            print(Fore.GREEN + f"[{session_name}] ✅ Connected!")
            
            # Register session for memory monitoring (FIXED)
            memory_optimizer.register_session(client)
            
            # Setup auto-reply
            await setup_auto_reply(client, session_name)
            
            # Reset retry count on successful connection
            retry_count = 0
            
            # Main operation loop
            while True:
                try:
                    # Check internet
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] 🌐 Internet lost, reconnecting...")
                        await client.disconnect()
                        await asyncio.sleep(10)
                        await client.connect()
                    
                    # Get message
                    message = await get_last_message(client)
                    
                    # Process groups
                    processed, failed = await process_groups_optimized(client, session_name, message)
                    
                    if processed == 0 and failed == 0:
                        print(Fore.YELLOW + f"[{session_name}] ⏸️ No operations, sleeping...")
                        await asyncio.sleep(60)
                        continue
                    
                    # Cycle completion
                    minutes = CYCLE_DELAY / 60
                    print(Fore.YELLOW + f"[{session_name}] ♻️ Cycle complete. Next in {minutes:.1f} min")
                    
                    # Sleep with progress updates
                    remaining = CYCLE_DELAY
                    while remaining > 0:
                        sleep_time = min(60, remaining)
                        await asyncio.sleep(sleep_time)
                        remaining -= sleep_time
                        
                        # Memory check during sleep
                        if memory_optimizer.should_cleanup():
                            memory_optimizer.perform_cleanup()
                        
                        if remaining > 0:
                            mins_left = remaining // 60
                            secs_left = remaining % 60
                            print(Fore.BLUE + f"[{session_name}] ⏳ Next cycle in: {mins_left:02d}:{secs_left:02d}")
                    
                except UserDeactivatedBanError:
                    print(Fore.RED + f"[{session_name}] 🚫 Account banned")
                    break
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] ❌ Operation error: {type(e).__name__}")
                    break
            
        except Exception as e:
            retry_count += 1
            error_msg = str(e)[:100]  # Truncate long error messages
            print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__} - {error_msg}")
            
            if retry_count < MAX_RETRIES:
                wait_time = 30 * retry_count
                print(Fore.YELLOW + f"[{session_name}] 🔄 Retrying in {wait_time} seconds...")
                await asyncio.sleep(wait_time)
        
        finally:
            # Cleanup client
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] 🔌 Disconnected")
                except:
                    pass
            
            # Force memory cleanup
            memory_optimizer.perform_cleanup()
    
    # Session ended
    session_duration = datetime.now() - session_start
    hours = session_duration.seconds // 3600
    minutes = (session_duration.seconds % 3600) // 60
    print(Fore.CYAN + f"[{session_name}] 🏁 Session ended after {hours}h {minutes}m")

async def memory_watchdog():
    """Background task to monitor and optimize memory"""
    while True:
        await asyncio.sleep(60)  # Check every minute
        
        memory_usage = memory_optimizer.get_memory_usage()
        
        if memory_optimizer.should_cleanup():
            print(Fore.YELLOW + f"🦮 Memory watchdog: {memory_usage:.1f}MB - Cleaning...")
            memory_optimizer.perform_cleanup()
        
        # Log memory status every 5 minutes
        if int(time.time()) % 300 < 60:  # Every 5 minutes
            print(Fore.CYAN + f"📊 System memory: {memory_usage:.1f}MB | "
                  f"Operations: {memory_optimizer.operation_counter}")

async def main_optimized():
    """Main function with enhanced management"""
    display_banner()
    
    # Initial memory check
    initial_memory = memory_optimizer.get_memory_usage()
    print(Fore.CYAN + f"📈 Initial memory: {initial_memory:.1f}MB")
    
    # Start memory watchdog
    watchdog_task = asyncio.create_task(memory_watchdog())
    
    try:
        # Load sessions
        num_sessions = int(input("Enter number of sessions: "))
        if num_sessions < 1:
            print(Fore.RED + "❌ At least 1 session required")
            return
        
        tasks = []
        
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = load_session(session_name)
            
            if not creds:
                print(Fore.CYAN + f"\n📝 Configuring {session_name}:")
                try:
                    creds = {
                        "api_id": int(input("API ID: ")),
                        "api_hash": input("API Hash: "),
                        "string_session": input("String Session: ")
                    }
                    save_session(session_name, creds)
                except ValueError:
                    print(Fore.RED + "❌ Invalid API ID")
                    continue
            
            # Stagger session starts
            if i > 1:
                stagger = random.uniform(5, 15)
                print(Fore.BLUE + f"⏱️ Staggering {session_name} by {stagger:.1f}s")
                await asyncio.sleep(stagger)
            
            task = asyncio.create_task(
                manage_session_optimized(session_name, creds)
            )
            tasks.append(task)
        
        print(Fore.GREEN + f"\n🚀 Starting {len(tasks)} sessions...")
        
        # Wait for all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⏹️ Stopped by user")
    except Exception as e:
        print(Fore.RED + f"💥 Fatal error: {type(e).__name__}")
        traceback.print_exc()
    finally:
        # Cancel watchdog
        watchdog_task.cancel()
        try:
            await watchdog_task
        except asyncio.CancelledError:
            pass
        
        # Final cleanup
        print(Fore.YELLOW + "🧹 Final memory cleanup...")
        memory_optimizer.perform_cleanup()
        
        final_memory = memory_optimizer.get_memory_usage()
        print(Fore.GREEN + f"✅ Cleanup complete. Final memory: {final_memory:.1f}MB")

class RestartManager:
    """Manage application restarts"""
    
    def __init__(self, max_restarts=10):
        self.max_restarts = max_restarts
        self.restart_count = 0
        self.last_restart = time.time()
    
    def can_restart(self):
        """Check if restart is allowed"""
        if self.restart_count >= self.max_restarts:
            return False
        
        # Don't restart too frequently
        if time.time() - self.last_restart < 30:
            return False
        
        return True
    
    def record_restart(self):
        """Record a restart"""
        self.restart_count += 1
        self.last_restart = time.time()
        
        # Log restart
        with open('restart_history.log', 'a') as f:
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            f.write(f"{timestamp} - Restart #{self.restart_count}\n")
        
        print(Fore.YELLOW + f"🔄 Restart #{self.restart_count}")

def signal_handler(signum, frame):
    """Handle termination signals"""
    print(Fore.YELLOW + f"\n✋ Received signal {signum}, shutting down gracefully...")
    sys.exit(0)

if __name__ == "__main__":
    # Setup signal handlers
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    restart_manager = RestartManager()
    
    # Main restart loop
    while restart_manager.can_restart():
        try:
            print(Fore.GREEN + "\n" + "="*50)
            print(Fore.GREEN + "       ORBIT ADBOT - 24/7 ENTERPRISE")
            print(Fore.GREEN + "="*50 + "\n")
            
            asyncio.run(main_optimized())
            
            # Normal exit
            print(Fore.GREEN + "🎉 Application finished normally")
            break
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n👋 User interrupted")
            break
        except SystemExit:
            print(Fore.YELLOW + "\n🛑 System exit requested")
            break
        except Exception as e:
            restart_manager.record_restart()
            
            print(Fore.RED + f"\n💥 Crash detected: {type(e).__name__}")
            
            # Clean traceback to avoid memory issues
            try:
                tb = traceback.format_exc()
                error_lines = tb.split('\n')[-5:]  # Last 5 lines
                print(Fore.RED + '\n'.join(error_lines))
            except:
                pass
            
            # Wait before restarting
            wait_time = min(300, 30 * restart_manager.restart_count)
            print(Fore.YELLOW + f"⏳ Waiting {wait_time}s before restart...")
            time.sleep(wait_time)
    
    if restart_manager.restart_count >= restart_manager.max_restarts:
        print(Fore.RED + f"\n🚫 Maximum restarts reached ({restart_manager.max_restarts})")
        print(Fore.RED + "Please check your configuration and restart manually.")
