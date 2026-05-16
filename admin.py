import os
import sys
import json
import uuid
import re
import threading
import platform
import time
from datetime import datetime, timedelta
from firebase_client import FirebaseClient
import config

# -------------------- Internal UI Library (WEB TOOL Signature Style) --------------------

def get_terminal_width():
    try:
        width = os.get_terminal_size().columns
        return width if width > 20 else 80
    except:
        return 80

class Console:
    def __init__(self):
        self.X = '\x1b[1;37m'; self.G = '\x1b[38;5;46m'; self.Y = '\x1b[38;5;220m'
        self.CYAN = '\x1b[38;5;51m'; self.RED = '\x1b[38;5;196m'; self.RESET = '\x1b[0m'
        self.BOLD = '\x1b[1m'; self.DIM = '\x1b[2m'

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
    def center_text(self, text, width):
        clean = self._strip_tags(text); padding = (width - len(clean)) // 2
        return " " * max(0, padding) + text

console = Console()

def safe_input(prompt: str) -> str:
    val = console.input(prompt)
    if val.strip().lower() == "/exit": sys.exit(0)
    return val

def linex(): console.print(f"[dim]{'─' * get_terminal_width()}[/dim]")

def show_panel(text, title=None, subtitle=None, style="dim"):
    width = get_terminal_width()
    top = f"╭──┤ {title} ├" if title else "╭"
    if subtitle: top += f"─┤ {subtitle} ├"
    top += "─" * (width - len(console._strip_tags(top)) - 1) + "╮"
    console.print(f"[{style}]{top}[/{style}]")
    for line in text.strip('\n').split('\n'):
        clean = console._strip_tags(line); padding = width - len(clean) - 2
        console.print(f"[{style}]│[/{style}] {line}{' ' * max(0, padding)} [{style}]│[/{style}]")
    bottom = "╰" + "─" * (width - 2) + "╯"
    console.print(f"[{style}]{bottom}[/{style}]")

def show_success(msg): console.print(f" [bold green]✓[/bold green] {msg}")
def show_error(msg): console.print(f" [bold red]×[/bold red] {msg}")

# -------------------- Admin Logic --------------------

db = FirebaseClient()

def admin_header():
    os.system('clear')
    width = get_terminal_width()
    # Ant-style 6-line block art for ADMIN
    art = [
        " █████╗ ██████╗ ███╗   ███╗██╗███╗   ██╗",
        "██╔══██╗██╔══██╗████╗ ████║██║████╗  ██║",
        "███████║██║  ██║██╔████╔██║██║██╔██╗ ██║",
        "██╔══██║██║  ██║██║╚██╔╝██║██║██║╚██╗██║",
        "██║  ██║██████╔╝██║ ╚═╝ ██║██║██║ ╚████║",
        "╚═╝  ╚═╝╚═════╝ ╚═╝     ╚═╝╚═╝╚═╝  ╚═══╝"
    ]
    
    console.print("\n".join([console.center_text(line, width) for line in art]))
    console.print("\n" + console.center_text("[bold yellow]WEB TOOL ADMIN PANEL[/bold yellow]", width) + "\n")
    linex()

def add_key():
    admin_header()
    console.print("\n [bold yellow]KEY GENERATION[/bold yellow]")
    linex()
    user_name = safe_input(" [?] Target User Name : ")
    if not user_name: return
    key = str(uuid.uuid4()).upper()[:8]
    console.print(f"\n [bold cyan]DURATION OPTIONS[/bold cyan]")
    linex()
    console.print(" ◆ [bold yellow]1[/bold yellow]  7 Days")
    console.print(" ◆ [bold yellow]2[/bold yellow]  15 Days")
    console.print(" ◆ [bold yellow]3[/bold yellow]  30 Days")
    console.print(" ◆ [bold yellow]4[/bold yellow]  Lifetime")
    linex()
    dur_choice = safe_input(" [?] Selection : ")
    days = {"1": 7, "2": 15, "3": 30, "4": 3650}.get(dur_choice, 7)
    expiry_date = (datetime.now() + timedelta(days=days)).strftime("%Y-%m-%d")
    data = {'name': user_name, 'key': key, 'expiry': expiry_date, 'status': 'PAID', 'added_on': datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
    linex()
    if db.set_data(f'keys/{key}', data):
        res = f"--- key created\n ▎ [bold green]user[/bold green]   {user_name}\n ▎ [bold green]key[/bold green]    {key}\n ▎ [bold green]expiry[/bold green] {expiry_date}"
        show_panel(res, title="SUCCESS", style="green")
    else: show_error("Failed to save key.")
    safe_input("\n [?] Press Enter to continue...")

def view_keys():
    admin_header()
    console.print("\n [bold yellow]GENERATED KEYS[/bold yellow]")
    linex()
    keys_data = db.get_data('keys')
    if not keys_data:
        show_error("No keys found in database.")
    else:
        for k, v in keys_data.items():
            hwid_stat = "[bold green]LINKED[/bold green]" if v.get('hwid') else "[dim]OPEN[/dim]"
            console.print(f" ◆ [bold cyan]{k}[/bold cyan] | {v.get('name', 'N/A'):<10} | Exp: {v.get('expiry', 'N/A')} | {hwid_stat}")
    linex()
    safe_input("\n [?] Press Enter to continue...")

def manage_key():
    admin_header()
    console.print("\n [bold yellow]KEY MANAGEMENT[/bold yellow]")
    linex()
    target_key = safe_input(" [?] Enter Key to Manage : ").upper()
    if not target_key: return
    
    key_data = db.get_data(f'keys/{target_key}')
    if not key_data:
        show_error("Key not found!")
        time.sleep(2); return

    while True:
        admin_header()
        info = f"--- key info\n ▎ [bold cyan]user[/bold cyan]   {key_data.get('name')}\n ▎ [bold cyan]expiry[/bold cyan] {key_data.get('expiry')}\n ▎ [bold cyan]hwid[/bold cyan]   {key_data.get('hwid', 'Not Registered')}"
        show_panel(info, title=f"MANAGING: {target_key}", style="yellow")
        
        console.print("\n [bold yellow]ACTIONS[/bold yellow]")
        linex()
        console.print(" ◆ [bold yellow]01[/bold yellow]  Reset HWID (Unlock Device)")
        console.print(" ◆ [bold yellow]02[/bold yellow]  Update Expiry Date")
        console.print(" ◆ [bold yellow]03[/bold yellow]  Delete Key")
        console.print(" ◆ [bold yellow]00[/bold yellow]  Back")
        linex()
        
        choice = safe_input(" [?] Selection : ")
        if choice == '1':
            if db.update_data(f'keys/{target_key}', {'hwid': None}):
                show_success("HWID Reset Successful!"); key_data['hwid'] = None
            else: show_error("Update failed!")
        elif choice == '2':
            new_date = safe_input(" [?] New Expiry (YYYY-MM-DD) : ")
            if re.match(r'\d{4}-\d{2}-\d{2}', new_date):
                if db.update_data(f'keys/{target_key}', {'expiry': new_date}):
                    show_success("Expiry Updated!"); key_data['expiry'] = new_date
                else: show_error("Update failed!")
            else: show_error("Invalid date format!")
        elif choice == '3':
            confirm = safe_input(" [!] Are you sure? (y/n): ")
            if confirm.lower() == 'y':
                if db.put_data(f'keys/{target_key}', None):
                    show_success("Key Deleted!"); break
                else: show_error("Delete failed!")
        elif choice == '0': break
        time.sleep(2)

def main():
    while True:
        admin_header()
        console.print("\n [bold yellow]MAIN MENU[/bold yellow]")
        linex()
        console.print(" ◆ [bold yellow]01[/bold yellow]  Generate New Key")
        console.print(" ◆ [bold yellow]02[/bold yellow]  View Generated Keys")
        console.print(" ◆ [bold yellow]03[/bold yellow]  Manage Existing Key")
        console.print(" ◆ [bold yellow]00[/bold yellow]  Exit")
        linex()
        choice = safe_input("\n [?] Selection : ")
        if choice == '1': add_key()
        elif choice == '2': view_keys()
        elif choice == '3': manage_key()
        elif choice == '0': sys.exit(0)


if __name__ == '__main__':
    main()
