import os
import shutil
import time
import subprocess
import ctypes
import threading
import sys
import json

# --- KÜTÜPHANE OTOMASYONU ---
def install_requirements():
    try:
        import customtkinter as ctk
        from rich.console import Console
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter", "rich"])

install_requirements()

import customtkinter as ctk
from tkinter import messagebox
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.prompt import Prompt

console = Console()
CONFIG_FILE = "cleaner_settings.json"

# --- TEMA MOTORU VE AYARLAR ---
THEMES = {
    "Atlas Karanlık": {"mode": "Dark", "color": "blue"},
    "Zümrüt": {"mode": "Dark", "color": "green"},
    "Siber": {"mode": "Dark", "color": "dark-blue"},
    "Aydınlık": {"mode": "Light", "color": "blue"},
    "Kırmızı Gece": {"mode": "Dark", "color": "blue"}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f: return json.load(f)
        except: pass
    return {"theme": "Atlas Karanlık"}

def save_config(theme_name):
    with open(CONFIG_FILE, "w") as f: json.dump({"theme": theme_name}, f)

# --- SİSTEM ÇEKİRDEĞİ ---
class CleanerEngine:
    @staticmethod
    def clean(paths):
        results = []
        for path in paths:
            if not os.path.exists(path): continue
            deleted = 0
            for item in os.listdir(path):
                try:
                    p = os.path.join(path, item)
                    if os.path.isfile(p) or os.path.islink(p): os.unlink(p)
                    else: shutil.rmtree(p)
                    deleted += 1
                except: pass
            results.append((path, deleted))
        return results

    @staticmethod
    def get_updates():
        try:
            # Atlas OS'ta winget genelde hazır gelir
            res = subprocess.run(["winget", "upgrade"], capture_output=True, text=True, encoding='utf-8', errors='ignore')
            return res.stdout if "upgrade" in res.stdout.lower() else "Sisteminiz tamamen güncel!"
        except: return "Winget erişilemedi!"

# --- MODERN GUI (Yenilenmiş Tema Mantığı) ---
class ModernGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        self.apply_theme_settings()
        
        self.title("WinCleaner Pro - Atlas OS")
        self.geometry("850x600")
        
        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=180, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(self.sidebar, text="WIN CLEANER", font=("Orbitron", 18, "bold")).pack(pady=20)

        # Navigasyon
        self.btn_clean = ctk.CTkButton(self.sidebar, text="🧹 Temizlik", command=self.show_clean).pack(pady=5, padx=10)
        self.btn_update = ctk.CTkButton(self.sidebar, text="🚀 Güncelleme", command=self.show_update).pack(pady=5, padx=10)
        self.btn_theme = ctk.CTkButton(self.sidebar, text="🎨 Tema", command=self.show_theme).pack(pady=5, padx=10)

        # Main Container
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)
        
        self.current_page = None
        self.show_clean()

    def apply_theme_settings(self):
        theme = self.config_data["theme"]
        ctk.set_appearance_mode(THEMES[theme]["mode"])
        ctk.set_default_color_theme(THEMES[theme]["color"])

    def show_clean(self):
        self.clear_main()
        ctk.CTkLabel(self.main_view, text="Güvenli Temizlik Paneli", font=("Arial", 22, "bold")).pack(anchor="w")
        
        self.log_box = ctk.CTkTextbox(self.main_view, height=300)
        self.log_box.pack(fill="both", expand=True, pady=10)
        
        ctk.CTkButton(self.main_view, text="TEMİZLİĞE BAŞLA", fg_color="#E74C3C", command=self.run_clean_task).pack(fill="x")

    def run_clean_task(self):
        self.log_box.insert("end", "Temizlik işlemi başlatıldı...\n")
        def work():
            paths = [os.environ.get('TEMP'), "C:\\Windows\\Temp"]
            results = CleanerEngine.clean(paths)
            for path, count in results:
                self.after(0, lambda p=path, c=count: self.log_box.insert("end", f"> {p}: {c} dosya silindi.\n"))
        threading.Thread(target=work, daemon=True).start()

    def show_update(self):
        self.clear_main()
        ctk.CTkLabel(self.main_view, text="Uygulama Güncellemeleri", font=("Arial", 22, "bold")).pack(anchor="w")
        
        self.upd_box = ctk.CTkTextbox(self.main_view, height=350)
        self.upd_box.pack(fill="both", expand=True, pady=10)
        
        btn_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text="Tara", command=self.scan_updates).pack(side="left", expand=True, padx=5)
        ctk.CTkButton(btn_frame, text="Tümünü Güncelle", fg_color="#2ECC71", command=self.install_updates).pack(side="right", expand=True, padx=5)

    def scan_updates(self):
        self.upd_box.insert("end", "Güncellemeler taranıyor...\n")
        threading.Thread(target=lambda: self.after(0, lambda: self.upd_box.insert("end", CleanerEngine.get_updates())), daemon=True).start()

    def install_updates(self):
        def work():
            proc = subprocess.Popen(["winget", "upgrade", "--all", "--accept-package-agreements"], 
                                    stdout=subprocess.PIPE, text=True, stderr=subprocess.STDOUT)
            for line in iter(proc.stdout.readline, ""):
                self.after(0, lambda l=line: [self.upd_box.insert("end", l), self.upd_box.see("end")])
        threading.Thread(target=work, daemon=True).start()

    def show_theme(self):
        self.clear_main()
        ctk.CTkLabel(self.main_view, text="Tema Ayarları", font=("Arial", 22, "bold")).pack(anchor="w")
        for t_name in THEMES.keys():
            ctk.CTkButton(self.main_view, text=t_name, command=lambda n=t_name: self.update_theme(n)).pack(pady=5, fill="x")

    def update_theme(self, name):
        save_config(name)
        # İşte "Restart" gerektirmeyen sihirli geçiş
        self.destroy() # Mevcut pencereyi kapat
        ModernGUI().mainloop() # Yeni pencereyi aynı tema ayarlarıyla aç

    def clear_main(self):
        for widget in self.main_view.winfo_children(): widget.destroy()

# --- GELİŞMİŞ CLI ---
def run_cli():
    while True:
        console.clear()
        console.print(Panel("[bold cyan]WIN CLEANER PRO - CLI[/bold cyan]\nAtlas OS Edition", border_style="blue"))
        
        table = Table(show_header=False, box=None)
        table.add_row("[1] Hızlı Temizlik", "[2] Güncellemeleri Tara")
        table.add_row("[3] Tümünü Güncelle", "[4] GUI Moduna Geç")
        table.add_row("[0] Çıkış", "")
        console.print(table)

        choice = Prompt.ask("\nİşlem seçin", choices=["1", "2", "3", "4", "0"])

        if choice == "1":
            results = CleanerEngine.clean([os.environ.get('TEMP'), "C:\\Windows\\Temp"])
            for p, c in results: console.print(f"[green]✔[/green] {p}: {c} dosya temizlendi.")
            time.sleep(2)
        elif choice == "2":
            console.print("[yellow]Taranıyor...[/yellow]")
            console.print(CleanerEngine.get_updates())
            input("\nDevam etmek için Enter...")
        elif choice == "3":
            os.system("winget upgrade --all --accept-package-agreements")
            input("\nBitti. Enter...")
        elif choice == "4":
            ModernGUI().mainloop()
            break
        elif choice == "0":
            break

if __name__ == "__main__":
    if "--cli" in sys.argv:
        run_cli()
    else:
        # Varsayılan olarak GUI açılır ama CLI her zaman hazır
        try:
            app = ModernGUI()
            app.mainloop()
        except Exception as e:
            console.print(f"[red]Hata oluştu, CLI başlatılıyor: {e}[/red]")
            run_cli()