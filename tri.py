#!/usr/bin/env python3
import asyncio
import os
import json
import random
import logging
import socket
import time
from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from telethon.errors import (
    UserDeactivatedBanError,
    FloodWaitError,
    ChannelPrivateError,
    ChatWriteForbiddenError,
    PeerIdInvalidError,
    AuthKeyError,
    SecurityError,
    RPCError
)
from colorama import init, Fore
from datetime import datetime, timedelta
import aiohttp
from typing import Optional, Dict, List

# Initialize colorama
init(autoreset=True)

# Configuration - Optimized for Termux
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "Og_Digital"  # Target username for DM forwarding

# POWERFUL TIMING SETTINGS - OPTIMIZED FOR 100+ SESSIONS
MIN_DELAY = 90   # 1.5 minutes minimum delay between groups
MAX_DELAY = 150  # 2.5 minutes maximum delay between groups
CYCLE_DELAY = 1500  # 25 minutes between full cycles
MAX_RETRIES = 3  # Maximum retry attempts
SESSION_RECONNECT_DELAY = 5  # Seconds between session reconnection attempts

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @Og_Digital For Buy"

# Global session manager
session_manager = {}

def check_internet_connection(host="8.8.8.8", port=53, timeout=5):
    """Check internet connection with timeout"""
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except socket.error:
        return False

async def wait_for_internet():
    """Wait until internet connection is available"""
    print(Fore.YELLOW + "Waiting for internet connection...")
    while not check_internet_connection():
        print(Fore.RED + "No internet connection. Retrying in 10 seconds...")
        await asyncio.sleep(10)
    print(Fore.GREEN + "Internet connection available!")

def display_banner():
    """Powerful banner for Termux"""
    print(Fore.CYAN + """
    ╔═══════════════════════════════════════╗
    ║        🔥 ORBIT ADBOT v4.0 🔥        ║
    ║    ULTIMATE POWER - NO LIMITS        ║
    ║    100+ SESSIONS SIMULTANEOUS        ║
    ╚═══════════════════════════════════════╝
    """)
    print(Fore.GREEN + "⚡ POWER MODE ACTIVATED ⚡")
    print(Fore.YELLOW + f"• Group Delay: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"• Cycle Delay: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + "• Concurrent Sessions: UNLIMITED")
    print(Fore.YELLOW + "• Auto-Reconnect: ENABLED\n")

def save_session(session_name: str, data: dict):
    """Save session data"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        with open(path, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass

def load_session(session_name: str) -> Optional[dict]:
    """Load session data"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

async def get_last_message(client: TelegramClient) -> Optional[types.Message]:
    """Get last message from target user"""
    for attempt in range(3):
        try:
            entity = await client.get_input_entity(TARGET_USER)
            messages = await client.get_messages(entity, limit=1)
            return messages[0] if messages else None
        except (PeerIdInvalidError, ChannelPrivateError):
            return None
        except Exception:
            await asyncio.sleep(2)
    return None

async def safe_forward(client: TelegramClient, group, message, session_name: str) -> bool:
    """Safe message forwarding with session protection"""
    try:
        await client.forward_messages(group, message)
        print(Fore.GREEN + f"[{session_name}] ✅ Sent to {getattr(group, 'title', 'GROUP')}")
        return True
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No access")
        return False
    except FloodWaitError as e:
        print(Fore.RED + f"[{session_name}] ⏳ Flood wait: {e.seconds}s")
        await asyncio.sleep(e.seconds)
        return False
    except (SecurityError, AuthKeyError, RPCError) as e:
        print(Fore.RED + f"[{session_name}] 🔒 Session error: {type(e).__name__}")
        # Mark session for reconnection
        if session_name in session_manager:
            session_manager[session_name]['needs_reconnect'] = True
        return False
    except Exception as e:
        error_msg = str(e)
        if "wrong session ID" in error_msg or "auth key" in error_msg.lower():
            print(Fore.RED + f"[{session_name}] 🔄 Session invalid, reconnecting...")
            if session_name in session_manager:
                session_manager[session_name]['needs_reconnect'] = True
        else:
            print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__}")
        return False

async def process_groups(client: TelegramClient, session_name: str, message):
    """Process groups for a session"""
    if not message:
        print(Fore.YELLOW + f"[{session_name}] 📭 No message to forward")
        return

    groups = []
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
                if len(groups) >= 200:  # Limit to prevent memory issues
                    break
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error getting groups: {type(e).__name__}")
        return

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] 📭 No groups found")
        return

    print(Fore.CYAN + f"[{session_name}] 🔄 Processing {len(groups)} groups")
    
    processed = 0
    total_groups = len(groups)
    
    for idx, group in enumerate(groups, 1):
        # Check if session needs reconnection
        if session_name in session_manager and session_manager[session_name].get('needs_reconnect'):
            print(Fore.YELLOW + f"[{session_name}] ⚠️ Reconnection required, stopping...")
            return
        
        start_time = datetime.now()
        
        success = await safe_forward(client, group, message, session_name)
        if success:
            processed += 1
        
        # Smart delay calculation
        if idx < total_groups:
            elapsed = (datetime.now() - start_time).total_seconds()
            base_delay = random.uniform(MIN_DELAY, MAX_DELAY)
            
            # Dynamic delay adjustment based on session count
            active_sessions = len([s for s in session_manager.values() if s.get('active')])
            if active_sessions > 50:
                base_delay *= 1.5  # Increase delay for many sessions
            
            remaining_delay = max(0.5, base_delay - elapsed)
            
            if remaining_delay > 1:
                minutes = remaining_delay / 60
                progress = f"{idx}/{total_groups}"
                print(Fore.BLUE + f"[{session_name}] ⏰ {progress} - Wait {minutes:.1f}m")
                await asyncio.sleep(remaining_delay)
    
    print(Fore.CYAN + f"[{session_name}] ✅ Completed: {processed}/{total_groups} groups")

async def setup_auto_reply(client: TelegramClient, session_name: str):
    """Setup auto-reply for private messages"""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                print(Fore.MAGENTA + f"[{session_name}] 💬 Auto-replied")
            except Exception:
                pass

async def create_client(session_name: str, credentials: dict) -> Optional[TelegramClient]:
    """Create and connect Telegram client with robust error handling"""
    try:
        # Generate unique device parameters
        device_id = random.randint(1000, 9999)
        app_version = f"8.{random.randint(1, 9)}"
        
        client = TelegramClient(
            StringSession(credentials["string_session"]),
            credentials["api_id"],
            credentials["api_hash"],
            device_model=f"Android {device_id}",
            system_version=f"10.{random.randint(1, 5)}",
            app_version=app_version,
            lang_code="en",
            system_lang_code="en-US",
            connection_retries=3,
            request_retries=2,
            timeout=30,
            proxy=None,
            use_ipv6=False
        )
        
        # Connect with timeout
        await asyncio.wait_for(client.connect(), timeout=30)
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Not authorized")
            await client.disconnect()
            return None
        
        # Get user info
        me = await client.get_me()
        if me:
            username = f"@{me.username}" if me.username else str(me.id)
            print(Fore.GREEN + f"[{session_name}] ✅ Connected as {username}")
        
        return client
        
    except asyncio.TimeoutError:
        print(Fore.RED + f"[{session_name}] ⏱️ Connection timeout")
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Connection failed: {type(e).__name__}")
    
    return None

async def manage_session(session_name: str, credentials: dict):
    """Main session management function - SIMULTANEOUS EXECUTION"""
    global session_manager
    
    # Initialize session in manager
    session_manager[session_name] = {
        'active': True,
        'needs_reconnect': False,
        'client': None,
        'last_activity': datetime.now()
    }
    
    reconnect_attempts = 0
    max_reconnect_attempts = 5
    
    while session_manager[session_name]['active'] and reconnect_attempts < max_reconnect_attempts:
        client = None
        try:
            # Wait for internet if needed
            if not check_internet_connection():
                print(Fore.YELLOW + f"[{session_name}] 🌐 Waiting for internet...")
                await wait_for_internet()
            
            print(Fore.CYAN + f"[{session_name}] 🔌 Connecting...")
            client = await create_client(session_name, credentials)
            
            if not client:
                reconnect_attempts += 1
                print(Fore.YELLOW + f"[{session_name}] 🔄 Reconnect attempt {reconnect_attempts}/{max_reconnect_attempts}")
                await asyncio.sleep(SESSION_RECONNECT_DELAY * reconnect_attempts)
                continue
            
            # Reset reconnect attempts on successful connection
            reconnect_attempts = 0
            session_manager[session_name]['client'] = client
            session_manager[session_name]['needs_reconnect'] = False
            
            # Setup auto-reply
            await setup_auto_reply(client, session_name)
            
            # Main operation loop
            cycle_count = 0
            while session_manager[session_name]['active'] and not session_manager[session_name].get('needs_reconnect'):
                try:
                    # Update last activity
                    session_manager[session_name]['last_activity'] = datetime.now()
                    
                    # Get message
                    message = await get_last_message(client)
                    
                    # Process groups
                    await process_groups(client, session_name, message)
                    
                    cycle_count += 1
                    print(Fore.YELLOW + f"[{session_name}] 🔁 Cycle {cycle_count} completed")
                    print(Fore.CYAN + f"[{session_name}] ⏳ Sleeping for {CYCLE_DELAY//60} minutes...")
                    
                    # Sleep between cycles with periodic checks
                    sleep_start = datetime.now()
                    while (datetime.now() - sleep_start).total_seconds() < CYCLE_DELAY:
                        if session_manager[session_name].get('needs_reconnect'):
                            break
                        
                        # Check connection every 30 seconds
                        if not await client.is_connected():
                            print(Fore.RED + f"[{session_name}] 🔌 Connection lost")
                            session_manager[session_name]['needs_reconnect'] = True
                            break
                        
                        await asyncio.sleep(30)
                    
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] ⚠️ Operation error: {type(e).__name__}")
                    await asyncio.sleep(10)
            
        except KeyboardInterrupt:
            break
        except Exception as e:
            print(Fore.RED + f"[{session_name}] 💥 Critical error: {type(e).__name__}")
            reconnect_attempts += 1
            await asyncio.sleep(SESSION_RECONNECT_DELAY * reconnect_attempts)
        finally:
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] 🔌 Disconnected")
                except:
                    pass
    
    # Cleanup
    if session_name in session_manager:
        session_manager[session_name]['active'] = False
        del session_manager[session_name]
    
    print(Fore.RED + f"[{session_name}] 🏁 Session terminated")

async def monitor_sessions():
    """Monitor all sessions and display status"""
    while True:
        try:
            active_count = len([s for s in session_manager.values() if s.get('active')])
            total_count = len(session_manager)
            
            print(Fore.CYAN + f"\n📊 SESSION STATUS: {active_count}/{total_count} active")
            
            # Show inactive sessions
            inactive = [name for name, data in session_manager.items() 
                       if not data.get('active')]
            if inactive:
                print(Fore.YELLOW + f"⚠️ Inactive: {', '.join(inactive[:5])}{'...' if len(inactive) > 5 else ''}")
            
            await asyncio.sleep(60)
        except:
            await asyncio.sleep(30)

async def main():
    """Main function - ALL SESSIONS SIMULTANEOUS"""
    display_banner()
    
    # Initial internet check
    if not check_internet_connection():
        print(Fore.RED + "🌐 No internet connection")
        await wait_for_internet()
    
    try:
        # Get number of sessions
        num_sessions = int(input(Fore.CYAN + "Enter number of sessions: "))
        if num_sessions < 1:
            raise ValueError("At least 1 session required")
        
        print(Fore.GREEN + f"\n🚀 Loading {num_sessions} sessions...")
        
        # Load or configure sessions
        session_tasks = []
        for i in range(1, num_sessions + 1):
            session_name = f"session{i}"
            creds = load_session(session_name)
            
            if not creds:
                print(Fore.CYAN + f"\n⚙️ Configuring {session_name}:")
                try:
                    creds = {
                        "api_id": int(input("API ID: ")),
                        "api_hash": input("API Hash: "),
                        "string_session": input("String Session: ")
                    }
                    save_session(session_name, creds)
                except KeyboardInterrupt:
                    raise
                except Exception as e:
                    print(Fore.RED + f"❌ Error configuring {session_name}: {e}")
                    continue
            
            # Create task for this session
            task = asyncio.create_task(manage_session(session_name, creds))
            session_tasks.append((session_name, task))
            
            # Small delay between starting sessions to avoid connection collisions
            if i < num_sessions:
                await asyncio.sleep(0.5)
        
        print(Fore.GREEN + f"\n✅ Starting {len(session_tasks)} sessions SIMULTANEOUSLY!")
        print(Fore.YELLOW + "Press Ctrl+C to stop\n")
        
        # Start session monitor
        monitor_task = asyncio.create_task(monitor_sessions())
        
        # Wait for all sessions (they run forever until stopped)
        try:
            await asyncio.gather(*[task for _, task in session_tasks], return_exceptions=True)
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n🛑 Stopping all sessions...")
            
            # Mark all sessions as inactive
            for session_name in list(session_manager.keys()):
                session_manager[session_name]['active'] = False
            
            # Wait a bit for cleanup
            await asyncio.sleep(3)
        
        # Cancel monitor
        monitor_task.cancel()
        try:
            await monitor_task
        except:
            pass
        
        print(Fore.GREEN + "👋 All sessions stopped")
        
    except (ValueError, KeyboardInterrupt):
        print(Fore.YELLOW + "\n🛑 Operation cancelled")
    except Exception as e:
        print(Fore.RED + f"💥 Fatal error: {type(e).__name__} - {str(e)}")

def cleanup():
    """Cleanup function"""
    print(Fore.YELLOW + "\n🧹 Cleaning up...")
    for session_name in list(session_manager.keys()):
        session_manager[session_name]['active'] = False
    time.sleep(2)

if __name__ == "__main__":
    import signal
    import sys
    
    def signal_handler(signum, frame):
        print(Fore.YELLOW + "\n🛑 Received stop signal")
        cleanup()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, signal_handler)
    signal.signal(signal.SIGTERM, signal_handler)
    
    # Auto-restart with cooldown
    restart_count = 0
    max_restarts = 3
    
    while restart_count < max_restarts:
        try:
            asyncio.run(main())
            break
        except KeyboardInterrupt:
            cleanup()
            print(Fore.YELLOW + "\n👋 Script stopped by user")
            break
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"💥 Script crashed: {type(e).__name__}")
            if restart_count < max_restarts:
                cooldown = restart_count * 30
                print(Fore.YELLOW + f"🔄 Restarting in {cooldown}s... ({restart_count}/{max_restarts})")
                time.sleep(cooldown)
    
    if restart_count >= max_restarts:
        print(Fore.RED + "🚨 Too many restarts. Please check configuration.")
    cleanup()
