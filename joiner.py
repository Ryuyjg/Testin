import asyncio
import os
import glob
import re
from telethon import TelegramClient
from telethon.tl.functions.channels import JoinChannelRequest, LeaveChannelRequest
from telethon.errors import FloodWaitError, UserAlreadyParticipantError, ChannelPrivateError, FloodError
from colorama import init, Fore

init(autoreset=True)

def display_banner():
    print(Fore.CYAN + """
    ╔══════════════════════════════════════════╗
    ║        GROUP JOINER - SESSION ONLY       ║
    ║        NO API ID/HASH NEEDED             ║
    ╚══════════════════════════════════════════╝
    """)
    print(Fore.YELLOW + "📁 Works with .session files only\n")

async def load_accounts():
    """Load all .session files from accounts/ folder"""
    accounts = []
    session_files = glob.glob('accounts/*.session')
    
    for session_file in session_files:
        base_name = os.path.basename(session_file).replace('.session', '')
        
        accounts.append({
            'session_path': session_file,
            'name': base_name
        })
        print(Fore.GREEN + f"✓ Session: {base_name}")
    
    return accounts

def load_groups_from_files():
    """Load groups from all .txt files in groups/ folder"""
    groups = []
    
    # Create groups folder if not exists
    os.makedirs('groups', exist_ok=True)
    
    # Check if groups folder exists
    if not os.path.exists('groups'):
        print(Fore.RED + "❌ 'groups/' folder not found!")
        return groups
    
    # Find all .txt files in groups folder
    group_files = glob.glob('groups/*.txt')
    
    if not group_files:
        print(Fore.RED + "❌ No .txt files found in 'groups/' folder!")
        print(Fore.YELLOW + "Add .txt files with group usernames (one per line)")
        return groups
    
    print(Fore.CYAN + f"📂 Found {len(group_files)} group files")
    
    for file_path in group_files:
        filename = os.path.basename(file_path)
        file_groups = []
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                lines = f.readlines()
            
            for line_num, line in enumerate(lines, 1):
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Extract username/link
                username = extract_username(line)
                if username:
                    file_groups.append(username)
                else:
                    print(Fore.YELLOW + f"⚠ {filename}: Line {line_num} - Invalid format: {line}")
            
            print(Fore.GREEN + f"✓ {filename}: Loaded {len(file_groups)} groups")
            groups.extend(file_groups)
            
        except Exception as e:
            print(Fore.RED + f"✗ Error reading {filename}: {str(e)[:50]}")
    
    # Remove duplicates
    unique_groups = list(dict.fromkeys(groups))
    
    print(Fore.CYAN + f"\n📊 Total unique groups: {len(unique_groups)}")
    
    # Save combined list for reference
    if unique_groups:
        with open('groups/_all_groups_combined.txt', 'w', encoding='utf-8') as f:
            f.write("# Combined groups from all files\n")
            for group in unique_groups:
                f.write(f"{group}\n")
        print(Fore.GREEN + f"✓ Saved combined list: groups/_all_groups_combined.txt")
    
    return unique_groups

def extract_username(line):
    """Extract username from various formats"""
    line = line.strip()
    
    # Remove @ if present
    if line.startswith('@'):
        return line[1:]  # Remove @
    
    # Extract from telegram links
    patterns = [
        r't\.me/([a-zA-Z0-9_]+)',           # t.me/username
        r'telegram\.me/([a-zA-Z0-9_]+)',    # telegram.me/username
        r'telegram\.dog/([a-zA-Z0-9_]+)',   # telegram.dog/username
        r'joinchat/([a-zA-Z0-9_-]+)',       # t.me/joinchat/xxxx
        r'\+(.+)',                          # +invite links
    ]
    
    for pattern in patterns:
        match = re.search(pattern, line)
        if match:
            return match.group(1)
    
    # If it's just alphanumeric, assume it's a username
    if re.match(r'^[a-zA-Z0-9_]+$', line):
        return line
    
    return None

async def process_account(account, groups, start_idx, groups_per_session, action, delay_between_groups):
    """Process groups for one account using ONLY session file"""
    joined = 0
    skipped = 0
    failed = 0
    
    client = None
    try:
        # 🚨 IMPORTANT: Use default api_id and api_hash for existing sessions
        # These are Telegram's official test credentials
        client = TelegramClient(
            session=account['session_path'],
            api_id=2040,  # Default Telegram test ID
            api_hash='b18441a1ff607e10a989891a5462e627',  # Default test hash
            connection_retries=1
        )
        
        print(Fore.YELLOW + f"[{account['name']}] Connecting...")
        await client.connect()
        
        # Check if session is valid
        if not await client.is_user_authorized():
            print(Fore.RED + f"✗ {account['name']}: Session not authorized")
            await client.disconnect()
            return joined, skipped, failed, True, False
        
        # Get account info
        me = await client.get_me()
        print(Fore.GREEN + f"✓ {account['name']}: Connected as @{me.username or me.first_name} (ID: {me.id})")
        
        end_idx = min(start_idx + groups_per_session, len(groups))
        
        if start_idx >= len(groups):
            await client.disconnect()
            return joined, skipped, failed, False, True  # reached_end=True
        
        print(Fore.CYAN + f"[{account['name']}] Processing {start_idx+1}-{end_idx} ({action})")
        
        for i in range(start_idx, end_idx):
            group_username = groups[i]
            group_entity = f"@{group_username}" if not group_username.startswith('+') else group_username
            
            try:
                if action == "join":
                    await client(JoinChannelRequest(group_entity))
                    print(Fore.GREEN + f"[{account['name']}] ✅ Joined {group_entity}")
                    joined += 1
                else:  # leave
                    entity = await client.get_entity(group_entity)
                    await client(LeaveChannelRequest(entity))
                    print(Fore.YELLOW + f"[{account['name']}] ← Left {group_entity}")
                    joined += 1
                
                if i < end_idx - 1:  # Don't delay after last group
                    await asyncio.sleep(delay_between_groups)
                
            except UserAlreadyParticipantError:
                if action == "join":
                    skipped += 1
                    print(Fore.YELLOW + f"[{account['name']}] ⚡ Already in {group_entity}")
                else:
                    failed += 1
                    print(Fore.RED + f"[{account['name']}] ❌ Not in {group_entity}")
                
            except (ChannelPrivateError, ValueError):
                failed += 1
                print(Fore.RED + f"[{account['name']}] 🔒 Private/Invalid: {group_entity}")
                
            except FloodWaitError as e:
                print(Fore.RED + f"[{account['name']}] ⏳ Flood wait {e.seconds}s")
                await asyncio.sleep(e.seconds)
                continue  # Try again after wait
                
            except FloodError as e:
                print(Fore.RED + f"[{account['name']}] 🚨 FLOOD ERROR - skipping")
                await client.disconnect()
                return joined, skipped, failed, False, True  # flood_wait=True
                
            except Exception as e:
                failed += 1
                print(Fore.RED + f"[{account['name']}] ❌ Failed {group_entity}: {str(e)[:50]}")
        
        await client.disconnect()
        return joined, skipped, failed, False, False
        
    except Exception as e:
        if client:
            try:
                await client.disconnect()
            except:
                pass
        print(Fore.RED + f"✗ {account['name']}: Error - {str(e)}")
        return joined, skipped, failed, False, False

async def main():
    display_banner()
    
    # Create necessary folders
    os.makedirs('accounts', exist_ok=True)
    os.makedirs('groups', exist_ok=True)
    
    # Load accounts (SESSION FILES ONLY)
    print(Fore.CYAN + "📂 Loading session files...\n")
    accounts = await load_accounts()
    
    if not accounts:
        print(Fore.RED + "\n❌ No .session files found!")
        print(Fore.YELLOW + "\nPut .session files in 'accounts/' folder")
        print(Fore.WHITE + "No .json files needed!")
        return
    
    print(Fore.GREEN + f"\n✅ Loaded {len(accounts)} session files")
    
    # Load groups from files
    print(Fore.CYAN + "\n📂 Loading groups from files...")
    groups = load_groups_from_files()
    
    if not groups:
        print(Fore.RED + "\n❌ No groups loaded!")
        print(Fore.YELLOW + "\nAdd .txt files to 'groups/' folder with usernames")
        print(Fore.WHITE + "Example: groups/my_groups.txt")
        print(Fore.WHITE + "Format: one username per line")
        return
    
    print(Fore.GREEN + f"\n✅ Loaded {len(groups)} unique groups")
    
    # Settings
    print(Fore.YELLOW + "\n🔧 Configure settings:")
    
    groups_per_session = int(input("Groups per account per cycle (default 5): ") or 5)
    delay_between_groups = int(input("Delay between groups in seconds (default 25): ") or 25)
    delay_between_accounts = int(input("Delay between accounts in seconds (default 45): ") or 45)
    delay_between_cycles = int(input("Delay between cycles in seconds (default 120): ") or 120)
    
    print(Fore.YELLOW + "\n🔧 Choose action:")
    print(Fore.WHITE + "1. Join groups")
    print(Fore.WHITE + "2. Leave groups")
    choice = input("\nEnter choice (1 or 2): ").strip()
    
    action = "join" if choice == "1" else "leave"
    
    # Start
    print(Fore.CYAN + "\n" + "="*60)
    print(Fore.CYAN + "STARTING GROUP PROCESSING")
    print(Fore.CYAN + "="*60)
    print(Fore.WHITE + f"• Action: {action.upper()}")
    print(Fore.WHITE + f"• Accounts: {len(accounts)}")
    print(Fore.WHITE + f"• Groups: {len(groups)}")
    print(Fore.WHITE + f"• Groups per account: {groups_per_session}")
    print(Fore.WHITE + f"• Delay between groups: {delay_between_groups}s")
    print(Fore.WHITE + f"• Delay between accounts: {delay_between_accounts}s")
    print(Fore.WHITE + f"• Delay between cycles: {delay_between_cycles}s")
    print(Fore.CYAN + "="*60 + "\n")
    
    # Variables
    current_offset = 0
    total_processed = 0
    total_skipped = 0
    total_failed = 0
    cycle_count = 0
    
    while current_offset < len(groups):
        cycle_count += 1
        
        print(Fore.CYAN + f"\n{'='*60}")
        print(Fore.CYAN + f"CYCLE {cycle_count}")
        print(Fore.CYAN + f"Offset: {current_offset}/{len(groups)}")
        print(Fore.CYAN + f"Remaining: {len(groups) - current_offset}")
        print(Fore.CYAN + f"{'='*60}\n")
        
        for account in accounts:
            if current_offset >= len(groups):
                break
            
            print(Fore.YELLOW + f"\n=== {account['name']} ===")
            
            joined, skipped, failed, flood_wait, reached_end = await process_account(
                account, groups, current_offset, groups_per_session, action, delay_between_groups
            )
            
            total_processed += joined
            total_skipped += skipped
            total_failed += failed
            
            # Move offset for next account
            current_offset += groups_per_session
            
            # Update current account status
            if joined > 0:
                print(Fore.GREEN + f"[{account['name']}] ✅ {action.capitalize()}ed: {joined}")
            if skipped > 0:
                print(Fore.YELLOW + f"[{account['name']}] ⚡ Skipped: {skipped}")
            if failed > 0:
                print(Fore.RED + f"[{account['name']}] ❌ Failed: {failed}")
            
            # Check if we're done
            if current_offset >= len(groups):
                break
            
            # Delay between accounts (unless last one)
            if account != accounts[-1] and current_offset < len(groups):
                print(Fore.BLUE + f"[{account['name']}] 💤 Sleeping {delay_between_accounts}s")
                await asyncio.sleep(delay_between_accounts)
        
        # Check if done
        if current_offset >= len(groups):
            break
        
        # Delay between cycles
        print(Fore.CYAN + f"\n{'='*60}")
        print(Fore.CYAN + f"CYCLE {cycle_count} COMPLETED")
        print(Fore.CYAN + f"Progress: {min(current_offset, len(groups))}/{len(groups)}")
        print(Fore.CYAN + f"Next offset: {current_offset}")
        print(Fore.CYAN + f"Sleeping {delay_between_cycles}s...")
        print(Fore.CYAN + f"{'='*60}\n")
        
        # Countdown
        for i in range(delay_between_cycles // 15):
            remaining = delay_between_cycles - (i * 15)
            print(Fore.YELLOW + f"⏰ Next cycle in: {remaining}s")
            await asyncio.sleep(15)
    
    # Final summary
    print(Fore.GREEN + f"\n{'='*60}")
    print(Fore.GREEN + "✅ PROCESSING COMPLETED!")
    print(Fore.GREEN + f"{'='*60}")
    print(Fore.WHITE + f"Action: {action.upper()}")
    print(Fore.WHITE + f"Accounts used: {len(accounts)}")
    print(Fore.WHITE + f"Total groups available: {len(groups)}")
    print(Fore.GREEN + f"✓ Successfully {action}ed: {total_processed}")
    print(Fore.YELLOW + f"⚠ Already in/not in: {total_skipped}")
    print(Fore.RED + f"✗ Failed: {total_failed}")
    
    # Save results
    with open('processing_results.txt', 'w', encoding='utf-8') as f:
        f.write(f"Action: {action}\n")
        f.write(f"Accounts used: {len(accounts)}\n")
        f.write(f"Groups available: {len(groups)}\n")
        f.write(f"Successfully {action}ed: {total_processed}\n")
        f.write(f"Skipped: {total_skipped}\n")
        f.write(f"Failed: {total_failed}\n")
    
    print(Fore.GREEN + f"📊 Results saved to: processing_results.txt")
    print(Fore.GREEN + f"{'='*60}")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + f"\n\n{'='*60}")
        print(Fore.YELLOW + "SCRIPT STOPPED BY USER")
        print(Fore.YELLOW + f"{'='*60}")
    except Exception as e:
        print(Fore.RED + f"\n💥 Fatal error: {e}")