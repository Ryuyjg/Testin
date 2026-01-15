import asyncio
import os
import json
import glob
from telethon import TelegramClient
from telethon.errors import FloodWaitError
from colorama import init, Fore
import pyfiglet

# Initialize colorama
init(autoreset=True)

def display_banner():
    """Display the banner"""
    print(Fore.RED + pyfiglet.figlet_format("DM SENDER"))
    print(Fore.GREEN + "Made by @Og_Flame\n")
    print(Fore.CYAN + "✓ Uses .session files with auto API setup\n")

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
    """Load accounts with session files, create minimal JSON if needed"""
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

async def send_dm(client, account_name, target_username, message):
    """Send direct message to target user"""
    try:
        # Get the target entity
        entity = await client.get_entity(target_username)
        
        # Send the message
        await client.send_message(entity, message)
        return True, f"[{account_name}] Message sent to {target_username}"
        
    except FloodWaitError as e:
        return False, f"[{account_name}] Flood wait: {e.seconds} seconds"
    except Exception as e:
        return False, f"[{account_name}] Error: {str(e)}"

async def main():
    display_banner()
    
    try:
        # Create accounts folder if not exists
        os.makedirs('accounts', exist_ok=True)
        
        print(Fore.CYAN + "📂 Loading accounts from 'accounts/' folder...\n")
        
        # Load all accounts
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
        
        # Get target and message
        target_username = input("\nEnter target username (e.g., @username or +number): ").strip()
        if not target_username:
            print(Fore.RED + "Target username required!")
            return
            
        message = input("Enter message to send: ").strip()
        if not message:
            print(Fore.RED + "Message required!")
            return
        
        print(Fore.YELLOW + f"\n📤 Sending to: {target_username}")
        print(Fore.CYAN + f"💬 Message: {message}\n")
        
        # Process all accounts in parallel
        tasks = []
        clients = []
        
        for account in accounts:
            try:
                client = TelegramClient(
                    account['session_path'],
                    account['api_id'],
                    account['api_hash'],
                    connection_retries=1
                )
                
                print(Fore.YELLOW + f"🔄 Connecting {account['name']}...")
                await client.connect()
                
                # Check if session is valid
                if not await client.is_user_authorized():
                    print(Fore.RED + f"✗ {account['name']}: Session not authorized")
                    continue
                
                # Get account info
                me = await client.get_me()
                print(Fore.GREEN + f"✓ {account['name']}: Connected as @{me.username or me.first_name} (ID: {me.id})")
                
                clients.append((client, account['name']))
                
                # Create send task
                task = send_dm(client, account['name'], target_username, message)
                tasks.append(task)
                
            except Exception as e:
                print(Fore.RED + f"✗ {account['name']}: Failed - {str(e)[:80]}")
                continue
        
        if not tasks:
            print(Fore.RED + "No valid sessions to send from!")
            return
        
        # Send all messages in parallel
        print(Fore.YELLOW + f"\n🚀 Sending from {len(tasks)} accounts...")
        results = await asyncio.gather(*tasks, return_exceptions=True)
        
        # Show results
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.CYAN + "📊 SENDING RESULTS:")
        print(Fore.CYAN + "="*50)
        
        success_count = 0
        failed_count = 0
        
        for i, (client, account_name) in enumerate(clients):
            if i < len(results):
                result = results[i]
                
                if isinstance(result, Exception):
                    print(Fore.RED + f"✗ {account_name}: Exception - {str(result)[:80]}")
                    failed_count += 1
                elif isinstance(result, tuple):
                    success, msg = result
                    if success:
                        print(Fore.GREEN + f"✓ {msg}")
                        success_count += 1
                    else:
                        print(Fore.YELLOW + f"⚠ {msg}")
                        failed_count += 1
                else:
                    print(Fore.RED + f"✗ {account_name}: Unknown result type")
                    failed_count += 1
        
        # Disconnect all clients
        for client, account_name in clients:
            try:
                await client.disconnect()
                print(Fore.BLUE + f"↩ {account_name}: Disconnected")
            except:
                pass
        
        print(Fore.CYAN + "="*50)
        print(Fore.GREEN + f"✅ SUCCESS: {success_count}")
        print(Fore.YELLOW + f"⚠ FAILED: {failed_count}")
        print(Fore.CYAN + f"📊 TOTAL: {len(clients)} accounts processed")
        print(Fore.CYAN + "="*50)
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Operation cancelled by user")
    except Exception as e:
        print(Fore.RED + f"\n💥 Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())