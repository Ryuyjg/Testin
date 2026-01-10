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
from colorama import init, Fore
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
MEMORY_CLEAN_INTERVAL = 100  # Clear memory every 100 operations
HEARTBEAT_INTERVAL = 300  # Send heartbeat every 5 minutes

# Performance Optimization
MAX_CONCURRENT_TASKS = 3  # Limit concurrent operations to prevent overload
BATCH_SIZE = 5  # Process groups in batches

# Enhanced logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('orbot_advanced.log'),
        logging.StreamHandler()
    ]
)

AUTO_REPLY_MESSAGE = "Dm @OgDigital For Buy"

# Memory monitoring
class MemoryMonitor:
    def __init__(self, max_memory_mb=150):
        self.max_memory_mb = max_memory_mb
        self.process = psutil.Process(os.getpid())
        
    def check_memory(self):
        """Check current memory usage"""
        memory_info = self.process.memory_info()
        memory_mb = memory_info.rss / 1024 / 1024
        return memory_mb
    
    def is_memory_critical(self):
        """Check if memory usage is critical"""
        return self.check_memory() > self.max_memory_mb
    
    def cleanup_memory(self):
        """Force garbage collection and memory cleanup"""
        gc.collect()
        
        # Clear asyncio event loop callbacks if too many
        try:
            loop = asyncio.get_event_loop()
            if len(loop._ready) > 1000:  # Too many pending callbacks
                loop._ready.clear()
            if len(loop._scheduled) > 1000:  # Too many scheduled tasks
                loop._scheduled.clear()
        except:
            pass
            
        return self.check_memory()

# Signal handler for graceful shutdown
def signal_handler(signum, frame):
    print(Fore.YELLOW + "\nReceived shutdown signal. Cleaning up...")
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)

def check_internet_connection(host="8.8.8.8", port=53, timeout=5):
    """Enhanced internet connection check"""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except (socket.error, OSError):
        return False

async def robust_internet_check(max_attempts=10):
    """Robust internet connection check with multiple attempts"""
    for attempt in range(max_attempts):
        if check_internet_connection():
            return True
        print(Fore.YELLOW + f"Internet check attempt {attempt + 1}/{max_attempts} failed")
        await asyncio.sleep(5)
    return False

async def safe_sleep(seconds, check_interval=30):
    """Sleep with periodic internet checks and memory monitoring"""
    memory_monitor = MemoryMonitor()
    elapsed = 0
    
    while elapsed < seconds:
        sleep_time = min(check_interval, seconds - elapsed)
        await asyncio.sleep(sleep_time)
        elapsed += sleep_time
        
        # Check memory every interval
        if memory_monitor.is_memory_critical():
            print(Fore.YELLOW + "High memory usage detected, cleaning...")
            memory_monitor.cleanup_memory()

def display_banner():
    """Enhanced banner"""
    print(Fore.GREEN + """
     ██████╗ ██████╗ ██████╗ ██╗████████╗
     ██╔═══██╗██╔══██╗██╔══██╗██║╚══██╔══╝
     ██║   ██║██████╔╝██████╔╝██║   ██║   
     ██║   ██║██╔══██╗██╔══██╗██║   ██║   
     ╚██████╔╝██║  ██║██████╔╝██║   ██║   
      ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   
    """)
    print(Fore.GREEN + "ORBIT ADBOT - 24/7 Enterprise Edition")
    print(Fore.GREEN + "=" * 40)
    print(Fore.CYAN + "Features:")
    print(Fore.CYAN + "• Memory Management & Auto-Cleanup")
    print(Fore.CYAN + "• Crash Recovery & Auto-Restart")
    print(Fore.CYAN + "• Connection Stability")
    print(Fore.CYAN + "• Resource Monitoring")
    print(Fore.GREEN + "=" * 40 + "\n")

class SessionManager:
    """Enhanced session management with memory optimization"""
    
    def __init__(self, session_name, credentials):
        self.session_name = session_name
        self.credentials = credentials
        self.client = None
        self.operation_count = 0
        self.last_heartbeat = datetime.now()
        self.memory_monitor = MemoryMonitor()
        self.session_start = datetime.now()
        
    async def initialize_client(self):
        """Initialize Telegram client with retry logic"""
        for attempt in range(MAX_RETRIES):
            try:
                print(Fore.YELLOW + f"[{self.session_name}] Initializing client (Attempt {attempt + 1})...")
                
                self.client = TelegramClient(
                    StringSession(self.credentials["string_session"]),
                    self.credentials["api_id"],
                    self.credentials["api_hash"],
                    device_model="Android",
                    system_version="10",
                    app_version="8.4",
                    lang_code="en",
                    system_lang_code="en-US",
                    connection_retries=5,
                    retry_delay=3,
                    timeout=30,
                    auto_reconnect=True
                )
                
                # Set download and upload workers to reduce memory
                self.client.session.set_dc(2, '149.154.167.40', 443)
                
                await self.client.connect()
                
                if not await self.client.is_user_authorized():
                    print(Fore.RED + f"[{self.session_name}] Not authorized")
                    return False
                    
                print(Fore.GREEN + f"[{self.session_name}] Client initialized successfully")
                return True
                
            except Exception as e:
                print(Fore.RED + f"[{self.session_name}] Init attempt {attempt + 1} failed: {str(e)}")
                if attempt < MAX_RETRIES - 1:
                    await asyncio.sleep(10 ** attempt)  # Exponential backoff
                    
        return False
    
    async def send_heartbeat(self):
        """Send heartbeat to check connection"""
        try:
            if self.client and self.client.is_connected():
                await self.client.get_me()
                self.last_heartbeat = datetime.now()
                return True
        except Exception:
            return False
        return False
    
    async def safe_operation(self, coro, operation_name="operation"):
        """Execute operation with error handling and memory management"""
        try:
            # Check memory before operation
            if self.memory_monitor.is_memory_critical():
                print(Fore.YELLOW + f"[{self.session_name}] Memory critical before {operation_name}, cleaning...")
                self.memory_monitor.cleanup_memory()
            
            result = await coro
            
            # Increment operation counter
            self.operation_count += 1
            
            # Clean memory periodically
            if self.operation_count % MEMORY_CLEAN_INTERVAL == 0:
                print(Fore.BLUE + f"[{self.session_name}] Performing periodic memory cleanup...")
                mem_after = self.memory_monitor.cleanup_memory()
                print(Fore.BLUE + f"[{self.session_name}] Memory after cleanup: {mem_after:.1f} MB")
            
            # Send heartbeat periodically
            if (datetime.now() - self.last_heartbeat).total_seconds() > HEARTBEAT_INTERVAL:
                if await self.send_heartbeat():
                    print(Fore.GREEN + f"[{self.session_name}] Heartbeat sent")
            
            return result
            
        except Exception as e:
            print(Fore.RED + f"[{self.session_name}] Error in {operation_name}: {str(e)}")
            raise
    
    async def cleanup(self):
        """Cleanup resources"""
        try:
            if self.client:
                await self.client.disconnect()
                self.client = None
        except:
            pass
        
        # Force garbage collection
        gc.collect()

async def process_groups_batch(session_manager, groups, message):
    """Process groups in batches to reduce memory pressure"""
    processed = 0
    failed = 0
    
    for i in range(0, len(groups), BATCH_SIZE):
        batch = groups[i:i + BATCH_SIZE]
        batch_tasks = []
        
        for group in batch:
            task = session_manager.safe_operation(
                safe_forward(session_manager.client, group, message, session_manager.session_name),
                f"forward to {getattr(group, 'title', 'group')}"
            )
            batch_tasks.append(task)
        
        # Execute batch with limited concurrency
        results = await asyncio.gather(*batch_tasks, return_exceptions=True)
        
        for result in results:
            if isinstance(result, Exception):
                failed += 1
            elif result is True:
                processed += 1
        
        # Delay between batches
        if i + BATCH_SIZE < len(groups):
            delay = random.uniform(MIN_DELAY/2, MAX_DELAY/2)  # Smaller delay between batches
            print(Fore.BLUE + f"[{session_manager.session_name}] Batch complete. Next batch in {delay/60:.1f} min")
            await safe_sleep(delay)
    
    return processed, failed

async def safe_forward(client, group, message, session_name):
    """Safe message forwarding with flood control"""
    try:
        # Check if we can send messages
        try:
            chat = await client.get_entity(group)
            if hasattr(chat, 'default_banned_rights') and chat.default_banned_rights.send_messages:
                print(Fore.YELLOW + f"[{session_name}] Cannot send messages to {getattr(chat, 'title', 'group')}")
                return False
        except:
            pass
        
        await client.forward_messages(group, message)
        print(Fore.GREEN + f"[{session_name}] Sent to {getattr(group, 'title', 'GROUP')}")
        return True
        
    except FloodWaitError as e:
        print(Fore.YELLOW + f"[{session_name}] Flood wait: {e.seconds} seconds")
        await safe_sleep(e.seconds + 5)
        return False
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] No access to group")
        return False
    except PeerIdInvalidError:
        print(Fore.YELLOW + f"[{session_name}] Invalid group ID")
        return False
    except Exception as e:
        error_type = type(e).__name__
        if "Too Many Requests" in str(e) or "FLOOD" in str(e).upper():
            print(Fore.YELLOW + f"[{session_name}] Rate limited, backing off...")
            await safe_sleep(random.uniform(30, 60))
        else:
            print(Fore.RED + f"[{session_name}] Forward error: {error_type}")
        return False

async def main_session_loop(session_manager):
    """Main loop for a single session with enhanced reliability"""
    
    print(Fore.CYAN + f"[{session_manager.session_name}] Starting main loop...")
    
    while True:
        try:
            # Ensure internet connection
            if not await robust_internet_check():
                print(Fore.RED + f"[{session_manager.session_name}] No internet, waiting...")
                await safe_sleep(30)
                continue
            
            # Reinitialize client if needed
            if not session_manager.client or not session_manager.client.is_connected():
                if not await session_manager.initialize_client():
                    print(Fore.RED + f"[{session_manager.session_name}] Failed to initialize, waiting...")
                    await safe_sleep(60)
                    continue
            
            # Setup auto-reply
            @session_manager.client.on(events.NewMessage(incoming=True))
            async def handler(event):
                if event.is_private:
                    try:
                        await event.reply(AUTO_REPLY_MESSAGE)
                        print(Fore.MAGENTA + f"[{session_manager.session_name}] Auto-replied to DM")
                    except Exception:
                        pass
            
            # Get message to forward
            message = await session_manager.safe_operation(
                get_last_message(session_manager.client),
                "get last message"
            )
            
            if not message:
                print(Fore.YELLOW + f"[{session_manager.session_name}] No message found")
                await safe_sleep(60)
                continue
            
            # Get groups
            groups = []
            try:
                async for dialog in session_manager.client.iter_dialogs(limit=200):  # Limit to reduce memory
                    if dialog.is_group:
                        groups.append(dialog.entity)
            except Exception as e:
                print(Fore.RED + f"[{session_manager.session_name}] Error getting groups: {str(e)}")
                await safe_sleep(30)
                continue
            
            if not groups:
                print(Fore.YELLOW + f"[{session_manager.session_name}] No groups found")
                await safe_sleep(CYCLE_DELAY)
                continue
            
            print(Fore.CYAN + f"[{session_manager.session_name}] Processing {len(groups)} groups")
            
            # Process groups in batches
            processed, failed = await process_groups_batch(session_manager, groups, message)
            
            print(Fore.CYAN + f"[{session_manager.session_name}] Batch completed: {processed} sent, {failed} failed")
            
            # Cycle delay with progress indicator
            print(Fore.YELLOW + f"[{session_manager.session_name}] Cycle complete. Next cycle in {CYCLE_DELAY//60} minutes")
            
            # Sleep with progress updates
            remaining = CYCLE_DELAY
            while remaining > 0:
                sleep_time = min(60, remaining)  # Update every minute
                await safe_sleep(sleep_time)
                remaining -= sleep_time
                
                if remaining > 0:
                    hours = remaining // 3600
                    minutes = (remaining % 3600) // 60
                    print(Fore.BLUE + f"[{session_manager.session_name}] Next cycle in: {hours:02d}:{minutes:02d}")
            
            # Force cleanup after each cycle
            gc.collect()
            
        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_manager.session_name}] Account banned. Stopping.")
            break
        except KeyboardInterrupt:
            print(Fore.YELLOW + f"[{session_manager.session_name}] Stopped by user")
            break
        except Exception as e:
            print(Fore.RED + f"[{session_manager.session_name}] Critical error: {str(e)}")
            traceback.print_exc()
            
            # Cleanup before retry
            await session_manager.cleanup()
            
            # Exponential backoff
            backoff_time = min(300, 30 * (session_manager.operation_count % 10))
            print(Fore.YELLOW + f"[{session_manager.session_name}] Backing off for {backoff_time} seconds...")
            await safe_sleep(backoff_time)

async def main():
    """Main function with session management"""
    display_banner()
    
    # Check system resources
    memory_monitor = MemoryMonitor()
    initial_memory = memory_monitor.check_memory()
    print(Fore.CYAN + f"Initial memory usage: {initial_memory:.1f} MB")
    
    # Check internet
    if not await robust_internet_check():
        print(Fore.RED + "No internet connection. Exiting.")
        return
    
    try:
        # Load sessions
        num_sessions = int(input("Enter number of sessions: "))
        if num_sessions < 1:
            raise ValueError("At least 1 session required")
        
        session_managers = []
        
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = load_session(session_name)
            
            if not creds:
                print(Fore.CYAN + f"\nConfiguring {session_name}:")
                creds = {
                    "api_id": int(input("API ID: ")),
                    "api_hash": input("API Hash: "),
                    "string_session": input("String Session: ")
                }
                save_session(session_name, creds)
            
            manager = SessionManager(session_name, creds)
            session_managers.append(manager)
        
        # Run sessions with staggered start
        print(Fore.GREEN + f"\nStarting {len(session_managers)} sessions...")
        
        tasks = []
        for i, manager in enumerate(session_managers):
            # Stagger start to avoid simultaneous connections
            if i > 0:
                await asyncio.sleep(random.uniform(5, 15))
            
            task = asyncio.create_task(main_session_loop(manager))
            task.set_name(f"Session-{manager.session_name}")
            tasks.append(task)
        
        # Monitor tasks
        while True:
            await asyncio.sleep(60)
            
            # Check memory periodically
            current_memory = memory_monitor.check_memory()
            if current_memory > 200:  # If over 200MB
                print(Fore.YELLOW + f"High system memory: {current_memory:.1f} MB")
                memory_monitor.cleanup_memory()
            
            # Log status
            active_tasks = sum(1 for t in tasks if not t.done())
            print(Fore.CYAN + f"Active sessions: {active_tasks}/{len(tasks)} | Memory: {current_memory:.1f} MB")
            
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nShutting down gracefully...")
    except Exception as e:
        print(Fore.RED + f"Fatal error: {str(e)}")
        traceback.print_exc()
    finally:
        # Cleanup all sessions
        print(Fore.YELLOW + "Cleaning up resources...")
        for manager in session_managers:
            await manager.cleanup()
        
        # Final memory cleanup
        gc.collect()
        print(Fore.GREEN + "Cleanup complete.")

# Helper functions (keep from original)
def save_session(session_name, data):
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)
    except Exception:
        pass

def load_session(session_name):
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

async def get_last_message(client):
    try:
        entity = await client.get_input_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=1)
        return messages[0] if messages else None
    except Exception:
        return None

class ApplicationMonitor:
    """Application level monitoring and restart"""
    
    def __init__(self):
        self.start_time = datetime.now()
        self.restart_count = 0
        self.max_restarts = 20
        self.last_restart = datetime.now()
    
    def should_restart(self):
        """Check if application should restart"""
        # Don't restart too frequently
        if (datetime.now() - self.last_restart).total_seconds() < 60:
            return False
        
        # Limit total restarts
        if self.restart_count >= self.max_restarts:
            return False
        
        return True
    
    def record_restart(self):
        """Record restart attempt"""
        self.restart_count += 1
        self.last_restart = datetime.now()
        
        # Write restart log
        with open('restart_log.txt', 'a') as f:
            f.write(f"{datetime.now()} - Restart {self.restart_count}\n")

if __name__ == "__main__":
    monitor = ApplicationMonitor()
    
    while monitor.should_restart():
        try:
            print(Fore.GREEN + f"\n{'='*50}")
            print(Fore.GREEN + f"ORBIT ADBOT - Starting (Attempt {monitor.restart_count + 1})")
            print(Fore.GREEN + f"{'='*50}\n")
            
            asyncio.run(main())
            
            # Normal exit
            print(Fore.GREEN + "Application finished normally")
            break
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nApplication stopped by user")
            break
        except Exception as e:
            monitor.record_restart()
            print(Fore.RED + f"\nApplication crashed: {type(e).__name__}")
            traceback.print_exc()
            
            # Wait before restarting
            wait_time = min(300, 30 * monitor.restart_count)
            print(Fore.YELLOW + f"Restarting in {wait_time} seconds...")
            time.sleep(wait_time)
    
    if monitor.restart_count >= monitor.max_restarts:
        print(Fore.RED + "Maximum restart attempts reached. Please check your configuration.")
