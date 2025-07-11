import asyncio
import os
import json
import logging
from telethon import TelegramClient, events, errors
from telethon.errors import UserDeactivatedBanError
from telethon.tl.functions.messages import GetHistoryRequest, DeleteHistoryRequest
from telethon.sessions import StringSession
from colorama import init, Fore
import pyfiglet

init(autoreset=True)

CREDENTIALS_FOLDER = 'sessions'

if not os.path.exists(CREDENTIALS_FOLDER):
    os.mkdir(CREDENTIALS_FOLDER)

logging.basicConfig(
    filename='og_flame_service.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)

AUTO_REPLY_MESSAGE = """
This account is managed by @OgDigital

For buying/selling accounts, please DM @OgDigital directly.

Official channel: @OgDigital
"""

def save_credentials(session_name, api_id, api_hash, session_string):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    with open(path, 'w') as f:
        json.dump({
            'api_id': api_id,
            'api_hash': api_hash,
            'session_string': session_string
        }, f)

def load_credentials(session_name):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    if os.path.exists(path):
        with open(path, 'r') as f:
            return json.load(f)
    return None

def display_banner():
    print(Fore.RED + pyfiglet.figlet_format("OgDigital Forwarder"))
    print(Fore.GREEN + "Managed by @OgDigital\n")

async def auto_reply(client, session_name):
    @client.on(events.NewMessage(incoming=True))
    async def handler(event):
        if event.is_private:
            try:
                await event.reply(AUTO_REPLY_MESSAGE)
                logging.info(f"Replied to {event.sender_id} in {session_name}")
                await client(DeleteHistoryRequest(peer=event.sender_id, max_id=0, revoke=False))
                print(Fore.GREEN + f"Deleted chat with {event.sender_id}")
            except errors.FloodWaitError as e:
                await asyncio.sleep(e.seconds)
            except Exception as e:
                logging.error(f"Auto-Reply Error: {str(e)}")

async def forward_with_delay(client, last_message, session_name, group, delay):
    try:
        await asyncio.sleep(delay)  # Wait for the specified delay
        await client.send_message(group, last_message.message, link_preview=False)
        print(Fore.GREEN + f"Message forwarded to {group.title} from {session_name}")
    except errors.FloodWaitError as e:
        await asyncio.sleep(e.seconds)
    except Exception as e:
        logging.error(f"Forward Error: {str(e)}")

async def get_last_ogdigital_message(client):
    try:
        ogdigital_entity = await client.get_input_entity('@Ogdigital')
        messages = await client.get_messages(ogdigital_entity, limit=1)
        if messages:
            return messages[0]
    except Exception as e:
        print(Fore.RED + f"Error getting @Ogdigital messages: {str(e)}")
    return None

async def initialize_session(session_name, credentials):
    try:
        client = TelegramClient(
            StringSession(credentials['session_string']),
            credentials['api_id'],
            credentials['api_hash']
        )
        await client.connect()

        if not await client.is_user_authorized():
            print(Fore.RED + f"Session authorization failed for {session_name}")
            return None, None

        last_message = await get_last_ogdigital_message(client)
        if not last_message:
            print(Fore.RED + f"No messages found from @Ogdigital for {session_name}")
            return None, None

        asyncio.create_task(auto_reply(client, session_name))
        return client, last_message

    except UserDeactivatedBanError:
        print(Fore.RED + f"Session {session_name} is BANNED!")
    except Exception as e:
        print(Fore.RED + f"Error in {session_name}: {str(e)}")

    return None, None

async def main():
    display_banner()

    try:
        num_sessions = int(input("Enter Number of Sessions: "))
        action_delay = int(input("Delay between Actions (Seconds): "))
        
        active_clients = []
        
        # Initialize all sessions immediately
        for i in range(1, num_sessions + 1):
            session_name = f'session{i}'
            credentials = load_credentials(session_name)
            
            if not credentials:
                print(Fore.CYAN + f"\nSetting up new session: {session_name}")
                api_id = int(input("API ID: "))
                api_hash = input("API Hash: ")
                session_string = input("Session String: ")
                save_credentials(session_name, api_id, api_hash, session_string)
                credentials = {
                    'api_id': api_id,
                    'api_hash': api_hash,
                    'session_string': session_string
                }
            else:
                print(Fore.GREEN + f"Using saved session: {session_name}")
            
            client, last_message = await initialize_session(session_name, credentials)
            if client:
                active_clients.append((client, last_message, session_name))
        
        print(Fore.GREEN + "\nAll sessions initialized. Starting message forwarding...")
        
        # Process actions with delays
        while True:
            for index, (client, last_message, session_name) in enumerate(active_clients):
                # Update the last message from @Ogdigital before forwarding
                updated_message = await get_last_ogdigital_message(client)
                if updated_message:
                    last_message = updated_message
                
                async for dialog in client.iter_dialogs():
                    if dialog.is_group:
                        await forward_with_delay(
                            client,
                            last_message,
                            session_name,
                            dialog.entity,
                            action_delay if index > 0 else 0  # No delay for first action
                        )

    except KeyboardInterrupt:
        print(Fore.YELLOW + "\nStopped by User")
    except ValueError:
        print(Fore.RED + "Invalid Number Input")

if __name__ == "__main__":
    asyncio.run(main())
