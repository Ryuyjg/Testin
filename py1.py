#!/usr/bin/env python3
import asyncio
import os
import json
import random
import logging
import socket
import time
import gc  # Added for garbage collection
import psutil  # Added for monitoring
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

# Updated Timing Settings - INCREASED DELAYS FOR CPU REDUCTION
MIN_DELAY = 180   # 3 minutes minimum delay between groups (increased from 60)
MAX_DELAY = 300   # 5 minutes maximum delay between groups (increased from 120)
CYCLE_DELAY = 3600  # 60 minutes between full cycles (increased from 1200)
MAX_RETRIES = 2  # Maximum retry attempts
CACHE_CLEAR_INTERVAL = 1800  # Clear cache every 30 minutes (seconds)
CPU_THROTTLE_THRESHOLD = 80  # CPU usage percentage to trigger throttling

# Lightweight logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @OgDigital For Buy"

def check_cpu_usage():
    """Check CPU usage and throttle if needed"""
    try:
        cpu_percent = psutil.cpu_percent(interval=1)
        if cpu_percent > CPU_THROTTLE_THRESHOLD:
            print(Fore.YELLOW + f"High CPU usage detected: {cpu_percent}% - Throttling...")
            return True
    except:
        pass
    return False

def clear_memory_cache():
    """Clear memory cache and run garbage collection"""
    gc.collect()  # Run garbage collection
    print(Fore.BLUE + "Memory cache cleared")
    return True

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
        print(Fore.RED + "No internet connection. Retrying in 30 seconds...")
        await asyncio.sleep(30)  # Increased from 10 seconds
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
    print(Fore.GREEN + "ORBIT ADBOT - RDP Optimized v2.2 (LOW CPU)\n")
    print(Fore.YELLOW + f"вҖў Delay Range: {MIN_DELAY//60}-{MAX_DELAY//60} mins")
    print(Fore.YELLOW + f"вҖў Cycle Delay: {CYCLE_DELAY//60} mins")
    print(Fore.YELLOW + f"вҖў Cache Clear: {CACHE_CLEAR_INTERVAL//60} mins interval")
    print(Fore.YELLOW + "вҖў CPU Throttle: Enabled\n")

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
    """Efficient group processing with increased delay for CPU reduction"""
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
        
        # Check CPU usage before processing
        if check_cpu_usage():
            print(Fore.YELLOW + f"[{session_name}] High CPU - Adding extra delay")
            await asyncio.sleep(random.uniform(60, 120))  # Extra 1-2 minutes
        
        if await safe_forward(client, group, message, session_name):
            processed += 1
        
        # Calculate and display delay (3-5 minutes - INCREASED)
        elapsed = (datetime.now() - start_time).total_seconds()
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        remaining_delay = max(0, delay - elapsed)
        
        if remaining_delay > 0:
            minutes = remaining_delay / 60
            print(Fore.BLUE + f"[{session_name}] Waiting {minutes:.1f} minutes before next group")
            # Split sleep into smaller chunks to check CPU
            for _ in range(int(remaining_delay // 30) + 1):
                await asyncio.sleep(min(30, remaining_delay))
                remaining_delay -= 30
                if remaining_delay <= 0:
                    break
                
                # Periodic CPU check during sleep
                if check_cpu_usage():
                    extra_sleep = random.uniform(30, 60)
                    print(Fore.YELLOW + f"[{session_name}] CPU high - Sleeping extra {extra_sleep:.0f}s")
                    await asyncio.sleep(extra_sleep)
    
    print(Fore.CYAN + f"[{session_name}] Sent to {processed}/{len(groups)} groups")

async def setup_auto_reply(client, session_name):
    """Lightweight auto-reply with CPU check"""
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            # Check CPU before auto-reply
            if check_cpu_usage():
                await asyncio.sleep(random.uniform(5, 10))  # Small delay if CPU high
            
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                print(Fore.MAGENTA + f"[{session_name}] Auto-replied")
            except Exception as e:
                print(Fore.RED + f"[{session_name}] Auto-reply failed: {str(e)}")

async def manage_session(session_name, credentials):
    """Robust session management with internet monitoring and CPU optimization"""
    cache_timer = time.time()
    
    while True:
        client = None
        try:
            print(Fore.CYAN + f"[{session_name}] Starting session...")
            
            # Clear cache at regular intervals
            if time.time() - cache_timer > CACHE_CLEAR_INTERVAL:
                clear_memory_cache()
                cache_timer = time.time()
            
            # Check CPU before connecting
            if check_cpu_usage():
                print(Fore.YELLOW + f"[{session_name}] High CPU - Delaying connection")
                await asyncio.sleep(random.uniform(60, 180))
            
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
                system_lang_code="en-US",
                connection_retries=2,  # Reduced retries
                request_retries=2,     # Reduced retries
                auto_reconnect=True,
                sequential_updates=True  # Process updates sequentially
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
                    # Clear cache at intervals
                    if time.time() - cache_timer > CACHE_CLEAR_INTERVAL:
                        clear_memory_cache()
                        cache_timer = time.time()
                    
                    # Check CPU before operation
                    if check_cpu_usage():
                        print(Fore.YELLOW + f"[{session_name}] High CPU - Delaying operation")
                        await asyncio.sleep(random.uniform(120, 300))
                    
                    # Check internet before operation
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] Internet lost, waiting...")
                        await wait_for_internet()
                        # Reconnect after internet restore
                        await client.connect()
                    
                    message = await get_last_message(client)
                    await process_groups(client, session_name, message)
                    
                    print(Fore.YELLOW + f"[{session_name}] Cycle completed. Sleeping for {CYCLE_DELAY//60} minutes...")
                    
                    # Sleep with periodic internet and CPU checks
                    sleep_chunks = CYCLE_DELAY // 60  # Check every minute
                    for i in range(sleep_chunks):
                        if not check_internet_connection():
                            print(Fore.YELLOW + f"[{session_name}] Internet check failed")
                            break
                        
                        # Clear cache at intervals during sleep
                        if time.time() - cache_timer > CACHE_CLEAR_INTERVAL:
                            clear_memory_cache()
                            cache_timer = time.time()
                        
                        # CPU check during sleep
                        if check_cpu_usage() and i < sleep_chunks - 1:
                            extra_sleep = random.uniform(30, 90)
                            print(Fore.YELLOW + f"[{session_name}] CPU high - Adding {extra_sleep:.0f}s sleep")
                            await asyncio.sleep(extra_sleep)
                        
                        await asyncio.sleep(60)  # Sleep in 1-minute chunks
                        
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] Operation error: {type(e).__name__} - {str(e)}")
                    # Clear cache on error
                    clear_memory_cache()
                    await asyncio.sleep(120)  # Increased from 60 seconds

        except UserDeactivatedBanError:
            print(Fore.RED + f"[{session_name}] Account banned")
            break
        except Exception as e:
            print(Fore.RED + f"[{session_name}] Connection failed: {type(e).__name__} - {str(e)}")
            print(Fore.YELLOW + f"[{session_name}] Retrying in 60 seconds...")
            clear_memory_cache()  # Clear cache on connection failure
            await asyncio.sleep(60)  # Increased from 30 seconds
        finally:
            if client:
                try:
                    await client.disconnect()
                    print(Fore.YELLOW + f"[{session_name}] Disconnected")
                except:
                    pass
            clear_memory_cache()  # Clear cache on disconnect

async def main():
    """Optimized main function with internet monitoring and CPU optimization"""
    display_banner()
    
    # Initial cache clear
    clear_memory_cache()

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
    # Install psutil if not available
    try:
        import psutil
    except ImportError:
        print(Fore.YELLOW + "Installing psutil for CPU monitoring...")
        os.system("pip install psutil")
        import psutil
    
    # Auto-restart mechanism with CPU consideration
    restart_count = 0
    while restart_count < 5:  # Reduced from 10 to prevent CPU overload
        try:
            asyncio.run(main())
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\nScript stopped by user")
            break
        except Exception as e:
            restart_count += 1
            print(Fore.RED + f"Script crashed: {type(e).__name__}")
            
            # Clear cache before restart
            clear_memory_cache()
            
            # Longer delay on restart if CPU might be high
            delay = min(30 * restart_count, 120)  # Max 2 minutes
            print(Fore.YELLOW + f"Restarting in {delay} seconds... (Attempt {restart_count}/5)")
            time.sleep(delay)
    
    if restart_count >= 5:
        print(Fore.RED + "Too many restarts. Please check your configuration.")
    
    # Final cache clear
    clear_memory_cache()