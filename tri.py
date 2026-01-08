
Then run: <code>python3 -c "from tri import load_sessions_from_file; load_sessions_from_file('sessions.txt')"</code>
"""
     
     keyboard = [
         [InlineKeyboardButton("🔙 Back", callback_data="add_session_options"),
          InlineKeyboardButton("📝 Example File", callback_data="show_example")]
     ]
     
     await query.edit_message_text(
         instructions,
         reply_markup=InlineKeyboardMarkup(keyboard),
         parse_mode='HTML'
     )
 
 elif data.startswith("list_sessions_"):
     page = int(data.split("_")[-1])
     await query.edit_message_text(
         f"<b>📋 Sessions (Page {page+1})</b>",
         reply_markup=create_session_keyboard(page),
         parse_mode='HTML'
     )
 
 elif data.startswith("session_"):
     session_name = data.split("_", 1)[1]
     session = state.sessions.get(session_name)
     
     if session:
         text = f"""
<b>👤 Session Control: {session_name}</b>

<b>Status:</b> {session.status.upper()}
<b>Phone:</b> {session.phone or 'Not set'}
<b>Last Active:</b> {session.last_active.strftime('%Y-%m-%d %H:%M:%S')}

<b>📊 Statistics:</b>
├─ Messages Sent: {session.stats['messages_sent']:,}
├─ Groups Processed: {session.stats['groups_processed']:,}
├─ Errors: {session.stats['errors']:,}
└─ Uptime: {datetime.now() - session.stats['start_time']}

<b>⚙️ Settings:</b>
├─ Active: {'✅' if session.settings['active'] else '❌'}
├─ Auto Reply: {'✅' if session.settings['auto_reply'] else '❌'}
├─ Forward Messages: {'✅' if session.settings['forward_messages'] else '❌'}
└─ Auto Profile: {'✅' if session.settings['change_profile'] else '❌'}
"""
     else:
         text = f"<b>❌ Session {session_name} not found!</b>"
     
     await query.edit_message_text(
         text,
         reply_markup=create_session_control_keyboard(session_name),
         parse_mode='HTML'
     )
 
 elif data.startswith("delete_"):
     session_name = data.split("_", 1)[1]
     
     if session_name in state.sessions:
         # Stop if running
         if session_name in state.active_tasks:
             await stop_session(session_name)
         
         # Delete from memory
         del state.sessions[session_name]
         
         # Delete from disk
         await save_sessions()
         
         await query.edit_message_text(
             f"<b>🗑️ Session '{session_name}' deleted!</b>",
             parse_mode='HTML'
         )
         await broadcast_to_admins(f"🗑️ Session deleted: <b>{session_name}</b>")
     else:
         await query.edit_message_text(
             f"<b>❌ Session '{session_name}' not found!</b>",
             parse_mode='HTML'
         )
 
 elif data.startswith("settings_"):
     session_name = data.split("_", 1)[1]
     await query.edit_message_text(
         f"<b>⚙️ Settings for {session_name}</b>\nToggle options:",
         reply_markup=create_settings_keyboard(session_name),
         parse_mode='HTML'
     )
 
 elif data.startswith("toggle_"):
     # Handle toggle actions
     parts = data.split("_")
     action = parts[1]
     session_name = parts[2]
     
     session = state.sessions.get(session_name)
     if session:
         if action == "autoreply":
             session.settings['auto_reply'] = not session.settings['auto_reply']
         elif action == "forward":
             session.settings['forward_messages'] = not session.settings['forward_messages']
         elif action == "active":
             session.settings['active'] = not session.settings['active']
         elif action == "profile":
             session.settings['change_profile'] = not session.settings['change_profile']
         
         await save_sessions()
         await query.edit_message_text(
             f"<b>✅ Setting updated for {session_name}</b>",
             reply_markup=create_settings_keyboard(session_name),
             parse_mode='HTML'
         )
 
 elif data.startswith("set_"):
     # Handle set actions (firstname, lastname, bio, photo)
     parts = data.split("_")
     action = parts[1]
     session_name = parts[2]
     
     context.user_data['awaiting_input'] = {
         'type': action,
         'session': session_name
     }
     
     prompts = {
         'firstname': "Send the new FIRST NAME:",
         'lastname': "Send the new LAST NAME:",
         'bio': "Send the new BIO (max 70 chars):",
         'photo': "Send a PHOTO (as document or image):"
     }
     
     await query.edit_message_text(
         f"<b>✏️ Set {action.upper()} for {session_name}</b>\n\n{prompts.get(action, 'Send input:')}",
         parse_mode='HTML'
     )
 
 elif data == "bulk_actions":
     await query.edit_message_text(
         "<b>🚀 Bulk Actions Control</b>\nSelect an action:",
         reply_markup=create_bulk_actions_keyboard(),
         parse_mode='HTML'
     )
 
 elif data.startswith("bulk_"):
     # Handle bulk actions
     parts = data.split("_")
     action = parts[1]
     
     if action in ["start", "stop"] and len(parts) == 4:
         start_range = int(parts[2])
         end_range = int(parts[3])
         
         # Filter sessions in range
         sessions_to_act = []
         for i in range(start_range, end_range + 1):
             session_name = f"session{i}"
             if session_name in state.sessions:
                 sessions_to_act.append(session_name)
         
         if action == "start":
             # Start sessions
             for session_name in sessions_to_act:
                 await start_session(session_name)
             msg = f"Started sessions {start_range}-{end_range}"
         else:
             # Stop sessions
             for session_name in sessions_to_act:
                 await stop_session(session_name)
             msg = f"Stopped sessions {start_range}-{end_range}"
         
         await query.edit_message_text(
             f"<b>✅ {msg}</b>\nAffected: {len(sessions_to_act)} sessions",
             parse_mode='HTML'
         )
     
     elif action == "rename":
         context.user_data['awaiting_input'] = {
             'type': 'bulk_rename',
             'pattern': 'session{number}'
         }
         await query.edit_message_text(
             "<b>✏️ Batch Rename</b>\nSend new name pattern (use {number} for index):\nExample: account_{number}_vps",
             parse_mode='HTML'
         )
     
     elif action == "bio":
         context.user_data['awaiting_input'] = {
             'type': 'bulk_bio'
         }
         await query.edit_message_text(
             "<b>📝 Set Bio for All Sessions</b>\nSend the bio text to apply to all sessions:",
             parse_mode='HTML'
         )
 
 elif data == "dashboard":
     await stats_command(update, context)
 
 elif data == "refresh_all":
     await refresh_all_sessions()
     await query.edit_message_text(
         "<b>🔄 Refreshing all sessions...</b>",
         parse_mode='HTML'
     )
 
 elif data.startswith("restart_"):
     session_name = data.split("_", 1)[1]
     await restart_session(session_name)
     await query.edit_message_text(
         f"<b>🔄 Restarting {session_name}...</b>",
         parse_mode='HTML'
     )
 
 elif data.startswith("stop_"):
     session_name = data.split("_", 1)[1]
     await stop_session(session_name)
     await query.edit_message_text(
         f"<b>⏹️ Stopped {session_name}</b>",
         parse_mode='HTML'
     )
 
 elif data == "system_stats":
     await stats_command(update, context)

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Handle regular messages for input"""
 user_data = context.user_data
 
 if 'adding_session' in user_data and user_data.get('method') == 'bot':
     # Handle interactive session addition via bot
     await handle_session_creation_bot(update, context)
     return
 
 if 'awaiting_input' in user_data:
     input_type = user_data['awaiting_input']['type']
     session_name = user_data['awaiting_input'].get('session')
     
     if input_type in ['firstname', 'lastname', 'bio']:
         text = update.message.text
         session = state.sessions.get(session_name)
         
         if session:
             if input_type == 'firstname':
                 session.settings['first_name'] = text
             elif input_type == 'lastname':
                 session.settings['last_name'] = text
             elif input_type == 'bio':
                 session.settings['bio'] = text
             
             await save_sessions()
             
             # Apply changes if session is online
             if session.client and session.status == "online":
                 await apply_profile_changes(session)
             
             await update.message.reply_text(
                 f"<b>✅ {input_type.upper()} updated for {session_name}</b>",
                 parse_mode='HTML'
             )
     
     elif input_type == 'photo':
         # Handle photo upload
         if update.message.photo:
             photo_file = await update.message.photo[-1].get_file()
             photo_bytes = await photo_file.download_as_bytearray()
             
             session = state.sessions.get(session_name)
             if session:
                 session.settings['profile_photo'] = base64.b64encode(photo_bytes).decode()
                 await save_sessions()
                 
                 if session.client and session.status == "online":
                     await apply_profile_changes(session)
                 
                 await update.message.reply_text(
                     f"<b>✅ Profile photo updated for {session_name}</b>",
                     parse_mode='HTML'
                 )
     
     elif input_type == 'bulk_rename':
         pattern = update.message.text
         # Rename sessions based on pattern
         for i, (old_name, session) in enumerate(list(state.sessions.items()), 1):
             new_name = pattern.replace('{number}', str(i))
             state.sessions[new_name] = session
             if old_name in state.active_tasks:
                 state.active_tasks[new_name] = state.active_tasks.pop(old_name)
             del state.sessions[old_name]
             session.name = new_name
         
         await save_sessions()
         await update.message.reply_text(
             f"<b>✅ Renamed all sessions</b>\nNew pattern: {pattern}",
             parse_mode='HTML'
         )
     
     elif input_type == 'bulk_bio':
         bio_text = update.message.text
         # Apply bio to all sessions
         for session in state.sessions.values():
             session.settings['bio'] = bio_text
             if session.client and session.status == "online":
                 await apply_profile_changes(session)
         
         await save_sessions()
         await update.message.reply_text(
             f"<b>✅ Bio applied to all sessions</b>",
             parse_mode='HTML'
         )
     
     del user_data['awaiting_input']
 
 # Check if it's a command to add session via script format
 elif update.message.text and "|" in update.message.text and len(update.message.text.split("|")) == 4:
     # Format: session_name|api_id|api_hash|string_session
     parts = update.message.text.split("|")
     session_name = parts[0].strip()
     api_id = parts[1].strip()
     api_hash = parts[2].strip()
     string_session = parts[3].strip()
     
     try:
         # Create session
         session_info = SessionInfo(
             name=session_name,
             api_id=int(api_id),
             api_hash=api_hash,
             string_session=string_session
         )
         
         state.sessions[session_name] = session_info
         await save_sessions()
         
         keyboard = InlineKeyboardMarkup([[
             InlineKeyboardButton("🚀 Start", callback_data=f"start_{session_name}"),
             InlineKeyboardButton("⚙️ Settings", callback_data=f"settings_{session_name}")
         ]])
         
         await update.message.reply_text(
             f"<b>✅ Session '{session_name}' added via script format!</b>",
             reply_markup=keyboard,
             parse_mode='HTML'
         )
         
     except Exception as e:
         await update.message.reply_text(
             f"<b>❌ Error adding session: {str(e)}</b>",
             parse_mode='HTML'
         )

async def handle_session_creation_bot(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Handle multi-step session creation via bot"""
 step = context.user_data.get('session_step')
 user_data = context.user_data
 
 if step == 'name':
     user_data['new_session'] = {'name': update.message.text}
     user_data['session_step'] = 'api_id'
     await update.message.reply_text("Send API ID:")
 
 elif step == 'api_id':
     try:
         user_data['new_session']['api_id'] = int(update.message.text)
         user_data['session_step'] = 'api_hash'
         await update.message.reply_text("Send API Hash:")
     except ValueError:
         await update.message.reply_text("Invalid API ID. Send number:")
 
 elif step == 'api_hash':
     user_data['new_session']['api_hash'] = update.message.text
     user_data['session_step'] = 'string_session'
     await update.message.reply_text("Send String Session:")
 
 elif step == 'string_session':
     session_data = user_data['new_session']
     session_data['string_session'] = update.message.text
     
     # Create and save session
     session_name = session_data['name']
     session_info = SessionInfo(
         name=session_name,
         api_id=session_data['api_id'],
         api_hash=session_data['api_hash'],
         string_session=session_data['string_session']
     )
     
     state.sessions[session_name] = session_info
     await save_sessions()
     
     # Clear temp data
     del user_data['adding_session']
     del user_data['session_step']
     del user_data['new_session']
     del user_data['method']
     
     keyboard = InlineKeyboardMarkup([[
         InlineKeyboardButton("🚀 Start Now", callback_data=f"start_{session_name}"),
         InlineKeyboardButton("⚙️ Configure", callback_data=f"settings_{session_name}"),
         InlineKeyboardButton("📋 Sessions List", callback_data="list_sessions_0")
     ]])
     
     await update.message.reply_text(
         f"<b>✅ Session '{session_name}' added via BOT!</b>",
         reply_markup=keyboard,
         parse_mode='HTML'
     )

# ====== SESSION MANAGEMENT FUNCTIONS ======
async def start_session(session_name: str):
 """Start a session"""
 if session_name in state.active_tasks:
     return
 
 session = state.sessions.get(session_name)
 if not session:
     return
 
 task = asyncio.create_task(run_session_worker(session))
 state.active_tasks[session_name] = task
 session.status = "starting"
 
 await broadcast_to_admins(f"🚀 Starting session: <b>{session_name}</b>")

async def stop_session(session_name: str):
 """Stop a session"""
 if session_name in state.active_tasks:
     task = state.active_tasks[session_name]
     task.cancel()
     del state.active_tasks[session_name]
 
 session = state.sessions.get(session_name)
 if session:
     session.status = "offline"
     if session.client:
         try:
             await session.client.disconnect()
         except:
             pass
 
 await broadcast_to_admins(f"⏹️ Stopped session: <b>{session_name}</b>")

async def restart_session(session_name: str):
 """Restart a session"""
 await stop_session(session_name)
 await asyncio.sleep(2)
 await start_session(session_name)

async def refresh_all_sessions():
 """Refresh all sessions"""
 for session_name in list(state.active_tasks.keys()):
     await restart_session(session_name)

async def apply_profile_changes(session: SessionInfo):
 """Apply profile changes to Telegram account"""
 if not session.client or session.status != "online":
     return
 
 try:
     settings = session.settings
     
     # Update name if changed
     if settings['first_name'] or settings['last_name']:
         await session.client(functions.account.UpdateProfileRequest(
             first_name=settings['first_name'] or "",
             last_name=settings['last_name'] or ""
         ))
     
     # Update bio if changed
     if settings['bio']:
         await session.client(functions.account.UpdateProfileRequest(
             about=settings['bio']
         ))
     
     # Update profile photo if changed
     if settings['profile_photo']:
         photo_bytes = base64.b64decode(settings['profile_photo'])
         file = await session.client.upload_file(photo_bytes)
         await session.client(functions.photos.UploadProfilePhotoRequest(file=file))
     
 except Exception as e:
     print(f"{Fore.RED}Profile update error for {session.name}: {e}")

# ====== SESSION WORKER ======
async def run_session_worker(session: SessionInfo):
 """Main worker for a session"""
 try:
     session.status = "connecting"
     
     # Create optimized client
     client = HighSpeedTelegramClient(session)
     
     # Connect
     await client.connect()
     
     if not await client.is_user_authorized():
         session.status = "unauthorized"
         await broadcast_to_admins(f"❌ Session <b>{session.name}</b> not authorized")
         return
     
     # Get phone number
     me = await client.get_me()
     session.phone = me.phone or ""
     session.status = "online"
     
     # Apply profile settings
     if session.settings['change_profile']:
         await apply_profile_changes(session)
     
     # Setup auto-reply
     if session.settings['auto_reply']:
         @client.on(events.NewMessage(incoming=True))
         async def auto_reply_handler(event):
             if event.is_private and not event.out:
                 try:
                     await event.reply(AppConfig.AUTO_REPLY_MSG)
                     session.stats['messages_sent'] += 1
                 except:
                     pass
     
     await broadcast_to_admins(f"✅ Session <b>{session.name}</b> online ({me.phone or me.username})")
     
     # Main loop
     while session.settings['active'] and session.status == "online":
         try:
             # Check if forwarding is enabled
             if session.settings['forward_messages']:
                 # Get target message
                 try:
                     entity = await client.get_input_entity(AppConfig.TARGET_USER)
                     messages = await client.get_messages(entity, limit=1)
                     message = messages[0] if messages else None
                 except:
                     message = None
                 
                 if message:
                     # Get groups
                     groups = []
                     async for dialog in client.iter_dialogs(limit=200):
                         if dialog.is_group:
                             groups.append(dialog.entity)
                     
                     if groups:
                         # Process groups with YOUR EXACT DELAYS
                         for group in groups:
                             start_time = datetime.now()
                             
                             try:
                                 await client.send_message(group, message)
                                 session.stats['messages_sent'] += 1
                                 session.stats['groups_processed'] += 1
                                 print(f"{Fore.GREEN}[{session.name}] Sent to group")
                             except (ChannelPrivateError, ChatWriteForbiddenError):
                                 pass
                             except FloodWaitError as e:
                                 await asyncio.sleep(e.seconds)
                             except:
                                 session.stats['errors'] += 1
                             
                             # YOUR EXACT DELAY CALCULATION
                             elapsed = (datetime.now() - start_time).total_seconds()
                             delay = random.uniform(AppConfig.MIN_DELAY, AppConfig.MAX_DELAY)
                             remaining_delay = max(0, delay - elapsed)
                             
                             if remaining_delay > 0:
                                 await asyncio.sleep(remaining_delay)
             
             # Cycle delay
             for i in range(AppConfig.CYCLE_DELAY // 30):
                 if not session.settings['active']:
                     break
                 await asyncio.sleep(30)
             
             # Update last active
             session.last_active = datetime.now()
             
         except Exception as e:
             print(f"{Fore.RED}[{session.name}] Worker error: {e}")
             await asyncio.sleep(60)
     
 except Exception as e:
     session.status = "error"
     print(f"{Fore.RED}[{session.name}] Critical error: {e}")
 finally:
     if 'client' in locals():
         try:
             await client.disconnect()
         except:
             pass
     session.status = "offline"
     if session.name in state.active_tasks:
         del state.active_tasks[session.name]

# ====== DATA PERSISTENCE ======
async def save_sessions():
 """Save all sessions to disk"""
 os.makedirs(AppConfig.CREDENTIALS_FOLDER, exist_ok=True)
 
 data = {}
 for name, session in state.sessions.items():
     data[name] = {
         'api_id': session.api_id,
         'api_hash': session.api_hash,
         'string_session': session.string_session,
         'phone': session.phone,
         'settings': session.settings,
         'stats': {
             'messages_sent': session.stats['messages_sent'],
             'groups_processed': session.stats['groups_processed'],
             'errors': session.stats['errors'],
             'start_time': session.stats['start_time'].isoformat()
         }
     }
 
 with open(os.path.join(AppConfig.CREDENTIALS_FOLDER, AppConfig.SESSIONS_DB), 'w') as f:
     json.dump(data, f, indent=2)

async def load_sessions():
 """Load sessions from disk"""
 path = os.path.join(AppConfig.CREDENTIALS_FOLDER, AppConfig.SESSIONS_DB)
 
 if os.path.exists(path):
     with open(path, 'r') as f:
         data = json.load(f)
     
     for name, session_data in data.items():
         session = SessionInfo(
             name=name,
             api_id=session_data['api_id'],
             api_hash=session_data['api_hash'],
             string_session=session_data['string_session'],
             phone=session_data.get('phone', ''),
             settings=session_data.get('settings', {}),
             stats={
                 'messages_sent': session_data['stats']['messages_sent'],
                 'groups_processed': session_data['stats']['groups_processed'],
                 'errors': session_data['stats']['errors'],
                 'start_time': datetime.fromisoformat(session_data['stats']['start_time'])
             }
         )
         state.sessions[name] = session

async def save_config():
 """Save bot configuration"""
 config = {
     'admin_ids': BotConfig.ADMIN_IDS,
     'log_channel': BotConfig.LOG_CHANNEL
 }
 
 with open(AppConfig.CONFIG_FILE, 'w') as f:
     json.dump(config, f)

async def load_config():
 """Load bot configuration"""
 if os.path.exists(AppConfig.CONFIG_FILE):
     with open(AppConfig.CONFIG_FILE, 'r') as f:
         config = json.load(f)
     
     BotConfig.ADMIN_IDS = config.get('admin_ids', [])
     BotConfig.LOG_CHANNEL = config.get('log_channel')

# ====== OLD SCRIPT COMPATIBILITY ======
async def add_session_script_style():
 """Add sessions the old script way (for backward compatibility)"""
 print(f"\n{Fore.CYAN}{'='*50}")
 print(f"{Fore.GREEN}📝 ADD SESSIONS (SCRIPT STYLE)")
 print(f"{Fore.CYAN}{'='*50}")
 
 try:
     num_sessions = int(input("Enter number of sessions: "))
     if num_sessions < 1:
         raise ValueError("At least 1 session required")
     
     for i in range(1, num_sessions + 1):
         session_name = f"session{i}"
         
         # Check if already exists
         if session_name in state.sessions:
             print(f"{Fore.YELLOW}Session {session_name} already exists. Skipping...")
             continue
         
         print(f"\n{Fore.CYAN}Configuring {session_name}:")
         
         try:
             api_id = int(input("API ID: "))
             api_hash = input("API Hash: ")
             string_session = input("String Session: ")
             
             session_info = SessionInfo(
                 name=session_name,
                 api_id=api_id,
                 api_hash=api_hash,
                 string_session=string_session
             )
             
             state.sessions[session_name] = session_info
             print(f"{Fore.GREEN}✅ Session {session_name} added!")
             
         except ValueError:
             print(f"{Fore.RED}Invalid input for session {session_name}. Skipping...")
             continue
     
     await save_sessions()
     print(f"\n{Fore.GREEN}✅ All sessions saved! Total: {len(state.sessions)}")
     
     # Ask to start sessions
     start_now = input(f"\n{Fore.YELLOW}Start all sessions now? (y/n): ").lower()
     if start_now == 'y':
         print(f"{Fore.GREEN}🚀 Starting all sessions...")
         for session_name in state.sessions.keys():
             await start_session(session_name)
             await asyncio.sleep(1)  # Stagger starts
     
     print(f"\n{Fore.GREEN}✅ Script-style session addition complete!")
     print(f"{Fore.YELLOW}You can now control sessions via the bot or script.")
     
 except (ValueError, KeyboardInterrupt):
     print(f"\n{Fore.YELLOW}Operation cancelled")
 except Exception as e:
     print(f"{Fore.RED}Error: {e}")

def load_sessions_from_file(filename: str = "sessions.txt"):
 """Load sessions from a text file (compatibility function)"""
 try:
     if not os.path.exists(filename):
         print(f"{Fore.RED}File {filename} not found!")
         return
     
     with open(filename, 'r') as f:
         lines = f.readlines()
     
     added = 0
     for line in lines:
         line = line.strip()
         if not line or line.startswith('#'):
             continue
         
         if "|" in line:
             parts = line.split("|")
             if len(parts) >= 4:
                 session_name = parts[0].strip()
                 api_id = parts[1].strip()
                 api_hash = parts[2].strip()
                 string_session = parts[3].strip()
                 
                 try:
                     session_info = SessionInfo(
                         name=session_name,
                         api_id=int(api_id),
                         api_hash=api_hash,
                         string_session=string_session
                     )
                     
                     state.sessions[session_name] = session_info
                     added += 1
                     print(f"{Fore.GREEN}Loaded: {session_name}")
                 except:
                     print(f"{Fore.RED}Failed to load line: {line}")
     
     # Save to database
     asyncio.run(save_sessions())
     print(f"{Fore.GREEN}✅ Loaded {added} sessions from file!")
     
 except Exception as e:
     print(f"{Fore.RED}Error loading from file: {e}")

# ====== SYSTEM MONITOR ======
async def system_monitor():
 """Monitor system and send alerts"""
 while True:
     try:
         sys_stats = get_system_stats()
         
         # Check for issues
         if sys_stats['cpu'] > 90:
             await broadcast_to_admins(f"⚠️ <b>High CPU Usage:</b> {sys_stats['cpu']:.1f}%")
         
         if sys_stats['memory_used'] > 85:
             await broadcast_to_admins(f"⚠️ <b>High Memory Usage:</b> {sys_stats['memory_used']:.1f}%")
         
         # Update performance stats
         online_sessions = sum(1 for s in state.sessions.values() if s.status == "online")
         state.performance_stats.update({
             'active_sessions': online_sessions,
             'total_sessions': len(state.sessions),
             'cpu_usage': sys_stats['cpu'],
             'memory_usage': sys_stats['memory_used']
         })
         
     except Exception as e:
         print(f"{Fore.RED}Monitor error: {e}")
     
     await asyncio.sleep(60)

# ====== MAIN FUNCTIONS ======
async def initialize_bot():
 """Initialize Telegram bot"""
 print(f"{Fore.GREEN}🤖 Initializing Control Bot...")
 
 # Create application
 app = Application.builder().token(BotConfig.TOKEN).build()
 state.bot_app = app
 
 # Add handlers
 app.add_handler(CommandHandler("start", start_command))
 app.add_handler(CommandHandler("sessions", sessions_command))
 app.add_handler(CommandHandler("stats", stats_command))
 app.add_handler(CommandHandler("bulk", bulk_command))
 app.add_handler(CommandHandler("tools", tools_command))
 app.add_handler(CommandHandler("help", help_command))
 
 app.add_handler(CallbackQueryHandler(button_callback))
 app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
 app.add_handler(MessageHandler(filters.PHOTO, handle_message))
 app.add_handler(MessageHandler(filters.Document.IMAGE, handle_message))
 
 # Add error handler
 app.add_error_handler(error_handler)
 
 # Start polling
 await app.initialize()
 await app.start()
 await app.updater.start_polling()
 
 print(f"{Fore.GREEN}✅ Control Bot Ready!")
 
 # Send startup message
 startup_msg = f"""
<b>🚀 ORBIT ADBOT VPS ULTIMATE STARTED</b>

<b>Server:</b> {os.uname().nodename}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
<b>Sessions:</b> {len(state.sessions)} loaded
<b>Status:</b> Operational

<b>VPS Specifications:</b>
• CPU Cores: {psutil.cpu_count()}
• RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB
• Network: 3-5 Gbps Optimized

<b>Access Methods:</b>
1. Use /start in bot
2. Run script-style: Just run the script
3. Import from file: sessions.txt

Use /start to begin.
"""
 
 for admin_id in BotConfig.ADMIN_IDS:
     await send_bot_message(admin_id, startup_msg)
 
 return app

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
 """Handle errors"""
 print(f"{Fore.RED}BOT ERROR: {context.error}")
 try:
     if update and update.effective_chat:
         await context.bot.send_message(
             chat_id=update.effective_chat.id,
             text="❌ An error occurred. Please try again."
         )
 except:
     pass

async def main():
 """Main function"""
 print(f"{Fore.CYAN}{'='*60}")
 print(f"{Fore.GREEN}🚀 ORBIT ADBOT - VPS ULTIMATE EDITION")
 print(f"{Fore.YELLOW}📱 BOT + SCRIPT COMBINATION")
 print(f"{Fore.CYAN}{'='*60}")
 
 # Load configuration
 await load_config()
 await load_sessions()
 
 print(f"{Fore.GREEN}📊 Loaded {len(state.sessions)} sessions")
 
 # Show menu
 print(f"\n{Fore.CYAN}Select mode:")
 print(f"{Fore.GREEN}1. 🤖 Bot Mode (Control via Telegram)")
 print(f"{Fore.GREEN}2. 📝 Script Mode (Add sessions old way)")
 print(f"{Fore.GREEN}3. 🔄 Both (Run bot + add sessions)")
 print(f"{Fore.GREEN}4. 📁 Load from file (sessions.txt)")
 
 try:
     choice = input(f"\n{Fore.YELLOW}Enter choice (1-4): ").strip()
     
     if choice in ['1', '3']:
         # Start bot
         bot_task = asyncio.create_task(initialize_bot())
     
     if choice in ['2', '3']:
         # Add sessions script style
         await add_session_script_style()
     
     if choice == '4':
         # Load from file
         load_sessions_from_file()
         print(f"{Fore.GREEN}✅ Sessions loaded! Starting bot...")
         bot_task = asyncio.create_task(initialize_bot())
     
     if choice not in ['1', '2', '3', '4']:
         print(f"{Fore.YELLOW}Starting in default mode (Bot + Script)...")
         bot_task = asyncio.create_task(initialize_bot())
         await add_session_script_style()
     
     # Start system monitor
     monitor_task = asyncio.create_task(system_monitor())
     
     # Auto-start sessions marked as active
     auto_start_count = 0
     for session_name, session in state.sessions.items():
         if session.settings.get('active', False):
             await start_session(session_name)
             auto_start_count += 1
             await asyncio.sleep(0.5)  # Stagger starts
     
     if auto_start_count > 0:
         print(f"{Fore.GREEN}🚀 Auto-started {auto_start_count} sessions")
     
     print(f"\n{Fore.GREEN}✅ System ready!")
     print(f"{Fore.YELLOW}Press Ctrl+C to stop")
     
     # Keep running
     try:
         tasks = []
         if 'bot_task' in locals():
             tasks.append(bot_task)
         tasks.append(monitor_task)
         
         await asyncio.gather(*tasks)
     except KeyboardInterrupt:
         print(f"\n{Fore.YELLOW}Shutting down...")
 
 except KeyboardInterrupt:
     print(f"\n{Fore.YELLOW}Process interrupted")
 finally:
     # Cleanup
     for session_name in list(state.active_tasks.keys()):
         await stop_session(session_name)
     
     if state.bot_app:
         try:
             await state.bot_app.stop()
         except:
             pass
     
     await save_sessions()
     print(f"{Fore.GREEN}Clean shutdown complete.")

if __name__ == "__main__":
 # Performance optimizations
 if hasattr(asyncio, 'WindowsProactorEventLoopPolicy') and sys.platform == 'win32':
     asyncio.set_event_loop_policy(asyncio.WindowsProactorEventLoopPolicy())
 
 # Run main function
 try:
     asyncio.run(main())
 except KeyboardInterrupt:
     print(f"\n{Fore.YELLOW}Process interrupted by user")
 except Exception as e:
     print(f"{Fore.RED}Fatal error: {e}")
     import traceback
     traceback.print_exc()
