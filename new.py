import asyncio
import json
import os
import random
from telethon.sync import TelegramClient
from telethon.sessions import StringSession
from telethon.tl.types import PeerUser
from telethon import events

SESSION_FILE = "sessions.json"
SOURCE_CHANNEL = "@OgDigital"
REPLY_TEXT = "DM @OgDigital"

async def prompt_and_login_sessions(required_count):
    existing_sessions = []

    # Load existing
    if os.path.exists(SESSION_FILE):
        with open(SESSION_FILE, "r") as f:
            try:
                existing_sessions = json.load(f)
            except:
                existing_sessions = []

    print(f"✅ Found {len(existing_sessions)} existing sessions.")

    # Add more if not enough
    while len(existing_sessions) < required_count:
        session_num = len(existing_sessions) + 1
        print(f"\n--- Login Session {session_num} ---")
        try:
            api_id = int(input("Enter API ID: "))
            api_hash = input("Enter API Hash: ")
            string = input("Enter STRING SESSION: ")

            client = TelegramClient(StringSession(string), api_id, api_hash)
            await client.start()
            me = await client.get_me()
            uname = me.username or me.first_name or str(me.id)
            print(f"✅ Logged in as: {uname}")
            existing_sessions.append({
                "api_id": api_id,
                "api_hash": api_hash,
                "string_session": string
            })
            await client.disconnect()

        except Exception as e:
            print(f"❌ Login failed: {e}")
            continue

    # Save updated list
    with open(SESSION_FILE, "w") as f:
        json.dump(existing_sessions, f, indent=4)

    return existing_sessions[:required_count]


async def forward_and_reply(account_data, session_number):
    try:
        client = TelegramClient(
            StringSession(account_data['string_session']),
            account_data['api_id'],
            account_data['api_hash']
        )
        await client.start()
        me = await client.get_me()
        uname = me.username or f"id_{me.id}"
        tag = f"[forward_session_{session_number}][@{uname}]"
        print(f"{tag} ✅ Started session.")

    except Exception as e:
        print(f"[forward_session_{session_number}] ❌ Session login failed or banned: {e}")
        return

    @client.on(events.NewMessage(incoming=True))
    async def handle_dm(event):
        if event.is_private:
            try:
                await event.reply(REPLY_TEXT)
                print(f"{tag} 💬 Replied to DM: {event.sender_id}")
            except Exception as e:
                print(f"{tag} ⚠️ Error replying: {e}")

    try:
        source = await client.get_entity(SOURCE_CHANNEL)
        messages = await client.get_messages(source, limit=1)
        if not messages:
            print(f"{tag} ❌ No messages found in {SOURCE_CHANNEL}")
            return

        last_message = messages[0]
        dialogs = await client.get_dialogs()
        groups = [d.entity for d in dialogs if getattr(d, 'is_group', False) or getattr(d, 'is_channel', False)]

        print(f"{tag} 📂 Found {len(groups)} groups/channels to forward to.")

        for idx, group in enumerate(groups, 1):
            group_name = getattr(group, 'title', 'Unknown')
            try:
                delay = random.randint(15, 30)
                print(f"{tag} Sending to {idx}/{len(groups)}: {group_name}")
                await client.send_message(group, last_message)

                for i in range(delay, 0, -1):
                    print(f"{tag} ⏳ Waiting {i}s...", end='\r')
                    await asyncio.sleep(1)
                print(f"{tag} ✅ Forwarded to: {group_name}")

            except Exception as e:
                if "banned" in str(e).lower():
                    print(f"{tag} ❌ BANNED from sending to: {group_name}")
                else:
                    print(f"{tag} ⚠️ Failed to send to {group_name}: {e}")

    except Exception as e:
        print(f"{tag} ❌ Could not fetch or forward message: {e}")

    await client.run_until_disconnected()


async def main():
    try:
        run_count = int(input("👥 How many accounts do you want to run? "))
    except ValueError:
        print("❌ Invalid number.")
        return

    accounts = await prompt_and_login_sessions(run_count)

    tasks = []
    for idx, acc in enumerate(accounts, 1):
        tasks.append(forward_and_reply(acc, idx))

    await asyncio.gather(*tasks)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n⛔ Script stopped by user.")