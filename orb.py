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
import weakref
from telethon import TelegramClient, events
from telethon.sessions import StringSession
from telethon.tl.types import Chat, Channel
from telethon.errors import (
    UserDeactivatedBanError,
    FloodWaitError,
    ChannelPrivateError,
    ChatWriteForbiddenError,
    PeerIdInvalidError
)
from colorama import init, Fore, Style, Back
from datetime import datetime, timedelta

# Initialize colorama
init(autoreset=True)

# ============= CONFIGURATION =============
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "Orgjhonysins"

# Optimized timing
MIN_DELAY = 60    # 1 minute between groups
MAX_DELAY = 120   # 2 minutes between groups  
CYCLE_DELAY = 1200  # 20 minutes between cycles
BATCH_SIZE = 5    # Process groups in batches

# Memory protection
MEMORY_LIMIT_MB = 8000  # 8GB for VPS with swap
GC_INTERVAL = 30        # Clean every 30 operations
MEMORY_CLEAN_INTERVAL = 300  # Force cleanup every 5 minutes

# Connection settings
MAX_CONNECT_RETRIES = 3
CONNECT_TIMEOUT = 20

# Logging
class ColorFormatter(logging.Formatter):
    """Colorful logging formatter"""
    COLORS = {
        'DEBUG': Fore.CYAN,
        'INFO': Fore.GREEN,
        'WARNING': Fore.YELLOW,
        'ERROR': Fore.RED,
        'CRITICAL': Fore.RED + Back.WHITE
    }
    
    def format(self, record):
        color = self.COLORS.get(record.levelname, Fore.WHITE)
        record.msg = f"{color}{record.msg}{Style.RESET_ALL}"
        return super().format(record)

logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @OgDigital For Buy"

# ============= MEMORY MANAGEMENT =============
class MemoryOptimizer:
    """Advanced memory management with parallel cleanup"""
    
    def __init__(self):
        self.operation_count = 0
        self.last_cleanup = time.time()
        self.group_cache = weakref.WeakValueDictionary()
        self.message_cache = {}
        self.session_refs = weakref.WeakSet()
    
    def register_session(self, session):
        """Register session for tracking"""
        self.session_refs.add(weakref.ref(session))
    
    def should_cleanup(self, force=False):
        """Check if cleanup is needed"""
        current_time = time.time()
        
        # Force cleanup every 5 minutes
        if force or (current_time - self.last_cleanup) >= MEMORY_CLEAN_INTERVAL:
            return True
        
        # Cleanup every N operations
        self.operation_count += 1
        if self.operation_count % GC_INTERVAL == 0:
            return True
        
        return False
    
    async def parallel_cleanup(self):
        """Run cleanup in parallel without blocking"""
        cleanup_tasks = []
        
        # 1. Clear caches in background
        cleanup_tasks.append(self._clear_caches())
        
        # 2. Run GC in background
        cleanup_tasks.append(self._run_gc())
        
        # 3. Clear imports in background
        cleanup_tasks.append(self._clear_imports())
        
        # Run all cleanup tasks concurrently
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.last_cleanup = time.time()
        self.operation_count = 0
        
        return True
    
    async def _clear_caches(self):
        """Clear various caches"""
        # Clear group cache
        self.group_cache.clear()
        
        # Clear message cache (keep only last 10)
        if len(self.message_cache) > 10:
            keys = list(self.message_cache.keys())
            for key in keys[:-10]:
                self.message_cache.pop(key, None)
        
        # Clear telethon caches if possible
        try:
            import telethon
            telethon.client.downloads._download_cache.clear()
        except:
            pass
        
        print(Fore.CYAN + "🧹 Cache cleared")
    
    async def _run_gc(self):
        """Run garbage collection"""
        # Collect generation 2
        collected = gc.collect(2)
        
        # Collect generation 1
        collected += gc.collect(1)
        
        # Collect generation 0
        collected += gc.collect(0)
        
        if collected > 0:
            print(Fore.CYAN + f"🗑️  GC collected {collected} objects")
    
    async def _clear_imports(self):
        """Clear import caches"""
        modules_to_clear = ['telethon', 'asyncio', 'json']
        
        for module_name in modules_to_clear:
            try:
                if module_name in sys.modules:
                    # Clear module attributes
                    module = sys.modules[module_name]
                    for attr in list(module.__dict__.keys()):
                        if not attr.startswith('__'):
                            try:
                                delattr(module, attr)
                            except:
                                pass
            except:
                pass
    
    def get_memory_info(self):
        """Get current memory usage"""
        try:
            import psutil
            process = psutil.Process()
            memory_info = process.memory_info()
            return {
                'rss': memory_info.rss / 1024 / 1024,  # MB
                'vms': memory_info.vms / 1024 / 1024,  # MB
                'percent': process.memory_percent()
            }
        except ImportError:
            return {'rss': 0, 'vms': 0, 'percent': 0}

# ============= GROUP CACHE =============
class GroupCache:
    """Cache group information for faster access"""
    
    def __init__(self):
        self.cache = {}
        self.last_updated = {}
        self.cache_ttl = 3600  # 1 hour TTL
    
    def get_group_name(self, group):
        """Get group name with caching"""
        group_id = self._get_group_id(group)
        
        # Check cache
        if group_id in self.cache:
            if time.time() - self.last_updated.get(group_id, 0) < self.cache_ttl:
                return self.cache[group_id]
        
        # Extract name
        name = self._extract_group_name(group)
        
        # Update cache
        self.cache[group_id] = name
        self.last_updated[group_id] = time.time()
        
        return name
    
    def _get_group_id(self, group):
        """Get unique group ID"""
        if hasattr(group, 'id'):
            return f"{group.__class__.__name__}_{group.id}"
        return str(id(group))
    
    def _extract_group_name(self, group):
        """Extract group name from various types"""
        try:
            if hasattr(group, 'title'):
                return group.title
            elif hasattr(group, 'username'):
                return f"@{group.username}"
            elif hasattr(group, 'first_name'):
                name = group.first_name or ""
                if hasattr(group, 'last_name') and group.last_name:
                    name += f" {group.last_name}"
                return name.strip() or "Unknown"
            else:
                return "Group"
        except:
            return "Group"
    
    def clear_old_entries(self):
        """Clear old cache entries"""
        current_time = time.time()
        to_remove = []
        
        for group_id, last_update in self.last_updated.items():
            if current_time - last_update > self.cache_ttl * 2:  # 2x TTL
                to_remove.append(group_id)
        
        for group_id in to_remove:
            self.cache.pop(group_id, None)
            self.last_updated.pop(group_id, None)
        
        if to_remove:
            print(Fore.CYAN + f"🧼 Cleared {len(to_remove)} old cache entries")

# ============= SYSTEM OPTIMIZATION =============
def optimize_system():
    """Optimize system settings for VPS"""
    try:
        # Set memory limit
        memory_bytes = MEMORY_LIMIT_MB * 1024 * 1024
        resource.setrlimit(resource.RLIMIT_AS, (memory_bytes, memory_bytes))
        
        # Increase open files limit
        resource.setrlimit(resource.RLIMIT_NOFILE, (65535, 65535))
        
        # Ignore broken pipe signals
        signal.signal(signal.SIGPIPE, signal.SIG_IGN)
        
        # Optimize Python
        sys.setrecursionlimit(100000)
        gc.set_threshold(70000, 100, 100)
        
        print(Fore.GREEN + "⚙️  System optimized")
        return True
    except Exception as e:
        print(Fore.YELLOW + f"⚠️  System optimization warning: {e}")
        return False

# ============= NETWORK UTILITIES =============
async def check_internet_async():
    """Async internet check"""
    try:
        # Try multiple DNS servers
        readers = []
        for host in ["8.8.8.8", "1.1.1.1", "208.67.222.222"]:
            try:
                reader, writer = await asyncio.wait_for(
                    asyncio.open_connection(host, 53),
                    timeout=3
                )
                writer.close()
                await writer.wait_closed()
                return True
            except:
                continue
        return False
    except:
        return False

# ============= TELEGRAM OPERATIONS =============
async def get_groups_batch(client, limit=100):
    """Get groups in batches to reduce memory"""
    groups = []
    try:
        async for dialog in client.iter_dialogs(limit=limit):
            if dialog.is_group:
                groups.append(dialog.entity)
                
                # Yield every 20 groups to prevent memory buildup
                if len(groups) >= 20:
                    yield groups
                    groups = []
        
        # Yield remaining groups
        if groups:
            yield groups
    except Exception as e:
        print(Fore.RED + f"Error getting groups: {e}")
        if groups:
            yield groups

async def forward_to_group_batch(client, groups_batch, message, session_name, group_cache):
    """Forward message to a batch of groups"""
    results = []
    
    for group in groups_batch:
        try:
            await client.forward_messages(group, message)
            
            # Get group name from cache
            group_name = group_cache.get_group_name(group)
            print(Fore.GREEN + f"[{session_name}] ✅ Sent to: {group_name}")
            
            results.append(True)
            
        except FloodWaitError as e:
            print(Fore.RED + f"[{session_name}] ⏳ Flood: {e.seconds}s")
            await asyncio.sleep(e.seconds)
            results.append(False)
            
        except (ChannelPrivateError, ChatWriteForbiddenError):
            group_name = group_cache.get_group_name(group)
            print(Fore.YELLOW + f"[{session_name}] ⚠️  No access: {group_name}")
            results.append(False)
            
        except PeerIdInvalidError:
            print(Fore.RED + f"[{session_name}] ❌ Invalid peer")
            results.append(False)
            
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__}")
            results.append(False)
    
    return results

async def process_groups_parallel(client, session_name, message, memory_optimizer, group_cache):
    """Process groups in parallel batches"""
    if not message:
        print(Fore.YELLOW + f"[{session_name}] ⚠️  No message")
        return 0, 0
    
    total_groups = 0
    total_sent = 0
    
    print(Fore.CYAN + f"[{session_name}] 📊 Loading groups...")
    
    # Process groups in batches
    async for groups_batch in get_groups_batch(client, limit=150):
        if not groups_batch:
            continue
        
        total_groups += len(groups_batch)
        
        # Forward to batch
        results = await forward_to_group_batch(client, groups_batch, message, session_name, group_cache)
        total_sent += sum(1 for r in results if r)
        
        # Memory cleanup check
        if memory_optimizer.should_cleanup():
            print(Fore.CYAN + f"[{session_name}] 🧹 Running parallel cleanup...")
            await memory_optimizer.parallel_cleanup()
            group_cache.clear_old_entries()
        
        # Delay between batches (except last batch)
        if len(groups_batch) >= 20:  # Only delay if we got a full batch
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            minutes = delay / 60
            
            # Show progress
            mem_info = memory_optimizer.get_memory_info()
            mem_percent = mem_info.get('percent', 0)
            
            print(Fore.BLUE + f"[{session_name}] ⏰ Next batch in {minutes:.1f}m | Sent: {total_sent}/{total_groups} | Mem: {mem_percent:.1f}%")
            await asyncio.sleep(delay)
    
    return total_sent, total_groups

# ============= SESSION MANAGEMENT =============
async def manage_session_optimized(session_name, credentials):
    """Optimized session management"""
    memory_optimizer = MemoryOptimizer()
    group_cache = GroupCache()
    session_stats = {
        'cycles': 0,
        'total_sent': 0,
        'total_groups': 0,
        'start_time': time.time()
    }
    
    print(Fore.CYAN + f"\n[{session_name}] 🚀 Starting...")
    
    while True:
        client = None
        try:
            # Internet check
            if not await check_internet_async():
                print(Fore.YELLOW + f"[{session_name}] 🌐 Waiting for internet...")
                await asyncio.sleep(10)
                continue
            
            # Create optimized client
            client = TelegramClient(
                StringSession(credentials["string_session"]),
                credentials["api_id"],
                credentials["api_hash"],
                connection_retries=2,
                request_retries=1,
                flood_sleep_threshold=60,
                device_model="Android",
                system_version="10",
                app_version="8.4",
                lang_code="en",
                system_lang_code="en-US"
            )
            
            # Quick connect
            print(Fore.YELLOW + f"[{session_name}] 🔗 Connecting...")
            await client.connect()
            
            if not await client.is_user_authorized():
                print(Fore.RED + f"[{session_name}] ❌ Not authorized")
                break
            
            print(Fore.GREEN + f"[{session_name}] ✅ Connected!")
            
            # Register session with memory optimizer
            memory_optimizer.register_session(client)
            
            # Get target entity
            try:
                target_entity = await client.get_input_entity(TARGET_USER)
            except:
                print(Fore.RED + f"[{session_name}] ❌ Target user not found")
                await asyncio.sleep(300)
                continue
            
            # Main cycle loop
            while True:
                cycle_start = time.time()
                session_stats['cycles'] += 1
                
                print(Fore.MAGENTA + f"\n[{session_name}] 🔄 Cycle {session_stats['cycles']} started")
                
                # Get last message
                try:
                    messages = await client.get_messages(target_entity, limit=1)
                    message = messages[0] if messages else None
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] ❌ Failed to get message: {e}")
                    message = None
                
                if message:
                    # Process groups
                    sent, total = await process_groups_parallel(
                        client, session_name, message, 
                        memory_optimizer, group_cache
                    )
                    
                    session_stats['total_sent'] += sent
                    session_stats['total_groups'] += total
                    
                    # Show cycle summary
                    cycle_time = time.time() - cycle_start
                    total_time = time.time() - session_stats['start_time']
                    
                    print(Fore.GREEN + f"[{session_name}] ✅ Cycle complete!")
                    print(Fore.CYAN + f"[{session_name}] 📈 Stats: Sent {sent}/{total} this cycle")
                    print(Fore.CYAN + f"[{session_name}] 🕐 Time: {cycle_time:.1f}s | Total: {total_time:.1f}s")
                    print(Fore.CYAN + f"[{session_name}] 📊 Total: {session_stats['total_sent']} sent to {session_stats['total_groups']} groups")
                
                # Sleep between cycles
                print(Fore.YELLOW + f"[{session_name}] 💤 Sleeping {CYCLE_DELAY//60} minutes...")
                
                # Sleep with periodic memory checks
                for i in range(CYCLE_DELAY // 60):
                    # Force cleanup every 5 minutes
                    if i % 5 == 0:
                        print(Fore.CYAN + f"[{session_name}] 🧹 Scheduled cleanup...")
                        await memory_optimizer.parallel_cleanup()
                        group_cache.clear_old_entries()
                    
                    await asyncio.sleep(60)
                
        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_name}] ⛔ Account banned")
            break
            
        except KeyboardInterrupt:
            print(Fore.YELLOW + f"[{session_name}] ⏹️  Stopped by user")
            break
            
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__}")
            print(Fore.YELLOW + f"[{session_name}] 🔄 Retrying in 30 seconds...")
            await asyncio.sleep(30)
            
        finally:
            # Clean disconnect
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] 🔌 Disconnected")
                except:
                    pass
    
    # Final stats
    total_time = time.time() - session_stats['start_time']
    hours = total_time / 3600
    
    print(Fore.MAGENTA + f"\n[{session_name}] 📊 FINAL STATS:")
    print(Fore.CYAN + f"[{session_name}] ⏱️  Total time: {hours:.2f} hours")
    print(Fore.CYAN + f"[{session_name}] 🔄 Cycles: {session_stats['cycles']}")
    print(Fore.CYAN + f"[{session_name}] 📤 Sent: {session_stats['total_sent']} messages")
    print(Fore.CYAN + f"[{session_name}] 👥 Groups: {session_stats['total_groups']}")

# ============= MAIN FUNCTION =============
async def main():
    """Main function"""
    print(Fore.CYAN + Style.BRIGHT + """
    ╔══════════════════════════════════════════╗
    ║     ORBIT ADBOT - PARALLEL EDITION       ║
    ║   50+ SESSIONS • MEMORY SAFE • FAST      ║
    ╚══════════════════════════════════════════╝
    """)
    
    # Optimize system
    optimize_system()
    
    # Check internet
    print(Fore.YELLOW + "🌐 Checking internet connection...")
    if not await check_internet_async():
        print(Fore.RED + "❌ No internet connection")
        return
    
    print(Fore.GREEN + "✅ Internet connected")
    
    try:
        # Get session count
        try:
            num_sessions = int(input(Fore.CYAN + "\n📝 Enter number of sessions: " + Fore.WHITE))
            if num_sessions < 1:
                raise ValueError("At least 1 session required")
        except ValueError:
            print(Fore.RED + "❌ Invalid number")
            return
        
        # Load or configure sessions
        sessions = []
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = None
            
            # Try to load from file
            file_path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
            if os.path.exists(file_path):
                try:
                    with open(file_path, 'r') as f:
                        creds = json.load(f)
                    print(Fore.GREEN + f"📂 Loaded: {session_name}")
                except:
                    pass
            
            # If not loaded, configure
            if not creds:
                print(Fore.CYAN + f"\n⚙️  Configuring {session_name}:")
                try:
                    creds = {
                        "api_id": int(input("API ID: ")),
                        "api_hash": input("API Hash: "),
                        "string_session": input("String Session: ")
                    }
                    
                    # Save to file
                    with open(file_path, 'w') as f:
                        json.dump(creds, f, indent=2)
                    
                    print(Fore.GREEN + f"💾 Saved: {session_name}")
                except Exception as e:
                    print(Fore.RED + f"❌ Error configuring {session_name}: {e}")
                    continue
            
            sessions.append((session_name, creds))
        
        if not sessions:
            print(Fore.RED + "❌ No sessions to run")
            return
        
        print(Fore.GREEN + f"\n✅ Ready to run {len(sessions)} sessions")
        print(Fore.YELLOW + "🚀 Starting all sessions in parallel...\n")
        
        # Start all sessions
        tasks = []
        for session_name, creds in sessions:
            task = asyncio.create_task(
                manage_session_optimized(session_name, creds)
            )
            tasks.append(task)
            
            # Stagger startup to prevent connection flooding
            await asyncio.sleep(random.uniform(1, 3))
        
        # Wait for all tasks
        await asyncio.gather(*tasks, return_exceptions=True)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n⏹️  Stopped by user")
    except Exception as e:
        print(Fore.RED + f"❌ Fatal error: {e}")

# ============= ENTRY POINT =============
if __name__ == "__main__":
    # Set up asyncio for better performance
    if sys.platform != 'win32':
        # Use uvloop if available
        try:
            import uvloop
            asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            print(Fore.GREEN + "⚡ Using UVLoop for maximum performance")
        except ImportError:
            print(Fore.YELLOW + "⚠️  Install uvloop for better performance: pip install uvloop")
    
    # Create event loop
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    
    # Auto-restart mechanism
    restart_count = 0
    max_restarts = 3
    
    while restart_count < max_restarts:
        try:
            loop.run_until_complete(main())
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
    
    # Clean shutdown
    try:
        loop.close()
    except:
        pass
    
    print(Fore.CYAN + "\n✨ Orbit AdBot terminated")

# Install required packages:
# pip install uvloop psutil
