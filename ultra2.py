import asyncio
import os
import json
import glob
import sys
from telethon import TelegramClient, errors
from telethon.tl.functions.channels import LeaveChannelRequest
from colorama import init, Fore

init(autoreset=True)

def display_banner():
    print(Fore.RED + """
    ╔══════════════════════════════════════════╗
    ║        ULTRA SPAMMER - SESSION MODE      ║
    ║        Uses .session + .json files       ║
    ║        Contact: @ogdigital               ║
    ║        ZERO DELAYS - MAXIMUM SPEED       ║
    ╚══════════════════════════════════════════╝
    """)
    print(Fore.YELLOW + "⚡ Parallel Processing - All Accounts at Once ⚡\n")

def create_minimal_json(session_name):
    """Create a minimal .json file if it doesn't exist"""
    json_path = f'accounts/{session_name}.json'
    
    # Don't overwrite if exists
    if os.path.exists(json_path):
        return True
    
    print(Fore.YELLOW + f"⚠ No API credentials for {session_name}")
    
    try:
        # Try to get from user
        api_id = input(f"Enter API ID for {session_name}: ").strip()
        api_hash = input(f"Enter API Hash for {session_name}: ").strip()
        
        if api_id and api_hash:
            credentials = {
                "api_id": int(api_id),
                "api_hash": api_hash
            }
            
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(credentials, f, indent=2)
            
            print(Fore.GREEN + f"✓ Created {session_name}.json")
            return True
        else:
            print(Fore.RED + f"✗ Skipping {session_name} - API credentials required")
            return False
            
    except KeyboardInterrupt:
        raise
    except Exception as e:
        print(Fore.RED + f"✗ Error creating JSON: {str(e)[:50]}")
        return False

async def load_accounts():
    """Load all .session + .json files from accounts/ folder"""
    accounts = []
    session_files = glob.glob('accounts/*.session')
    
    for session_file in session_files:
        base_name = os.path.basename(session_file).replace('.session', '')
        
        # Check if JSON exists
        json_file = f'accounts/{base_name}.json'
        
        if not os.path.exists(json_file):
            # Try to create minimal JSON
            if not create_minimal_json(base_name):
                continue
        
        try:
            # Load credentials from JSON
            with open(json_file, 'r', encoding='utf-8') as f:
                credentials = json.load(f)
            
            accounts.append({
                'session_path': session_file,
                'api_id': credentials.get('api_id') or credentials.get('app_id'),
                'api_hash': credentials.get('api_hash') or credentials.get('app_hash'),
                'name': base_name
            })
            print(Fore.GREEN + f"✓ Loaded: {base_name}")
            
        except Exception as e:
            print(Fore.RED + f"✗ Error loading {base_name}: {str(e)[:50]}")
    
    return accounts

async def spam_groups(client, account_name, message):
    """Send message to all groups for one account"""
    success = 0
    failed = 0
    
    try:
        async for dialog in client.iter_dialogs():
            if dialog.is_group or dialog.is_channel:
                try:
                    await client.send_message(dialog.entity, message)
                    print(Fore.GREEN + f"✓ {account_name}: Sent to {dialog.name[:30]}")
                    success += 1
                except Exception as e:
                    try:
                        await client(LeaveChannelRequest(dialog.entity))
                        print(Fore.YELLOW + f"← {account_name}: Left {dialog.name[:30]}")
                    except:
                        pass
                    failed += 1
        
        print(Fore.CYAN + f"📊 {account_name}: {success} sent, {failed} failed")
        
    except Exception as e:
        print(Fore.RED + f"✗ {account_name}: Error - {str(e)[:50]}")
    
    return success, failed

async def process_account(account, session_num):
    """Process one account"""
    try:
        client = TelegramClient(
            account['session_path'],
            account['api_id'],
            account['api_hash'],
            connection_retries=1
        )
        
        await client.start()
        me = await client.get_me()
        print(Fore.GREEN + f"✓ {account['name']}: Connected as @{me.username or me.first_name}")
        
        message = "📢 DM @ogdigital to buy cheap spam software! 📢\nBest prices for Telegram tools!"
        
        success, failed = await spam_groups(client, account['name'], message)
        
        await client.disconnect()
        print(Fore.BLUE + f"✓ {account['name']}: Completed ({success} sent, {failed} failed)\n")
        
    except Exception as e:
        print(Fore.RED + f"✗ {account['name']}: Failed - {str(e)[:50]}")

async def main():
    display_banner()
    
    # Create accounts folder if not exists
    os.makedirs('accounts', exist_ok=True)
    
    print(Fore.CYAN + "📂 Loading accounts from 'accounts/' folder...\n")
    
    accounts = await load_accounts()
    
    if not accounts:
        print(Fore.RED + "\n❌ No valid accounts found!")
        print(Fore.YELLOW + "\nRequired files for each account:")
        print(Fore.WHITE + "accounts/")
        print(Fore.WHITE + "├── user1.session")
        print(Fore.WHITE + "└── user1.json")
        print(Fore.YELLOW + "\n.json format (minimal):")
        print(Fore.WHITE + '''{
  "api_id": 1234567,
  "api_hash": "your_api_hash_here"
}''')
        return
    
    print(Fore.GREEN + f"\n✅ Loaded {len(accounts)} accounts")
    print(Fore.YELLOW + "🚀 Starting spam in parallel...\n")
    
    # Run ALL accounts in parallel
    tasks = []
    for i, account in enumerate(accounts, 1):
        task = asyncio.create_task(process_account(account, i))
        tasks.append(task)
    
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    print(Fore.GREEN + "\n" + "="*50)
    print(Fore.GREEN + f"✅ ALL {len(accounts)} ACCOUNTS COMPLETED!")
    print(Fore.YELLOW + "📞 Contact @ogdigital for more tools!")
    print(Fore.GREEN + "="*50)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Stopped by user")
    except Exception as e:
        print(Fore.RED + f"\n💥 Error: {str(e)}")