from telethon.sync import TelegramClient
from telethon.sessions import StringSession

print("Telethon Multi-Session Generator")
print("(Press Ctrl+C to stop)\n")

# Get API credentials once
API_ID = input("Enter your API ID (from https://my.telegram.org): ")
API_HASH = input("Enter your API Hash (from https://my.telegram.org): ")

session_count = 1

while True:
    print(f"\n{'='*60}")
    print(f"Creating Session #{session_count}")
    print(f"{'='*60}")
    
    # Get phone number for this session
    PHONE_NUMBER = input("Enter phone number (with country code, e.g., +1234567890): ")
    
    try:
        # Create a Telethon client
        with TelegramClient(StringSession(), API_ID, API_HASH) as client:
            # Connect and log in
            client.connect()

            if not client.is_user_authorized():
                # Send OTP if not logged in
                client.send_code_request(PHONE_NUMBER)
                code = input("Enter the OTP you received: ")
                client.sign_in(PHONE_NUMBER, code)

            # Get the string session
            string_session = client.session.save()

            # Display the string session
            print(f"\n✅ Session #{session_count} created successfully!")
            print("Your Telethon string session is:")
            print(string_session)
            print(f"{'='*60}")
            print("Save this string session in a safe place!\n")
            
    except Exception as e:
        print(f"Error: {e}")
        if "password" in str(e):  # Handle 2FA
            try:
                with TelegramClient(StringSession(), API_ID, API_HASH) as client:
                    client.connect()
                    password = input("Your account has 2FA enabled. Enter your 2FA password: ")
                    client.sign_in(password=password)
                    string_session = client.session.save()
                    print(f"\n✅ Session #{session_count} created successfully!")
                    print("Your Telethon string session is:")
                    print(string_session)
                    print(f"{'='*60}")
                    print("Save this string session in a safe place!\n")
            except Exception as e2:
                print(f"2FA Error: {e2}")
                print("Skipping this number...\n")
    
    session_count += 1