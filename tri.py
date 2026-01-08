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
    SecurityError
)
from colorama import init, Fore
from datetime import datetime
import aiohttp

# Initialize colorama
init(autoreset=True)

# Configuration - Optimized for Termux
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "Og_Digital"  # Target username for DM forwarding

# Updated Timing Settings - 2 to 3 minutes between groups (increased)
MIN_DELAY = 120   # 2 minutes minimum delay between groups (seconds)
MAX_DELAY = 180   # 3 minutes maximum delay between groups (seconds)
CYCLE_DELAY = 1800  # 30 minutes between full cycles (seconds)
MAX_RETRIES = 2  # Maximum retry attempts
SESSION_BATCH_SIZE = 5  # Process sessions in batches to avoid Telegram limits
BATCH_DELAY = 10  # Delay between session batches in seconds

# Lightweight logging - Disable telethon debug logging
logging.getLogger('telethon').setLevel(logging.WARNING)
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @Og_Digital For Buy"

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
    """Minimal banner for Termux"""
    print(Fore.GREEN + """
     в–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•— в–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•— в–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•— в–Ҳв–Ҳв•—в–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•—
     в–Ҳв–Ҳв•”в•җв•җв•җв–Ҳв–Ҳв•—в–Ҳв–Ҳв•”в•җв•җв–Ҳв–Ҳв•—в–Ҳв–Ҳв•”в•җв•җв–Ҳв–Ҳв•—в–Ҳв–Ҳв•‘в•ҡв•җв•җв–Ҳв–Ҳв•”в•җв•җв•қ
     в–Ҳв–Ҳв•‘   в–Ҳв–Ҳв•‘в–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•”в•қв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•”в•қв–Ҳв–Ҳв•‘   в–Ҳв–Ҳв•‘   
     в–Ҳв–Ҳв•‘   в–Ҳв–Ҳв•‘в–Ҳв–Ҳв•”в•җв•җв–Ҳв–Ҳв•—в–Ҳв–Ҳв•”в•җв•җв–Ҳв–Ҳв•—в–Ҳв–Ҳв•‘   в–Ҳв–Ҳв•‘   
     в•ҡв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•”в•қв–Ҳв–Ҳв•‘  в–Ҳв–Ҳв•‘в–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв–Ҳв•”в•қв–Ҳв–Ҳв•‘   в–Ҳв–Ҳв•‘   
      в•ҡв•җв•җв•җв•җв•җв•қ в•ҡв•җв•қ  в•ҡв•җв•қв•ҡв•җв•җв•җв•җв•җв•қ в•ҡв•җв•қ   в•ҡв•җв•қ   
    """)
    print(Fore.GREEN + "ORBIT ADBOT - Termux Optimized v3.0")
    print(Fore.CYAN + "POWERFUL VERSION - 100+ SESSIONS SUPPORT\n")
    print(Fore.YELLOW + f"вҖў Delay Range: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"вҖў Cycle Delay: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + f"вҖў Session Batch Size: {SESSION_BATCH_SIZE}")
    print(Fore.YELLOW + f"вҖў Batch Delay: {BATCH_DELAY} seconds\n")

def save_session(session_name, data):
    """Save session data with error handling"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        with open(path, 'w') as f:
            json.dump(data, f)
    except Exception:
        pass

def load_session(session_name):
    """Load session data with error handling"""
    try:
        path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
        if os.path.exists(path):
            with open(path, 'r') as f:
                return json.load(f)
    except Exception:
        pass
    return None

async def get_last_message(client):
    """Get last message with robust error handling"""
    try:
        entity = await client.get_input_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=1)
        return messages[0] if messages else None
    except (PeerIdInvalidError, ChannelPrivateError):
        print(Fore.YELLOW + "[GET_MSG] Target user/channel not accessible")
        return None
    except Exception as e:
        print(Fore.RED + f"[GET_MSG] Error: {type(e).__name__}")
        return None

async def safe_forward(client, group, message, session_name):
    """Safe message forwarding with intelligent error handling"""
    try:
        await client.forward_messages(group, message)
        print(Fore.GREEN + f"[{session_name}] Sent to {getattr(group, 'title', 'GROUP')}")
        return True
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] No access")
        return False
    except FloodWaitError as e:
        print(Fore.RED + f"[{session_name}] Flood wait: {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        return False
    except SecurityError as e:
        print(Fore.RED + f"[{session_name}] Security error, skipping...")
        return False
    except Exception as e:
        error_type = type(e).__name__
        if "wrong session ID" in str(e) or isinstance(e, AuthKeyError):
            print(Fore.RED + f"[{session_name}] Session validation failed, reconnecting...")
            await client.disconnect()
            await asyncio.sleep(2)
            await client.connect()
            return False
        print(Fore.RED + f"[{session_name}] Error: {error_type}")
        return False

async def process_groups(client, session_name, message):
    """Efficient group processing with increased delays"""
    if not message:
        print(Fore.YELLOW + f"[{session_name}] No message to forward")
        return

    groups = []
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Error getting groups: {type(e).__name__}")
        return

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] No groups found")
        return

    print(Fore.CYAN + f"[{session_name}] Processing {len(groups)} groups")
    
    processed = 0
    for idx, group in enumerate(groups, 1):
        start_time = datetime.now()
        
        success = await safe_forward(client, group, message, session_name)
        if success:
            processed += 1
        
        # Increased delay between groups (2-3 minutes)
        elapsed = (datetime.now() - start_time).total_seconds()
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        remaining_delay = max(0, delay - elapsed)
        
        if remaining_delay > 0 and idx < len(groups):
            minutes = remaining_delay / 60
            print(Fore.BLUE + f"[{session_name}] {idx}/{len(groups)} - Waiting {minutes:.1f} minutes")
            await asyncio.sleep(remaining_delay)
    
    print(Fore.CYAN + f"[{session_name}] Sent to {processed}/{len(groups)} groups")

async def setup_auto_reply(client, session_name):
    """Lightweight auto-reply"""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                print(Fore.MAGENTA + f"[{session_name}] Auto-replied")
            except Exception:
                pass

async def validate_session(client, session_name):
    """Validate session before using"""
    try:
        if await client.is_user_authorized():
            me = await client.get_me()
            if me:
                print(Fore.GREEN + f"[{session_name}] Validated: @{me.username}")
                return True
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Validation failed: {type(e).__name__}")
    return False

async def manage_session(session_name, credentials):
    """Robust session management with reconnection logic"""
    while True:
        client = None
        try:
            print(Fore.CYAN + f"[{session_name}] Starting session...")
            
            # Wait for internet before starting
            if not check_internet_connection():
                print(Fore.YELLOW + f"[{session_name}] Waiting for internet...")
                await wait_for_internet()
            
            # Create client with different connection params to avoid collisions
            client = TelegramClient(
                StringSession(credentials["string_session"]),
                credentials["api_id"],
                credentials["api_hash"],
                device_model=f"Android_{random.randint(1, 10)}",
                system_version=f"10.{random.randint(1, 5)}",
                app_version=f"8.{random.randint(1, 9)}",
                lang_code="en",
                system_lang_code="en-US",
                connection_retries=2,
                request_retries=2,
                auto_reconnect=False  # We handle reconnection manually
            )
            
            # Connect with timeout
            print(Fore.YELLOW + f"[{session_name}] Connecting...")
            await client.connect(timeout=30)
            
            # Validate session
            if not await validate_session(client, session_name):
                print(Fore.RED + f"[{session_name}] Session invalid, skipping...")
                return
            
            print(Fore.GREEN + f"[{session_name}] Successfully connected!")
            
            await setup_auto_reply(client, session_name)

            # Main operation loop
            cycle_count = 0
            while True:
                try:
                    # Check internet before operation
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] Internet lost, waiting...")
                        await wait_for_internet()
                        # Reconnect after internet restore
                        await client.disconnect()
                        await asyncio.sleep(2)
                        await client.connect()
                    
                    # Get message once per cycle
                    message = await get_last_message(client)
                    
                    # Process groups with this message
                    await process_groups(client, session_name, message)
                    
                    cycle_count += 1
                    print(Fore.YELLOW + f"[{session_name}] Cycle {cycle_count} completed. Sleeping for {CYCLE_DELAY//60} minutes...")
                    
                    # Sleep with periodic internet and session checks
                    for i in range(CYCLE_DELAY // 60):  # Check every minute
                        if not check_internet_connection():
                            print(Fore.YELLOW + f"[{session_name}] Internet check failed at minute {i+1}")
                            break
                        
                        # Validate session every 5 minutes
                        if i % 5 == 0:
                            if not await validate_session(client, session_name):
                                print(Fore.RED + f"[{session_name}] Session validation failed, reconnecting...")
                                await client.disconnect()
                                await asyncio.sleep(3)
                                await client.connect()
                                break
                        
                        await asyncio.sleep(60)
                        
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] Operation error: {type(e).__name__}")
                    await asyncio.sleep(60)

        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_name}] Account banned")
            break
        except Exception as e:
            print(Fore.RED + f"[{session_name}] Connection failed: {type(e).__name__}")
            print(Fore.YELLOW + f"[{session_name}] Retrying in 30 seconds...")
            await asyncio.sleep(30)
        finally:
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] Disconnected")
                except:
                    pass

async def process_sessions_in_batches(sessions_data):
    """Process sessions in batches to avoid Telegram limits"""
    all_tasks = []
    
    # Create all session tasks
    for session_name, credentials in sessions_data.items():
        task = manage_session(session_name, credentials)
        all_tasks.append(task)
    
    # Process in batches
    completed = 0
    for i in range(0, len(all_tasks), SESSION_BATCH_SIZE):
        batch = all_tasks[i:i + SESSION_BATCH_SIZE]
        print(Fore.CYAN + f"\nStarting batch {i//SESSION_BATCH_SIZE + 1} with {len(batch)} sessions...")
        
        # Start batch
        batch_tasks = [asyncio.create_task(task) for task in batch]
        
        # Wait for batch to complete with error handling
        try:
            await asyncio.gather(*batch_tasks, return_exceptions=True)
        except Exception as e:
            print(Fore.RED + f"Batch error: {type(e).__name__}")
        
        completed += len(batch)
        print(Fore.GREEN + f"Batch completed. Total sessions: {completed}/{len(all_tasks)}")
        
        # Add delay between batches if not last batch
        if i + SESSION_BATCH_SIZE < len(all_tasks):
            print(Fore.BLUE + f"Waiting {BATCH_DELAY} seconds before next batch...")
            await asyncio.sleep(BATCH_DELAY)

async def main():
    """Optimized main function with batch processing"""
    display_banner()

    # Initial internet check
    if not check_internet_connection():
        print(Fore.RED + "No internet connection detected")
        await wait_for_internet()

    try:
        # Session management with batch processing
        num_sessions = int(input("Enter number of sessions: "))
        if num_sessions < 1:
            raise ValueError("At least 1 session required")

        sessions_data = {}
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
            
            sessions_data[session_name] = creds
        
        print(Fore.GREEN + f"\nLoaded {len(sessions_data)} sessions")
        print(Fore.YELLOW + f"Processing in batches of {SESSION_BATCH_SIZE}...")
        
        # Process sessions in batches
        await process_sessions_in_batches(sessions_data)

    except (ValueError, KeyboardInterrupt):
        print(Fore.YELLOW + "\nOperation cancelled")
    except Exception as e:
        print(Fore.RED + f"Fatal error: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    # Auto-restart mechanism with longer delays
    restart_count = 0
    while restart_count < 5:  # Reduced restart attempts
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nScript stopped by user")
            break
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"Script crashed: {type(e).__name__}")
            print(Fore.YELLOW + f"Restarting in 30 seconds... (Attempt {restart_count}/5)")
            time.sleep(30)
    
    if restart_count >= 5:
        print(Fore.RED + "Too many restarts. Please check your configuration.")
