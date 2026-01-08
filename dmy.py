import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession
from telethon.errors import FloodWaitError
from colorama import init, Fore
import pyfiglet

# Initialize colorama
init(autoreset=True)

def display_banner():
    """Display the banner"""
    print(Fore.RED + pyfiglet.figlet_format("DM Sender"))
    print(Fore.GREEN + "Made by @Og_Flame\n")

async def send_dm(client, session_num, target_username, message):
    """Send direct message to target user"""
    try:
        # Get the target entity
        entity = await client.get_entity(target_username)
        
        # Send the message
        await client.send_message(entity, message)
        print(Fore.GREEN + f"[Session {session_num}] Message sent to {target_username}")
        
    except FloodWaitError as e:
        print(Fore.RED + f"[Session {session_num}] Flood wait: {e.seconds} seconds")
        await asyncio.sleep(e.seconds)
        await send_dm(client, session_num, target_username, message)
    except Exception as e:
        print(Fore.RED + f"[Session {session_num}] Error: {str(e)}")

async def main():
    display_banner()
    
    try:
        # Get target username and message
        target_username = input("Enter target username (e.g., @username): ").strip()
        message = input("Enter message to send: ").strip()
        num_sessions = int(input("How many sessions to use? "))
        
        clients = []
        
        # Create and start each session
        for i in range(1, num_sessions + 1):
            print(Fore.CYAN + f"\nConfiguring Session {i}")
            api_id = input("Enter API ID: ")
            api_hash = input("Enter API hash: ")
            string_session = input("Enter string session (or leave empty for new session): ")
            
            client = TelegramClient(
                StringSession(string_session) if string_session else None,
                int(api_id),
                api_hash
            )
            
            try:
                await client.start()
                if not string_session:
                    print(Fore.YELLOW + "New session created. String session:")
                    print(Fore.WHITE + client.session.save())
                
                clients.append((client, i))
                print(Fore.GREEN + f"Session {i} ready!")
            except Exception as e:
                print(Fore.RED + f"Failed to start session {i}: {str(e)}")
                continue
        
        if not clients:
            print(Fore.RED + "No valid sessions available")
            return
        
        # Send messages
        print(Fore.YELLOW + f"\nSending message to {target_username}...")
        
        tasks = []
        for client, session_num in clients:
            tasks.append(send_dm(client, session_num, target_username, message))
        
        await asyncio.gather(*tasks)
        
        # Disconnect all clients
        for client, _ in clients:
            await client.disconnect()
            
        print(Fore.GREEN + "\nOperation completed!")
        
    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nOperation cancelled by user")
    except Exception as e:
        print(Fore.RED + f"Error: {str(e)}")

if __name__ == "__main__":
    asyncio.run(main())