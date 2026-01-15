import asyncio
import os
import json
import sys
from telethon import TelegramClient, errors
from telethon.sessions import StringSession
from telethon.tl.functions.channels import LeaveChannelRequest
from colorama import init, Fore

init(autoreset=True)

def display_banner():
    print(Fore.RED + """
    ╔══════════════════════════════════════════╗
    ║        OG SPAM SOFTWARE - ULTRA MEGA     ║
    ║        PARALLEL MODE - 100+ ACCOUNTS     ║
    ║        Contact: @ogdigital               ║
    ║        ZERO DELAYS - MAXIMUM SPEED       ║
    ╚══════════════════════════════════════════╝
    """)
    print(Fore.YELLOW + "⚡ DM @ogdigital to buy cheap spam software! ⚡\n")

# Create a global list to store all group links
all_group_links = []
links_file_lock = asyncio.Lock()

async def save_group_links_to_file():
    """Save all collected group links to a text file"""
    async with links_file_lock:
        # Remove duplicates while preserving order
        unique_links = []
        for link in all_group_links:
            if link not in unique_links:
                unique_links.append(link)
        
        # Create folder if it doesn't exist
        folder_name = "Collected_Groups"
        if not os.path.exists(folder_name):
            os.makedirs(folder_name)
        
        # Save to file
        filename = f"{folder_name}/all_group_links.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"Total Groups Collected: {len(unique_links)}\n")
            f.write("="*50 + "\n\n")
            for i, link in enumerate(unique_links, 1):
                f.write(f"{i}. {link}\n")
        
        print(Fore.GREEN + f"\n✅ Saved {len(unique_links)} unique group links to: {filename}")
        return len(unique_links)

async def fetch_groups(client, session_num):
    """Fetch all groups (not channels) and collect their links"""
    session_groups = 0
    
    try:
        async for dialog in client.iter_dialogs():
            # Check if it's a group (not a channel)
            if dialog.is_group:
                try:
                    # Get the chat entity
                    chat = dialog.entity
                    
                    # Get username or ID for link
                    if hasattr(chat, 'username') and chat.username:
                        link = f"https://t.me/{chat.username}"
                    else:
                        # For private groups, use the ID
                        link = f"Private Group ID: {chat.id}"
                    
                    # Get group name
                    group_name = dialog.name or "Unnamed Group"
                    
                    # Add to global list
                    all_group_links.append(link)
                    
                    print(Fore.GREEN + f"✓ S{session_num}: Found group: {group_name[:30]} - {link}")
                    session_groups += 1
                    
                except Exception as e:
                    print(Fore.RED + f"✗ S{session_num}: Error fetching group {dialog.name[:20]}: {str(e)[:50]}")
        
        print(Fore.CYAN + f"📊 S{session_num}: Found {session_groups} groups")
        return session_groups
        
    except Exception as e:
        print(Fore.RED + f"✗ S{session_num}: Error - {str(e)[:50]}")
        return 0

async def process_session(api_id, api_hash, string_session, session_num):
    """Process one session"""
    try:
        client = TelegramClient(
            StringSession(string_session),
            api_id,
            api_hash,
            connection_retries=1
        )
        
        await client.start()
        me = await client.get_me()
        print(Fore.GREEN + f"✓ Session {session_num}: Connected as @{me.username or me.first_name}")
        
        # Fetch groups instead of spamming
        groups_found = await fetch_groups(client, session_num)
        
        await client.disconnect()
        print(Fore.BLUE + f"✓ Session {session_num}: Completed - Found {groups_found} groups\n")
        
        return groups_found
        
    except Exception as e:
        print(Fore.RED + f"✗ Session {session_num}: Failed - {str(e)[:50]}")
        return 0

async def main():
    display_banner()
    
    print(Fore.CYAN + "📝 Enter sessions (3 lines each):")
    print(Fore.YELLOW + "Format:")
    print("API_ID")
    print("API_HASH")
    print("STRING_SESSION")
    print("(repeat for next session)")
    print("\nEnter sessions below (Ctrl+C to finish):")
    
    sessions = []
    session_count = 0
    
    try:
        while True:
            session_count += 1
            print(Fore.CYAN + f"\n┌─── Session {session_count} ───")
            
            try:
                api_id = input("API ID: ").strip()
                if not api_id:
                    session_count -= 1
                    break
                    
                api_hash = input("API HASH: ").strip()
                string_session = input("STRING SESSION: ").strip()
                
                if api_id and api_hash and string_session:
                    sessions.append({
                        'api_id': int(api_id),
                        'api_hash': api_hash,
                        'string_session': string_session,
                        'num': session_count
                    })
                    print(Fore.GREEN + f"✓ Added session {session_count}")
                else:
                    print(Fore.RED + "Missing data, skipping...")
                    session_count -= 1
                    
            except ValueError:
                print(Fore.RED + "Invalid API ID")
                session_count -= 1
            except KeyboardInterrupt:
                break
                
    except KeyboardInterrupt:
        pass
    
    if not sessions:
        print(Fore.RED + "\n❌ No sessions to process!")
        return
    
    print(Fore.GREEN + f"\n✅ Loaded {len(sessions)} sessions")
    print(Fore.YELLOW + "🚀 Starting group collection...\n")
    
    # Clear global list
    global all_group_links
    all_group_links = []
    
    # Run ALL sessions in parallel
    tasks = []
    for session in sessions:
        task = asyncio.create_task(
            process_session(
                session['api_id'],
                session['api_hash'],
                session['string_session'],
                session['num']
            )
        )
        tasks.append(task)
    
    # Wait for all sessions to complete
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Save all collected group links to file
    total_groups = await save_group_links_to_file()
    
    print(Fore.GREEN + "\n" + "="*50)
    print(Fore.GREEN + f"✅ ALL {len(sessions)} SESSIONS COMPLETED!")
    print(Fore.CYAN + f"📊 Total unique groups collected: {total_groups}")
    print(Fore.YELLOW + "📁 Groups saved in 'Collected_Groups/all_group_links.txt'")
    print(Fore.YELLOW + "📞 Contact @ogdigital for more tools!")
    print(Fore.GREEN + "="*50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Stopped by user")
    except Exception as e:
        print(Fore.RED + f"\n💥 Error: {str(e)}")