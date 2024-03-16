from pyrogram import Client
import asyncio
from colorama import Fore, Style, init
import requests
import getpass
import uuid
init(autoreset=True)
import firebase_admin
from firebase_admin import credentials, firestore

# Replace the following placeholders with your actual Firebase credentials
firebase_credentials = {
    "type": "service_account",
    "project_id": "banded-lexicon-374509",
    "private_key_id": "9faef72167d99fcfb63810d736cd2c9777deeb59",
    "private_key": "-----BEGIN PRIVATE KEY-----\nMIIEvQIBADANBgkqhkiG9w0BAQEFAASCBKcwggSjAgEAAoIBAQDAjQYXJ7SCS1RW\nwiiD2SfEAv8am6N33DFBTFqAZxTsp+tTY8N/xSYhbn3BkTzfJvJI2rflc+5DVH03\nMYAROp+6R45UETIJ2nRylGNw9IXVZDGLhUUWyLPSbclnxHfVWRsz26dBR/gr1o2m\nIXk2jqQ69H9mf1SwNuzry0NCdPT6FjAps50csumMZWejkdsz7vHH7YG7rEQZGaLs\nxGCl5AZ7puReULeeGDD1PzsZl/88KiPD0mNjFbDHgeyOeaTGkaesli8iCrLiHrhp\nyS2iHfQ+xmZLZ6HFSf4KfrHam3tRwr7JVGlNp3knAjChQOk4tCcSBN6Ox0SRT8mt\nSDfkujljAgMBAAECggEAI16kVEOMYnTA8NDojVOp/NUKFFKro/xUJekHJNgKnXA5\nB4/nXQSTfQelXRW3R0yJq/1VU3ZIuaB/AdD7c+6/YYH8cI/aD7pLsrJ0U87u+KRX\nf4gDCWzjr09QdFnAI3YjS5LZNeIpAbB/Q5mZgP6Rx2ybLHJOVbI5MhUb7Uy7pWZ0\n8E4+qUA8TgsISOS0X3iTv40hjgbCDUpAZc8WSgTcrD1ikjkPgehNtXpGkxMK5x8o\niiW27ErP+ktsAK5HsLN+SA954rhim5RTO2evZWFNAOEyxw14/BTFLpW/jHItkR0L\nM4Oe9ORq/V1EMKBe/absA11+BS4OlvXfc/ToyLy6XQKBgQD3/qDYvLNvBRziC8u+\nIgNQnGEtSO00TeBPN3+ooj0ONTP+X0z/s2zo/ccLOLG7M9Exmdmc/q1Bn2MNC6PO\ngD0YZ5bJmnDWN42IMrzuojeCtmFPF003O5YK+Zin98UGITNY9PPWRcoErfeu0hom\n0kDJ5zgAbAjVqiW0CSJ5iwRehwKBgQDGxDiAsumuQrI2jVKCwYoU9LVAmAnnDzvi\nrA+ba8t9EtkJ69dawUJgvAtiC8yhkwbLoAUFrVIsrgICkH37o07fISZa/Rh6Y+0G\nlWyUzY0D+1QYsoeRtQO4TY8NBMAxY+x1M/pzBAz2tzGJu5NY3yHJl4Scf08rHr3W\nGsyNdXYJRQKBgQCAmcFNQ2WFH9Cfg+Buw3KWndFiy1t+cRft3GjNyPwCXyKMOV1T\nh/blR5ytPAQmgLNtlkubtxGfYwjZXfze++8ytZ0jBHyZCYvSYgVJdkN0/CCwA/Rd\nvP+Mx2wbRkgcaqEW80dzCRO+o3w6Yud+1C8WxFltFpjqO+Z7WvVOtAFbBwKBgCqy\nb+jFhgkW7q1lQjowVPcXcfAEOOxXi2evylJ6n2WorNLCxKoMJbQd8NwI6NY0fRs0\nrp9/kc1jO69NVqK9e+3WcyTMhXuVB4+IfaChXw9h57i+cPzNw5TNpFMJmDeD3YF3\nvu8CCb7dr1iE4KwQknN5htUPS/RZUDIz44jnmIl5AoGAdUaiIuKuKkgEIpz0Bi37\n//bBJgupH4SVM9+kyDbQGKlprrPT/AiH9nQgfhiLRqVTbOMtBjQcaa5sJQunejWX\nJ5XcusI2mi/+r/x1izpzayO2iD+/UZJ1Q/7KppaQSy+c6nBoQjwtx0WuwdKR6AG7\nEFdMffj90gYd9FrnAmSSV9E=\n-----END PRIVATE KEY-----\n",
    "client_email": "firebase-adminsdk-iqopq@banded-lexicon-374509.iam.gserviceaccount.com",
    "client_id": "106157612129827927729",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/firebase-adminsdk-iqopq%40banded-lexicon-374509.iam.gserviceaccount.com",
    "universe_domain": "googleapis.com"
}

cred = credentials.Certificate(firebase_credentials)
firebase_admin.initialize_app(cred)
db = firestore.client()

def generate_auth_key():
    raise Exception('No authorization key provided. Please enter a valid key.')

def store_device_id(device_id, doc_ref):
    doc = doc_ref.get()
    if doc.exists and 'device_id' in doc.to_dict():
        if doc.to_dict().get('device_id') != device_id:
            raise Exception('Different Device ID already present on the server')
    else:
        doc_ref.update({'device_id': device_id})

def validate_auth_key(auth_key):
    device_id = str(uuid.getnode())  # Get the device's unique identifier
    docs = db.collection('passes').stream()
    for doc in docs:
        if doc.to_dict().get('auth') == auth_key:
            store_device_id(device_id, doc.reference)  # Store the device ID on the server if it's not already there
            return True
    return False

async def get_chat_ids(app: Client):
    chat_ids = []
    chat_with_topic = {}
    async for dialog in app.get_dialogs():
        if dialog.chat.is_forum == True:
            chat_with_topic[dialog.chat.id]=dialog.top_message.topics.id
        chat_ids.append(dialog.chat.id)
        chat_ids = [str(chat_id) for chat_id in chat_ids if str(chat_id).startswith('-')]
        chat_ids = [int(chat_id) for chat_id in chat_ids]
    return [chat_ids, chat_with_topic]

async def send_last_message_to_groups(apps, timee, numtime):
    async def send_last_message(app: Client):
        ac = await get_chat_ids(app)
        chat_ids = ac[0]
        chat_with_topic = ac[1]
        for i in range(numtime):
            try:
                async for message in app.get_chat_history('me', limit=1):
                    last_message = message.id
                    break  # Break the loop after fetching the last message
            except Exception as e:
                print(f"{Fore.RED}Failed to fetch last message: {e}")
                last_message = None

            if last_message is not None:
                for i in chat_with_topic.keys():
                    try:
                        await app.forward_messages(chat_id=i, from_chat_id="me", message_ids=last_message, message_thread_id=chat_with_topic[i])
                    except Exception as e:
                        print(f"Failed to: {i} due to: {e}")
                    else:
                        print(f"{Fore.GREEN}Message sent to chat_id {i}")
                    await asyncio.sleep(2)
                for chat_id in chat_ids:
                    try:
                        await app.forward_messages(chat_id, "me", last_message)
                        print(f"{Fore.GREEN}Message sent to chat_id {chat_id}")
                        await asyncio.sleep(2)
                    except Exception as e:
                        print(f"{Fore.RED}Failed to send message to chat_id {chat_id}: {e}")
                    await asyncio.sleep(5)

            await asyncio.sleep(timee)

    await asyncio.gather(*(send_last_message(app) for app in apps))

async def leave_chats(app, chat_ids):
    for chat_id in chat_ids:
        try:
            await app.leave_chat(chat_id)
            print(f"{Fore.CYAN}Left chat_id {chat_id}")
        except Exception as e:
            print(f"{Fore.RED}Failed to leave chat_id {chat_id}: {e}")

async def join_group(app, chat_id):
    try:
        await app.join_chat(chat_id)
        print(f"{Fore.MAGENTA}Joined chat_id {chat_id}")
    except Exception as e:
        print(f"{Fore.RED}Failed to join chat_id {chat_id}: {e}")


async def main():
    num_sessions = int(input("Enter the number of sessions: "))
    apps = []

    for i in range(num_sessions):
        session_name = f"my_account{i+1}"
        try:
            # Try loading the existing session
            app = Client(session_name)
            await app.start()
        except:
            # If the session file doesn't exist, ask for API credentials
            api_id = int(input(f"Enter api id for {session_name}: "))
            api_hash = input(f"Enter api_hash for {session_name}: ")
            app = Client(session_name, api_id=api_id, api_hash=api_hash)
            await app.start()
        apps.append(app)

    while True:
        a = int(input(
            f"{Style.BRIGHT}{Fore.YELLOW}2. AutoSender\n3. Auto Group Joiner\n4. Leave all groups\n5. Add user to all groups(will only work with one login)\n6. Exit\nEnter the choice: {Style.RESET_ALL}"
        ))

        # if a == 1:
        #     for app in apps:
        #         chat_ids = await get_chat_ids(app)
        #         print(f"{Fore.CYAN}Group IDs for {app.session_name}: {chat_ids}")

        if a == 2:
            numtime = int(input("How many times you want to send the message: "))
            timee = int(input("Enter the time delay: "))
            await send_last_message_to_groups(apps, timee, numtime)
            #await apps[0].send_message(-1001752971759, text = "Hello!!", message_thread_id=4510)

        elif a == 3:
            for app in apps:
                chat_id = input("Enter the Chat ID to join: ")
                await join_group(app, chat_id)

        elif a == 4:
            for app in apps:
                chat_ids = await get_chat_ids(app)
                await leave_chats(app, chat_ids)

        elif a == 5:
            user_id = input("Enter the user ID to add to all groups: ")
            chat_ids = await get_chat_ids(app)
            for chat_id in chat_ids:
                for app in apps:
                    await app.add_chat_members(chat_id, user_id)

        elif a == 6:
            for app in apps:
                await app.stop()
            break

if __name__ == "__main__":
    # if __name__ == "__main__":
    asyncio.run(main())
    
