import asyncio
import random
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.functions.messages import ReportRequest
from telethon.tl.types import InputReportReasonSpam, InputReportReasonViolence, InputReportReasonPornography, InputReportReasonChildAbuse, InputReportReasonOther
from colorama import init, Fore, Style

init(autoreset=True)

def display_banner():
    print(Fore.RED + Style.BRIGHT + """
    ╔══════════════════════════════════════════╗
    ║          OG DIGITAL TOOL                ║
    ║          Made by @ogdigital              ║
    ║     Buy cheap spam software              ║
    ╚══════════════════════════════════════════╝
    """)
    print(Fore.YELLOW + "📞 Contact: @ogdigital for tools & services\n")

class OGTool:
    def __init__(self):
        self.client = None
        
    async def connect_account(self):
        """Connect to Telegram account"""
        print(Fore.CYAN + "\n" + "="*50)
        print(Fore.CYAN + "📱 ACCOUNT LOGIN")
        print(Fore.CYAN + "="*50)
        
        try:
            api_id = int(input("Enter API ID: "))
            api_hash = input("Enter API HASH: ")
            string_session = input("Enter STRING SESSION: ")
            
            self.client = TelegramClient(
                StringSession(string_session),
                api_id,
                api_hash
            )
            
            await self.client.start()
            me = await self.client.get_me()
            print(Fore.GREEN + f"✅ Connected: @{me.username or me.first_name}")
            return True
            
        except Exception as e:
            print(Fore.RED + f"❌ Connection failed: {str(e)[:50]}")
            return False
    
    async def mass_report_channels(self):
        """Mass report channels"""
        print(Fore.RED + "\n" + "="*50)
        print(Fore.RED + "🚨 MASS REPORT CHANNELS")
        print(Fore.RED + "="*50)
        
        channel_links = input("Enter channel links (comma separated): ").split(',')
        channel_links = [link.strip() for link in channel_links if link.strip()]
        
        if not channel_links:
            print(Fore.RED + "❌ No channels provided")
            return
        
        reason = self.select_report_reason()
        
        print(Fore.YELLOW + f"\n🚨 Reporting {len(channel_links)} channels...")
        
        for i, link in enumerate(channel_links, 1):
            try:
                entity = await self.client.get_entity(link)
                await self.client(ReportRequest(
                    peer=entity,
                    id=[random.randint(1, 1000)],
                    reason=reason,
                    message="Mass report - violating content"
                ))
                print(Fore.GREEN + f"✅ {i}. Reported: {link}")
                await asyncio.sleep(random.uniform(2, 5))
                
            except Exception as e:
                print(Fore.RED + f"❌ {i}. Failed: {link} - {str(e)[:30]}")
    
    async def mass_report_groups(self):
        """Mass report groups"""
        print(Fore.RED + "\n" + "="*50)
        print(Fore.RED + "🚨 MASS REPORT GROUPS")
        print(Fore.RED + "="*50)
        
        group_links = input("Enter group links (comma separated): ").split(',')
        group_links = [link.strip() for link in group_links if link.strip()]
        
        if not group_links:
            print(Fore.RED + "❌ No groups provided")
            return
        
        reason = self.select_report_reason()
        
        print(Fore.YELLOW + f"\n🚨 Reporting {len(group_links)} groups...")
        
        for i, link in enumerate(group_links, 1):
            try:
                entity = await self.client.get_entity(link)
                await self.client(ReportRequest(
                    peer=entity,
                    id=[random.randint(1, 1000)],
                    reason=reason,
                    message="Mass report - spam group"
                ))
                print(Fore.GREEN + f"✅ {i}. Reported: {link}")
                await asyncio.sleep(random.uniform(3, 6))
                
            except Exception as e:
                print(Fore.RED + f"❌ {i}. Failed: {link} - {str(e)[:30]}")
    
    async def spam_groups(self):
        """Send spam message to groups"""
        print(Fore.GREEN + "\n" + "="*50)
        print(Fore.GREEN + "📢 SPAM MESSAGES TO GROUPS")
        print(Fore.GREEN + "="*50)
        
        message = input("Enter spam message: ")
        if not message:
            message = "📢 DM @ogdigital to buy cheap spam software! Best prices for Telegram tools! 📢"
        
        group_links = input("Enter group links (comma separated): ").split(',')
        group_links = [link.strip() for link in group_links if link.strip()]
        
        if not group_links:
            print(Fore.YELLOW + "⚠ Using your joined groups...")
            groups = []
            async for dialog in self.client.iter_dialogs():
                if dialog.is_group:
                    groups.append(dialog.entity)
            
            group_links = [f"t.me/{getattr(g, 'username', g.id)}" for g in groups[:50]]
        
        print(Fore.YELLOW + f"\n📤 Sending to {len(group_links)} groups...")
        
        for i, link in enumerate(group_links, 1):
            try:
                entity = await self.client.get_entity(link)
                await self.client.send_message(entity, message)
                print(Fore.GREEN + f"✅ {i}. Sent to: {link}")
                await asyncio.sleep(random.uniform(5, 15))
                
            except Exception as e:
                print(Fore.RED + f"❌ {i}. Failed: {link}")
    
    async def mass_report_usernames(self):
        """Mass report by username"""
        print(Fore.RED + "\n" + "="*50)
        print(Fore.RED + "🚨 MASS REPORT USERNAMES")
        print(Fore.RED + "="*50)
        
        usernames = input("Enter usernames (comma separated, with @): ").split(',')
        usernames = [user.strip() for user in usernames if user.strip()]
        
        if not usernames:
            print(Fore.RED + "❌ No usernames provided")
            return
        
        reason = self.select_report_reason()
        
        print(Fore.YELLOW + f"\n🚨 Reporting {len(usernames)} users...")
        
        for i, username in enumerate(usernames, 1):
            try:
                if not username.startswith('@'):
                    username = '@' + username
                
                entity = await self.client.get_entity(username)
                await self.client(ReportRequest(
                    peer=entity,
                    id=[random.randint(1, 1000)],
                    reason=reason,
                    message="Mass report - suspicious account"
                ))
                print(Fore.GREEN + f"✅ {i}. Reported: {username}")
                await asyncio.sleep(random.uniform(2, 4))
                
            except Exception as e:
                print(Fore.RED + f"❌ {i}. Failed: {username}")
    
    def select_report_reason(self):
        """Select report reason"""
        print(Fore.CYAN + "\nSelect report reason:")
        print("1. Spam")
        print("2. Violence")
        print("3. Pornography")
        print("4. Child Abuse")
        print("5. Other")
        
        choice = input("\nChoice (1-5): ").strip()
        
        reasons = {
            '1': InputReportReasonSpam(),
            '2': InputReportReasonViolence(),
            '3': InputReportReasonPornography(),
            '4': InputReportReasonChildAbuse(),
            '5': InputReportReasonOther()
        }
        
        return reasons.get(choice, InputReportReasonSpam())
    
    async def show_menu(self):
        """Display main menu"""
        while True:
            print(Fore.CYAN + "\n" + "="*50)
            print(Fore.CYAN + "📱 OG DIGITAL TOOL - MAIN MENU")
            print(Fore.CYAN + "="*50)
            print(Fore.YELLOW + "1. Mass Reports (Channels)")
            print(Fore.YELLOW + "2. Mass Reports (Groups)")
            print(Fore.YELLOW + "3. Send Spam Message to Groups")
            print(Fore.YELLOW + "4. Mass Telegram Report (Usernames)")
            print(Fore.RED + "5. Exit")
            print(Fore.CYAN + "="*50)
            
            choice = input("\nSelect option (1-5): ").strip()
            
            if choice == '1':
                await self.mass_report_channels()
            elif choice == '2':
                await self.mass_report_groups()
            elif choice == '3':
                await self.spam_groups()
            elif choice == '4':
                await self.mass_report_usernames()
            elif choice == '5':
                print(Fore.YELLOW + "\n👋 Thanks for using OG Digital Tool!")
                print(Fore.RED + "📞 Contact: @ogdigital")
                break
            else:
                print(Fore.RED + "❌ Invalid choice")
            
            input(Fore.CYAN + "\nPress Enter to continue...")

async def main():
    display_banner()
    
    tool = OGTool()
    
    # Connect account
    connected = await tool.connect_account()
    if not connected:
        print(Fore.RED + "\n❌ Cannot continue without account connection")
        return
    
    # Show menu
    await tool.show_menu()
    
    # Disconnect
    if tool.client:
        await tool.client.disconnect()
        print(Fore.GREEN + "✅ Disconnected")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\n\n👋 Tool stopped by user")
    except Exception as e:
        print(Fore.RED + f"\n💥 Error: {str(e)}")