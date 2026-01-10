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
from datetime import datetime
import signal
import sys

# Initialize colorama
init(autoreset=True)

# Configuration
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "Orgjhonysins"

# Timing Settings
MIN_DELAY = 60   # 1 minute
MAX_DELAY = 120  # 2 minutes
CYCLE_DELAY = 1200  # 20 minutes
MAX_RETRIES = 3

# Memory Settings
MEMORY_CHECK_INTERVAL = 50  # Check memory every 50 operations
MAX_MEMORY_MB = 150  # Warning threshold
BATCH_SIZE = 5  # Groups per batch

AUTO_REPLY_MESSAGE = "Dm @OgDigital For Buy"

# Simple logging
logging.basicConfig(level=logging.WARNING)

class SimpleMemoryManager:
    """Simple memory management without weakref complications"""
    
    def __init__(self):
        self.process = psutil.Process(os.getpid())
        self.operation_count = 0
        self.session_ids = set()  # Just track session IDs instead of objects
        
    def get_memory_usage(self):
        """Get memory usage in MB"""
        try:
            return self.process.memory_info().rss / 1024 / 1024
        except:
            return 0
    
    def check_and_clean(self):
        """Check memory and clean if needed"""
        memory = self.get_memory_usage()
        self.operation_count += 1
        
        # Clean if memory is high or too many operations
        if memory > MAX_MEMORY_MB or self.operation_count >= MEMORY_CHECK_INTERVAL:
            return self.force_cleanup(memory)
        
        return memory
    
    def force_cleanup(self, memory_before=None):
        """Force memory cleanup"""
        if memory_before is None:
            memory_before = self.get_memory_usage()
        
        # Clear session tracking
        self.session_ids.clear()
        
        # Force garbage collection
        gc.collect(2)  # Generation 2
        
        memory_after = self.get_memory_usage()
        self.operation_count = 0
        
        if memory_before > memory_after:
            print(Fore.CYAN + f"🧹 Memory cleaned: {memory_before:.1f}MB → {memory_after:.1f}MB")
        
        return memory_after
    
    def track_session(self, session_name):
        """Simply track session name"""
        self.session_ids.add(session_name)

# Global memory manager
memory_manager = SimpleMemoryManager()

def check_internet_connection():
    """Check internet connection"""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=5)
        return True
    except:
        return False

async def wait_for_internet():
    """Wait for internet with timeout"""
    for i in range(30):  # 5 minutes max
        if check_internet_connection():
            return True
        await asyncio.sleep(10)
    return False

def display_banner():
    """Simple banner"""
    print(Fore.GREEN + """
    ╔══════════════════════════════╗
    ║       ORBIT ADBOT 24/7       ║
    ║    No Weakrefs Edition       ║
    ╚══════════════════════════════╝
    """)
    print(Fore.CYAN + "✅ Fixed memory management")
    print(Fore.CYAN + "✅ No weak reference errors")
    print(Fore.CYAN + "✅ Stable 24/7 operation")
    print()

def save_session(session_name, data):
    """Save session"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        with open(path, 'w') as f:
            json.dump(data, f)
    except:
        pass

def load_session(session_name):
    """Load session"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except:
        pass
    return None

async def get_last_message(client):
    """Get last message from target"""
    try:
        entity = await client.get_input_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=1)
        return messages[0] if messages else None
    except:
        return None

async def safe_forward(client, group, message, session_name):
    """Forward message with error handling"""
    try:
        # Check memory
        memory_manager.check_and_clean()
        
        await client.forward_messages(group, message)
        print(Fore.GREEN + f"[{session_name}] ✅ Sent")
        return True
        
    except FloodWaitError as e:
        print(Fore.YELLOW + f"[{session_name}] ⏳ Wait {e.seconds}s")
        await asyncio.sleep(e.seconds + 5)
        return False
    except (ChannelPrivateError, ChatWriteForbiddenError):
        return False
    except Exception as e:
        error_name = type(e).__name__
        if "Too Many" in str(e) or "Flood" in str(e):
            await asyncio.sleep(30)
        return False

async def process_groups_safely(client, session_name, message):
    """Process groups with memory safety"""
    if not message:
        return 0, 0
    
    groups = []
    try:
        async for dialog in client.iter_dialogs(limit=100):
            if dialog.is_group:
                groups.append(dialog.entity)
    except:
        return 0, 0
    
    if not groups:
        return 0, 0
    
    processed = 0
    total = len(groups)
    
    for i, group in enumerate(groups):
        if await safe_forward(client, group, message, session_name):
            processed += 1
        
        # Delay between groups (except last)
        if i < total - 1:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            minutes = delay / 60
            print(Fore.BLUE + f"[{session_name}] Next in {minutes:.1f} min")
            await asyncio.sleep(delay)
        
        # Memory check every 10 groups
        if i % 10 == 0:
            memory_manager.check_and_clean()
    
    failed = total - processed
    print(Fore.CYAN + f"[{session_name}] 📊 {processed}/{total} sent")
    return processed, failed

async def setup_auto_reply(client, session_name):
    """Setup auto-reply"""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                print(Fore.MAGENTA + f"[{session_name}] 🤖 Auto-reply")
            except:
                pass

async def run_session(session_name, credentials):
    """Main session loop - SIMPLIFIED and FIXED"""
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        client = None
        try:
            print(Fore.CYAN + f"[{session_name}] 🚀 Starting...")
            
            # Track session (NO WEAKREFS!)
            memory_manager.track_session(session_name)
            
            # Wait for internet
            if not check_internet_connection():
                print(Fore.YELLOW + f"[{session_name}] Waiting for internet...")
                if not await wait_for_internet():
                    retry_count += 1
                    continue
            
            # Create client
            client = TelegramClient(
                StringSession(credentials["string_session"]),
                credentials["api_id"],
                credentials["api_hash"],
                device_model="Android",
                system_version="10",
                app_version="8.4"
            )
            
            print(Fore.YELLOW + f"[{session_name}] 🔗 Connecting...")
            await client.connect()
            
            if not await client.is_user_authorized():
                print(Fore.RED + f"[{session_name}] ❌ Not authorized")
                break
            
            print(Fore.GREEN + f"[{session_name}] ✅ Connected!")
            
            # Setup auto-reply
            await setup_auto_reply(client, session_name)
            
            # Main loop
            while True:
                # Check connection
                if not check_internet_connection():
                    print(Fore.YELLOW + f"[{session_name}] Reconnecting...")
                    await client.disconnect()
                    await asyncio.sleep(5)
                    await client.connect()
                
                # Get message
                message = await get_last_message(client)
                
                # Process groups
                processed, failed = await process_groups_safely(client, session_name, message)
                
                # Cycle delay
                print(Fore.YELLOW + f"[{session_name}] ⏸️ Resting {CYCLE_DELAY//60} min")
                
                # Sleep with memory checks
                for _ in range(CYCLE_DELAY // 30):
                    await asyncio.sleep(30)
                    memory_manager.check_and_clean()
                
        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_name}] 🚫 Banned")
            break
        except KeyboardInterrupt:
            raise
        except Exception as e:
            retry_count += 1
            error_type = type(e).__name__
            print(Fore.RED + f"[{session_name}] ❌ {error_type}")
            
            if retry_count < MAX_RETRIES:
                wait = retry_count * 30
                print(Fore.YELLOW + f"[{session_name}] 🔄 Retry in {wait}s")
                await asyncio.sleep(wait)
        
        finally:
            if client:
                try:
                    await client.disconnect()
                except:
                    pass
            
            # Memory cleanup
            memory_manager.force_cleanup()
    
    print(Fore.RED + f"[{session_name}] 🏁 Stopped after {retry_count} retries")

async def memory_monitor():
    """Background memory monitor"""
    while True:
        await asyncio.sleep(60)
        memory = memory_manager.get_memory_usage()
        
        if memory > MAX_MEMORY_MB:
            print(Fore.YELLOW + f"⚠️ High memory: {memory:.1f}MB")
            memory_manager.force_cleanup(memory)

async def main():
    """Main function"""
    display_banner()
    
    # Start memory monitor
    monitor_task = asyncio.create_task(memory_monitor())
    
    try:
        # Get session count
        try:
            num_sessions = int(input("Sessions to run: "))
            if num_sessions < 1:
                return
        except:
            return
        
        # Load or create sessions
        tasks = []
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = load_session(session_name)
            
            if not creds:
                print(Fore.CYAN + f"\nSetup {session_name}:")
                try:
                    creds = {
                        "api_id": int(input("API ID: ")),
                        "api_hash": input("API Hash: "),
                        "string_session": input("String Session: ")
                    }
                    save_session(session_name, creds)
                except:
                    print(Fore.RED + "❌ Invalid input")
                    continue
            
            # Stagger starts
            if i > 1:
                await asyncio.sleep(random.uniform(2, 5))
            
            # Start session
            task = asyncio.create_task(run_session(session_name, creds))
            tasks.append(task)
        
        print(Fore.GREEN + f"\n🚀 Running {len(tasks)} sessions...")
        
        # Wait for all sessions
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⏹️ Stopped")
    except Exception as e:
        print(Fore.RED + f"💥 Error: {e}")
    finally:
        # Stop monitor
        monitor_task.cancel()
        try:
            await monitor_task
        except:
            pass
        
        # Final cleanup
        memory_manager.force_cleanup()
        print(Fore.GREEN + "✅ Clean shutdown")

def signal_handler(signum, frame):
    """Handle signals"""
    print(Fore.YELLOW + f"\n🛑 Signal {signum}, exiting...")
    sys.exit(0)

if __name__ == "__main__":
    # Setup signals
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Auto-restart loop
    restart_count = 0
    max_restarts = 10
    
    while restart_count < max_restarts:
        try:
            print(Fore.GREEN + f"\n{'='*40}")
            print(Fore.GREEN + f"   STARTUP #{restart_count + 1}")
            print(Fore.GREEN + f"{'='*40}")
            
            asyncio.run(main())
            
            # Normal exit
            print(Fore.GREEN + "🎉 Script completed")
            break
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n👋 User exit")
            break
        except SystemExit:
            break
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"\n💥 Crash: {type(e).__name__}")
            
            if restart_count < max_restarts:
                wait = min(300, restart_count * 30)
                print(Fore.YELLOW + f"🔄 Restarting in {wait}s...")
                time.sleep(wait)
    
    if restart_count >= max_restarts:
        print(Fore.RED + f"\n🚫 Max restarts ({max_restarts}) reached")
