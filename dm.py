#!/usr/bin/env python3
import asyncio
import os
import json
import random
import logging
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

# Initialize colorama
init(autoreset=True)

# Configuration - Optimized for Termux
CREDENTIALS_FOLDER = 'tdata'
os.makedirs(CREDENTIALS_FOLDER, exist_ok=True)
TARGET_USER = "OgDigital"  # Target username for DM forwarding

# Optimized Timing Settings
MIN_DELAY = 25  # Minimum delay between groups (seconds)
MAX_DELAY = 45  # Maximum delay between groups (seconds)
CYCLE_DELAY = 1200  # 20 minutes between full cycles (seconds)
MAX_CONCURRENT = 20  # Number of accounts to run simultaneously
MAX_RETRIES = 2  # Maximum retry attempts

# Lightweight logging
logging.basicConfig(
    level=logging.WARNING,
    format='%(asctime)s - %(message)s'
)

# Auto-Reply Message
AUTO_REPLY_MESSAGE = "Dm @OGDIGITAL"

def display_banner():
    """Minimal banner for Termux"""
    print(Fore.RED + """
     ██████╗ ██████╗ ██████╗ ██╗████████╗
     ██╔═══██╗██╔══██╗██╔══██╗██║╚══██╔══╝
     ██║   ██║██████╔╝██████╔╝██║   ██║   
     ██║   ██║██╔══██╗██╔══██╗██║   ██║   
     ╚██████╔╝██║  ██║██████╔╝██║   ██║   
      ╚═════╝ ╚═╝  ╚═╝╚═════╝ ╚═╝   ╚═╝   
    """)
    print(Fore.GREEN + "ORBIT ADBOT - Termux Optimized v2.0\n")
    print(Fore.YELLOW + f"• Concurrent Sessions: {MAX_CONCURRENT}")
    print(Fore.YELLOW + f"• Delay Range: {MIN_DELAY}-{MAX_DELAY}s")
    print(Fore.YELLOW + f"• Cycle Delay: {CYCLE_DELAY//60} mins\n")

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
    except Exception:
        return None

async def safe_forward(client, group, message, session_name):
    """Safe message forwarding with retries"""
    for attempt in range(MAX_RETRIES):
        try:
            await client.forward_messages(group, message)
            print(Fore.GREEN + f"[{session_name}] Sent to {getattr(group, 'title', 'GROUP')}")
            return True
        except FloodWaitError as e:
            wait = min(e.seconds, 30)
            print(Fore.YELLOW + f"[{session_name}] Flood wait: {wait}s")
            await asyncio.sleep(wait)
        except (ChannelPrivateError, ChatWriteForbiddenError):
            print(Fore.YELLOW + f"[{session_name}] No access")
            return False
        except Exception as e:
            print(Fore.RED + f"[{session_name}] Error: {type(e).__name__}")
            if attempt == MAX_RETRIES - 1:
                return False
            await asyncio.sleep(5)
    return False

async def process_groups(client, session_name, message):
    """Efficient group processing"""
    if not message:
        return

    groups = []
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
    except Exception:
        return

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] No groups found")
        return

    print(Fore.CYAN + f"[{session_name}] Processing {len(groups)} groups")
    
    processed = 0
    for group in groups:
        start_time = asyncio.get_event_loop().time()
        
        if await safe_forward(client, group, message, session_name):
            processed += 1
        
        # Dynamic delay calculation
        elapsed = asyncio.get_event_loop().time() - start_time
        remaining = max(0, random.uniform(MIN_DELAY, MAX_DELAY) - elapsed)
        if remaining > 0:
            await asyncio.sleep(remaining)
    
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

async def manage_session(session_name, credentials):
    """Robust session management"""
    client = None
    try:
        client = TelegramClient(
            StringSession(credentials["string_session"]),
            credentials["api_id"],
            credentials["api_hash"],
            device_model=f"Termux-{random.randint(1000,9999)}",
            system_version="4.16.30",
            connection_retries=1,
            request_retries=1,
            auto_reconnect=True,
            sequential_updates=True
        )

        await client.start()
        print(Fore.GREEN + f"[{session_name}] Session started")
        
        await setup_auto_reply(client, session_name)

        while True:
            try:
                message = await get_last_message(client)
                await process_groups(client, session_name, message)
                
                print(Fore.YELLOW + f"[{session_name}] Sleeping for {CYCLE_DELAY//60} mins")
                await asyncio.sleep(CYCLE_DELAY)
                
            except Exception as e:
                print(Fore.RED + f"[{session_name}] Error: {type(e).__name__}")
                await asyncio.sleep(300)  # 5 minute cooldown

    except UserDeactivatedBanError:
        print(Fore.RED + f"[{session_name}] Account banned")
    except Exception as e:
        print(Fore.RED + f"[{session_name}] Fatal error: {type(e).__name__}")
    finally:
        if client:
            await client.disconnect()

async def main():
    """Optimized main function"""
    display_banner()

    try:
        # Simple session management
        num_sessions = min(20, int(input("Enter number of sessions (1-20): ")))
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

        # Concurrent execution with limit
        semaphore = asyncio.Semaphore(MAX_CONCURRENT)
        
        async def limited_task(task):
            async with semaphore:
                await task
                
        await asyncio.gather(*[limited_task(task) for task in tasks])

    except (ValueError, KeyboardInterrupt):
        print(Fore.YELLOW + "\nOperation cancelled")
    except Exception as e:
        print(Fore.RED + f"Fatal error: {type(e).__name__}")

if __name__ == "__main__":
    # Termux-friendly execution
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nScript stopped gracefully")
