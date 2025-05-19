import os
import time
import json
import asyncio
from telethon import TelegramClient
from telethon.tl.functions.messages import GetHistoryRequest
from telethon.tl.functions.channels import LeaveChannelRequest
from colorama import Fore, Style, init
import pyfiglet

# Initialize colorama for colorful outputs
init(autoreset=True)

# Folder for saving session credentials
CREDENTIALS_FOLDER = "sessions"

# Create the sessions folder if it doesn't exist
if not os.path.exists(CREDENTIALS_FOLDER):
    os.mkdir(CREDENTIALS_FOLDER)

# Function to save session credentials
def save_credentials(session_name, credentials):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    with open(path, "w") as f:
        json.dump(credentials, f)

# Function to load session credentials
def load_credentials(session_name):
    path = os.path.join(CREDENTIALS_FOLDER, f"{session_name}.json")
    if os.path.exists(path):
        with open(path, "r") as f:
            return json.load(f)
    return {}

# Function to display banner
def display_banner():
    banner = pyfiglet.figlet_format("OrbitService")
    print(Fore.RED + banner)
    print(Fore.GREEN + Style.BRIGHT + "Made by @OrbitService\n")

# Function for Auto Pro Sender
async def auto_pro_sender(client, repetitions, delay_after_all_groups):
    try:
        history = await client(GetHistoryRequest(
            peer="me",  # 'me' represents the "Saved Messages" chat
            limit=1,
            offset_date=None,
            offset_id=0,
            max_id=0,
            min_id=0,
            add_offset=0,
            hash=0
        ))
        if history.messages:
            last_saved_message = history.messages[0]
            print(Fore.CYAN + "Last saved message retrieved. Forwarding...\n")
        else:
            print(Fore.RED + "No messages found in Saved Messages.")
            return
    except Exception as e:
        print(Fore.RED + f"Failed to retrieve the last saved message: {e}")
        return

    for _ in range(repetitions):
        groups = [d for d in await client.get_dialogs() if d.is_group]
        for idx, group in enumerate(groups, start=1):
            try:
                await client.forward_messages(group.id, last_saved_message.id, "me")
                print(Fore.GREEN + f"Message successfully forwarded to group: {group.name or group.id}")
            except Exception as e:
                print(Fore.RED + f"Error forwarding message to {group.name or group.id}: {e}")

            # Delay between groups
            if idx % 10 == 0:
                print(Fore.YELLOW + "Reached 10 groups. Waiting 5 seconds before continuing...")
                time.sleep(5)
            else:
                time.sleep(2)

        print(Fore.YELLOW + f"Waiting {delay_after_all_groups} seconds before the next repetition...")
        time.sleep(delay_after_all_groups)

# Function for Pro Leave Groups
async def pro_leave_groups(client):
    predefined_message = (
        "For buying OTT platforms, auto-forwarding scripts, or other digital/social media services, "
        "please contact @OrbitService."
    )

    groups = [d for d in await client.get_dialogs() if d.is_group]
    for group in groups:
        try:
            print(Fore.BLUE + f"Testing group: {group.name or group.id}")
            await client.send_message(group.id, predefined_message)
            print(Fore.GREEN + f"Test message sent successfully to group: {group.name or group.id}")
        except Exception as e:
            print(Fore.RED + f"Failed to send test message to {group.name or group.id}: {e}")
            # Leave group if unable to send a message
            try:
                await client(LeaveChannelRequest(group.id))
                print(Fore.LIGHTMAGENTA_EX + f"Left group: {group.name or group.id}")
            except Exception as leave_error:
                print(Fore.RED + f"Failed to leave group: {group.name or group.id}: {leave_error}")

        # 1-second delay between testing groups
        time.sleep(1)

# Main function to run tasks concurrently for all logged-in clients
async def run_tasks(clients, option, repetitions, delay_after_all_groups):
    tasks = []
    for client in clients:
        if option == 1:
            tasks.append(auto_pro_sender(client, repetitions, delay_after_all_groups))
        elif option == 2:
            tasks.append(pro_leave_groups(client))
    await asyncio.gather(*tasks)

# Main logic
async def main():
    display_banner()  # Display the OrbitService banner

    num_sessions = int(input(Fore.MAGENTA + "How many sessions would you like to log in? "))  # Ask for the number of sessions
    clients = []

    for i in range(1, num_sessions + 1):
        session_name = f"session{i}"
        credentials = load_credentials(session_name)

        if credentials:
            print(Fore.GREEN + f"\nUsing saved credentials for session {i}.")
            api_id = credentials["api_id"]
            api_hash = credentials["api_hash"]
            phone_number = credentials["phone_number"]
        else:
            print(Fore.YELLOW + f"\nEnter details for account {i}:")
            api_id = int(input(Fore.CYAN + f"Enter API ID for session {i}: "))
            api_hash = input(Fore.CYAN + f"Enter API hash for session {i}: ")
            phone_number = input(Fore.CYAN + f"Enter phone number for session {i} (with country code): ")

            credentials = {
                "api_id": api_id,
                "api_hash": api_hash,
                "phone_number": phone_number,
            }
            save_credentials(session_name, credentials)

        client = TelegramClient(session_name, api_id, api_hash)
        await client.start(phone=phone_number)
        clients.append(client)

    print(Fore.MAGENTA + "\nChoose an option:")
    print(Fore.YELLOW + "1. Auto Pro Sender (Forward last saved message to all groups)")
    print(Fore.YELLOW + "2. Pro Leave Groups (Send predefined message and leave groups where sending fails)")

    option = int(input(Fore.CYAN + "Enter your choice: "))
    repetitions, delay_after_all_groups = 0, 0

    if option == 1:
        repetitions = int(input(Fore.MAGENTA + "How many times should the message be sent to all groups? "))
        delay_after_all_groups = float(input(Fore.MAGENTA + "Enter delay (in seconds) after all groups are processed: "))
        print(Fore.GREEN + "Starting Auto Pro Sender...")
    elif option == 2:
        print(Fore.GREEN + "Starting Pro Leave Groups...")
    else:
        print(Fore.RED + "Invalid option selected.")
        return

    # Run tasks for all clients simultaneously
    await run_tasks(clients, option, repetitions, delay_after_all_groups)

    # Disconnect all clients
    for client in clients:
        await client.disconnect()

# Entry point
if __name__ == "__main__":
    asyncio.run(main())
