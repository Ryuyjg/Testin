import requests
import json
import time
import random
import string
from colorama import Fore, init
import sys
import os

init()

print(f"""{Fore.CYAN}
╔══════════════════════════════════════════════════╗
║    TELEGRAM API AUTO-CREATOR - POWER MODE        ║
║    100% PowerShell - No Browser                  ║
║    Telegram: @ogdigital                           ║
╚══════════════════════════════════════════════════╝\n
""")

class TelegramAPIForceCreator:
    def __init__(self):
        self.session = None
        self.setup_new_session()
        
    def setup_new_session(self):
        """Create a fresh session with new headers"""
        self.session = requests.Session()
        self.setup_realistic_headers()
    
    def setup_realistic_headers(self):
        """Setup headers to look like real Telegram app with random user agent"""
        user_agent = self.get_random_user_agent()
        self.session.headers.update({
            'User-Agent': user_agent,
            'Accept': 'application/json, text/plain, */*',
            'Accept-Language': 'en-US,en;q=0.9',
            'Accept-Encoding': 'gzip, deflate, br',
            'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
            'X-Requested-With': 'XMLHttpRequest',
            'Origin': 'https://my.telegram.org',
            'Referer': 'https://my.telegram.org/',
            'Connection': 'keep-alive',
            'Sec-Fetch-Dest': 'empty',
            'Sec-Fetch-Mode': 'cors',
            'Sec-Fetch-Site': 'same-origin',
            'TE': 'trailers',
        })
    
    def get_random_user_agent(self):
        """Get random realistic user agent from 100+ browser list"""
        # Comprehensive list of user agents (100+)
        user_agents = [
            # Chrome Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # Chrome macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
            
            # Chrome Linux
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux i686) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # Firefox Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:120.0) Gecko/20100101 Firefox/120.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Windows NT 10.0; rv:123.0) Gecko/20100101 Firefox/123.0',
            
            # Firefox macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.15; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.14; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10.13; rv:123.0) Gecko/20100101 Firefox/123.0',
            
            # Firefox Linux
            'Mozilla/5.0 (X11; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
            'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:123.0) Gecko/20100101 Firefox/123.0',
            
            # Safari macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_13_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/13.1.2 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 11_2_3) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0.3 Safari/605.1.15',
            
            # Safari iOS
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
            
            # Edge Windows
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 Edg/121.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
            
            # Edge macOS
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Edg/122.0.0.0',
            
            # Opera
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/107.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36 OPR/107.0.0.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/107.0.0.0',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 OPR/107.0.0.0',
            
            # Samsung Browser
            'Mozilla/5.0 (Linux; Android 10; SM-G981B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/22.0 Chrome/108.0.5359.128 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/23.0 Chrome/112.0.5615.48 Mobile Safari/537.36',
            
            # Android Chrome
            'Mozilla/5.0 (Linux; Android 14; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; SM-G980F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            
            # Android Firefox
            'Mozilla/5.0 (Android 14; Mobile; rv:123.0) Gecko/123.0 Firefox/123.0',
            'Mozilla/5.0 (Android 13; Mobile; rv:122.0) Gecko/122.0 Firefox/122.0',
            
            # Brave Browser
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Brave/122.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Brave/122.0',
            
            # Vivaldi
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Vivaldi/6.5',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Vivaldi/6.5',
            
            # Chrome Older Versions
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/110.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/105.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/100.0.0.0 Safari/537.36',
            
            # Firefox Older Versions
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:115.0) Gecko/20100101 Firefox/115.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:110.0) Gecko/20100101 Firefox/110.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:105.0) Gecko/20100101 Firefox/105.0',
            
            # Safari Older Versions
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/15.6 Safari/605.1.15',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_6) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.2 Safari/605.1.15',
            
            # Internet Explorer (legacy)
            'Mozilla/5.0 (Windows NT 10.0; WOW64; Trident/7.0; rv:11.0) like Gecko',
            'Mozilla/5.0 (Windows NT 6.1; WOW64; Trident/7.0; rv:11.0) like Gecko',
            
            # Edge Legacy
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/64.0.3282.140 Safari/537.36 Edge/17.17134',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.102 Safari/537.36 Edge/18.18362',
            
            # UC Browser
            'Mozilla/5.0 (Linux; U; Android 10; en-US; SM-G975F) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/57.0.2987.108 UCBrowser/12.14.0.1221 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; U; Android 11; en-US; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 Chrome/78.0.3904.108 UCBrowser/13.4.0.1306 Mobile Safari/537.36',
            
            # QQ Browser
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 QQBrowser/10.7.4310.400',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.25 Safari/537.36 Core/1.70.3861.400 QQBrowser/10.7.4313.400',
            
            # 360 Browser
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 360SE/13.0',
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 360SE/10.0',
            
            # Maxthon
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/86.0.4240.198 Safari/537.36 Maxthon/6.1.0.2000',
            
            # Yandex Browser
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/23.9.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 YaBrowser/23.9.0.0 Safari/537.36',
            
            # Dolphin Browser
            'Mozilla/5.0 (Linux; Android 12; SM-G998B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/99.0.4844.88 Mobile Safari/537.36 Dolphin/INT-1.0',
            
            # Puffin Browser
            'Mozilla/5.0 (X11; U; Linux x86_64; en-US) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Puffin/8.0.0.0',
            
            # Silk Browser
            'Mozilla/5.0 (Linux; Android 11; KFMAWI) AppleWebKit/537.36 (KHTML, like Gecko) Silk/87.2.15 like Chrome/87.0.4280.141 Safari/537.36',
            
            # DuckDuckGo Browser
            'Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Version/4.0 DuckDuckGo/5.133.0 Mobile Safari/537.36',
            
            # Focus Browser
            'Mozilla/5.0 (Linux; Android 13; SM-S901B) AppleWebKit/537.36 (KHTML, like Gecko) Focus/122.0.0 Mobile Safari/537.36',
            
            # Kiwi Browser
            'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            
            # Ghostery Browser
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Ghostery/8.9.0',
            
            # Waterfox
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:2023.12) Gecko/20100101 Firefox/115.0 Waterfox/2023.12',
            
            # Pale Moon
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Goanna/6.2 Firefox/102.0 PaleMoon/32.4.0',
            
            # Basilisk
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Goanna/6.2 Firefox/102.0 Basilisk/2023.12.0',
            
            # SeaMonkey
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:102.0) Gecko/20100101 Firefox/102.0 SeaMonkey/2.53.17',
            
            # Midori
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36 Midori/7.0',
            
            # Falkon
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Falkon/3.2.0 Chrome/122.0.0.0 Safari/537.36',
            
            # Konqueror
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Konqueror/5.0 Safari/537.36',
            
            # Lynx (text browser)
            'Lynx/2.8.9rel.1 libwww-FM/2.14 SSL-MM/1.4.1 OpenSSL/1.1.1w',
            
            # w3m (text browser)
            'w3m/0.5.3',
            
            # Links (text browser)
            'Links (2.28; Linux 5.15.0 x86_64; GNU C 11.3.0; text)',
            
            # Elinks (text browser)
            'ELinks/0.12pre6 (textmode; Linux 5.15.0 x86_64; 80x24)',
            
            # Legacy Chrome for compatibility
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/60.0.3112.90 Safari/537.36',
            
            # Legacy Firefox for compatibility
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64; rv:60.0) Gecko/20100101 Firefox/60.0',
            'Mozilla/5.0 (Windows NT 5.1; rv:60.0) Gecko/20100101 Firefox/60.0',
            
            # Random mobile agents
            'Mozilla/5.0 (Linux; Android 14; Pixel 8 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; Galaxy S21) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; OnePlus 9 Pro) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            
            # Tablet agents
            'Mozilla/5.0 (Linux; Android 13; SM-X916B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 12; SM-T970) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; Lenovo TB-X505F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # iOS Safari variants
            'Mozilla/5.0 (iPhone14,6; U; CPU iPhone OS 15_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/15.0 Mobile/19A346 Safari/602.1',
            'Mozilla/5.0 (iPhone12,1; U; CPU iPhone OS 13_0 like Mac OS X) AppleWebKit/602.1.50 (KHTML, like Gecko) Version/10.0 Mobile/15E148 Safari/602.1',
            'Mozilla/5.0 (iPad; CPU OS 14_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.0 Mobile/15E148 Safari/604.1',
            
            # Windows Phone (legacy)
            'Mozilla/5.0 (Windows Phone 10.0; Android 6.0.1; Microsoft; Lumia 950 XL) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/52.0.2743.116 Mobile Safari/537.36 Edge/15.15063',
            
            # BlackBerry (legacy)
            'Mozilla/5.0 (BB10; Touch) AppleWebKit/537.10+ (KHTML, like Gecko) Version/10.3.3.2205 Mobile Safari/537.10+',
            'Mozilla/5.0 (PlayBook; U; RIM Tablet OS 2.1.0; en-US) AppleWebKit/536.2+ (KHTML, like Gecko) Version/7.2.1.0 Safari/536.2+',
            
            # Nintendo 3DS
            'Mozilla/5.0 (Nintendo 3DS; U; ; en) Version/1.7567.US',
            
            # PlayStation 4
            'Mozilla/5.0 (PlayStation 4 9.51) AppleWebKit/605.1.15 (KHTML, like Gecko)',
            
            # PlayStation Vita
            'Mozilla/5.0 (PlayStation Vita 3.73) AppleWebKit/537.73 (KHTML, like Gecko) Silk/3.2',
            
            # Smart TVs
            'Mozilla/5.0 (SMART-TV; Linux; Tizen 6.5) AppleWebKit/537.36 (KHTML, like Gecko) SamsungBrowser/4.0 Chrome/76.0.3809.146 TV Safari/537.36',
            'Mozilla/5.0 (Linux; Android 11; SHIELD Android TV) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/87.0.4280.141 Safari/537.36',
            
            # Desktop App User Agents
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) TelegramDesktop/4.10.0 Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) TelegramDesktop/4.10.0 Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) TelegramDesktop/4.10.0 Chrome/122.0.0.0 Safari/537.36',
            
            # Discord Desktop (impersonation)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9032 Chrome/120.0.6099.291 Electron/27.1.3 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) discord/1.0.9032 Chrome/120.0.6099.291 Electron/27.1.3 Safari/537.36',
            
            # WhatsApp Desktop (impersonation)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) WhatsApp/2.2349.51 Chrome/120.0.6099.291 Electron/27.1.3 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) WhatsApp/2.2349.51 Chrome/120.0.6099.291 Electron/27.1.3 Safari/537.36',
            
            # Slack Desktop (impersonation)
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) slack/4.36.130 Chrome/120.0.6099.291 Electron/27.1.3 Safari/537.36',
            
            # Custom Bot User Agents
            'Mozilla/5.0 (compatible; TelegramBot/1.0; +https://core.telegram.org/bots)',
            'TelegramBot/1.0 (+https://core.telegram.org/bots)',
            'Mozilla/5.0 (compatible; TelegramAPI/2.0)',
            
            # Generic Browser
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            'AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0',
            
            # Empty User Agent (sometimes works for bypass)
            '',
            
            # Random mobile with different Android versions
            'Mozilla/5.0 (Linux; Android 10; VOG-L29) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 9; SM-N960F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.1.0; Mi A2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 8.0.0; SM-G950F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 7.1.2; Redmi Note 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 6.0.1; SM-G920F) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            'Mozilla/5.0 (Linux; Android 5.1.1; SM-J120H) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Mobile Safari/537.36',
            
            # iOS with different devices
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.0.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPad; CPU OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) CriOS/122.0.0.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (iPod touch; CPU iPhone OS 17_3 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.3 Mobile/15E148 Safari/604.1',
            
            # Windows with different architectures
            'Mozilla/5.0 (Windows NT 11.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.3; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 6.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.2; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 5.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # 32-bit Windows
            'Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # ARM Windows
            'Mozilla/5.0 (Windows NT 10.0; ARM; ARM) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # Chrome OS
            'Mozilla/5.0 (X11; CrOS x86_64 15662.64.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            'Mozilla/5.0 (X11; CrOS armv7l 15662.64.0) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # FreeBSD
            'Mozilla/5.0 (X11; FreeBSD amd64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # OpenBSD
            'Mozilla/5.0 (X11; OpenBSD amd64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # NetBSD
            'Mozilla/5.0 (X11; NetBSD amd64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # Solaris
            'Mozilla/5.0 (X11; SunOS i86pc) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
            
            # Haiku
            'Mozilla/5.0 (X11; Haiku x86_64) AppleWebKit/537.36 (KHTML, like Gecko) QtWebEngine/5.15.2 Chrome/87.0.4280.144 Safari/537.36',
        ]
        
        # Add 10+ more random combinations
        for _ in range(10):
            chrome_versions = ['122', '121', '120', '119', '118', '117', '116', '115']
            firefox_versions = ['123', '122', '121', '120', '119', '118', '117', '116']
            safari_versions = ['17.3', '17.2', '17.1', '17.0', '16.6', '16.5', '16.4', '16.3']
            android_versions = ['14', '13', '12', '11', '10', '9', '8.1', '8.0', '7.1', '7.0']
            ios_versions = ['17_3', '17_2', '17_1', '17_0', '16_6', '16_5', '16_4', '16_3']
            
            random_chrome = random.choice(chrome_versions)
            random_firefox = random.choice(firefox_versions)
            random_safari = random.choice(safari_versions)
            random_android = random.choice(android_versions)
            random_ios = random.choice(ios_versions)
            
            # Random Chrome
            user_agents.append(f'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random_chrome}.0.0.0 Safari/537.36')
            # Random Firefox
            user_agents.append(f'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:{random_firefox}.0) Gecko/20100101 Firefox/{random_firefox}.0')
            # Random Safari
            user_agents.append(f'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random_safari} Safari/605.1.15')
            # Random Android Chrome
            user_agents.append(f'Mozilla/5.0 (Linux; Android {random_android}; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/{random_chrome}.0.0.0 Mobile Safari/537.36')
            # Random iOS Safari
            user_agents.append(f'Mozilla/5.0 (iPhone; CPU iPhone OS {random_ios} like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/{random_safari} Mobile/15E148 Safari/604.1')
        
        return random.choice(user_agents)
    
    def generate_random_string(self, length=8):
        """Generate random string for app names"""
        letters = string.ascii_lowercase
        return ''.join(random.choice(letters) for _ in range(length))
    
    def login(self, phone):
        """Login and return session"""
        print(f"{Fore.YELLOW}[1] Requesting login code for {phone}...")
        
        try:
            # First, get the main page to set cookies
            print(f"{Fore.CYAN}[*] Initializing session with random user agent...")
            self.session.get('https://my.telegram.org', timeout=10)
            
            # Send phone
            print(f"{Fore.CYAN}[*] Sending phone number...")
            response = self.session.post(
                'https://my.telegram.org/auth/send_password',
                data={'phone': phone},
                timeout=15
            )
            
            if response.status_code != 200:
                print(f"{Fore.RED}[!] Failed to send code: {response.status_code}")
                return False
            
            data = response.json()
            if 'random_hash' not in data:
                print(f"{Fore.RED}[!] No hash in response")
                return False
            
            random_hash = data['random_hash']
            print(f"{Fore.GREEN}[✓] Code sent to Telegram!")
            
            # Get code
            code = input(f"{Fore.CYAN}[?] Enter Telegram code for {phone}: {Fore.YELLOW}")
            
            # Login with code
            print(f"{Fore.YELLOW}[2] Logging in...")
            login_data = {
                'phone': phone,
                'random_hash': random_hash,
                'password': code
            }
            
            response = self.session.post(
                'https://my.telegram.org/auth/login',
                data=login_data,
                timeout=15
            )
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}[✓] Login successful for {phone}!")
                return True
            else:
                print(f"{Fore.RED}[!] Login failed: {response.status_code}")
                return False
                
        except Exception as e:
            print(f"{Fore.RED}[!] Login error for {phone}: {e}")
            return False
    
    def direct_api_create_app(self):
        """Direct API method to create app - Bypasses web interface"""
        print(f"{Fore.YELLOW}[3] Using direct API method...")
        
        # First, we need to get the user's config
        try:
            # Get user config (this often triggers app creation)
            config_url = "https://my.telegram.org/apps/api"
            response = self.session.get(config_url, timeout=15)
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}[✓] Got API endpoint")
                return self.parse_api_response(response.text)
            
            # If that doesn't work, try the web API
            return self.web_api_create_app()
            
        except Exception as e:
            print(f"{Fore.RED}[!] API method failed: {e}")
            return self.web_api_create_app()
    
    def parse_api_response(self, text):
        """Parse API response to extract credentials"""
        import re
        
        # Try to parse as JSON
        try:
            data = json.loads(text)
            if 'api_id' in data and 'api_hash' in data:
                return data
        except:
            pass
        
        # Try regex extraction
        api_id_match = re.search(r'"api_id"\s*:\s*"?(\d{5,9})"?', text)
        api_hash_match = re.search(r'"api_hash"\s*:\s*"?([a-f0-9]{32})"?', text)
        
        if api_id_match and api_hash_match:
            return {
                'api_id': api_id_match.group(1),
                'api_hash': api_hash_match.group(1)
            }
        
        return None
    
    def web_api_create_app(self):
        """Web API method for app creation"""
        print(f"{Fore.YELLOW}[4] Using web API method...")
        
        # Generate random names
        random_suffix = self.generate_random_string(6)
        app_title = f"Telegram{random_suffix}"
        app_shortname = f"tg{random_suffix}"
        
        # Prepare app data
        app_data = {
            'app_title': app_title,
            'app_shortname': app_shortname,
            'app_url': '',
            'app_platform': 'desktop',
            'app_desc': f'Telegram Desktop Client {random_suffix}',
            'hash': self.get_form_hash()
        }
        
        print(f"{Fore.CYAN}[*] Creating app: {app_title} ({app_shortname})")
        
        try:
            # Submit creation
            response = self.session.post(
                'https://my.telegram.org/apps/create',
                data=app_data,
                timeout=20
            )
            
            if response.status_code == 200:
                print(f"{Fore.GREEN}[✓] App creation submitted via web!")
                time.sleep(2)
                
                # Now try to get the credentials
                return self.get_credentials_from_apps()
            else:
                print(f"{Fore.RED}[!] Web API failed: {response.status_code}")
                return None
                
        except Exception as e:
            print(f"{Fore.RED}[!] Web API error: {e}")
            return None
    
    def get_form_hash(self):
        """Get form hash from create page"""
        try:
            response = self.session.get('https://my.telegram.org/apps/create', timeout=10)
            
            # Look for hash in the page
            import re
            hash_match = re.search(r'name=["\']hash["\']\s+value=["\']([^"\']+)["\']', response.text)
            if hash_match:
                return hash_match.group(1)
            
            # Alternative pattern
            hash_match = re.search(r'hash["\']?\s*[:=]\s*["\']([^"\']+)["\']', response.text)
            if hash_match:
                return hash_match.group(1)
            
            return "dummy_hash"
            
        except:
            return "dummy_hash"
    
    def get_credentials_from_apps(self):
        """Get credentials from apps page"""
        print(f"{Fore.YELLOW}[5] Extracting credentials...")
        
        try:
            # Get apps page
            response = self.session.get('https://my.telegram.org/apps', timeout=15)
            page_content = response.text
            
            # Try multiple extraction methods
            credentials = self.brute_force_extract(page_content)
            
            if credentials:
                return credentials
            
            # If still not found, try the raw API endpoint
            return self.try_raw_api_endpoint()
            
        except Exception as e:
            print(f"{Fore.RED}[!] Extraction error: {e}")
            return None
    
    def brute_force_extract(self, html):
        """Brute force extract credentials from HTML"""
        import re
        
        # Try multiple patterns
        patterns = [
            # Pattern 1: JSON-like
            (r'"api_id"\s*:\s*"?(\d{5,9})"?', 'api_id'),
            (r'"api_hash"\s*:\s*"?([a-f0-9]{32})"?', 'api_hash'),
            
            # Pattern 2: HTML text
            (r'>\s*(\d{5,9})\s*<', 'api_id'),
            (r'>\s*([a-f0-9]{32})\s*<', 'api_hash'),
            
            # Pattern 3: In form values
            (r'value=["\'](\d{5,9})["\']', 'api_id'),
            (r'value=["\']([a-f0-9]{32})["\']', 'api_hash'),
            
            # Pattern 4: In script tags
            (r'api_id\s*=\s*["\']?(\d{5,9})["\']?', 'api_id'),
            (r'api_hash\s*=\s*["\']?([a-f0-9]{32})["\']?', 'api_hash'),
            
            # Pattern 5: Any numbers/hex in certain contexts
            (r'App api_id[^<]*<[^>]*>([^<]+)', 'api_id'),
            (r'App api_hash[^<]*<[^>]*>([^<]+)', 'api_hash'),
        ]
        
        api_id = None
        api_hash = None
        
        for pattern, field in patterns:
            matches = re.findall(pattern, html, re.I)
            for match in matches:
                if field == 'api_id' and not api_id:
                    if str(match).isdigit() and 10000 <= int(match) <= 999999999:
                        api_id = match
                elif field == 'api_hash' and not api_hash:
                    if re.match(r'^[a-f0-9]{32}$', str(match), re.I):
                        api_hash = match
            
            if api_id and api_hash:
                break
        
        if api_id and api_hash:
            return {'api_id': api_id, 'api_hash': api_hash}
        
        return None
    
    def try_raw_api_endpoint(self):
        """Try raw API endpoints that might exist"""
        print(f"{Fore.YELLOW}[6] Trying raw API endpoints...")
        
        endpoints = [
            'https://my.telegram.org/apps/api',
            'https://my.telegram.org/api/v1/apps',
            'https://my.telegram.org/api/apps',
        ]
        
        for endpoint in endpoints:
            try:
                response = self.session.get(endpoint, timeout=10)
                if response.status_code == 200:
                    # Try to parse as JSON
                    try:
                        data = response.json()
                        if 'api_id' in data and 'api_hash' in data:
                            print(f"{Fore.GREEN}[✓] Found in API endpoint!")
                            return data
                    except:
                        pass
            except:
                continue
        
        return None
    
    def create_app_telegram_api(self):
        """Alternative: Use Telegram's own API if web fails"""
        print(f"{Fore.YELLOW}[7] Using Telegram Core API...")
        
        # This is a more direct approach
        try:
            # Get the current user's app list
            apps_response = self.session.get('https://my.telegram.org/apps/list', timeout=15)
            
            if apps_response.status_code == 200:
                # Try to parse response
                import re
                
                # Look for create app endpoint
                create_pattern = r'/apps/create/[^"\']+'
                matches = re.findall(create_pattern, apps_response.text)
                
                if matches:
                    create_url = f"https://my.telegram.org{matches[0]}"
                    
                    # Try to create app via this URL
                    response = self.session.post(create_url, timeout=20)
                    
                    if response.status_code == 200:
                        print(f"{Fore.GREEN}[✓] App created via direct endpoint!")
                        return self.get_credentials_from_apps()
            
            return None
            
        except Exception as e:
            print(f"{Fore.RED}[!] Telegram API error: {e}")
            return None
    
    def run_full_creation(self, phone):
        """Run the full creation process for a single phone"""
        print(f"\n{Fore.CYAN}" + "="*60)
        print(f"{Fore.CYAN}[*] Starting API creation for: {phone}")
        print(f"{Fore.CYAN}" + "="*60)
        
        # Reset session for each phone
        self.setup_new_session()
        
        # Step 1: Login
        if not self.login(phone):
            print(f"{Fore.RED}[!] Login failed for {phone}")
            return False
        
        # Step 2: Try multiple creation methods
        methods = [
            self.direct_api_create_app,
            self.web_api_create_app,
            self.create_app_telegram_api,
        ]
        
        credentials = None
        
        for method in methods:
            if credentials:
                break
                
            print(f"{Fore.YELLOW}[*] Trying method: {method.__name__}...")
            credentials = method()
            
            if credentials and 'api_id' in credentials and 'api_hash' in credentials:
                if credentials['api_id'] and credentials['api_hash']:
                    break
        
        # Final check
        if credentials and credentials.get('api_id') and credentials.get('api_hash'):
            self.show_results(phone, credentials['api_id'], credentials['api_hash'])
            return True
        else:
            print(f"{Fore.RED}[!] ALL auto-methods failed for {phone}!")
            print(f"{Fore.YELLOW}[*] But you're logged in! Trying ONE LAST METHOD...")
            self.last_resort_method(phone)
            return False
    
    def last_resort_method(self, phone):
        """Last resort: Create app using simulated browser"""
        print(f"{Fore.YELLOW}[*] Using simulated browser method...")
        
        try:
            # This simulates a full browser session
            import re
            
            # Get the create form with all details
            response = self.session.get('https://my.telegram.org/apps', timeout=15)
            
            # Check if we're on the right page
            if 'app_creation' in response.text or 'Create application' in response.text:
                # Extract all form fields
                form_fields = self.extract_all_form_fields(response.text)
                
                if form_fields:
                    print(f"{Fore.GREEN}[✓] Got form fields, submitting...")
                    
                    # Submit with all fields
                    submit_response = self.session.post(
                        'https://my.telegram.org/apps/create',
                        data=form_fields,
                        timeout=20
                    )
                    
                    if submit_response.status_code == 200:
                        print(f"{Fore.GREEN}[✓] Form submitted!")
                        
                        # Try to extract one more time
                        final_response = self.session.get('https://my.telegram.org/apps', timeout=15)
                        credentials = self.brute_force_extract(final_response.text)
                        
                        if credentials:
                            self.show_results(phone, credentials['api_id'], credentials['api_hash'])
                            return
            
            print(f"{Fore.RED}[!] Even last method failed for {phone}.")
            print(f"{Fore.CYAN}[*] However, you ARE logged in to: https://my.telegram.org")
            print(f"{Fore.CYAN}[*] Session cookies are active.")
            
        except Exception as e:
            print(f"{Fore.RED}[!] Last method error: {e}")
    
    def extract_all_form_fields(self, html):
        """Extract all form fields from HTML"""
        import re
        
        fields = {}
        
        # Extract all input fields
        input_pattern = r'<input[^>]+name=["\']([^"\']+)["\'][^>]+value=["\']([^"\']*)["\']'
        matches = re.findall(input_pattern, html, re.I)
        
        for name, value in matches:
            fields[name] = value
        
        # Add our app data
        random_suffix = self.generate_random_string(4)
        fields.update({
            'app_title': f'TelegramDesktop{random_suffix}',
            'app_shortname': f'tg{random_suffix}',
            'app_url': 'https://desktop.telegram.org',
            'app_platform': 'desktop',
            'app_desc': 'Official Telegram Desktop',
        })
        
        return fields
    
    def show_results(self, phone, api_id, api_hash):
        """Show successful results"""
        print(f"\n{Fore.GREEN}" + "="*60)
        print(f"{Fore.CYAN}    SUCCESS! API CREDENTIALS CREATED")
        print(f"{Fore.GREEN}" + "="*60)
        print(f"{Fore.YELLOW}Phone: {Fore.WHITE}{phone}")
        print(f"{Fore.YELLOW}API ID: {Fore.WHITE}{api_id}")
        print(f"{Fore.YELLOW}API Hash: {Fore.WHITE}{api_hash}")
        print(f"{Fore.GREEN}" + "="*60)
        
        # Save to multiple formats
        self.save_credentials(phone, api_id, api_hash)
        
        # Show usage examples
        self.show_usage_examples(api_id, api_hash, phone)
    
    def save_credentials(self, phone, api_id, api_hash):
        """Save credentials to files"""
        import os
        
        # Clean phone for filename
        clean_phone = phone.replace('+', '').replace(' ', '')
        
        # Save as text
        txt_content = f"""TELEGRAM API CREDENTIALS
=======================
Phone: {phone}
API ID: {api_id}
API Hash: {api_hash}
Generated: {time.strftime('%Y-%m-%d %H:%M:%S')}
By: @ogdigital
"""
        
        with open(f"api_{clean_phone}.txt", "w") as f:
            f.write(txt_content)
        
        # Save as JSON
        json_content = {
            "phone": phone,
            "api_id": int(api_id),
            "api_hash": api_hash,
            "app_title": "Telegram Desktop",
            "app_platform": "desktop",
            "generated": time.strftime('%Y-%m-%d %H:%M:%S')
        }
        
        with open(f"api_{clean_phone}.json", "w") as f:
            json.dump(json_content, f, indent=2)
        
        # Save as Python config
        py_content = f"""# Telegram API Configuration
API_ID = {api_id}
API_HASH = "{api_hash}"
PHONE = "{phone}"

# Pyrogram
from pyrogram import Client
app = Client("my_account", api_id=API_ID, api_hash=API_HASH, phone_number=PHONE)

# Telethon
from telethon import TelegramClient
client = TelegramClient('session', API_ID, API_HASH)
"""
        
        with open(f"api_{clean_phone}.py", "w") as f:
            f.write(py_content)
        
        print(f"{Fore.CYAN}[✓] Saved credentials to:")
        print(f"{Fore.YELLOW}    - api_{clean_phone}.txt")
        print(f"{Fore.YELLOW}    - api_{clean_phone}.json")
        print(f"{Fore.YELLOW}    - api_{clean_phone}.py")
    
    def show_usage_examples(self, api_id, api_hash, phone):
        """Show usage examples"""
        print(f"\n{Fore.CYAN}[*] Usage Examples:")
        print(f"{Fore.YELLOW}" + "-"*40)
        
        print(f"{Fore.GREEN}Pyrogram:")
        print(f"{Fore.WHITE}from pyrogram import Client")
        print(f"app = Client(")
        print(f"    'my_account',")
        print(f"    api_id={api_id},")
        print(f"    api_hash='{api_hash}',")
        print(f"    phone_number='{phone}'")
        print(f")")
        
        print(f"\n{Fore.GREEN}Telethon:")
        print(f"{Fore.WHITE}from telethon import TelegramClient")
        print(f"client = TelegramClient(")
        print(f"    'session',")
        print(f"    {api_id},")
        print(f"    '{api_hash}'")
        print(f")")

# Main execution with continuous loop
def main_loop():
    creator = TelegramAPIForceCreator()
    
    print(f"{Fore.CYAN}[*] TELEGRAM API CREATOR - CONTINUOUS MODE")
    print(f"{Fore.YELLOW}[*] This script will run in a loop until you stop it")
    print(f"{Fore.YELLOW}[*] Press Ctrl+C to stop at any time")
    print(f"{Fore.CYAN}" + "="*60)
    
    created_count = 0
    failed_count = 0
    
    while True:
        try:
            print(f"\n{Fore.CYAN}" + "="*60)
            print(f"{Fore.CYAN}[*] SESSION #{created_count + failed_count + 1}")
            print(f"{Fore.CYAN}[*] Stats: {Fore.GREEN}{created_count} created{Fore.WHITE} | {Fore.RED}{failed_count} failed")
            print(f"{Fore.CYAN}" + "="*60)
            
            print(f"\n{Fore.CYAN}[*] This script will:")
            print(f"{Fore.YELLOW}    1. Login to your Telegram account")
            print(f"{Fore.YELLOW}    2. Automatically create app")
            print(f"{Fore.YELLOW}    3. Extract API ID & Hash")
            print(f"{Fore.YELLOW}    4. Save to files")
            print()
            
            phone = input(f"{Fore.GREEN}[?] Enter phone (+91XXXXXXXXXX) or type 'exit' to stop: {Fore.YELLOW}")
            
            if phone.lower() == 'exit':
                print(f"\n{Fore.CYAN}[*] Exiting...")
                print(f"{Fore.GREEN}[*] Total created: {created_count}")
                print(f"{Fore.RED}[*] Total failed: {failed_count}")
                break
            
            # Validate phone number format
            if not phone.startswith('+'):
                print(f"{Fore.RED}[!] Phone must start with + (e.g., +911234567890)")
                failed_count += 1
                continue
            
            # Run creation process
            success = creator.run_full_creation(phone)
            
            if success:
                created_count += 1
            else:
                failed_count += 1
            
            # Ask if user wants to continue
            print(f"\n{Fore.CYAN}" + "="*60)
            print(f"{Fore.CYAN}[*] Creation completed for: {phone}")
            print(f"{Fore.GREEN}[*] Total created: {created_count}")
            print(f"{Fore.RED}[*] Total failed: {failed_count}")
            print(f"{Fore.CYAN}" + "="*60)
            
            # Small delay before next iteration
            time.sleep(1)
            
        except KeyboardInterrupt:
            print(f"\n{Fore.RED}[!] Interrupted by user")
            print(f"{Fore.CYAN}[*] Total created: {created_count}")
            print(f"{Fore.CYAN}[*] Total failed: {failed_count}")
            break
        except Exception as e:
            print(f"\n{Fore.RED}[!] Unexpected error: {e}")
            failed_count += 1
            # Continue with next iteration
    
    print(f"\n{Fore.CYAN}" + "="*60)
    print(f"{Fore.CYAN}[*] Script finished")
    print(f"{Fore.GREEN}[*] Total API created: {created_count}")
    print(f"{Fore.RED}[*] Total failed attempts: {failed_count}")
    print(f"{Fore.CYAN}[*] Files saved in current directory")
    print(f"{Fore.CYAN}" + "="*60)
    
    input(f"\n{Fore.CYAN}Press Enter to exit...")

if __name__ == "__main__":
    try:
        main_loop()
    except KeyboardInterrupt:
        print(f"\n{Fore.RED}[!] Script stopped by user")
    except Exception as e:
        print(f"\n{Fore.RED}[!] Fatal error: {e}")
        input(f"\n{Fore.CYAN}Press Enter to exit...")