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
TARGET_USER = "Og_Digital"  # Target username for DM forwarding

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
     ██████╗ ██████╗ ██████╗ ██╗████████╗
     ██╔═══██╗██╔══██╗██╔══██╗██║╚══██╔══╝
     ██║   ██║██████╔╝██████╔╝██║   ██║   
     ██║   ██║██╔══██╗██╔══██╗██║   ██║   
     ╚██████╔╝██║  ██║██████╔╝██║   ██║   
      ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   
    """)
    print(Fore.GREEN + "ORBIT ADBOT - COPY PASTE MODE v2.2\n")
    print(Fore.YELLOW + f"• Delay Range: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"• Cycle Delay: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + "• Mode: COPY-PASTE (Not Forward)")
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

async def get_last_message_content(client):
    """Get last message content with media if available"""
    try:
        entity = await client.get_input_entity(TARGET_USER)
        messages = await client.get_messages(entity, limit=1)
        
        if not messages:
            return None, None
        
        message = messages[0]
        
        # Extract message content
        message_text = message.text or message.caption or ""
        
        # Check if message has media
        if message.media:
            # Download media
            media_path = await client.download_media(message, file="temp_media/")
            return message_text, media_path
        else:
            return message_text, None
            
    except Exception as e:
        print(Fore.RED + f"Error getting message: {str(e)}")
        return None, None

async def copy_paste_message(client, group, message_text, media_path, session_name):
    """Copy-paste message with media if available"""
    try:
        if media_path:
            # Send message with media
            await client.send_file(
                group,
                media_path,
                caption=message_text if message_text else None
            )
            # Clean up temp file
            if os.path.exists(media_path):
                os.remove(media_path)
        else:
            # Send text only
            await client.send_message(group, message_text)
        
        print(Fore.GREEN + f"[{session_name}] Copied to {getattr(group, 'title', 'GROUP')}")
        return True
        
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] No access")
        return False
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Error: {type(e).__name__} - {str(e)}")
        # Clean up temp file on error
        if media_path and os.path.exists(media_path):
            os.remove(media_path)
        return False

async def get_all_groups(client):
    """Get ALL groups with retry mechanism to ensure none are missed"""
    groups = []
    retry_count = 0
    
    while retry_count < MAX_RETRIES:
        try:
            groups = []
            async for dialog in client.iter_dialogs():
                if dialog.is_group:
                    groups.append({
                        'entity': dialog.entity,
                        'id': dialog.id,
                        'title': dialog.title
                    })
            
            print(Fore.CYAN + f"[Session] Found {len(groups)} groups")
            
            # Store groups for tracking
            with open('groups_tracking.json', 'w') as f:
                json.dump([{'id': g['id'], 'title': g['title']} for g in groups], f)
            
            return groups
            
        except Exception as e:
            retry_count += 1
            print(Fore.RED + f"[Session] Error getting groups (Attempt {retry_count}/{MAX_RETRIES}): {str(e)}")
            await asyncio.sleep(10)
    
    print(Fore.RED + "[Session] Failed to get groups after retries")
    return []

async def process_all_groups(client, session_name, message_text, media_path, processed_groups_tracker):
    """Process ALL groups ensuring none are missed"""
    if not message_text and not media_path:
        print(Fore.YELLOW + f"[{session_name}] No message content to copy")
        return [], []

    # Get all groups
    all_groups = await get_all_groups(client)
    
    if not all_groups:
        print(Fore.YELLOW + f"[{session_name}] No groups found")
        return [], []

    print(Fore.CYAN + f"[{session_name}] Processing ALL {len(all_groups)} groups")
    
    # Track processed and failed groups
    processed_groups = []
    failed_groups = []
    
    for group_info in all_groups:
        group = group_info['entity']
        group_id = group_info['id']
        group_title = group_info['title']
        
        # Skip if already processed in this cycle
        if group_id in processed_groups_tracker:
            print(Fore.YELLOW + f"[{session_name}] Skipping already processed group: {group_title}")
            continue
        
        start_time = datetime.now()
        
        if await copy_paste_message(client, group, message_text, media_path, session_name):
            processed_groups.append({'id': group_id, 'title': group_title})
            processed_groups_tracker.add(group_id)
        else:
            failed_groups.append({'id': group_id, 'title': group_title})
        
        # Calculate and display delay (1-2 minutes)
        elapsed = (datetime.now() - start_time).total_seconds()
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        remaining_delay = max(0, delay - elapsed)
        
        if remaining_delay > 0:
            minutes = remaining_delay / 60
            print(Fore.BLUE + f"[{session_name}] Waiting {minutes:.1f} minutes before next group")
            await asyncio.sleep(remaining_delay)
    
    # Log results
    print(Fore.CYAN + f"[{session_name}] COMPLETED: Sent to {len(processed_groups)}/{len(all_groups)} groups")
    if failed_groups:
        print(Fore.YELLOW + f"[{session_name}] Failed groups: {len(failed_groups)}")
        with open(f'failed_groups_{session_name}.txt', 'a') as f:
            for group in failed_groups:
                f.write(f"{group['title']} (ID: {group['id']})\n")
    
    return processed_groups, failed_groups

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
    """Robust session management with internet monitoring and group tracking"""
    
    # Create temp directory for media
    os.makedirs("temp_media", exist_ok=True)
    
    # Track processed groups across cycles
    processed_groups_tracker = set()
    
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
            cycle_count = 0
            while True:
                try:
                    # Check internet before operation
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] Internet lost, waiting...")
                        await wait_for_internet()
                        # Reconnect after internet restore
                        await client.connect()
                    
                    cycle_count += 1
                    print(Fore.CYAN + f"\n[{session_name}] Starting cycle #{cycle_count}")
                    
                    # Get latest message from @Og_Digital
                    message_text, media_path = await get_last_message_content(client)
                    
                    # Process ALL groups
                    processed, failed = await process_all_groups(
                        client, session_name, 
                        message_text, media_path, 
                        processed_groups_tracker
                    )
                    
                    # Clear tracker for next cycle (optional - comment out to avoid repeats)
                    processed_groups_tracker.clear()
                    
                    print(Fore.YELLOW + f"[{session_name}] Cycle #{cycle_count} completed.")
                    print(Fore.YELLOW + f"[{session_name}] Sleeping for {CYCLE_DELAY//60} minutes...")
                    
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
            
            # Clean up temp directory
            try:
                import shutil
                if os.path.exists("temp_media"):
                    shutil.rmtree("temp_media")
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