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
from telethon import TelegramClient, events, functions
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
    ║               ULTIMATE TELEGRAM TOOLKIT v4.0                 ║
    ║              THE MOST POWERFUL SCRIPT IN THE WORLD           ║
    ║                                                              ║
    ╚══════════════════════════════════════════════════════════════╝
    """)
    print(Fore.CYAN + "📱 " + Fore.WHITE + "Created by: " + Fore.YELLOW + "@ogdigital @DARKCONTENTWORLD")
    print(Fore.GREEN + "🔥 " + Fore.WHITE + "Features: " + Fore.YELLOW + "5-IN-1 Ultimate Toolkit")
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
        
        # Get last 5 messages from channel
        messages = []
        try:
            async for message in client.iter_messages(channel, limit=5):
                messages.append(message)
        except Exception as e:
            print(Fore.RED + f"[{session_name}] ❌ Can't fetch messages: {str(e)[:50]}")
            return None
        
        if not messages:
            print(Fore.YELLOW + f"[{session_name}] ⚠️ No messages found in channel")
            return None
        
        # Select random message from last 5
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
        
        print(Fore.YELLOW + f"[{session_name}] 🔄 Forwarding from channel: {channel_username}")
        
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

async def option7_channel_forwarder():
    display_banner()
    print(Fore.CYAN + "\n" + "═" * 60)
    print(Fore.GREEN + "🔄 CHANNEL FORWARDER")
    print(Fore.CYAN + "═" * 60)
    
    channel_username = input(Fore.YELLOW + "\n📢 Channel username (with or without @): ").strip()
    if not channel_username:
        print(Fore.RED + "❌ Channel username is required!")
        return
    
    print(Fore.YELLOW + f"\n📝 Will forward random message from last 5 messages of: {channel_username}")
    
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
    print(Fore.WHITE + "   7. 🔄 Channel Forwarder")  # Changed from 🚪 Exit to new option
    print(Fore.WHITE + "   8. 🚪 Exit")  # Added new exit option
    print(Fore.CYAN + "═" * 60)
    
    try:
        choice = input(Fore.GREEN + "\n   Select option (1-8): ").strip()
        return choice
    except KeyboardInterrupt:
        return "8"

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
            
            elif choice == "7":  # New option
                await option7_channel_forwarder()
                input(Fore.YELLOW + "\n   Press Enter to continue...")
            
            elif choice == "8":  # Updated exit option
                print(Fore.YELLOW + "\n👋 Goodbye! See you next time!")
                break
            
            else:
                print(Fore.RED + "❌ Invalid choice! Please select 1-8")
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