import os
import asyncio
from telethon import TelegramClient
from telethon.sessions import StringSession

INPUT_FILE = "session.txt"
OUTPUT_DIR = "accounts"

os.makedirs(OUTPUT_DIR, exist_ok=True)

async def main():
    with open(INPUT_FILE, "r", encoding="utf-8") as f:
        lines = [line.strip() for line in f if line.strip()]

    if len(lines) % 3 != 0:
        print("❌ Invalid file format")
        return

    print(f"[+] Found {len(lines)//3} string sessions")

    for i in range(0, len(lines), 3):
        api_id = int(lines[i])
        api_hash = lines[i + 1]
        string = lines[i + 2]

        try:
            # Step 1: login using string session (NO FILE)
            temp_client = TelegramClient(
                StringSession(string),
                api_id,
                api_hash
            )
            await temp_client.connect()

            if not await temp_client.is_user_authorized():
                print("[-] Unauthorized string, skipped")
                await temp_client.disconnect()
                continue

            me = await temp_client.get_me()
            user_id = me.id

            # Step 2: create REAL .session file using user_id
            session_path = os.path.join(OUTPUT_DIR, str(user_id))

            real_client = TelegramClient(
                session_path,
                api_id,
                api_hash
            )

            # copy auth key
            real_client.session.auth_key = temp_client.session.auth_key
            real_client.session.set_dc(
                temp_client.session.dc_id,
                temp_client.session.server_address,
                temp_client.session.port
            )

            real_client.session.save()

            await temp_client.disconnect()
            await real_client.disconnect()

            print(f"[✓] Created: {user_id}.session")

        except Exception as e:
            print(f"[!] Error: {e}")

asyncio.run(main())
