#!/usr/bin/env python3
import asyncio
import os
import sys
import json
import glob
import random
import time
import socket
import logging
from datetime import datetime
from telethon import TelegramClient, events, functions, types
from telethon.sessions import StringSession
from telethon.errors import (
    UserDeactivatedBanError,
    FloodWaitError,
    SessionPasswordNeededError,
    PhoneCodeInvalidError,
    PhoneCodeExpiredError,
    PhoneNumberInvalidError,
    ChannelPrivateError,
    ChatWriteForbiddenError,
    PeerIdInvalidError,
    PhoneNumberFloodError,
    PasswordHashInvalidError
)
from colorama import init, Fore, Style, Back
import hashlib
import base64
import struct

# Initialize colorama
init(autoreset=True)

# ==================== CONFIGURATION ====================
ACCOUNTS_FOLDER = 'accounts'
SESSIONS_FOLDER = 'sessions'
os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
os.makedirs(SESSIONS_FOLDER, exist_ok=True)

API_CREDENTIALS = [
    {"api_id": 30645628, "api_hash": "7e0519fe42ea9c18d8ee0382f621042d"},
    {"api_id": 30808688, "api_hash": "1349dabd9280694bd939951963258729"},
    {"api_id": 36898273, "api_hash": "1ae96cb5ab3d4601cd147b4b58ceb2b4"},
    {"api_id": 39357850, "api_hash": "ad4559302ff6ea47c20f0d42b32099c1"},
    {"api_id": 35583095, "api_hash": "30b24cfdabf6862ac9e68ef2037fbf1c"},
    {"api_id": 39532169, "api_hash": "d3bb92ae9bd86de82eff01a834e29cf7"},
    {"api_id": 2040, "api_hash": "b18441a1ff607e10a989891a5462e627"},
    {"api_id": 38512195, "api_hash": "2154b7e5bcad8fed4ac2a44fb87be0b4"}
]

MIN_DELAY = 60
MAX_DELAY = 120
CYCLE_DELAY = 1200
MAX_RETRIES = 3

AUTO_REPLY_MESSAGE = "dm @ogdigital"
TARGET_USERNAME = "orgjhonysins"
SPAM_MESSAGE = "for buy ott and tg softwares dm @ogdigital"

logging.basicConfig(level=logging.WARNING)
logger = logging.getLogger(__name__)

def get_rotated_api():
    return random.choice(API_CREDENTIALS)

def check_internet_connection(host="8.8.8.8", port=53, timeout=5):
    try:
        socket.create_connection((host, port), timeout=timeout)
        return True
    except socket.error:
        return False

async def wait_for_internet():
    print(Fore.YELLOW + "🌐 Waiting for internet connection...")
    while not check_internet_connection():
        print(Fore.RED + "❌ No internet connection. Retrying in 10 seconds...")
        await asyncio.sleep(10)
    print(Fore.GREEN + "✅ Internet connection available!")

def clean_phone_for_filename(phone):
    clean = phone.replace('+', '').replace(' ', '').replace('-', '')
    clean = ''.join(filter(str.isdigit, clean))
    return clean

def display_banner():
    os.system('cls' if os.name == 'nt' else 'clear')
    print(Fore.RED + """
    ╔══════════════════════════════════════════════════════════════╗
    ║                                                              ║
    ║      ██████╗ ██╗   ██╗██╗     ███████╗███████╗████████╗     ║
    ║     ██╔════╝ ██║   ██║██║     ██╔════╝██╔════╝╚══██╔══╝     ║
    ║     ██║  ███╗██║   ██║██║     █████╗  ███████╗   ██║        ║
    ║     ██║   ██║██║   ██║██║     ██╔══╝  ╚════██║   ██║        ║
    ║     ╚██████╔╝╚██████╔╝███████╗███████╗███████║   ██║        ║
    ║      ╚═════╝  ╚═════╝ ╚══════╝╚══════╝╚══════╝   ╚═╝        ║
    ║                                                              ║
    ║               ULTIMATE TELEGRAM TOOLKIT v5.0                 ║
    ║              THE MOST POWERFUL SCRIPT IN THE WORLD           ║
    ║                     WITH FULL 2FA SUPPORT                    ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    print(Fore.CYAN + "📱 " + Fore.WHITE + "Created by: " + Fore.YELLOW + "@ogdigital")
    print(Fore.GREEN + "🔥 " + Fore.WHITE + "Features: " + Fore.YELLOW + "12-IN-1 Ultimate Toolkit")
    print(Fore.MAGENTA + "⚡ " + Fore.WHITE + "Status: " + Fore.GREEN + "READY FOR MASS OPERATIONS")
    print()

def display_stats():
    session_files = glob.glob(os.path.join(SESSIONS_FOLDER, '*.session'))
    account_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    print(Fore.CYAN + "📊 " + Fore.WHITE + "Session Stats:")
    print(Fore.YELLOW + f"   • Account Sessions: {len(account_files)}")
    print(Fore.YELLOW + f"   • Session Files: {len(session_files)}")
    print(Fore.YELLOW + f"   • Available APIs: {len(API_CREDENTIALS)}")

async def send_direct_message(client, target_username, message_text, session_name):
    try:
        if target_username.isdigit():
            user = await client.get_entity(int(target_username))
        else:
            user = await client.get_entity(target_username)
        
        await client.send_message(user, message_text)
        print(Fore.GREEN + f"[{session_name}] ✅ Message sent to @{target_username}")
        return True
        
    except Exception as e:
        error_msg = str(e)[:50]
        print(Fore.RED + f"[{session_name}] ❌ Failed to send to @{target_username}: {error_msg}")
        return False

async def send_dm_from_session(session_path, session_name, target_username, message_text):
    client = None
    try:
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            device_model="Android",
            system_version="10",
            app_version="8.4",
            lang_code="en",
            system_lang_code="en-US"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return False
        
        me = await client.get_me()
        print(Fore.CYAN + f"[{session_name}] 👤 Connected as @{me.username or me.first_name}")
        
        success = await send_direct_message(client, target_username, message_text, session_name)
        
        await client.disconnect()
        return success
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] 💥 Error: {str(e)[:50]}")
        if client:
            try:
                await client.disconnect()
            except:
                pass
        return False

async def option1_direct_messager():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "📨 DIRECT MESSAGE SENDER")
    print(Fore.CYAN + "═" * 60)
    
    target_username = input(Fore.YELLOW + "\n🎯 Target username/ID (without @): ").strip()
    if target_username.startswith('@'):
        target_username = target_username[1:]
    
    if not target_username:
        print(Fore.RED + "❌ Target is required!")
        return
    
    message_text = input(Fore.YELLOW + "💬 Message to send: ").strip()
    
    if not message_text:
        print(Fore.RED + "❌ Message is required!")
        return
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found in '{ACCOUNTS_FOLDER}/' folder!")
        print(Fore.YELLOW + f"Place your .session files in the '{ACCOUNTS_FOLDER}/' folder")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} available sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    use_all = input(Fore.CYAN + "🚀 Use ALL sessions? (y/n): ").strip().lower()
    
    if use_all == 'y':
        selected_sessions = available_sessions
        print(Fore.GREEN + f"\n🔥 Sending message from ALL {len(available_sessions)} sessions...")
    else:
        print(Fore.CYAN + "\n📝 Enter session numbers (comma-separated, e.g., 1,3,5)")
        print(Fore.CYAN + "   Or type 'all' to use all sessions")
        selection = input(Fore.CYAN + "   Selection: ").strip().lower()
        
        if selection == 'all':
            selected_sessions = available_sessions
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
            except:
                print(Fore.RED + "❌ Invalid selection, using all sessions")
                selected_sessions = available_sessions
    
    tasks = []
    for session_name, session_file in selected_sessions:
        tasks.append(send_dm_from_session(session_file, session_name, target_username, message_text))
    
    if not tasks:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    print(Fore.GREEN + f"\n⚡ SENDING MESSAGES FROM {len(tasks)} SESSIONS...\n")
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    success_count = sum(1 for r in results if r is True)
    print(Fore.GREEN + f"\n✅ COMPLETED! {success_count}/{len(tasks)} messages sent successfully!")

async def safe_forward(client, group, session_name):
    try:
        await client.send_message(group, SPAM_MESSAGE)
        group_name = getattr(group, 'title', 'Unknown Group')[:30]
        print(Fore.GREEN + f"[{session_name}] ✅ Sent to {group_name}")
        return True
    except (ChannelPrivateError, ChatWriteForbiddenError):
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No access to group - LEAVING")
        try:
            await client.delete_dialog(group)
            print(Fore.YELLOW + f"[{session_name}] 🚪 Left inaccessible group")
        except:
            pass
        return False
    except Exception as e:
        error_msg = str(e)[:30]
        print(Fore.RED + f"[{session_name}] ❌ Error: {error_msg}")
        return False

async def process_groups(client, session_name):
    try:
        groups = []
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
        
        if not groups:
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No groups found")
            return
        
        print(Fore.CYAN + f"[{session_name}] 📊 Processing {len(groups)} groups")
        
        processed = 0
        for group in groups:
            start_time = datetime.now()
            
            if await safe_forward(client, group, session_name):
                processed += 1
            
            elapsed = (datetime.now() - start_time).total_seconds()
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
            remaining_delay = max(0, delay - elapsed)
            
            if remaining_delay > 0:
                minutes = remaining_delay / 60
                print(Fore.BLUE + f"[{session_name}] ⏳ Waiting {minutes:.1f} minutes...")
                await asyncio.sleep(remaining_delay)
        
        print(Fore.CYAN + f"[{session_name}] 📈 Completed: {processed}/{len(groups)} groups")
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] 💥 Error: {str(e)[:50]}")

async def run_spammer_session(session_path, session_name):
    client = None
    try:
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            device_model="Android",
            system_version="10",
            system_lang_code="en-US"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] 👤 Connected as @{me.username or me.first_name}")
        
        while True:
            try:
                if not check_internet_connection():
                    print(Fore.YELLOW + f"[{session_name}] 🌐 Internet lost, waiting...")
                    await wait_for_internet()
                    await client.connect()
                
                await process_groups(client, session_name)
                
                print(Fore.YELLOW + f"[{session_name}] 🔄 Cycle completed. Sleeping for {CYCLE_DELAY//60} minutes...")
                
                for i in range(CYCLE_DELAY // 30):
                    if not check_internet_connection():
                        break
                    await asyncio.sleep(30)
                    
            except Exception as e:
                print(Fore.RED + f"[{session_name}] 💥 Operation error: {str(e)[:50]}")
                await asyncio.sleep(60)
                
    except UserDeactivatedBanError:
        print(Fore.RED + f"[{session_name}] 🚫 Account banned")
    except Exception as e:
        print(Fore.RED + f"[{session_name}] 💥 Connection failed: {str(e)[:50]}")
    finally:
        if client:
            try:
                await client.disconnect()
                print(Fore.YELLOW + f"[{session_name}] 🔌 Disconnected")
            except:
                pass

async def option2_group_spammer():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "📢 GROUP SPAMMER")
    print(Fore.CYAN + "═" * 60)
    
    print(Fore.YELLOW + f"\n🔥 Spam Message: {SPAM_MESSAGE}")
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found!")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} available sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    use_all = input(Fore.CYAN + "🚀 Use ALL sessions? (y/n): ").strip().lower()
    
    if use_all == 'y':
        selected_sessions = available_sessions
        print(Fore.GREEN + f"\n🔥 Starting ALL {len(available_sessions)} sessions...")
    else:
        print(Fore.CYAN + "\n📝 Enter session numbers (comma-separated, e.g., 1,3,5)")
        selection = input(Fore.CYAN + "   Selection: ").strip().lower()
        
        if selection == 'all':
            selected_sessions = available_sessions
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
            except:
                print(Fore.RED + "❌ Invalid selection, using all sessions")
                selected_sessions = available_sessions
    
    tasks = []
    for session_name, session_file in selected_sessions:
        tasks.append(run_spammer_session(session_file, session_name))
    
    if not tasks:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    print(Fore.GREEN + f"\n⚡ STARTING {len(tasks)} SESSIONS...\n")
    
    for i in range(3, 0, -1):
        print(Fore.YELLOW + f"🚀 Starting in {i}...")
        await asyncio.sleep(1)
    
    print(Fore.GREEN + "\n🔥 ALL SESSIONS RUNNING SIMULTANEOUSLY!\n")
    
    await asyncio.gather(*tasks, return_exceptions=True)

async def get_last_message(client):
    try:
        entity = await client.get_input_entity(TARGET_USERNAME)
        messages = await client.get_messages(entity, limit=1)
        return messages[0] if messages else None
    except Exception as e:
        print(Fore.RED + f"Error getting message: {str(e)}")
        return None

async def process_groups_forward(client, session_name, message):
    if not message:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No message to forward")
        return

    groups = []
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error getting groups: {str(e)}")
        return

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No groups found")
        return

    print(Fore.CYAN + f"[{session_name}] 📊 Processing {len(groups)} groups")
    
    processed = 0
    for group in groups:
        start_time = datetime.now()
        
        try:
            await client.forward_messages(group, message)
            group_name = getattr(group, 'title', 'GROUP')[:30]
            print(Fore.GREEN + f"[{session_name}] ✅ Sent to {group_name}")
            processed += 1
        except (ChannelPrivateError, ChatWriteForbiddenError):
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No access")
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__} - {str(e)}")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        remaining_delay = max(0, delay - elapsed)
        
        if remaining_delay > 0:
            minutes = remaining_delay / 60
            print(Fore.BLUE + f"[{session_name}] ⏳ Waiting {minutes:.1f} minutes before next group")
            await asyncio.sleep(remaining_delay)
    
    print(Fore.CYAN + f"[{session_name}] 📈 Sent to {processed}/{len(groups)} groups")

async def run_auto_reply_forwarder_session(session_path, session_name):
    client = None
    try:
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            device_model="Android",
            system_version="10",
            app_version="8.4",
            lang_code="en",
            system_lang_code="en-US"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] 👤 Auto-reply + forwarder active as @{me.username or me.first_name}")
        
        @client.on(events.NewMessage(incoming=True))
        async def handler(event):
            if event.is_private:
                try:
                    await event.reply(AUTO_REPLY_MESSAGE)
                    sender = event.sender
                    sender_name = f"@{sender.username}" if sender.username else sender.first_name
                    print(Fore.MAGENTA + f"[{session_name}] 🤖 Auto-replied to {sender_name}")
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] ❌ Auto-reply failed: {str(e)}")
        
        print(Fore.YELLOW + f"[{session_name}] 🤖 Auto-reply bot running with message: {AUTO_REPLY_MESSAGE}")
        print(Fore.YELLOW + f"[{session_name}] 🔄 Forwarding from: @{TARGET_USERNAME}")
        
        while True:
            try:
                if not check_internet_connection():
                    print(Fore.YELLOW + f"[{session_name}] 🌐 Internet lost, waiting...")
                    await wait_for_internet()
                    await client.connect()
                
                message = await get_last_message(client)
                await process_groups_forward(client, session_name, message)
                
                print(Fore.YELLOW + f"[{session_name}] 🔄 Cycle completed. Sleeping for {CYCLE_DELAY//60} minutes...")
                
                for i in range(CYCLE_DELAY // 30):
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] 🌐 Internet check failed")
                        break
                    await asyncio.sleep(30)
                    
            except Exception as e:
                print(Fore.RED + f"[{session_name}] 💥 Operation error: {type(e).__name__} - {str(e)}")
                await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"[{session_name}] ⏹️ Auto-reply + forwarder stopped")
    except UserDeactivatedBanError:
        print(Fore.RED + f"[{session_name}] 🚫 Account banned")
    except Exception as e:
        print(Fore.RED + f"[{session_name}] 💥 Error: {str(e)[:50]}")
    finally:
        if client:
            try:
                await client.disconnect()
            except:
                pass

async def option3_auto_reply_forwarder():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "🤖 AUTO-REPLY + FORWARDER BOT")
    print(Fore.CYAN + "═" * 60)
    
    print(Fore.YELLOW + f"\n💬 Auto-reply message: {AUTO_REPLY_MESSAGE}")
    print(Fore.YELLOW + f"🎯 Forwarding from: @{TARGET_USERNAME}")
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found!")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} available sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    use_all = input(Fore.CYAN + "🚀 Use ALL sessions? (y/n): ").strip().lower()
    
    if use_all == 'y':
        selected_sessions = available_sessions
        print(Fore.GREEN + f"\n🔥 Starting auto-reply + forwarder on ALL {len(available_sessions)} sessions...")
    else:
        print(Fore.CYAN + "\n📝 Enter session numbers (comma-separated, e.g., 1,3,5)")
        selection = input(Fore.CYAN + "   Selection: ").strip().lower()
        
        if selection == 'all':
            selected_sessions = available_sessions
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
            except:
                print(Fore.RED + "❌ Invalid selection, using all sessions")
                selected_sessions = available_sessions
    
    tasks = []
    for session_name, session_file in selected_sessions:
        tasks.append(run_auto_reply_forwarder_session(session_file, session_name))
    
    if not tasks:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    print(Fore.GREEN + f"\n🤖 STARTING AUTO-REPLY + FORWARDER ON {len(tasks)} SESSIONS...\n")
    
    for i in range(3, 0, -1):
        print(Fore.YELLOW + f"🚀 Starting in {i}...")
        await asyncio.sleep(1)
    
    print(Fore.GREEN + "\n🔥 ALL SESSIONS RUNNING SIMULTANEOUSLY!\n")
    
    await asyncio.gather(*tasks, return_exceptions=True)

async def flood_wait_handler(seconds):
    print(Fore.YELLOW + f"⏳ Flood wait: {seconds} seconds")
    for i in range(seconds, 0, -1):
        print(Fore.CYAN + f"   Waiting {i}s...", end="\r")
        await asyncio.sleep(1)
    print(" " * 30, end="\r")
    print(Fore.GREEN + "✅ Flood wait complete")

async def send_code_with_retry(client, phone):
    for attempt in range(2):
        try:
            print(Fore.YELLOW + "📤 Sending verification code...")
            return await client.send_code_request(phone)
        except FloodWaitError as e:
            await flood_wait_handler(e.seconds)
            continue
        except PhoneNumberFloodError:
            print(Fore.RED + "❌ Phone number flood! Try later")
            return None
        except:
            if attempt < 1:
                await asyncio.sleep(2)
                continue
            return None
    return None

async def create_single_session():
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "🔧 SINGLE SESSION CREATION")
    print(Fore.CYAN + "═" * 60)
    
    phone = input(Fore.YELLOW + "\n📱 Phone number (+1234567890): ").strip()
    if not phone:
        print(Fore.RED + "❌ Phone number is required!")
        return False
    
    session_filename = clean_phone_for_filename(phone)
    session_path = os.path.join(ACCOUNTS_FOLDER, f"{session_filename}.session")
    
    if os.path.exists(session_path):
        print(Fore.YELLOW + f"⚠️ Session for {phone} already exists in accounts folder")
        overwrite = input(Fore.YELLOW + "Overwrite? (y/n): ").strip().lower()
        if overwrite != 'y':
            print(Fore.YELLOW + "⏭️ Skipping")
            return False
    
    api_creds = get_rotated_api()
    api_id = api_creds['api_id']
    api_hash = api_creds['api_hash']
    
    print(Fore.GREEN + f"🔑 Using API ID: {api_id}")
    
    client = None
    try:
        client = TelegramClient(session_path, api_id, api_hash)
        await client.connect()
        print(Fore.GREEN + "✅ Connected to Telegram")
        
        sent_code = await send_code_with_retry(client, phone)
        if not sent_code:
            print(Fore.RED + "❌ Failed to send verification code")
            await client.disconnect()
            if os.path.exists(session_path):
                os.remove(session_path)
            return False
        
        phone_code_hash = sent_code.phone_code_hash
        print(Fore.GREEN + "✅ Verification code sent")
        
        for otp_attempt in range(3):
            otp = input(Fore.YELLOW + f"📝 OTP (attempt {otp_attempt+1}/3, 'r' to resend, 's' to skip): ").strip()
            
            if otp.lower() == 'r':
                sent_code = await send_code_with_retry(client, phone)
                if sent_code:
                    phone_code_hash = sent_code.phone_code_hash
                    otp_attempt = -1
                    continue
                else:
                    continue
            
            if otp.lower() == 's':
                print(Fore.YELLOW + "⏭️ Skipping")
                await client.disconnect()
                if os.path.exists(session_path):
                    os.remove(session_path)
                return False
            
            if not otp.isdigit() or len(otp) != 5:
                print(Fore.RED + "❌ Invalid OTP format (must be 5 digits)")
                if otp_attempt < 2:
                    continue
                break
            
            try:
                await client.sign_in(
                    phone=phone,
                    code=otp,
                    phone_code_hash=phone_code_hash
                )
                success = True
                break
            except SessionPasswordNeededError:
                print(Fore.YELLOW + "🔒 2FA password required")
                password = input(Fore.YELLOW + "🔑 2FA password: ").strip()
                if password:
                    try:
                        await client.sign_in(password=password)
                        success = True
                        break
                    except:
                        print(Fore.RED + "❌ Wrong 2FA password")
                        success = False
                        break
                else:
                    success = False
                    break
            except PhoneCodeInvalidError:
                print(Fore.RED + "❌ Invalid OTP")
                if otp_attempt < 2:
                    continue
                success = False
                break
            except Exception as e:
                if "two-step" in str(e).lower():
                    print(Fore.YELLOW + "🔒 2FA password required")
                    password = input(Fore.YELLOW + "🔑 2FA password: ").strip()
                    if password:
                        try:
                            await client.sign_in(password=password)
                            success = True
                            break
                        except:
                            print(Fore.RED + "❌ Wrong 2FA password")
                            success = False
                            break
                    else:
                        success = False
                        break
                else:
                    print(Fore.RED + f"❌ Error: {str(e)[:50]}")
                    success = False
                    break
        
        if not success:
            print(Fore.RED + "❌ Login failed")
            await client.disconnect()
            if os.path.exists(session_path):
                os.remove(session_path)
            return False
        
        try:
            me = await client.get_me()
            print(Fore.GREEN + f"✅ Logged in as: @{me.username or me.first_name or me.id}")
        except:
            pass
        
        try:
            session_string = StringSession.save(client.session)
            string_filename = f"{session_filename}_string.txt"
            string_file = os.path.join(SESSIONS_FOLDER, string_filename)
            with open(string_file, 'w') as f:
                f.write(session_string)
            print(Fore.GREEN + f"📝 String session saved: {string_filename}")
        except:
            pass
        
        print(Fore.GREEN + f"\n🎉 Session created successfully!")
        print(Fore.YELLOW + f"📁 Session file: {ACCOUNTS_FOLDER}/{session_filename}.session")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(Fore.RED + f"❌ Error: {str(e)[:50]}")
        if client:
            try:
                await client.disconnect()
            except:
                pass
        if os.path.exists(session_path):
            os.remove(session_path)
        return False

async def bulk_create_sessions():
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "📦 BULK SESSION CREATION")
    print(Fore.CYAN + "═" * 60)
    
    numbers_file = "phone_numbers.txt"
    if not os.path.exists(numbers_file):
        print(Fore.RED + f"❌ {numbers_file} not found!")
        print(Fore.YELLOW + "Create 'phone_numbers.txt' with phone numbers (one per line)")
        return
    
    with open(numbers_file, 'r') as f:
        phones = [line.strip() for line in f if line.strip()]
    
    if not phones:
        print(Fore.RED + "❌ No phone numbers in file!")
        return
    
    print(Fore.GREEN + f"✅ Found {len(phones)} phone numbers")
    
    success_count = 0
    for i, phone in enumerate(phones, 1):
        print(Fore.CYAN + f"\n[{i}/{len(phones)}] Processing: {phone}")
        
        session_filename = clean_phone_for_filename(phone)
        session_path = os.path.join(ACCOUNTS_FOLDER, f"{session_filename}.session")
        
        if os.path.exists(session_path):
            print(Fore.YELLOW + f"⚠️ Session exists in accounts folder: {session_filename}.session")
            overwrite = input(Fore.YELLOW + "Overwrite? (y/n/skip): ").strip().lower()
            if overwrite == 'n':
                print(Fore.YELLOW + "⏭️ Skipping")
                continue
            elif overwrite == 'skip':
                print(Fore.YELLOW + "⏭️ Skipping all duplicates")
                break
        
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = None
        try:
            client = TelegramClient(session_path, api_id, api_hash)
            await client.connect()
            
            sent_code = await send_code_with_retry(client, phone)
            if not sent_code:
                print(Fore.RED + "❌ Can't send code")
                continue
            
            phone_code_hash = sent_code.phone_code_hash
            print(Fore.YELLOW + "📤 Code sent, enter OTP below")
            
            otp = input(Fore.YELLOW + f"OTP for {phone}: ").strip()
            if not otp or len(otp) != 5:
                print(Fore.RED + "❌ Invalid OTP")
                continue
            
            try:
                await client.sign_in(
                    phone=phone,
                    code=otp,
                    phone_code_hash=phone_code_hash
                )
            except SessionPasswordNeededError:
                print(Fore.YELLOW + "🔒 2FA needed")
                password = input(Fore.YELLOW + f"2FA for {phone}: ").strip()
                if password:
                    try:
                        await client.sign_in(password=password)
                    except:
                        print(Fore.RED + "❌ 2FA failed")
                        continue
                else:
                    continue
            except Exception as e:
                if "two-step" in str(e).lower():
                    print(Fore.YELLOW + "🔒 2FA needed")
                    password = input(Fore.YELLOW + f"2FA for {phone}: ").strip()
                    if password:
                        try:
                            await client.sign_in(password=password)
                        except:
                            print(Fore.RED + "❌ 2FA failed")
                            continue
                    else:
                        continue
                else:
                    print(Fore.RED + f"❌ Login error: {str(e)[:50]}")
                    continue
            
            print(Fore.GREEN + f"✅ Saved to accounts folder: {session_filename}.session")
            success_count += 1
            
            await client.disconnect()
            
        except Exception as e:
            print(Fore.RED + f"❌ Failed: {str(e)[:50]}")
            if client:
                try:
                    await client.disconnect()
                except:
                    pass
            if os.path.exists(session_path):
                os.remove(session_path)
            continue
    
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + f"✅ BULK CREATION COMPLETE!")
    print(Fore.YELLOW + f"📊 Success: {success_count}/{len(phones)}")
    print(Fore.CYAN + "═" * 60)

async def option4_session_creator():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "🔧 SESSION CREATOR")
    print(Fore.CYAN + "═" * 60)
    
    print(Fore.YELLOW + "\n📱 Choose creation mode:")
    print(Fore.WHITE + "   1. 📱 Create Single Session")
    print(Fore.WHITE + "   2. 📦 Bulk Create Sessions (from phone_numbers.txt)")
    print(Fore.WHITE + "   3. 🔙 Back to Main Menu")
    
    choice = input(Fore.CYAN + "\n   Select option (1-3): ").strip()
    
    if choice == "1":
        await create_single_session()
    elif choice == "2":
        await bulk_create_sessions()
    else:
        return

async def change_session_name_func(session_path, session_name, new_first_name, new_last_name=""):
    client = None
    try:
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            device_model="Android",
            system_version="10",
            app_version="8.4"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return False
        
        await client(functions.account.UpdateProfileRequest(
            first_name=new_first_name,
            last_name=new_last_name
        ))
        
        print(Fore.GREEN + f"[{session_name}] ✅ Name changed to: {new_first_name} {new_last_name}")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error: {str(e)[:50]}")
        if client:
            try:
                await client.disconnect()
            except:
                pass
        return False

async def option5_name_changer():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "👤 NAME CHANGER")
    print(Fore.CYAN + "═" * 60)
    
    print(Fore.YELLOW + "\n🎯 Choose name change mode:")
    print(Fore.WHITE + "   1. 🔄 Set Same Name for All Sessions")
    print(Fore.WHITE + "   2. ✏️ Set Custom Names for Each Session")
    print(Fore.WHITE + "   3. 🔙 Back to Main Menu")
    
    choice = input(Fore.CYAN + "\n   Select option (1-3): ").strip()
    
    if choice == "1":
        first_name = input(Fore.YELLOW + "\n   Enter first name: ").strip()
        if not first_name:
            print(Fore.RED + "❌ First name is required!")
            return
        
        last_name = input(Fore.YELLOW + "   Enter last name (optional): ").strip()
        
        session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
        
        if not session_files:
            print(Fore.RED + "❌ No .session files found!")
            return
        
        available_sessions = []
        for session_file in session_files:
            session_name = os.path.basename(session_file).replace('.session', '')
            available_sessions.append((session_name, session_file))
        
        print(Fore.GREEN + f"✅ Found {len(available_sessions)} sessions in accounts folder")
        
        tasks = []
        for session_name, session_file in available_sessions:
            tasks.append(change_session_name_func(session_file, session_name, first_name, last_name))
        
        if tasks:
            print(Fore.GREEN + f"\n⚡ CHANGING NAMES FOR {len(tasks)} SESSIONS...\n")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            print(Fore.GREEN + f"\n✅ COMPLETED! {success_count}/{len(tasks)} names changed successfully!")
    
    elif choice == "2":
        session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
        
        if not session_files:
            print(Fore.RED + "❌ No .session files found!")
            return
        
        available_sessions = []
        for session_file in session_files:
            session_name = os.path.basename(session_file).replace('.session', '')
            available_sessions.append((session_name, session_file))
        
        print(Fore.GREEN + f"✅ Found {len(available_sessions)} sessions in accounts folder")
        
        for session_name, session_file in available_sessions:
            print(Fore.CYAN + f"\n📱 Session: {session_name}")
            first_name = input(Fore.YELLOW + f"   Enter first name for {session_name}: ").strip()
            
            if not first_name:
                print(Fore.YELLOW + "   ⏭️ Skipping...")
                continue
            
            last_name = input(Fore.YELLOW + f"   Enter last name for {session_name} (optional): ").strip()
            
            success = await change_session_name_func(session_file, session_name, first_name, last_name)
            
            if success:
                print(Fore.GREEN + f"   ✅ Name changed for {session_name}")
            else:
                print(Fore.RED + f"   ❌ Failed to change name for {session_name}")
    
    else:
        return

async def change_session_bio(session_path, session_name, new_bio):
    client = None
    try:
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            device_model="Android",
            system_version="10",
            app_version="8.4"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return False
        
        await client(functions.account.UpdateProfileRequest(
            about=new_bio
        ))
        
        print(Fore.GREEN + f"[{session_name}] ✅ Bio changed to: {new_bio[:50]}...")
        
        await client.disconnect()
        return True
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error: {str(e)[:50]}")
        if client:
            try:
                await client.disconnect()
            except:
                pass
        return False

async def option6_bio_changer():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "📝 BIO CHANGER")
    print(Fore.CYAN + "═" * 60)
    
    print(Fore.YELLOW + "\n🎯 Choose bio change mode:")
    print(Fore.WHITE + "   1. 🔄 Set Same Bio for All Sessions")
    print(Fore.WHITE + "   2. ✏️ Set Custom Bio for Each Session")
    print(Fore.WHITE + "   3. 🔙 Back to Main Menu")
    
    choice = input(Fore.CYAN + "\n   Select option (1-3): ").strip()
    
    if choice == "1":
        bio = input(Fore.YELLOW + "\n   Enter bio text: ").strip()
        if not bio:
            print(Fore.RED + "❌ Bio text is required!")
            return
        
        session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
        
        if not session_files:
            print(Fore.RED + "❌ No .session files found!")
            return
        
        available_sessions = []
        for session_file in session_files:
            session_name = os.path.basename(session_file).replace('.session', '')
            available_sessions.append((session_name, session_file))
        
        print(Fore.GREEN + f"✅ Found {len(available_sessions)} sessions in accounts folder")
        
        tasks = []
        for session_name, session_file in available_sessions:
            tasks.append(change_session_bio(session_file, session_name, bio))
        
        if tasks:
            print(Fore.GREEN + f"\n⚡ CHANGING BIOS FOR {len(tasks)} SESSIONS...\n")
            results = await asyncio.gather(*tasks, return_exceptions=True)
            success_count = sum(1 for r in results if r is True)
            print(Fore.GREEN + f"\n✅ COMPLETED! {success_count}/{len(tasks)} bios changed successfully!")
    
    elif choice == "2":
        session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
        
        if not session_files:
            print(Fore.RED + "❌ No .session files found!")
            return
        
        available_sessions = []
        for session_file in session_files:
            session_name = os.path.basename(session_file).replace('.session', '')
            available_sessions.append((session_name, session_file))
        
        print(Fore.GREEN + f"✅ Found {len(available_sessions)} sessions in accounts folder")
        
        for session_name, session_file in available_sessions:
            print(Fore.CYAN + f"\n📱 Session: {session_name}")
            bio = input(Fore.YELLOW + f"   Enter bio for {session_name}: ").strip()
            
            if not bio:
                print(Fore.YELLOW + "   ⏭️ Skipping...")
                continue
            
            success = await change_session_bio(session_file, session_name, bio)
            
            if success:
                print(Fore.GREEN + f"   ✅ Bio changed for {session_name}")
            else:
                print(Fore.RED + f"   ❌ Failed to change bio for {session_name}")
    
    else:
        return

# ==================== MODIFIED OPTION: DM FORWARDER (COPY-PASTE) - FIXED ====================
async def get_target_user_last_message(client, session_name, target_username):
    """Get the last message from target user instead of random DMs"""
    try:
        # Get the target user entity
        if target_username.isdigit():
            target_entity = await client.get_entity(int(target_username))
        else:
            target_entity = await client.get_entity(target_username)
        
        # Get last 1 message from target user
        messages = []
        try:
            async for message in client.iter_messages(target_entity, limit=1):
                if message.text and message.text.strip():  # Only messages with text
                    messages.append(message)
        except:
            pass
        
        if not messages:
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No text messages found from target user")
            return None
        
        # Get the last message
        selected_message = messages[0]
        
        # Get user info for logging
        user_name = getattr(target_entity, 'username', 'Unknown')
        if not user_name or user_name == 'Unknown':
            user_name = getattr(target_entity, 'first_name', 'Target User')
        
        print(Fore.CYAN + f"[{session_name}] 📩 Last message from @{user_name}: {selected_message.text[:50]}...")
        
        return selected_message
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error fetching target user message: {str(e)[:50]}")
        return None

async def process_groups_copy_dm(client, session_name, target_username):
    # Get last message from target user
    message = await get_target_user_last_message(client, session_name, target_username)
    
    if not message:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No message to copy from target user")
        return
    
    # Get all groups
    groups = []
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error getting groups: {str(e)}")
        return

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No groups found")
        return

    print(Fore.CYAN + f"[{session_name}] 📊 Processing {len(groups)} groups with target user's message")
    
    processed = 0
    for group in groups:
        start_time = datetime.now()
        
        try:
            # Copy and paste the message (not forward)
            await client.send_message(group, message.text)
            group_name = getattr(group, 'title', 'GROUP')[:30]
            msg_preview = message.text[:30] + "..." if len(message.text) > 30 else message.text
            print(Fore.GREEN + f"[{session_name}] ✅ Copied '{msg_preview}' to {group_name}")
            processed += 1
        except (ChannelPrivateError, ChatWriteForbiddenError):
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No access to group")
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__}")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        remaining_delay = max(0, delay - elapsed)
        
        if remaining_delay > 0:
            minutes = remaining_delay / 60
            print(Fore.BLUE + f"[{session_name}] ⏳ Waiting {minutes:.1f} minutes before next group")
            await asyncio.sleep(remaining_delay)
    
    print(Fore.CYAN + f"[{session_name}] 📈 Copied message to {processed}/{len(groups)} groups")

async def run_dm_forwarder_session(session_path, session_name, target_username):
    client = None
    try:
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            device_model="Android",
            system_version="10",
            app_version="8.4",
            lang_code="en",
            system_lang_code="en-US"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] 👤 DM Forwarder active as @{me.username or me.first_name}")
        print(Fore.YELLOW + f"[{session_name}] 🔄 Copying last message from @{target_username} to groups (copy-paste mode)")
        
        while True:
            try:
                if not check_internet_connection():
                    print(Fore.YELLOW + f"[{session_name}] 🌐 Internet lost, waiting...")
                    await wait_for_internet()
                    await client.connect()
                
                await process_groups_copy_dm(client, session_name, target_username)
                
                print(Fore.YELLOW + f"[{session_name}] 🔄 Cycle completed. Sleeping for {CYCLE_DELAY//60} minutes...")
                
                for i in range(CYCLE_DELAY // 30):
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] 🌐 Internet check failed")
                        break
                    await asyncio.sleep(30)
                    
            except Exception as e:
                print(Fore.RED + f"[{session_name}] 💥 Operation error: {type(e).__name__} - {str(e)}")
                await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"[{session_name}] ⏹️ DM Forwarder stopped")
    except UserDeactivatedBanError:
        print(Fore.RED + f"[{session_name}] 🚫 Account banned")
    except Exception as e:
        print(Fore.RED + f"[{session_name}] 💥 Error: {str(e)[:50]}")
    finally:
        if client:
            try:
                await client.disconnect()
            except:
                pass

async def option7_dm_forwarder():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "📩 DM FORWARDER (COPY-PASTE)")
    print(Fore.CYAN + "═" * 60)
    
    target_username = input(Fore.YELLOW + "\n🎯 Target username to get last message from (without @): ").strip()
    if not target_username:
        print(Fore.RED + "❌ Target username is required!")
        return
    
    print(Fore.YELLOW + f"\n📝 Will copy last message from @{target_username} to groups")
    print(Fore.YELLOW + "🎯 Source: Last message from @{target_username}")
    print(Fore.YELLOW + "🎯 Target: All groups you're in")
    print(Fore.YELLOW + "🔒 Mode: Copy-paste (not forward, shows as your message)")
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found!")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} available sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    use_all = input(Fore.CYAN + "🚀 Use ALL sessions? (y/n): ").strip().lower()
    
    if use_all == 'y':
        selected_sessions = available_sessions
        print(Fore.GREEN + f"\n🔥 Starting DM forwarder on ALL {len(available_sessions)} sessions...")
    else:
        print(Fore.CYAN + "\n📝 Enter session numbers (comma-separated, e.g., 1,3,5)")
        selection = input(Fore.CYAN + "   Selection: ").strip().lower()
        
        if selection == 'all':
            selected_sessions = available_sessions
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
            except:
                print(Fore.RED + "❌ Invalid selection, using all sessions")
                selected_sessions = available_sessions
    
    tasks = []
    for session_name, session_file in selected_sessions:
        tasks.append(run_dm_forwarder_session(session_file, session_name, target_username))
    
    if not tasks:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    print(Fore.GREEN + f"\n📩 STARTING DM FORWARDER ON {len(tasks)} SESSIONS...\n")
    
    for i in range(3, 0, -1):
        print(Fore.YELLOW + f"🚀 Starting in {i}...")
        await asyncio.sleep(1)
    
    print(Fore.GREEN + "\n🔥 ALL SESSIONS RUNNING SIMULTANEOUSLY!\n")
    
    await asyncio.gather(*tasks, return_exceptions=True)
# ==================== END MODIFIED OPTION ====================

# ==================== NEW OPTION: CHANNEL FORWARDER ====================
async def forward_from_channel(client, session_name, channel_username):
    try:
        if not channel_username:
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No channel username provided")
            return None
        
        # Get the channel entity
        try:
            if channel_username.isdigit():
                channel = await client.get_entity(int(channel_username))
            else:
                if not channel_username.startswith('@'):
                    channel_username = '@' + channel_username
                channel = await client.get_entity(channel_username)
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Can't access channel: {str(e)[:50]}")
            return None
        
        # Get last 10 messages from channel
        messages = []
        try:
            async for message in client.iter_messages(channel, limit=10):
                messages.append(message)
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Can't fetch messages: {str(e)[:50]}")
            return None
        
        if not messages:
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No messages found in channel")
            return None
        
        # Select random message from last 10
        selected_message = random.choice(messages)
        
        # Check if message has content
        if not selected_message.text and not selected_message.media:
            print(Fore.YELLOW + f"[{session_name}] ⚠️ Selected message has no content")
            return None
        
        return selected_message
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Channel error: {str(e)[:50]}")
        return None

async def process_groups_forward_from_channel(client, session_name, channel_username):
    # Get random message from channel
    message = await forward_from_channel(client, session_name, channel_username)
    
    if not message:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No message to forward from channel")
        return
    
    # Get all groups
    groups = []
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group:
                groups.append(dialog.entity)
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error getting groups: {str(e)}")
        return

    if not groups:
        print(Fore.YELLOW + f"[{session_name}] ⚠️ No groups found")
        return

    print(Fore.CYAN + f"[{session_name}] 📊 Processing {len(groups)} groups with channel content")
    
    processed = 0
    for group in groups:
        start_time = datetime.now()
        
        try:
            # Forward message instead of copying
            await client.forward_messages(group, message)
            group_name = getattr(group, 'title', 'GROUP')[:30]
            msg_preview = message.text[:30] + "..." if message.text else "[MEDIA]"
            print(Fore.GREEN + f"[{session_name}] ✅ Forwarded '{msg_preview}' to {group_name}")
            processed += 1
        except (ChannelPrivateError, ChatWriteForbiddenError):
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No access to group")
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Error: {type(e).__name__}")
        
        elapsed = (datetime.now() - start_time).total_seconds()
        delay = random.uniform(MIN_DELAY, MAX_DELAY)
        remaining_delay = max(0, delay - elapsed)
        
        if remaining_delay > 0:
            minutes = remaining_delay / 60
            print(Fore.BLUE + f"[{session_name}] ⏳ Waiting {minutes:.1f} minutes before next group")
            await asyncio.sleep(remaining_delay)
    
    print(Fore.CYAN + f"[{session_name}] 📈 Forwarded to {processed}/{len(groups)} groups")

async def run_channel_forwarder_session(session_path, session_name, channel_username):
    client = None
    try:
        api_creds = get_rotated_api()
        api_id = api_creds['api_id']
        api_hash = api_creds['api_hash']
        
        client = TelegramClient(
            session_path,
            api_id,
            api_hash,
            device_model="Android",
            system_version="10",
            app_version="8.4",
            lang_code="en",
            system_lang_code="en-US"
        )
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] 👤 Channel forwarder active as @{me.username or me.first_name}")
        
        print(Fore.YELLOW + f"[{session_name}] 🔄 Forwarding random message from last 10 messages of: {channel_username}")
        
        while True:
            try:
                if not check_internet_connection():
                    print(Fore.YELLOW + f"[{session_name}] 🌐 Internet lost, waiting...")
                    await wait_for_internet()
                    await client.connect()
                
                await process_groups_forward_from_channel(client, session_name, channel_username)
                
                print(Fore.YELLOW + f"[{session_name}] 🔄 Cycle completed. Sleeping for {CYCLE_DELAY//60} minutes...")
                
                for i in range(CYCLE_DELAY // 30):
                    if not check_internet_connection():
                        print(Fore.YELLOW + f"[{session_name}] 🌐 Internet check failed")
                        break
                    await asyncio.sleep(30)
                    
            except Exception as e:
                print(Fore.RED + f"[{session_name}] 💥 Operation error: {type(e).__name__} - {str(e)}")
                await asyncio.sleep(60)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"[{session_name}] ⏹️ Channel forwarder stopped")
    except UserDeactivatedBanError:
        print(Fore.RED + f"[{session_name}] 🚫 Account banned")
    except Exception as e:
        print(Fore.RED + f"[{session_name}] 💥 Error: {str(e)[:50]}")
    finally:
        if client:
            try:
                await client.disconnect()
            except:
                pass

async def option8_channel_forwarder():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "🔄 CHANNEL FORWARDER")
    print(Fore.CYAN + "═" * 60)
    
    channel_username = input(Fore.YELLOW + "\n📢 Channel username (with or without @): ").strip()
    if not channel_username:
        print(Fore.RED + "❌ Channel username is required!")
        return
    
    print(Fore.YELLOW + f"\n📝 Will forward random message from last 10 messages of: {channel_username}")
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found!")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} available sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    use_all = input(Fore.CYAN + "🚀 Use ALL sessions? (y/n): ").strip().lower()
    
    if use_all == 'y':
        selected_sessions = available_sessions
        print(Fore.GREEN + f"\n🔥 Starting channel forwarder on ALL {len(available_sessions)} sessions...")
    else:
        print(Fore.CYAN + "\n📝 Enter session numbers (comma-separated, e.g., 1,3,5)")
        selection = input(Fore.CYAN + "   Selection: ").strip().lower()
        
        if selection == 'all':
            selected_sessions = available_sessions
        else:
            try:
                indices = [int(x.strip()) - 1 for x in selection.split(',')]
                selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
            except:
                print(Fore.RED + "❌ Invalid selection, using all sessions")
                selected_sessions = available_sessions
    
    tasks = []
    for session_name, session_file in selected_sessions:
        tasks.append(run_channel_forwarder_session(session_file, session_name, channel_username))
    
    if not tasks:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    print(Fore.GREEN + f"\n🔄 STARTING CHANNEL FORWARDER ON {len(tasks)} SESSIONS...\n")
    
    for i in range(3, 0, -1):
        print(Fore.YELLOW + f"🚀 Starting in {i}...")
        await asyncio.sleep(1)
    
    print(Fore.GREEN + "\n🔥 ALL SESSIONS RUNNING SIMULTANEOUSLY!\n")
    
    await asyncio.gather(*tasks, return_exceptions=True)
# ==================== END NEW OPTION ====================

# ==================== NEW OPTIONS FROM SEX.PY ====================

# DELAY CONFIGURATION FOR NEW OPTIONS
MIN_DELAY_BETWEEN_GROUPS = 15
MAX_DELAY_BETWEEN_GROUPS = 30
MIN_DELAY_BETWEEN_SESSIONS = 10
MAX_DELAY_BETWEEN_SESSIONS = 20
FLOOD_WAIT_DELAY = 30

async def check_session_valid(session_path, session_name):
    """Check if session is valid and authorized"""
    client = None
    try:
        api_creds = get_rotated_api()
        client = TelegramClient(session_path, api_creds['api_id'], api_creds['api_hash'])
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return False
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] ✅ Valid session - @{me.username or me.first_name}")
        return True
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Invalid session: {str(e)[:50]}")
        return False
    finally:
        if client:
            await client.disconnect()

async def option9_check_sessions():
    """Check all sessions in accounts folder"""
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "✅ SESSION VALIDITY CHECK")
    print(Fore.CYAN + "═" * 60)
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found in '{ACCOUNTS_FOLDER}/' folder!")
        return
    
    print(Fore.GREEN + f"✅ Found {len(session_files)} session files")
    print()
    
    valid_count = 0
    tasks = []
    
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        tasks.append(check_session_valid(session_file, session_name))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    valid_count = sum(1 for r in results if r is True)
    
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.YELLOW + f"📊 RESULTS: {valid_count}/{len(session_files)} sessions are valid")
    print(Fore.CYAN + "═" * 60)

# ==================== HELPER FUNCTIONS FOR PASSWORD HASHING ====================
def compute_password_hash(password, salt):
    """Compute password hash for SRP"""
    import hashlib
    import base64
    
    hash_func = hashlib.sha256
    hash1 = hash_func(salt + password.encode('utf-8')).digest()
    hash2 = hash_func(hash1).digest()
    return hash_func(hash2 + salt).digest()

def compute_check_password(password, algo):
    """Compute check password for SRP verification"""
    import hashlib
    import base64
    
    pw_hash = compute_password_hash(password, algo.salt)
    return hashlib.sha256(algo.p + pw_hash).digest()

# ==================== POWERFUL 2FA PASSWORD CHANGER ====================
async def change_2fa_password_powerful(session_path, session_name):
    """Powerful 2FA password changer that works for ALL accounts"""
    client = None
    try:
        api_creds = get_rotated_api()
        client = TelegramClient(session_path, api_creds['api_id'], api_creds['api_hash'])
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return False
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] 👤 Account: @{me.username or me.first_name}")
        
        # Get current password info
        try:
            password_info = await client(functions.account.GetPasswordRequest())
            
            if password_info.has_password:
                print(Fore.YELLOW + f"[{session_name}] 🔒 2FA is ENABLED")
                
                # Ask for current password
                current_password = input(Fore.YELLOW + f"   Enter CURRENT 2FA password: ").strip()
                if not current_password:
                    print(Fore.RED + f"   ❌ Current password required")
                    return False
                
                # Verify current password first
                try:
                    # Ask for new password
                    new_password = input(Fore.YELLOW + f"   Enter NEW 2FA password: ").strip()
                    if not new_password:
                        print(Fore.RED + f"   ❌ New password required")
                        return False
                    
                    confirm_password = input(Fore.YELLOW + f"   Confirm NEW 2FA password: ").strip()
                    if new_password != confirm_password:
                        print(Fore.RED + f"   ❌ Passwords don't match")
                        return False
                    
                    hint = input(Fore.YELLOW + f"   Enter password hint (optional): ").strip()
                    
                    # Use edit_2fa method which is simpler and more reliable
                    try:
                        await client.edit_2fa(
                            current_password=current_password,
                            new_password=new_password,
                            hint=hint
                        )
                        
                        print(Fore.GREEN + f"[{session_name}] ✅ 2FA PASSWORD CHANGED SUCCESSFULLY!")
                        print(Fore.YELLOW + f"   Old password: {current_password}")
                        print(Fore.YELLOW + f"   New password: {new_password}")
                        print(Fore.YELLOW + f"   Hint: {hint if hint else 'None'}")
                        return True
                        
                    except PasswordHashInvalidError:
                        print(Fore.RED + f"[{session_name}] ❌ WRONG CURRENT PASSWORD!")
                        return False
                    except Exception as e:
                        print(Fore.RED + f"[{session_name}] ❌ Password change error: {str(e)[:100]}")
                        # Try alternative method
                        try:
                            await client(functions.account.UpdatePasswordSettingsRequest(
                                password=types.InputCheckPasswordSRP(
                                    srp_id=password_info.current_algo.srp_id,
                                    A=password_info.current_algo.A,
                                    M1=compute_check_password(current_password, password_info.current_algo)
                                ),
                                new_settings=types.account.PasswordInputSettings(
                                    new_algo=password_info.new_algo,
                                    new_password_hash=compute_check_password(new_password, password_info.new_algo),
                                    hint=hint,
                                    email=password_info.email_unconfirmed_pattern,
                                    new_secure_settings=None
                                )
                            ))
                            print(Fore.GREEN + f"[{session_name}] ✅ 2FA PASSWORD CHANGED (alternative method)!")
                            return True
                        except Exception as e2:
                            print(Fore.RED + f"[{session_name}] ❌ Alternative method also failed: {str(e2)[:100]}")
                            return False
                            
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] ❌ Password verification failed: {str(e)[:50]}")
                    return False
                    
            else:
                print(Fore.YELLOW + f"[{session_name}] 🔓 2FA is NOT ENABLED")
                
                enable = input(Fore.YELLOW + f"   Enable 2FA? (y/n): ").strip().lower()
                if enable != 'y':
                    print(Fore.YELLOW + f"   ⏭️ Skipping")
                    return False
                
                new_password = input(Fore.YELLOW + f"   Enter NEW 2FA password: ").strip()
                if not new_password:
                    print(Fore.RED + f"   ❌ Password required")
                    return False
                
                confirm_password = input(Fore.YELLOW + f"   Confirm NEW 2FA password: ").strip()
                if new_password != confirm_password:
                    print(Fore.RED + f"   ❌ Passwords don't match")
                    return False
                
                hint = input(Fore.YELLOW + f"   Enter password hint (optional): ").strip()
                
                # Enable 2FA using simpler method
                try:
                    await client.edit_2fa(new_password=new_password, hint=hint)
                    print(Fore.GREEN + f"[{session_name}] ✅ 2FA ENABLED successfully!")
                    print(Fore.YELLOW + f"   Password: {new_password}")
                    print(Fore.YELLOW + f"   Hint: {hint if hint else 'None'}")
                    return True
                except Exception as e:
                    print(Fore.RED + f"[{session_name}] ❌ Failed to enable 2FA: {str(e)[:100]}")
                    return False
                    
        except SessionPasswordNeededError:
            print(Fore.RED + f"[{session_name}] ❌ Session requires 2FA password to login")
            print(Fore.YELLOW + f"   Please login with 2FA first")
            return False
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Error checking 2FA: {str(e)[:100]}")
            return False
            
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Connection error: {str(e)[:100]}")
        return False
    finally:
        if client:
            try:
                await client.disconnect()
            except:
                pass

async def option10_change_2fa():
    """POWERFUL 2FA PASSWORD MANAGER - Works for ALL accounts"""
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "🔐 POWERFUL 2FA PASSWORD MANAGER")
    print(Fore.CYAN + "═" * 60)
    
    print(Fore.YELLOW + "\n⚡ FEATURES:")
    print(Fore.YELLOW + "   ✅ Change 2FA password for accounts WITH existing 2FA")
    print(Fore.YELLOW + "   ✅ Enable 2FA for accounts WITHOUT 2FA")
    print(Fore.YELLOW + "   ✅ Works with ALL Telegram accounts")
    print(Fore.YELLOW + "   ✅ Secure password verification")
    print()
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found!")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    print(Fore.CYAN + "📝 Select sessions to manage 2FA")
    selection = input(Fore.CYAN + "   Enter session numbers (comma-separated) or 'all': ").strip().lower()
    
    if selection == 'all':
        selected_sessions = available_sessions
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
        except:
            print(Fore.RED + "❌ Invalid selection")
            return
    
    if not selected_sessions:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    print(Fore.YELLOW + f"\n⚠️  Will process {len(selected_sessions)} sessions")
    
    proceed = input(Fore.YELLOW + f"\nProceed? (y/n): ").strip().lower()
    if proceed != 'y':
        print(Fore.YELLOW + "⏹️ Cancelled")
        return
    
    print(Fore.GREEN + f"\n⚡ PROCESSING {len(selected_sessions)} SESSIONS...\n")
    
    enabled_count = 0
    changed_count = 0
    skipped_count = 0
    failed_count = 0
    
    for idx, (session_name, session_file) in enumerate(selected_sessions, 1):
        print(Fore.MAGENTA + f"\n📱 Processing session {idx}/{len(selected_sessions)}: {session_name}")
        
        success = await change_2fa_password_powerful(session_file, session_name)
        
        if success:
            # Check if this was enable or change
            # Simple check based on message
            if "ENABLED" in str(success):
                enabled_count += 1
            else:
                changed_count += 1
        else:
            failed_count += 1
        
        # Delay between sessions
        if idx < len(selected_sessions):
            delay = random.uniform(10, 20)
            print(Fore.BLUE + f"⏳ Waiting {delay:.1f}s before next session...")
            await asyncio.sleep(delay)
    
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + f"📊 POWERFUL 2FA MANAGEMENT RESULTS:")
    print(Fore.GREEN + f"   ✅ 2FA Enabled: {enabled_count}")
    print(Fore.CYAN + f"   🔄 2FA Changed: {changed_count}")
    print(Fore.RED + f"   ❌ Failed: {failed_count}")
    print(Fore.YELLOW + f"   📊 Total Processed: {enabled_count + changed_count + failed_count}")
    print(Fore.CYAN + "═" * 60)

async def handle_flood_wait(error, session_name, action):
    """Handle flood wait errors"""
    if hasattr(error, 'seconds'):
        wait_time = error.seconds
        print(Fore.RED + f"[{session_name}] ⏳ Flood wait for {action}: {wait_time} seconds")
        
        total_wait = wait_time + 5
        for remaining in range(total_wait, 0, -1):
            print(Fore.YELLOW + f"[{session_name}] ⏰ Waiting: {remaining}s remaining", end='\r')
            await asyncio.sleep(1)
        print(Fore.GREEN + f"[{session_name}] ✅ Flood wait complete, resuming...")
        return True
    return False

async def join_groups_for_session(session_path, session_name, groups_to_join, delay_between_groups_min, delay_between_groups_max):
    """Join groups for a single session"""
    client = None
    try:
        api_creds = get_rotated_api()
        client = TelegramClient(session_path, api_creds['api_id'], api_creds['api_hash'])
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return 0, 0
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] 👤 Account: @{me.username or me.first_name}")
        
        joined = 0
        total = len(groups_to_join)
        
        for i, group_username in enumerate(groups_to_join, 1):
            try:
                if not group_username.startswith('@'):
                    group_username = '@' + group_username
                
                print(Fore.CYAN + f"[{session_name}] 🔗 Joining {group_username} ({i}/{total})...")
                
                entity = await client.get_entity(group_username)
                await client(functions.channels.JoinChannelRequest(entity))
                
                print(Fore.GREEN + f"[{session_name}] ✅ Joined {group_username}")
                joined += 1
                
                # DELAY BETWEEN GROUPS
                if i < total:
                    delay = random.uniform(delay_between_groups_min, delay_between_groups_max)
                    print(Fore.BLUE + f"[{session_name}] ⏳ Waiting {delay:.1f}s before next group...")
                    await asyncio.sleep(delay)
                
            except FloodWaitError as e:
                if await handle_flood_wait(e, session_name, f"joining {group_username}"):
                    continue
                else:
                    print(Fore.RED + f"[{session_name}] ❌ Flood wait error for {group_username}")
            except Exception as e:
                error_msg = str(e)
                if "USER_ALREADY_PARTICIPANT" in error_msg:
                    print(Fore.YELLOW + f"[{session_name}] ⚠️ Already in {group_username}")
                elif "USER_NOT_MUTUAL_CONTACT" in error_msg:
                    print(Fore.RED + f"[{session_name}] ❌ Can't join private group {group_username}")
                elif "CHANNEL_PRIVATE" in error_msg:
                    print(Fore.RED + f"[{session_name}] ❌ Private channel {group_username}")
                elif "INVITE_REQUEST_SENT" in error_msg:
                    print(Fore.YELLOW + f"[{session_name}] 📨 Join request sent for {group_username}")
                    joined += 1
                elif "FLOOD_WAIT" in error_msg.upper():
                    print(Fore.RED + f"[{session_name}] ⏳ Flood wait, waiting {FLOOD_WAIT_DELAY}s...")
                    await asyncio.sleep(FLOOD_WAIT_DELAY)
                    continue
                else:
                    print(Fore.RED + f"[{session_name}] ❌ Failed to join {group_username}: {error_msg[:50]}")
        
        return joined, total
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error: {str(e)[:50]}")
        return 0, 0
    finally:
        if client:
            await client.disconnect()

async def option11_join_groups():
    """Join groups from groups.txt file with automatic cycles"""
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "👥 JOIN GROUPS FROM FILE (AUTOMATIC CYCLES)")
    print(Fore.CYAN + "═" * 60)
    
    # Ask for delays
    print(Fore.YELLOW + "\n⏱️ SET DELAY CONFIGURATION:")
    
    try:
        delay_between_groups_min = float(input(Fore.CYAN + "   Delay between groups (min seconds): ").strip() or "15")
        delay_between_groups_max = float(input(Fore.CYAN + "   Delay between groups (max seconds): ").strip() or "30")
        
        delay_between_sessions_min = float(input(Fore.CYAN + "   Delay between sessions (min seconds): ").strip() or "10")
        delay_between_sessions_max = float(input(Fore.CYAN + "   Delay between sessions (max seconds): ").strip() or "20")
        
        delay_between_cycles_min = float(input(Fore.CYAN + "   Delay between cycles (min minutes): ").strip() or "5")
        delay_between_cycles_max = float(input(Fore.CYAN + "   Delay between cycles (max minutes): ").strip() or "10")
        
        # Convert minutes to seconds
        delay_between_cycles_min *= 60
        delay_between_cycles_max *= 60
        
    except ValueError:
        print(Fore.RED + "❌ Invalid delay values, using defaults")
        delay_between_groups_min = 15
        delay_between_groups_max = 30
        delay_between_sessions_min = 10
        delay_between_sessions_max = 20
        delay_between_cycles_min = 300  # 5 minutes
        delay_between_cycles_max = 600  # 10 minutes
    
    # Ask for total cycles
    try:
        total_cycles = int(input(Fore.YELLOW + "🔄 Enter total number of cycles to run (0 for unlimited): ").strip() or "0")
    except:
        total_cycles = 0
    
    groups_file = "groups.txt"
    if not os.path.exists(groups_file):
        print(Fore.RED + f"❌ {groups_file} not found!")
        print(Fore.YELLOW + "Create 'groups.txt' with group usernames (one per line)")
        return
    
    with open(groups_file, 'r') as f:
        all_groups = [line.strip() for line in f if line.strip()]
    
    if not all_groups:
        print(Fore.RED + "❌ No group usernames in file!")
        return
    
    print(Fore.GREEN + f"✅ Found {len(all_groups)} total groups in {groups_file}")
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found!")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    print(Fore.CYAN + "📝 Select sessions to join groups")
    selection = input(Fore.CYAN + "   Enter session numbers (comma-separated) or 'all': ").strip().lower()
    
    if selection == 'all':
        selected_sessions = available_sessions
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
        except:
            print(Fore.RED + "❌ Invalid selection")
            return
    
    if not selected_sessions:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    # Ask for groups per session per cycle
    try:
        groups_per_session_per_cycle = int(input(Fore.YELLOW + "🎯 Enter number of groups per session per cycle: ").strip() or "5")
        if groups_per_session_per_cycle < 1:
            groups_per_session_per_cycle = 5
    except:
        groups_per_session_per_cycle = 5
    
    # Ask for mode
    print(Fore.YELLOW + "\n📊 DISTRIBUTION MODE:")
    print(Fore.WHITE + "   1. 🎯 Fixed groups per session (same groups each cycle)")
    print(Fore.WHITE + "   2. 🔄 Different groups each cycle (recommended)")
    
    mode_choice = input(Fore.CYAN + "   Select mode (1-2): ").strip()
    
    if mode_choice == "1":
        # Fixed groups mode
        session_groups = {}
        total_needed = groups_per_session_per_cycle * len(selected_sessions)
        
        if total_needed > len(all_groups):
            print(Fore.RED + f"❌ Not enough groups! Need {total_needed}, have {len(all_groups)}")
            return
        
        # Distribute groups evenly
        for idx, (session_name, _) in enumerate(selected_sessions):
            start_idx = idx * groups_per_session_per_cycle
            end_idx = start_idx + groups_per_session_per_cycle
            session_groups[session_name] = all_groups[start_idx:end_idx]
        
        print(Fore.GREEN + f"\n📊 FIXED DISTRIBUTION:")
        for session_name, groups in session_groups.items():
            print(Fore.CYAN + f"   {session_name}: {len(groups)} groups")
        
    else:
        # Different groups each cycle mode
        print(Fore.GREEN + f"\n📊 DIFFERENT GROUPS EACH CYCLE:")
        print(Fore.YELLOW + f"   Each session will get {groups_per_session_per_cycle} NEW groups each cycle")
        print(Fore.YELLOW + f"   Total available groups: {len(all_groups)}")
        
        if groups_per_session_per_cycle * len(selected_sessions) > len(all_groups):
            print(Fore.RED + f"❌ Not enough groups for one cycle! Need {groups_per_session_per_cycle * len(selected_sessions)}, have {len(all_groups)}")
            return
    
    confirm = input(Fore.YELLOW + f"\n⚠️  Start joining groups? (y/n): ").strip().lower()
    if confirm != 'y':
        print(Fore.YELLOW + "⏹️ Cancelled")
        return
    
    print(Fore.GREEN + f"\n⚡ STARTING AUTOMATIC GROUP JOINING...\n")
    print(Fore.YELLOW + f"⏱️  Delays: {delay_between_groups_min}-{delay_between_groups_max}s between groups, {delay_between_sessions_min}-{delay_between_sessions_max}s between sessions")
    print(Fore.YELLOW + f"🔄 Cycles: {'Unlimited' if total_cycles == 0 else total_cycles}")
    
    cycle_count = 0
    total_joined_all = 0
    total_attempted_all = 0
    
    # Track used groups for mode 2
    used_groups = set()
    
    try:
        while True:
            if total_cycles > 0 and cycle_count >= total_cycles:
                print(Fore.GREEN + f"\n✅ REACHED MAXIMUM CYCLES: {total_cycles}")
                break
            
            cycle_count += 1
            print(Fore.MAGENTA + "\n" + "═" * 60)
            print(Fore.MAGENTA + f"🔄 STARTING CYCLE {cycle_count}")
            print(Fore.MAGENTA + "═" * 60)
            
            # Prepare groups for this cycle
            if mode_choice == "1":
                # Fixed groups mode - use same groups each cycle
                cycle_session_groups = session_groups.copy()
            else:
                # Different groups each cycle mode
                cycle_session_groups = {}
                available_for_cycle = [g for g in all_groups if g not in used_groups]
                
                if len(available_for_cycle) < groups_per_session_per_cycle * len(selected_sessions):
                    print(Fore.YELLOW + f"⚠️  Not enough unused groups for cycle {cycle_count}")
                    print(Fore.YELLOW + f"   Available: {len(available_for_cycle)}, Needed: {groups_per_session_per_cycle * len(selected_sessions)}")
                    break
                
                # Distribute available groups to sessions
                for idx, (session_name, _) in enumerate(selected_sessions):
                    start_idx = idx * groups_per_session_per_cycle
                    end_idx = start_idx + groups_per_session_per_cycle
                    cycle_session_groups[session_name] = available_for_cycle[start_idx:end_idx]
                    
                    # Mark these groups as used
                    for group in cycle_session_groups[session_name]:
                        used_groups.add(group)
            
            cycle_joined = 0
            cycle_attempted = 0
            
            for idx, (session_name, session_file) in enumerate(selected_sessions, 1):
                print(Fore.MAGENTA + f"\n📱 Processing session {idx}/{len(selected_sessions)}: {session_name}")
                
                # Get this session's groups for this cycle
                groups_for_session = cycle_session_groups.get(session_name, [])
                if not groups_for_session:
                    print(Fore.YELLOW + f"[{session_name}] ⚠️ No groups assigned for this cycle")
                    continue
                
                print(Fore.CYAN + f"[{session_name}] 📊 Joining {len(groups_for_session)} groups")
                
                joined, attempted = await join_groups_for_session(
                    session_file, 
                    session_name, 
                    groups_for_session,
                    delay_between_groups_min,
                    delay_between_groups_max
                )
                cycle_joined += joined
                cycle_attempted += attempted
                total_joined_all += joined
                total_attempted_all += attempted
                
                # DELAY BETWEEN SESSIONS
                if idx < len(selected_sessions):
                    delay = random.uniform(delay_between_sessions_min, delay_between_sessions_max)
                    print(Fore.BLUE + f"\n⏳ Waiting {delay:.1f}s before starting next session...")
                    await asyncio.sleep(delay)
            
            print(Fore.GREEN + f"\n✅ CYCLE {cycle_count} COMPLETED!")
            print(Fore.YELLOW + f"📊 Cycle Results: {cycle_joined}/{cycle_attempted} group joins successful")
            print(Fore.YELLOW + f"📊 Total Results: {total_joined_all}/{total_attempted_all} group joins successful")
            
            # Check if we should continue
            if total_cycles > 0 and cycle_count >= total_cycles:
                print(Fore.GREEN + f"\n✅ REACHED MAXIMUM CYCLES: {total_cycles}")
                break
            
            if mode_choice == "2":
                # Check if we have enough groups for next cycle
                available_for_next = len(all_groups) - len(used_groups)
                needed_for_next = groups_per_session_per_cycle * len(selected_sessions)
                
                if available_for_next < needed_for_next:
                    print(Fore.YELLOW + f"\n⚠️  NOT ENOUGH GROUPS FOR NEXT CYCLE!")
                    print(Fore.YELLOW + f"   Available: {available_for_next}, Needed: {needed_for_next}")
                    break
            
            # DELAY BETWEEN CYCLES
            delay = random.uniform(delay_between_cycles_min, delay_between_cycles_max)
            minutes = delay / 60
            print(Fore.BLUE + f"\n⏳ Waiting {minutes:.1f} minutes before next cycle...")
            await asyncio.sleep(delay)
    
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"\n\n⏹️ AUTOMATIC JOINING STOPPED BY USER")
    
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.YELLOW + f"📊 FINAL RESULTS:")
    print(Fore.YELLOW + f"   Total cycles completed: {cycle_count}")
    print(Fore.YELLOW + f"   Total joins successful: {total_joined_all}/{total_attempted_all}")
    print(Fore.YELLOW + f"   Success rate: {(total_joined_all/total_attempted_all*100 if total_attempted_all > 0 else 0):.1f}%")
    print(Fore.CYAN + "═" * 60)

async def terminate_other_sessions(session_path, session_name):
    """Terminate all other active sessions except current one"""
    client = None
    try:
        api_creds = get_rotated_api()
        client = TelegramClient(session_path, api_creds['api_id'], api_creds['api_hash'])
        
        await client.connect()
        
        if not await client.is_user_authorized():
            print(Fore.RED + f"[{session_name}] ❌ Session not authorized")
            return False
        
        me = await client.get_me()
        print(Fore.GREEN + f"[{session_name}] 👤 Account: @{me.username or me.first_name}")
        
        # Get all active sessions
        result = await client(functions.account.GetAuthorizationsRequest())
        
        # Count total sessions
        total_sessions = len(result.authorizations)
        print(Fore.YELLOW + f"[{session_name}] 📱 Found {total_sessions} active sessions")
        
        if total_sessions <= 1:
            print(Fore.YELLOW + f"[{session_name}] ⚠️ Only current session active, nothing to terminate")
            return True
        
        # Terminate all other sessions
        terminated = 0
        for auth in result.authorizations:
            if auth.current:
                continue
            
            try:
                await client(functions.account.ResetAuthorizationRequest(hash=auth.hash))
                terminated += 1
                print(Fore.GREEN + f"[{session_name}] ✅ Terminated session from {auth.device_model}")
                
                await asyncio.sleep(1)
                
            except Exception as e:
                print(Fore.RED + f"[{session_name}] ❌ Failed to terminate session: {str(e)[:50]}")
        
        print(Fore.GREEN + f"[{session_name}] ✅ Terminated {terminated}/{total_sessions-1} other sessions")
        return True
        
    except Exception as e:
        print(Fore.RED + f"[{session_name}] ❌ Error: {str(e)[:50]}")
        return False
    finally:
        if client:
            await client.disconnect()

async def option12_terminate_sessions():
    """Terminate other active sessions"""
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "🚫 TERMINATE OTHER SESSIONS")
    print(Fore.CYAN + "═" * 60)
    
    print(Fore.YELLOW + "\n⚠️  This will log out all other active sessions (web, mobile, etc.)")
    print(Fore.YELLOW + "   Only the current session files will remain active")
    
    session_files = glob.glob(os.path.join(ACCOUNTS_FOLDER, '*.session'))
    
    if not session_files:
        print(Fore.RED + f"❌ No .session files found!")
        return
    
    available_sessions = []
    for session_file in session_files:
        session_name = os.path.basename(session_file).replace('.session', '')
        available_sessions.append((session_name, session_file))
    
    print(Fore.GREEN + f"✅ Found {len(available_sessions)} sessions in accounts folder")
    
    for i, (session_name, session_file) in enumerate(available_sessions, 1):
        print(Fore.CYAN + f"   {i:2d}. {session_name}")
    
    print(Fore.YELLOW + "\n" + "─" * 40)
    print(Fore.CYAN + "📝 Select sessions to terminate other sessions")
    selection = input(Fore.CYAN + "   Enter session numbers (comma-separated) or 'all': ").strip().lower()
    
    if selection == 'all':
        selected_sessions = available_sessions
    else:
        try:
            indices = [int(x.strip()) - 1 for x in selection.split(',')]
            selected_sessions = [available_sessions[i] for i in indices if 0 <= i < len(available_sessions)]
        except:
            print(Fore.RED + "❌ Invalid selection")
            return
    
    if not selected_sessions:
        print(Fore.RED + "❌ No sessions selected!")
        return
    
    confirm = input(Fore.RED + f"\n⚠️ ⚠️  TERMINATE ALL OTHER SESSIONS FOR {len(selected_sessions)} ACCOUNTS? (type 'YES' to confirm): ").strip()
    if confirm != 'YES':
        print(Fore.YELLOW + "⏹️ Cancelled")
        return
    
    print(Fore.GREEN + f"\n⚡ TERMINATING OTHER SESSIONS FOR {len(selected_sessions)} ACCOUNTS...\n")
    
    tasks = []
    for session_name, session_file in selected_sessions:
        tasks.append(terminate_other_sessions(session_file, session_name))
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    success_count = sum(1 for r in results if r is True)
    
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.YELLOW + f"📊 RESULTS: {success_count}/{len(selected_sessions)} accounts processed")
    print(Fore.CYAN + "═" * 60)

# ==================== END NEW OPTIONS FROM SEX.PY ====================

def show_main_menu():
    display_banner()
    display_stats()
    
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "⚡ MAIN MENU - SELECT OPTION:")
    print(Fore.CYAN + "═" * 60)
    print(Fore.WHITE + "   1. 📨 Direct Message Sender")
    print(Fore.WHITE + "   2. 📢 Group Spammer")
    print(Fore.WHITE + "   3. 🤖 Auto-Reply + Forwarder Bot")
    print(Fore.WHITE + "   4. 🔧 Session Creator (API Rotation)")
    print(Fore.WHITE + "   5. 👤 Name Changer")
    print(Fore.WHITE + "   6. 📝 Bio Changer")
    print(Fore.WHITE + "   7. 📩 DM Forwarder (Copy-Paste)")
    print(Fore.WHITE + "   8. 🔄 Channel Forwarder")
    print(Fore.WHITE + "   9. ✅ Check Session Validity")
    print(Fore.WHITE + "   10. 🔐 POWERFUL 2FA Password Manager")
    print(Fore.WHITE + "   11. 👥 Join Groups (from groups.txt - AUTOMATIC CYCLES)")
    print(Fore.WHITE + "   12. 🚫 Terminate Other Sessions")
    print(Fore.WHITE + "   13. 🚪 Exit")
    print(Fore.CYAN + "═" * 60)
    
    try:
        choice = input(Fore.GREEN + "\n   Select option (1-13): ").strip()
        return choice
    except KeyboardInterrupt:
        return "13"

async def main():
    if not check_internet_connection():
        print(Fore.RED + "❌ No internet connection detected")
        await wait_for_internet()
    
    os.makedirs(ACCOUNTS_FOLDER, exist_ok=True)
    os.makedirs(SESSIONS_FOLDER, exist_ok=True)
    
    while True:
        try:
            choice = show_main_menu()
            
            if choice == "1":
                await option1_direct_messager()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "2":
                await option2_group_spammer()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "3":
                await option3_auto_reply_forwarder()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "4":
                await option4_session_creator()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "5":
                await option5_name_changer()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "6":
                await option6_bio_changer()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "7":
                await option7_dm_forwarder()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "8":
                await option8_channel_forwarder()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "9":
                await option9_check_sessions()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "10":
                await option10_change_2fa()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "11":
                await option11_join_groups()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "12":
                await option12_terminate_sessions()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "13":
                print(Fore.YELLOW + "\n👋 Goodbye! See you next time!")
                break
            
            else:
                print(Fore.RED + "❌ Invalid choice! Please select 1-13")
                time.sleep(1)
        
        except KeyboardInterrupt:
            print(Fore.YELLOW + "\n\n⏹️ Operation cancelled by user")
            input(Fore.YELLOW + "   Press Enter to continue...")
        
        except Exception as e:
            print(Fore.RED + f"\n💥 Unexpected error: {str(e)}")
            input(Fore.YELLOW + "   Press Enter to continue...")

if __name__ == "__main__":
    try:
        import telethon
    except ImportError:
        print(Fore.RED + "❌ Telethon not installed!")
        print(Fore.YELLOW + "Installing requirements...")
        os.system("pip install telethon colorama")
        print(Fore.GREEN + "✅ Requirements installed!")
    
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Script stopped by user")
    except Exception as e:
        print(Fore.RED + f"\n💥 Fatal error: {str(e)}")
        input(Fore.YELLOW + "Press Enter to exit...")