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
    PeerIdInvalidError
)
from colorama import init, Fore
from datetime import datetime

# Initialize colorama
init(autoreset=True)

# Configuration - Optimized for Termux
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "OgDigital"  # Target username for DM forwarding

# Updated Timing Settings - 1 to 2 minutes between groups
MIN_DELAY = 60   # 1 minute minimum delay between groups (seconds)
MAX_DELAY = 120  # 2 minutes maximum delay between groups (seconds)
CYCLE_DELAY = 1200  # 20 minutes between full cycles (seconds)
MAX_RETRIES = 2  # Maximum retry attempts

# Lightweight logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @OgDigital For Buy"

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
     ██████╗ ██████╗ ██████╗ ██╗████████╗
     ██╔═══██╗██╔══██╗██╔══██╗██║╚══██╔══╝
     ██║   ██║██████╔╝██████╔╝██║   ██║   
     ██║   ██║██╔══██╗██╔══██╗██║   ██║   
     ╚██████╔╝██║  ██║██████╔╝██║   ██║   
      ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   
    """)
    print(Fore.GREEN + "ORBIT ADBOT - Termux Optimized v2.1\n")
    print(Fore.YELLOW + f"• Delay Range: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"• Cycle Delay: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + "• Concurrent Sessions: UNLIMITED\n")

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
    """Get last message with minimal requests"""
    try:
        entity = await client.get_input_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=1)
        return messages[0] if messages else None
    except Exception as e:
        print(Fore.RED + f"Error getting message: {str(e)}")
        return None

async def safe_forward(client, group, message, session_name):
    """Safe message forwarding with NO flood wait handling"""
    try:
        await client.forward_messages(group, message)
        print(Fore.GREEN + f"[{session_name}] Sent to {getattr(group, 'title', 'GROUP')}")
        return True
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] No access")
        return False
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Error: {type(e).__name__} - {str(e)}")
        return False

async def process_groups(client, session_name, message):
    """Efficient group processing with 1-2 minute delay"""
    if not message:
        print(Fore.YELLOW + f"[{session_name}] No message to forward")
        return

    groups = []
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Error getting groups: {str(e)}")
        return

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] No groups found")
        return

    print(Fore.CYAN + f"[{session_name}] Processing {len(groups)} groups")
    
    processed = 0
    for group in groups:
        start_time = datetime.now()
        
        if await safe_forward(client, group, message, session_name):
            processed += 1
        
        # Calculate and display delay (1-2 minutes)
        elapsed = (datetime.now() - start_time).total_seconds()
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        remaining_delay = max(0, delay - elapsed)
        
        if remaining_delay > 0:
            minutes = remaining_delay / 60
            print(Fore.BLUE + f"[{session_name}] Waiting {minutes:.1f} minutes before next group")
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
            except Exception as e:
                print(Fore.RED + f"[{session_name}] Auto-reply failed: {str(e)}")

async def manage_session(session_name, credentials):
    """Robust session management with internet monitoring"""
    while True:
        client = None
        try:
            print(Fore.CYAN + f"[{session_name}] Starting session...")
            
            # Wait for internet before starting
            if not check_internet_connection():
                print(Fore.YELLOW + f"[{session_name}] Waiting for internet...")
                await wait_for_internet()
            
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
            
            # Connect with timeout
            print(Fore.YELLOW + f"[{session_name}] Connecting to Telegram...")
            await client.connect()
            
            # Check if authorized
            if not await client.is_user_authorized():
                print(Fore.RED + f"[{session_name}] Session not authorized")
                return
                
            print(Fore.GREEN + f"[{session_name}] Successfully connected!")
            
            await setup_auto_reply(client, session_name)

            # Main operation loop
            while True:
                try:
                    # Check internet before operation
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] Internet lost, waiting...")
                        await wait_for_internet()
                        # Reconnect after internet restore
                        await client.connect()
                    
                    message = await get_last_message(client)
                    await process_groups(client, session_name, message)
                    
                    print(Fore.YELLOW + f"[{session_name}] Cycle completed. Sleeping for {CYCLE_DELAY//60} minutes...")
                    
                    # Sleep with periodic internet checks
                    for i in range(CYCLE_DELAY // 30):
                        if not check_internet_connection():
                            print(Fore.YELLOW + f"[{session_name}] Internet check failed")
                            break
                        await asyncio.sleep(30)
                        
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] Operation error: {type(e).__name__} - {str(e)}")
                    await asyncio.sleep(60)

        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_name}] Account banned")
            break
        except Exception as e:
            print(Fore.RED + f"[{session_name}] Connection failed: {type(e).__name__} - {str(e)}")
            print(Fore.YELLOW + f"[{session_name}] Retrying in 30 seconds...")
            await asyncio.sleep(30)
        finally:
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] Disconnected")
                except:
                    pass

async def main():
    """Optimized main function with internet monitoring"""
    display_banner()

    # Initial internet check
    if not check_internet_connection():
        print(Fore.RED + "No internet connection detected")
        await wait_for_internet()

    try:
        # Simple session management - NO CONCURRENT LIMIT
        num_sessions = int(input("Enter number of sessions: "))
        if num_sessions < 1:
            raise ValueError("At least 1 session required")

        tasks = []
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
            
            tasks.append(manage_session(session_name, creds))

        # Run ALL sessions concurrently without limits
        print(Fore.GREEN + f"Starting {len(tasks)} sessions with NO concurrent limit...")
        
        # Run all tasks concurrently without any restrictions
        await asyncio.gather(*tasks, return_exceptions=True)

    except (ValueError, KeyboardInterrupt):
        print(Fore.YELLOW + "\nOperation cancelled")
    except Exception as e:
        print(Fore.RED + f"Fatal error: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    # Auto-restart mechanism
    restart_count = 0
    while restart_count < 10:  # Prevent infinite restart loop
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nScript stopped by user")
            break
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"Script crashed: {type(e).__name__}")
            print(Fore.YELLOW + f"Restarting in 10 seconds... (Attempt {restart_count}/10)")
            time.sleep(10)
    
    if restart_count >= 10:
        print(Fore.RED + "Too many restarts. Please check your configuration.")
