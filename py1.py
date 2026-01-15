#!/usr/bin/env python3
import asyncio
import os
import glob
import random
import logging
import socket
import time
from telethon import TelegramClient, events, types
from telethon.sessions import SQLiteSession
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
ACCOUNTS_FOLDER = 'accounts'
os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
TARGET_USER = "orgjhonysins"  # Target username for DM forwarding

# Updated Timing Settings - 1 to 2 minutes between groups
MIN_DELAY = 60   # 1 minute minimum delay between groups (seconds)
MAX_DELAY = 120  # 2 minutes maximum delay between groups (seconds)
CYCLE_DELAY = 1200  # 20 minutes between full cycles (seconds)
MAX_RETRIES = 2  # Maximum retry attempts

# API credentials - using same for all to avoid issues
API_ID = 2040
API_HASH = "b18441a1ff607e10a989891a5462e627"

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
    print(Fore.GREEN + "ORBIT ADBOT - Session File Version v2.2\n")
    print(Fore.YELLOW + f"• Using .session files from '{ACCOUNTS_FOLDER}/' folder")
    print(Fore.YELLOW + f"• Delay Range: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"• Cycle Delay: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + "• Concurrent Sessions: UNLIMITED\n")

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

async def manage_session(session_path, session_name):
    """Robust session management with .session files"""
    while True:
        client = None
        try:
            print(Fore.CYAN + f"[{session_name}] Starting from .session file...")
            
            # Wait for internet before starting
            if not check_internet_connection():
                print(Fore.YELLOW + f"[{session_name}] Waiting for internet...")
                await wait_for_internet()
            
            # Use .session file directly
            client = TelegramClient(
                session_path,
                API_ID,
                API_HASH,
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
                
            me = await client.get_me()
            print(Fore.GREEN + f"[{session_name}] Successfully connected as @{me.username or me.first_name or me.id}!")
            
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
    """Optimized main function with .session file support"""
    display_banner()

    # Initial internet check
    if not check_internet_connection():
        print(Fore.RED + "No internet connection detected")
        await wait_for_internet()

    try:
        # Find all .session files in accounts folder
        session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
        
        if not session_files:
            print(Fore.RED + f"❌ No .session files found in '{ACCOUNTS_FOLDER}/' folder!")
            print(Fore.YELLOW + f"Place your .session files in the '{ACCOUNTS_FOLDER}/' folder")
            print(Fore.YELLOW + "Example: accounts/916205219094.session")
            return
        
        print(Fore.GREEN + f"✅ Found {len(session_files)} .session files")
        
        # Display found sessions
        for i, session_file in enumerate(session_files, 1):
            session_name = os.path.basename(session_file).replace('.session', '')
            print(Fore.CYAN + f"{i:2d}. {session_name}")
        
        print(Fore.YELLOW + "\n" + "═" * 50)
        
        # Ask for confirmation
        use_all = input(Fore.CYAN + "Use ALL sessions? (y/n): ").strip().lower()
        
        tasks = []
        if use_all == 'y':
            # Use all sessions
            selected_files = session_files
            print(Fore.GREEN + f"\n🚀 Starting ALL {len(session_files)} sessions simultaneously...")
        else:
            # Let user select specific sessions
            print(Fore.CYAN + "\nEnter session numbers to use (comma-separated, e.g., 1,3,5)")
            print(Fore.CYAN + "Or type 'all' to use all sessions")
            selection = input(Fore.CYAN + "Selection: ").strip().lower()
            
            if selection == 'all':
                selected_files = session_files
            else:
                try:
                    indices = [int(x.strip()) - 1 for x in selection.split(',')]
                    selected_files = [session_files[i] for i in indices if 0 <= i < len(session_files)]
                except:
                    print(Fore.RED + "Invalid selection, using all sessions")
                    selected_files = session_files
        
        # Create tasks for selected sessions
        for session_file in selected_files:
            session_name = os.path.basename(session_file).replace('.session', '')
            tasks.append(manage_session(session_file, session_name))
        
        if not tasks:
            print(Fore.RED + "❌ No sessions selected!")
            return
        
        # Run ALL sessions concurrently without limits
        print(Fore.GREEN + f"\n🔥 Starting {len(tasks)} sessions with NO concurrent limit...")
        
        # Show starting countdown
        for i in range(3, 0, -1):
            print(Fore.YELLOW + f"Starting in {i}...")
            await asyncio.sleep(1)
        
        print(Fore.GREEN + "⚡ ALL SESSIONS RUNNING SIMULTANEOUSLY NOW!\n")
        
        # Run all tasks concurrently
        await asyncio.gather(*tasks, return_exceptions=True)

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nOperation cancelled by user")
    except Exception as e:
        print(Fore.RED + f"Fatal error: {type(e).__name__} - {str(e)}")

if __name__ == "__main__":
    # Auto-restart mechanism
    restart_count = 0
    while restart_count < 5:  # Prevent infinite restart loop
        try:
            asyncio.run(main())
            break  # Exit loop if main completes normally
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nScript stopped by user")
            break
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"Script crashed: {type(e).__name__}")
            if restart_count < 5:
                print(Fore.YELLOW + f"Restarting in 10 seconds... (Attempt {restart_count}/5)")
                time.sleep(10)
            else:
                print(Fore.RED + "Too many restarts. Please check your configuration.")
    
    print(Fore.CYAN + "\n" + "═" * 50)
    print(Fore.CYAN + "Script execution completed")