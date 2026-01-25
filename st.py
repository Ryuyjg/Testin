#!/usr/bin/env python3
"""
Telegram String to Session Converter
Creates valid .session files for Telethon
"""

import os
import base64
import sqlite3
import struct
from pathlib import Path

def setup_folders():
    """Create necessary folders"""
    Path("strings").mkdir(exist_ok=True)
    Path("accounts").mkdir(exist_ok=True)
    print("✅ Folders created")

def parse_session_string(session_string):
    """Parse Telegram string session"""
    try:
        # Remove version prefix
        if session_string.startswith('1') or session_string.startswith('2'):
            data = session_string[1:]
        else:
            data = session_string
        
        # Fix base64 padding
        padding = 4 - len(data) % 4
        if padding != 4:
            data += "=" * padding
        
        # Decode
        decoded = base64.urlsafe_b64decode(data)
        
        # Parse binary structure
        idx = 0
        dc_id = struct.unpack('<i', decoded[idx:idx+4])[0]
        idx += 4
        ip_len = struct.unpack('<i', decoded[idx:idx+4])[0]
        idx += 4
        ip = decoded[idx:idx+ip_len].decode('ascii', errors='ignore')
        idx += ip_len
        port = struct.unpack('<i', decoded[idx:idx+4])[0]
        idx += 4
        auth_key = decoded[idx:]
        
        return {
            'dc_id': dc_id,
            'ip': ip,
            'port': port,
            'auth_key': auth_key
        }
    except Exception as e:
        print(f"Parse error: {e}")
        return None

def create_sqlite_session(session_data, api_id, api_hash):
    """Create SQLite session file"""
    try:
        filename = f"accounts/{api_id}.session"
        
        # Connect to SQLite database
        conn = sqlite3.connect(filename)
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute('CREATE TABLE IF NOT EXISTS sessions (dc_id INTEGER PRIMARY KEY, server_address TEXT, port INTEGER, auth_key BLOB, takeout_id INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS version (version INTEGER PRIMARY KEY)')
        cursor.execute('CREATE TABLE IF NOT EXISTS entities (id INTEGER PRIMARY KEY, hash INTEGER NOT NULL, username TEXT, phone INTEGER, name TEXT, date INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS sent_files (md5_digest BLOB PRIMARY KEY, file_size INTEGER, type INTEGER, id INTEGER, hash INTEGER)')
        cursor.execute('CREATE TABLE IF NOT EXISTS update_state (id INTEGER PRIMARY KEY, pts INTEGER, qts INTEGER, date INTEGER, seq INTEGER)')
        
        # Clear old data
        cursor.execute('DELETE FROM sessions')
        cursor.execute('DELETE FROM version')
        
        # Insert data
        cursor.execute('INSERT INTO version (version) VALUES (7)')
        cursor.execute('INSERT INTO sessions (dc_id, server_address, port, auth_key) VALUES (?, ?, ?, ?)',
                      (session_data['dc_id'], session_data['ip'], session_data['port'], session_data['auth_key']))
        
        conn.commit()
        conn.close()
        
        print(f"✅ Created: {filename}")
        print(f"   DC: {session_data['dc_id']}, Server: {session_data['ip']}:{session_data['port']}")
        
        # Save API info
        with open(f"accounts/{api_id}.txt", 'w') as f:
            f.write(f"API ID: {api_id}\n")
            f.write(f"API Hash: {api_hash}\n")
            f.write(f"DC ID: {session_data['dc_id']}\n")
            f.write(f"Server: {session_data['ip']}:{session_data['port']}\n")
        
        return True
    except Exception as e:
        print(f"❌ SQLite error: {e}")
        return False

def convert_file(filepath):
    """Convert a text file with sessions"""
    print(f"\n📄 Processing: {filepath.name}")
    print("-" * 50)
    
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            lines = [line.strip() for line in f if line.strip()]
        
        if len(lines) < 3:
            print("Not enough data")
            return 0, 0
        
        success = 0
        total = 0
        
        for i in range(0, len(lines), 3):
            if i + 2 >= len(lines):
                break
            
            api_id = lines[i]
            api_hash = lines[i+1]
            session_string = lines[i+2]
            
            # Basic validation
            if not api_id.isdigit():
                continue
            if len(api_hash) != 32:
                continue
            if len(session_string) < 100:
                continue
            
            total += 1
            print(f"\nSession {total}: API {api_id}")
            
            # Parse session
            session_data = parse_session_string(session_string)
            if not session_data:
                print("  ❌ Failed to parse")
                continue
            
            # Create SQLite file
            if create_sqlite_session(session_data, api_id, api_hash):
                success += 1
        
        print(f"\n📊 Result: {success}/{total} sessions converted")
        return success, total
        
    except Exception as e:
        print(f"❌ File error: {e}")
        return 0, 0

def main():
    """Main function"""
    print("=" * 60)
    print("TELEGRAM SESSION CONVERTER")
    print("=" * 60)
    
    # Setup
    setup_folders()
    
    # Find text files
    text_files = list(Path("strings").glob("*.txt")) + list(Path("strings").glob("*.text"))
    
    if not text_files:
        print("\n❌ No text files found in 'strings/' folder!")
        print("\nCreate a file like 'strings/sessions.txt' with this format:")
        print("""
39357850
ad4559302ff6ea47c20f0d42b32099c1
1BVtsOGQBu6l1_-ltRTAXvVm3NIBgwx6nHIE4TS9hIVt3zvMM_K_RT4Pe10r3dvJTdLI10z5uhjQWlxwmfvX90Z6oZzTKxJBo2Lnzt06kA068m5TmJNi27j_Fchjs_ccUPfT6-iqoWCNYd261ijkwcg2_0JB5VtCYvJeKVTTw4OjJkPiM8EuMFv8Rzmvm7ZdYYGzfeCgbt9Dr4WxVbf3Qj7bhono5Uj-OduH_jvjtHyTVhjX-y8HoxdB0GywnC0MOqNz5BafVBuKvmSRLi_nehzt2ChzMF0kTEvCHhI531gfKs5hrn74g70wgrGnx2Lljp-JwJk3--YzT8oWlw33LfZnBjIt2bws=
        """)
        return
    
    total_success = 0
    total_sessions = 0
    
    # Process each file
    for filepath in text_files:
        success, sessions = convert_file(filepath)
        total_success += success
        total_sessions += sessions
        
        # Move processed file
        archive_dir = Path("strings/processed")
        archive_dir.mkdir(exist_ok=True)
        filepath.rename(archive_dir / filepath.name)
    
    # Create test script
    create_test_script()
    
    print("\n" + "=" * 60)
    print("✅ CONVERSION COMPLETE!")
    print("=" * 60)
    print(f"\n📊 Total: {total_success}/{total_sessions} sessions converted")
    print(f"\n📁 Session files saved in: accounts/")
    print(f"\n🔧 Next steps:")
    print("   1. Install Telethon: pip install telethon")
    print("   2. Test sessions: python test_sessions.py")
    print(f"\n💡 Each session has a .txt file with API credentials")

def create_test_script():
    """Create script to test sessions"""
    script = '''#!/usr/bin/env python3
import os
import sqlite3
import glob

def test_sessions():
    print("Testing Telegram Session Files")
    print("="*50)
    
    session_files = glob.glob("accounts/*.session")
    
    if not session_files:
        print("No session files found!")
        return
    
    print(f"Found {len(session_files)} session file(s)")
    
    valid = 0
    invalid = 0
    
    for session_file in session_files:
        print(f"\n{session_file}:")
        
        try:
            conn = sqlite3.connect(session_file)
            cursor = conn.cursor()
            
            # Check tables
            cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
            tables = [row[0] for row in cursor.fetchall()]
            
            if 'sessions' in tables and 'version' in tables:
                cursor.execute("SELECT dc_id, server_address, port FROM sessions")
                session_data = cursor.fetchone()
                
                if session_data:
                    print(f"  ✅ Valid (DC: {session_data[0]}, Server: {session_data[1]})")
                    valid += 1
                else:
                    print(f"  ❌ No session data")
                    invalid += 1
            else:
                print(f"  ❌ Missing tables")
                invalid += 1
            
            conn.close()
            
        except Exception as e:
            print(f"  ❌ Error: {e}")
            invalid += 1
    
    print(f"\n" + "="*50)
    print(f"RESULTS: {valid} valid, {invalid} invalid")
    print("="*50)

if __name__ == "__main__":
    test_sessions()
'''
    
    with open("test_sessions.py", "w") as f:
        f.write(script)
    
    print("\n📜 Test script created: test_sessions.py")

if __name__ == "__main__":
    main()