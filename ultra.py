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

async def spam_groups(client, session_num):
    """Send message to all groups"""
    message = "📢 DM @ogdigital to buy cheap spam software! 📢\nBest prices for Telegram tools!"
    
    success = 0
    failed = 0
    
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client.send_message(dialog.entity, message)
                    print(Fore.GREEN + f"✓ S{session_num}: Sent to {dialog.name[:30]}")
                    success += 1
                except Exception as e:
                    try:
                        await client(LeaveChannelRequest(dialog.entity))
                        print(Fore.YELLOW + f"← S{session_num}: Left {dialog.name[:30]}")
                    except:
                        pass
                    failed += 1
        
        print(Fore.CYAN + f"📊 S{session_num}: {success} sent, {failed} failed")
        
    except Exception as e:
        print(Fore.RED + f"✗ S{session_num}: Error - {str(e)[:50]}")

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
        
        await spam_groups(client, session_num)
        
        await client.disconnect()
        print(Fore.BLUE + f"✓ Session {session_num}: Completed\n")
        
    except Exception as e:
        print(Fore.RED + f"✗ Session {session_num}: Failed - {str(e)[:50]}")

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
    print(Fore.YELLOW + "🚀 Starting spam...\n")
    
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
    
    await asyncio.gather(*tasks, return_exceptions=True)
    
    print(Fore.GREEN + "\n" + "="*50)
    print(Fore.GREEN + f"✅ ALL {len(sessions)} SESSIONS COMPLETED!")
    print(Fore.YELLOW + "📞 Contact @ogdigital for more tools!")
    print(Fore.GREEN + "="*50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Stopped by user")
    except Exception as e:
        print(Fore.RED + f"\n💥 Error: {str(e)}")