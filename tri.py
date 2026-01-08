#!/usr/bin/env python3
"""
ORBIT ADBOT - ULTIMATE VPS EDITION WITH FULL-CONTROL BOT
Optimized for 3-5 Gbps VPS with complete Telegram bot management interface
"""

import asyncio
import os
import json
import random
import logging
import socket
import time
import sys
import uuid
import hashlib
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
from enum import Enum

from telethon import TelegramClient, events, types
from telethon.sessions import StringSession
from telethon.tl import functions, types as tl_types
from telethon.errors import (
    UserDeactivatedBanError, FloodWaitError, ChannelPrivateError,
    ChatWriteForbiddenError, PeerIdInvalidError, RPCError,
    SessionPasswordNeededError, PhoneNumberInvalidError
)

from colorama import init, Fore, Style
from datetime import datetime, timedelta
import aiohttp
import psutil
from concurrent.futures import ThreadPoolExecutor
import uvloop
import qrcode
from io import BytesIO
import base64

# ====== BOT INTEGRATION ======
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    ReplyKeyboardMarkup, KeyboardButton, InputFile
)
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    ContextTypes, filters, ConversationHandler
)

# ====== FORCE PERFORMANCE OPTIMIZATION ======
if sys.platform != 'win32':
    try:
        uvloop.install()
        print(f"{Fore.GREEN}UVLOOP ENABLED - 4X PERFORMANCE BOOST")
    except:
        pass

# ====== GLOBAL CONFIGURATION ======
init(autoreset=True)
logging.basicConfig(level=logging.WARNING)

class BotConfig:
    TOKEN = "7948128943:AAGQbjzFfG2sbIHj6-QV7fEpO7G4ptIlZz8"
    ADMIN_IDS = []  # Will be set from environment or input
    LOG_CHANNEL = None

class AppConfig:
    CREDENTIALS_FOLDER = 'tdata_vps'
    SESSIONS_DB = 'sessions_db.json'
    STATS_DB = 'stats_db.json'
    CONFIG_FILE = 'bot_config.json'
    
    TARGET_USER = "Og_Digital"
    AUTO_REPLY_MSG = "Dm @Og_Digital For Buy"
    
    # BAN PROTECTION SETTINGS (KEEP AS IS)
    MIN_DELAY = 60      # 1 minute
    MAX_DELAY = 120     # 2 minutes
    CYCLE_DELAY = 1200  # 20 minutes
    MAX_RETRIES = 2
    
    # VPS PERFORMANCE SETTINGS
    MAX_CONCURRENT = 1000
    TCP_BUFFER_SIZE = 2 * 1024 * 1024  # 2MB
    DNS_CACHE_TTL = 600
    REQUEST_TIMEOUT = 15

# ====== DATA STRUCTURES ======
@dataclass
class SessionInfo:
    name: str
    api_id: int
    api_hash: str
    string_session: str
    phone: str = ""
    status: str = "offline"
    client: Optional[TelegramClient] = None
    last_active: datetime = field(default_factory=datetime.now)
    stats: Dict = field(default_factory=lambda: {
        'messages_sent': 0,
        'groups_processed': 0,
        'errors': 0,
        'start_time': datetime.now()
    })
    settings: Dict = field(default_factory=lambda: {
        'active': True,
        'auto_reply': True,
        'forward_messages': True,
        'change_profile': False,
        'profile_photo': None,
        'first_name': "",
        'last_name': "",
        'bio': ""
    })

@dataclass
class BotState:
    sessions: Dict[str, SessionInfo] = field(default_factory=dict)
    active_tasks: Dict[str, asyncio.Task] = field(default_factory=dict)
    performance_stats: Dict = field(default_factory=lambda: {
        'total_sessions': 0,
        'active_sessions': 0,
        'total_messages': 0,
        'uptime': datetime.now(),
        'cpu_usage': 0.0,
        'memory_usage': 0.0,
        'network_speed': 0.0
    })
    bot_app: Optional[Application] = None

# ====== GLOBAL STATE ======
state = BotState()

# ====== PERFORMANCE OPTIMIZATIONS ======
class HighSpeedTelegramClient(TelegramClient):
    """Ultra-optimized Telegram client for VPS"""
    
    def __init__(self, session_info: SessionInfo):
        super().__init__(
            StringSession(session_info.string_session),
            session_info.api_id,
            session_info.api_hash,
            connection_retries=10,
            request_retries=5,
            timeout=AppConfig.REQUEST_TIMEOUT,
            device_model=f"VPS-{os.uname().nodename}",
            system_version="Ubuntu 22.04",
            app_version="9.0",
            lang_code="en",
            system_lang_code="en-US",
            proxy=None,
            auto_reconnect=True
        )
        self.session_info = session_info
    
    async def connect(self, *args, **kwargs):
        """Connect with VPS optimizations"""
        result = await super().connect(*args, **kwargs)
        
        # Optimize socket settings
        if hasattr(self._sender, '_connection'):
            try:
                writer = self._sender._connection._writer.transport
                reader = self._sender._connection._reader.transport
                
                # TCP optimizations
                writer.set_nodelay(True)
                writer.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
                writer.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPIDLE, 30)
                writer.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPINTVL, 10)
                writer.setsockopt(socket.IPPROTO_TCP, socket.TCP_KEEPCNT, 3)
                
                # Increase buffer sizes
                writer.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, AppConfig.TCP_BUFFER_SIZE)
                reader.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, AppConfig.TCP_BUFFER_SIZE)
                
            except:
                pass
        
        return result

# ====== UTILITY FUNCTIONS ======
def get_system_stats() -> Dict:
    """Get detailed system statistics"""
    cpu_percent = psutil.cpu_percent(interval=1)
    memory = psutil.virtual_memory()
    disk = psutil.disk_usage('/')
    network = psutil.net_io_counters()
    
    return {
        'cpu': cpu_percent,
        'memory_used': memory.percent,
        'memory_total_gb': memory.total / (1024**3),
        'disk_used': disk.percent,
        'network_sent_mb': network.bytes_sent / (1024**2),
        'network_recv_mb': network.bytes_recv / (1024**2),
        'uptime_seconds': time.time() - psutil.boot_time()
    }

async def send_bot_message(chat_id: int, text: str, 
                          reply_markup: Optional[InlineKeyboardMarkup] = None,
                          parse_mode: str = 'HTML'):
    """Send message through bot with error handling"""
    try:
        if state.bot_app:
            await state.bot_app.bot.send_message(
                chat_id=chat_id,
                text=text,
                reply_markup=reply_markup,
                parse_mode=parse_mode,
                disable_web_page_preview=True
            )
    except Exception as e:
        print(f"{Fore.RED}BOT SEND ERROR: {e}")

async def broadcast_to_admins(text: str, 
                            reply_markup: Optional[InlineKeyboardMarkup] = None):
    """Send message to all admin users"""
    for admin_id in BotConfig.ADMIN_IDS:
        await send_bot_message(admin_id, text, reply_markup)

def create_session_keyboard(page: int = 0) -> InlineKeyboardMarkup:
    """Create paginated keyboard for session selection"""
    sessions = list(state.sessions.keys())
    sessions_per_page = 8
    start_idx = page * sessions_per_page
    end_idx = start_idx + sessions_per_page
    
    keyboard = []
    row = []
    
    for i, session_name in enumerate(sessions[start_idx:end_idx], start=1):
        session = state.sessions.get(session_name)
        status_icon = "✅" if session and session.status == "online" else "❌"
        btn_text = f"{status_icon} {session_name}"
        row.append(InlineKeyboardButton(btn_text, callback_data=f"session_{session_name}"))
        
        if i % 2 == 0:
            keyboard.append(row)
            row = []
    
    if row:
        keyboard.append(row)
    
    # Navigation buttons
    nav_buttons = []
    if page > 0:
        nav_buttons.append(InlineKeyboardButton("Prev", callback_data=f"page_{page-1}"))
    
    if end_idx < len(sessions):
        nav_buttons.append(InlineKeyboardButton("Next", callback_data=f"page_{page+1}"))
    
    if nav_buttons:
        keyboard.append(nav_buttons)
    
    # Action buttons
    keyboard.extend([
        [InlineKeyboardButton("Add Session (BOT)", callback_data="add_session_bot"),
         InlineKeyboardButton("Add Session (SCRIPT)", callback_data="add_session_script")],
        [InlineKeyboardButton("Delete Session", callback_data="delete_session"),
         InlineKeyboardButton("Refresh All", callback_data="refresh_all")],
        [InlineKeyboardButton("Stop All", callback_data="stop_all"),
         InlineKeyboardButton("System Stats", callback_data="system_stats")],
        [InlineKeyboardButton("Quick Start", callback_data="quick_start"),
         InlineKeyboardButton("Main Menu", callback_data="main_menu")]
    ])
    
    return InlineKeyboardMarkup(keyboard)

def create_session_control_keyboard(session_name: str) -> InlineKeyboardMarkup:
    """Create control keyboard for specific session"""
    session = state.sessions.get(session_name)
    
    keyboard = [
        [InlineKeyboardButton(f"Status: {session.status if session else 'unknown'}", 
                            callback_data=f"status_{session_name}")],
        [InlineKeyboardButton("Restart", callback_data=f"restart_{session_name}"),
         InlineKeyboardButton("Stop", callback_data=f"stop_{session_name}")],
        [InlineKeyboardButton("Stats", callback_data=f"stats_{session_name}"),
         InlineKeyboardButton("Settings", callback_data=f"settings_{session_name}")],
        [InlineKeyboardButton("Profile", callback_data=f"profile_{session_name}"),
         InlineKeyboardButton("Bio", callback_data=f"bio_{session_name}")],
        [InlineKeyboardButton("Photo", callback_data=f"photo_{session_name}"),
         InlineKeyboardButton("Forward", callback_data=f"forward_{session_name}")],
        [InlineKeyboardButton("Rename", callback_data=f"rename_{session_name}"),
         InlineKeyboardButton("Info", callback_data=f"info_{session_name}")],
        [InlineKeyboardButton("Delete", callback_data=f"delete_{session_name}"),
         InlineKeyboardButton("Back", callback_data="list_sessions_0")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_settings_keyboard(session_name: str) -> InlineKeyboardMarkup:
    """Create settings toggle keyboard"""
    session = state.sessions.get(session_name)
    if not session:
        return InlineKeyboardMarkup([[]])
    
    settings = session.settings
    
    # Toggle buttons with current status
    auto_reply_icon = "ON" if settings['auto_reply'] else "OFF"
    forward_icon = "ON" if settings['forward_messages'] else "OFF"
    active_icon = "ON" if settings['active'] else "OFF"
    profile_icon = "ON" if settings['change_profile'] else "OFF"
    
    keyboard = [
        [InlineKeyboardButton(f"Auto Reply: {auto_reply_icon}", 
                            callback_data=f"toggle_autoreply_{session_name}"),
         InlineKeyboardButton(f"Forwarding: {forward_icon}", 
                            callback_data=f"toggle_forward_{session_name}")],
        [InlineKeyboardButton(f"Active: {active_icon}", 
                            callback_data=f"toggle_active_{session_name}"),
         InlineKeyboardButton(f"Auto Profile: {profile_icon}", 
                            callback_data=f"toggle_profile_{session_name}")],
        [InlineKeyboardButton("Set First Name", 
                            callback_data=f"set_firstname_{session_name}"),
         InlineKeyboardButton("Set Last Name", 
                            callback_data=f"set_lastname_{session_name}")],
        [InlineKeyboardButton("Set Bio", 
                            callback_data=f"set_bio_{session_name}"),
         InlineKeyboardButton("Set Photo", 
                            callback_data=f"set_photo_{session_name}")],
        [InlineKeyboardButton("Save Settings", 
                            callback_data=f"save_settings_{session_name}"),
         InlineKeyboardButton("Reset Defaults", 
                            callback_data=f"reset_settings_{session_name}")],
        [InlineKeyboardButton("Back", callback_data=f"session_{session_name}")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_bulk_actions_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for bulk actions"""
    keyboard = [
        [InlineKeyboardButton("Start 1-10", callback_data="bulk_start_1_10"),
         InlineKeyboardButton("Start 11-20", callback_data="bulk_start_11_20")],
        [InlineKeyboardButton("Start 21-30", callback_data="bulk_start_21_30"),
         InlineKeyboardButton("Start 31-40", callback_data="bulk_start_31_40")],
        [InlineKeyboardButton("Stop 1-10", callback_data="bulk_stop_1_10"),
         InlineKeyboardButton("Stop 11-20", callback_data="bulk_stop_11_20")],
        [InlineKeyboardButton("Rename Batch", callback_data="bulk_rename"),
         InlineKeyboardButton("Bio All", callback_data="bulk_bio")],
        [InlineKeyboardButton("Photo All", callback_data="bulk_photo"),
         InlineKeyboardButton("Settings All", callback_data="bulk_settings")],
        [InlineKeyboardButton("Forward All", callback_data="bulk_forward"),
         InlineKeyboardButton("Restart All", callback_data="bulk_restart")],
        [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_main_menu_keyboard() -> InlineKeyboardMarkup:
    """Create main menu keyboard"""
    keyboard = [
        [InlineKeyboardButton("Manage Sessions", callback_data="list_sessions_0")],
        [InlineKeyboardButton("Bulk Actions", callback_data="bulk_actions"),
         InlineKeyboardButton("Dashboard", callback_data="dashboard")],
        [InlineKeyboardButton("Global Settings", callback_data="global_settings"),
         InlineKeyboardButton("Analytics", callback_data="analytics")],
        [InlineKeyboardButton("Tools", callback_data="tools"),
         InlineKeyboardButton("Help", callback_data="help")],
        [InlineKeyboardButton("System Refresh", callback_data="system_refresh"),
         InlineKeyboardButton("Add Session", callback_data="add_session_options")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

def create_add_session_options_keyboard() -> InlineKeyboardMarkup:
    """Create keyboard for adding sessions"""
    keyboard = [
        [InlineKeyboardButton("Add via BOT (Interactive)", callback_data="add_session_bot")],
        [InlineKeyboardButton("Add via SCRIPT (Manual)", callback_data="add_session_script")],
        [InlineKeyboardButton("Add Multiple Sessions", callback_data="add_multiple")],
        [InlineKeyboardButton("QR Code Login", callback_data="qr_login")],
        [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
    ]
    
    return InlineKeyboardMarkup(keyboard)

# ====== BOT COMMAND HANDLERS ======
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /start command"""
    user_id = update.effective_user.id
    
    if not BotConfig.ADMIN_IDS:
        BotConfig.ADMIN_IDS.append(user_id)
        await save_config()
    
    welcome_text = f"""
<b>ORBIT ADBOT VPS ULTIMATE</b>

<b>Status:</b> Ready
<b>Sessions:</b> {len(state.sessions)}
<b>VPS:</b> {os.uname().nodename}

<b>Commands:</b>
/start - Start bot
/sessions - List sessions
/stats - System statistics
/control - Control panel
/bulk - Bulk actions
/tools - Advanced tools
/help - Show help

<b>Quick Actions:</b>
- Manage unlimited sessions
- Bulk profile updates
- Real-time monitoring
- Auto-reply system
- High-speed forwarding
"""
    
    await update.message.reply_text(
        welcome_text,
        reply_markup=create_main_menu_keyboard(),
        parse_mode='HTML'
    )

async def sessions_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /sessions command"""
    if not state.sessions:
        await update.message.reply_text(
            "No sessions found. Add sessions first!",
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton("Add Session", callback_data="add_session_options")
            ]])
        )
        return
    
    text = f"<b>Active Sessions ({len(state.sessions)})</b>\n\n"
    
    for i, (name, session) in enumerate(state.sessions.items(), 1):
        status_icon = "✅" if session.status == "online" else "❌"
        text += f"{i}. <b>{name}</b> {status_icon}\n"
        text += f"   Stats: Msgs {session.stats['messages_sent']} | "
        text += f"Groups {session.stats['groups_processed']}\n"
        text += f"   Settings: {'ON' if session.settings['active'] else 'OFF'}\n\n"
    
    await update.message.reply_text(
        text,
        reply_markup=create_session_keyboard(0),
        parse_mode='HTML'
    )

async def stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /stats command"""
    sys_stats = get_system_stats()
    
    # Calculate bot stats
    total_msgs = sum(s.stats['messages_sent'] for s in state.sessions.values())
    total_groups = sum(s.stats['groups_processed'] for s in state.sessions.values())
    online_sessions = sum(1 for s in state.sessions.values() if s.status == "online")
    
    stats_text = f"""
<b>SYSTEM DASHBOARD</b>

<b>Bot Statistics:</b>
- Total Sessions: {len(state.sessions)}
- Online Sessions: {online_sessions}
- Total Messages: {total_msgs:,}
- Groups Processed: {total_groups:,}

<b>VPS Statistics:</b>
- CPU Usage: {sys_stats['cpu']:.1f}%
- Memory: {sys_stats['memory_used']:.1f}% ({sys_stats['memory_total_gb']:.1f}GB)
- Disk: {sys_stats['disk_used']:.1f}%
- Network Up: {sys_stats['network_sent_mb']:.1f}MB
- Network Down: {sys_stats['network_recv_mb']:.1f}MB

<b>Performance:</b>
- Uptime: {timedelta(seconds=int(sys_stats['uptime_seconds']))}
- Connection Speed: Optimized for 3-5 Gbps
"""
    
    keyboard = [
        [InlineKeyboardButton("Refresh", callback_data="refresh_stats"),
         InlineKeyboardButton("Detailed", callback_data="detailed_stats")],
        [InlineKeyboardButton("Graphs", callback_data="show_graphs"),
         InlineKeyboardButton("Main Menu", callback_data="main_menu")]
    ]
    
    await update.message.reply_text(
        stats_text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def bulk_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /bulk command"""
    text = """
<b>BULK ACTIONS CONTROL</b>

Perform actions on multiple sessions simultaneously:

<b>Available Bulk Operations:</b>
- Start/Stop ranges of sessions (1-10, 11-20, etc.)
- Batch rename sessions
- Set bio for all sessions
- Upload profile photos to all
- Apply settings to all sessions
- Mass message forwarding

<b>Quick Selection:</b>
Choose from predefined ranges or customize.
"""
    
    await update.message.reply_text(
        text,
        reply_markup=create_bulk_actions_keyboard(),
        parse_mode='HTML'
    )

async def tools_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /tools command"""
    text = """
<b>ADVANCED TOOLS</b>

<b>Available Tools:</b>

1. <b>Session Generator</b> - Create multiple sessions
2. <b>Profile Cloner</b> - Clone profiles between accounts
3. <b>Mass Checker</b> - Check all sessions status
4. <b>Backup System</b> - Backup/Restore all data
5. <b>QR Code Login</b> - Login via QR code
6. <b>Proxy Manager</b> - Manage proxies for sessions
7. <b>Auto Scraper</b> - Scrape groups automatically
8. <b>Message Scheduler</b> - Schedule messages

Select a tool to continue:
"""
    
    keyboard = [
        [InlineKeyboardButton("Session Generator", callback_data="tool_generator"),
         InlineKeyboardButton("Profile Cloner", callback_data="tool_cloner")],
        [InlineKeyboardButton("Mass Checker", callback_data="tool_checker"),
         InlineKeyboardButton("Backup", callback_data="tool_backup")],
        [InlineKeyboardButton("QR Login", callback_data="tool_qr"),
         InlineKeyboardButton("Proxy Manager", callback_data="tool_proxy")],
        [InlineKeyboardButton("Auto Scraper", callback_data="tool_scraper"),
         InlineKeyboardButton("Scheduler", callback_data="tool_scheduler")],
        [InlineKeyboardButton("Main Menu", callback_data="main_menu")]
    ]
    
    await update.message.reply_text(
        text,
        reply_markup=InlineKeyboardMarkup(keyboard),
        parse_mode='HTML'
    )

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle /help command"""
    help_text = """
<b>ORBIT ADBOT HELP GUIDE</b>

<b>Basic Commands:</b>
/start - Start the bot
/sessions - List all sessions
/stats - Show statistics
/control - Control panel
/bulk - Bulk actions
/tools - Advanced tools
/help - This help message

<b>Session Management:</b>
- Each session = One Telegram account
- Sessions run independently
- Can be controlled individually or in bulk
- Settings persist across restarts

<b>Key Features:</b>
1. <b>Auto-Reply</b> - Auto reply to DMs
2. <b>Message Forwarding</b> - Forward to groups
3. <b>Profile Management</b> - Change names, photos, bio
4. <b>Bulk Operations</b> - Control multiple sessions
5. <b>Real-time Monitoring</b> - Live stats and logs
6. <b>VPS Optimized</b> - High-speed performance

<b>Important Notes:</b>
- Keep your API credentials safe
- Monitor session limits to avoid bans
- Use delays between actions
- Backup sessions regularly

<b>Support:</b>
For issues or questions, contact @Og_Digital
"""
    
    await update.message.reply_text(
        help_text,
        parse_mode='HTML',
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton("Tutorial", callback_data="tutorial"),
            InlineKeyboardButton("Restart Bot", callback_data="restart_bot")
        ]])
    )

# ====== CALLBACK QUERY HANDLERS ======
async def button_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Handle all button callbacks"""
    query = update.callback_query
    await query.answer()
    
    data = query.data
    
    if data == "main_menu":
        await query.edit_message_text(
            "<b>Main Menu</b>\nSelect an option:",
            reply_markup=create_main_menu_keyboard(),
            parse_mode='HTML'
        )
    
    elif data == "add_session_options":
        await query.edit_message_text(
            "<b>Add Session</b>\nChoose method:",
            reply_markup=create_add_session_options_keyboard(),
            parse_mode='HTML'
        )
    
    elif data == "add_session_bot":
        # Start interactive session addition via bot
        context.user_data['adding_session'] = True
        context.user_data['session_step'] = 'name'
        context.user_data['method'] = 'bot'
        
        await query.edit_message_text(
            "<b>Add Session via BOT</b>\n\nSend session name:",
            parse_mode='HTML'
        )
    
    elif data == "add_session_script":
        # Show instructions for script-based addition
        instructions = """
<b>Add Session via SCRIPT</b>

To add sessions via script (like before):

1. <b>Run the script normally:</b>
   Just run: python3 script.py

2. <b>It will ask:</b>
   - Number of sessions
   - API ID, API Hash, String Session for each

3. <b>Sessions will be:</b>
   - Automatically saved to database
   - Available in bot immediately
   - Can be controlled via bot

4. <b>Or use quick add:</b>
   Create file sessions.txt with format:
   session_name|api_id|api_hash|string_session
   session1|123456|hash123|session_string_here

Then run: python3 -c "from tri import load_sessions_from_file; load_sessions_from_file('sessions.txt')"
"""
        
        keyboard = [
            [InlineKeyboardButton("Back", callback_data="add_session_options"),
             InlineKeyboardButton("Example File", callback_data="show_example")]
        ]
        
        await query.edit_message_text(
            instructions,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='HTML'
        )
    
    elif data.startswith("list_sessions_"):
        page = int(data.split("_")[-1])
        await query.edit_message_text(
            f"<b>Sessions (Page {page+1})</b>",
            reply_markup=create_session_keyboard(page),
            parse_mode='HTML'
        )
    
    elif data.startswith("session_"):
        session_name = data.split("_", 1)[1]
        session = state.sessions.get(session_name)
        
        if session:
            text = f"""
<b>Session Control: {session_name}</b>

<b>Status:</b> {session.status.upper()}
<b>Phone:</b> {session.phone or 'Not set'}
<b>Last Active:</b> {session.last_active.strftime('%Y-%m-%d %H:%M:%S')}

<b>Statistics:</b>
- Messages Sent: {session.stats['messages_sent']:,}
- Groups Processed: {session.stats['groups_processed']:,}
- Errors: {session.stats['errors']:,}
- Uptime: {datetime.now() - session.stats['start_time']}

<b>Settings:</b>
- Active: {'ON' if session.settings['active'] else 'OFF'}
- Auto Reply: {'ON' if session.settings['auto_reply'] else 'OFF'}
- Forward Messages: {'ON' if session.settings['forward_messages'] else 'OFF'}
- Auto Profile: {'ON' if session.settings['change_profile'] else 'OFF'}
"""
        else:
            text = f"<b>Session {session_name} not found!</b>"
        
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
                f"<b>Session '{session_name}' deleted!</b>",
                parse_mode='HTML'
            )
            await broadcast_to_admins(f"Session deleted: <b>{session_name}</b>")
        else:
            await query.edit_message_text(
                f"<b>Session '{session_name}' not found!</b>",
                parse_mode='HTML'
            )
    
    elif data.startswith("settings_"):
        session_name = data.split("_", 1)[1]
        await query.edit_message_text(
            f"<b>Settings for {session_name}</b>\nToggle options:",
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
                f"<b>Setting updated for {session_name}</b>",
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
            f"<b>Set {action.upper()} for {session_name}</b>\n\n{prompts.get(action, 'Send input:')}",
            parse_mode='HTML'
        )
    
    elif data == "bulk_actions":
        await query.edit_message_text(
            "<b>Bulk Actions Control</b>\nSelect an action:",
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
                f"<b>{msg}</b>\nAffected: {len(sessions_to_act)} sessions",
                parse_mode='HTML'
            )
        
        elif action == "rename":
            context.user_data['awaiting_input'] = {
                'type': 'bulk_rename',
                'pattern': 'session{number}'
            }
            await query.edit_message_text(
                "<b>Batch Rename</b>\nSend new name pattern (use {number} for index):\nExample: account_{number}_vps",
                parse_mode='HTML'
            )
        
        elif action == "bio":
            context.user_data['awaiting_input'] = {
                'type': 'bulk_bio'
            }
            await query.edit_message_text(
                "<b>Set Bio for All Sessions</b>\nSend the bio text to apply to all sessions:",
                parse_mode='HTML'
            )
    
    elif data == "dashboard":
        await stats_command(update, context)
    
    elif data == "refresh_all":
        await refresh_all_sessions()
        await query.edit_message_text(
            "<b>Refreshing all sessions...</b>",
            parse_mode='HTML'
        )
    
    elif data.startswith("restart_"):
        session_name = data.split("_", 1)[1]
        await restart_session(session_name)
        await query.edit_message_text(
            f"<b>Restarting {session_name}...</b>",
            parse_mode='HTML'
        )
    
    elif data.startswith("stop_"):
        session_name = data.split("_", 1)[1]
        await stop_session(session_name)
        await query.edit_message_text(
            f"<b>Stopped {session_name}</b>",
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
                    f"<b>{input_type.upper()} updated for {session_name}</b>",
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
                        f"<b>Profile photo updated for {session_name}</b>",
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
                f"<b>Renamed all sessions</b>\nNew pattern: {pattern}",
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
                f"<b>Bio applied to all sessions</b>",
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
                InlineKeyboardButton("Start", callback_data=f"start_{session_name}"),
                InlineKeyboardButton("Settings", callback_data=f"settings_{session_name}")
            ]])
            
            await update.message.reply_text(
                f"<b>Session '{session_name}' added via script format!</b>",
                reply_markup=keyboard,
                parse_mode='HTML'
            )
            
        except Exception as e:
            await update.message.reply_text(
                f"<b>Error adding session: {str(e)}</b>",
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
            InlineKeyboardButton("Start Now", callback_data=f"start_{session_name}"),
            InlineKeyboardButton("Configure", callback_data=f"settings_{session_name}"),
            InlineKeyboardButton("Sessions List", callback_data="list_sessions_0")
        ]])
        
        await update.message.reply_text(
            f"<b>Session '{session_name}' added via BOT!</b>",
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
    
    await broadcast_to_admins(f"Starting session: <b>{session_name}</b>")

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
    
    await broadcast_to_admins(f"Stopped session: <b>{session_name}</b>")

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
            await broadcast_to_admins(f"Session <b>{session.name}</b> not authorized")
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
        
        await broadcast_to_admins(f"Session <b>{session.name}</b> online ({me.phone or me.username})")
        
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
    print(f"{Fore.GREEN}ADD SESSIONS (SCRIPT STYLE)")
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
                print(f"{Fore.GREEN}Session {session_name} added!")
                
            except ValueError:
                print(f"{Fore.RED}Invalid input for session {session_name}. Skipping...")
                continue
        
        await save_sessions()
        print(f"\n{Fore.GREEN}All sessions saved! Total: {len(state.sessions)}")
        
        # Ask to start sessions
        start_now = input(f"\n{Fore.YELLOW}Start all sessions now? (y/n): ").lower()
        if start_now == 'y':
            print(f"{Fore.GREEN}Starting all sessions...")
            for session_name in state.sessions.keys():
                await start_session(session_name)
                await asyncio.sleep(1)  # Stagger starts
        
        print(f"\n{Fore.GREEN}Script-style session addition complete!")
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
        print(f"{Fore.GREEN}Loaded {added} sessions from file!")
        
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
                await broadcast_to_admins(f"High CPU Usage: {sys_stats['cpu']:.1f}%")
            
            if sys_stats['memory_used'] > 85:
                await broadcast_to_admins(f"High Memory Usage: {sys_stats['memory_used']:.1f}%")
            
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
    print(f"{Fore.GREEN}Initializing Control Bot...")
    
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
    
    print(f"{Fore.GREEN}Control Bot Ready!")
    
    # Send startup message
    startup_msg = f"""
<b>ORBIT ADBOT VPS ULTIMATE STARTED</b>

<b>Server:</b> {os.uname().nodename}
<b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
<b>Sessions:</b> {len(state.sessions)} loaded
<b>Status:</b> Operational

<b>VPS Specifications:</b>
- CPU Cores: {psutil.cpu_count()}
- RAM: {psutil.virtual_memory().total / (1024**3):.1f} GB
- Network: 3-5 Gbps Optimized

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
                text="An error occurred. Please try again."
            )
    except:
        pass

async def main():
    """Main function"""
    print(f"{Fore.CYAN}{'='*60}")
    print(f"{Fore.GREEN}ORBIT ADBOT - VPS ULTIMATE EDITION")
    print(f"{Fore.YELLOW}BOT + SCRIPT COMBINATION")
    print(f"{Fore.CYAN}{'='*60}")
    
    # Load configuration
    await load_config()
    await load_sessions()
    
    print(f"{Fore.GREEN}Loaded {len(state.sessions)} sessions")
    
    # Show menu
    print(f"\n{Fore.CYAN}Select mode:")
    print(f"{Fore.GREEN}1. Bot Mode (Control via Telegram)")
    print(f"{Fore.GREEN}2. Script Mode (Add sessions old way)")
    print(f"{Fore.GREEN}3. Both (Run bot + add sessions)")
    print(f"{Fore.GREEN}4. Load from file (sessions.txt)")
    
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
            print(f"{Fore.GREEN}Sessions loaded! Starting bot...")
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
            print(f"{Fore.GREEN}Auto-started {auto_start_count} sessions")
        
        print(f"\n{Fore.GREEN}System ready!")
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
