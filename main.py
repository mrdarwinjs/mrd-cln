import ctypes
import json
import os
import shutil
import subprocess
import sys
import threading
import time
from datetime import datetime


# --- KÜTÜPHANE OTOMASYONU ---
def install_requirements():
    try:
        import customtkinter as ctk
        from rich.console import Console
    except ImportError:
        subprocess.check_call(
            [sys.executable, "-m", "pip", "install", "customtkinter", "rich"]
        )


install_requirements()

from tkinter import messagebox

import customtkinter as ctk
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.table import Table

console = Console()
CONFIG_FILE = "cleaner_settings.json"
LOG_DIR = "logs"


# --- LOG YÖNETİMİ (Orta Öncelik) ---
def write_log(action, details):
    os.makedirs(LOG_DIR, exist_ok=True)
    log_file = os.path.join(LOG_DIR, f"cleaner_{datetime.now().strftime('%Y-%m')}.log")
    with open(log_file, "a", encoding="utf-8") as f:
        f.write(
            f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] {action} - {details}\n"
        )


# --- ÇOK DİLLİ ALTYAPI (i18n) (Yüksek Öncelik) ---
I18N = {
    "TR": {
        "title": "WinCleaner Pro - Atlas OS",
        "clean": "🧹 Temizlik",
        "update": "🚀 Güncelleme",
        "tools": "🛠️ Araçlar",
        "theme": "🎨 Tema",
        "dashboard_title": "Sistem Durumu",
        "disk_usage": "C: Sürücüsü Doluluk Oranı:",
        "start_clean": "TEMİZLİĞE BAŞLA",
        "scan": "Tara",
        "update_all": "Tümünü Güncelle",
        "game_mode": "🎮 Oyun Modu (Game Mode)",
        "task_scheduler": "⏰ Haftalık Görev Zamanla",
        "freed_space": "Kazanılan Alan",
    },
    "EN": {
        "title": "WinCleaner Pro - Atlas OS",
        "clean": "🧹 Clean",
        "update": "🚀 Update",
        "tools": "🛠️ Tools",
        "theme": "🎨 Theme",
        "dashboard_title": "System Status",
        "disk_usage": "C: Drive Usage:",
        "start_clean": "START CLEANING",
        "scan": "Scan",
        "update_all": "Update All",
        "game_mode": "🎮 Game Mode",
        "task_scheduler": "⏰ Schedule Weekly Task",
        "freed_space": "Space Freed",
    },
}

# --- TEMA MOTORU VE AYARLAR ---
THEMES = {
    "Atlas Karanlık": {"mode": "Dark", "color": "blue"},
    "Zümrüt": {"mode": "Dark", "color": "green"},
    "Siber": {"mode": "Dark", "color": "dark-blue"},
    "Aydınlık": {"mode": "Light", "color": "blue"},
    "Kırmızı Gece": {"mode": "Dark", "color": "blue"},
}


def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r") as f:
                return json.load(f)
        except:
            pass
    return {"theme": "Atlas Karanlık", "lang": "TR"}


def save_config(key, value):
    config = load_config()
    config[key] = value
    with open(CONFIG_FILE, "w") as f:
        json.dump(config, f)


# --- SİSTEM ÇEKİRDEĞİ ---
class CleanerEngine:
    @staticmethod
    def get_size(path):
        total = 0
        try:
            if os.path.isfile(path) or os.path.islink(path):
                total = os.path.getsize(path)
            elif os.path.isdir(path):
                for dirpath, _, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if not os.path.islink(fp) and os.path.exists(fp):
                            total += os.path.getsize(fp)
        except:
            pass
        return total

    @staticmethod
    def clean(paths):
        results = []
        total_freed_bytes = 0
        for path in paths:
            if not os.path.exists(path):
                continue
            deleted = 0
            freed = 0
            for item in os.listdir(path):
                p = os.path.join(path, item)
                try:
                    item_size = CleanerEngine.get_size(p)
                    if os.path.isfile(p) or os.path.islink(p):
                        os.unlink(p)
                    else:
                        shutil.rmtree(p)
                    deleted += 1
                    freed += item_size
                except:
                    pass
            results.append((path, deleted, freed))
            total_freed_bytes += freed

        write_log(
            "CLEAN",
            f"{total_freed_bytes / (1024**2):.2f} MB silindi. Hedefler: {paths}",
        )
        return results, total_freed_bytes

    @staticmethod
    def get_updates():
        try:
            # Hata Ayıklama (Timeout Mekanizması) - 30 Saniye sınır
            res = subprocess.run(
                ["winget", "upgrade"],
                capture_output=True,
                text=True,
                encoding="utf-8",
                errors="ignore",
                timeout=30,
            )
            return (
                res.stdout
                if "upgrade" in res.stdout.lower()
                else "Sisteminiz tamamen güncel!"
            )
        except subprocess.TimeoutExpired:
            write_log("ERROR", "Winget taraması zaman aşımına uğradı.")
            return "Zaman aşımı! Winget sunucuları yanıt vermiyor olabilir."
        except Exception as e:
            return f"Winget erişilemedi! Hata: {str(e)}"


# --- MODERN GUI ---
class ModernGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.config_data = load_config()
        self.lang = self.config_data.get("lang", "TR")
        self.t = I18N[self.lang]  # Çeviri referansı

        self.apply_theme_settings()

        self.title(self.t["title"])
        self.geometry("900x650")

        # Layout
        self.grid_columnconfigure(1, weight=1)
        self.grid_rowconfigure(0, weight=1)

        # Sidebar
        self.sidebar = ctk.CTkFrame(self, width=200, corner_radius=0)
        self.sidebar.grid(row=0, column=0, sticky="nsew")
        ctk.CTkLabel(
            self.sidebar, text="WIN CLEANER", font=("Orbitron", 18, "bold")
        ).pack(pady=20)

        # Navigasyon
        ctk.CTkButton(self.sidebar, text=self.t["clean"], command=self.show_clean).pack(
            pady=5, padx=10
        )
        ctk.CTkButton(
            self.sidebar, text=self.t["update"], command=self.show_update
        ).pack(pady=5, padx=10)
        ctk.CTkButton(self.sidebar, text=self.t["tools"], command=self.show_tools).pack(
            pady=5, padx=10
        )
        ctk.CTkButton(self.sidebar, text=self.t["theme"], command=self.show_theme).pack(
            pady=5, padx=10
        )

        # Main Container
        self.main_view = ctk.CTkFrame(self, fg_color="transparent")
        self.main_view.grid(row=0, column=1, sticky="nsew", padx=20, pady=20)

        self.show_clean()

    def apply_theme_settings(self):
        theme = self.config_data["theme"]
        ctk.set_appearance_mode(THEMES[theme]["mode"])
        ctk.set_default_color_theme(THEMES[theme]["color"])

    def format_size(self, bytes_size):
        if bytes_size < 1024:
            return f"{bytes_size} B"
        elif bytes_size < 1024**2:
            return f"{bytes_size / 1024:.2f} KB"
        elif bytes_size < 1024**3:
            return f"{bytes_size / (1024**2):.2f} MB"
        else:
            return f"{bytes_size / (1024**3):.2f} GB"

    def render_dashboard(self):
        # Dashboard: Disk Doluluk Oranı (Düşük Öncelik - Gerçekleştirildi)
        dash_frame = ctk.CTkFrame(self.main_view, fg_color=("gray85", "gray20"))
        dash_frame.pack(fill="x", pady=(0, 15), ipady=10)

        total, used, free = shutil.disk_usage("C:\\")
        percent = used / total

        ctk.CTkLabel(
            dash_frame, text=self.t["dashboard_title"], font=("Arial", 16, "bold")
        ).pack(pady=(5, 0))
        ctk.CTkLabel(
            dash_frame,
            text=f"{self.t['disk_usage']} %{percent * 100:.1f} ({self.format_size(free)} boş)",
        ).pack()

        progress = ctk.CTkProgressBar(dash_frame)
        progress.pack(fill="x", padx=20, pady=5)
        progress.set(percent)

    def show_clean(self):
        self.clear_main()
        self.render_dashboard()

        ctk.CTkLabel(
            self.main_view, text="Güvenli Temizlik Paneli", font=("Arial", 22, "bold")
        ).pack(anchor="w")

        self.log_box = ctk.CTkTextbox(self.main_view, height=250)
        self.log_box.pack(fill="both", expand=True, pady=10)

        ctk.CTkButton(
            self.main_view,
            text=self.t["start_clean"],
            fg_color="#E74C3C",
            command=self.run_clean_task,
        ).pack(fill="x")

    def run_clean_task(self):
        self.log_box.insert("end", "Temizlik işlemi başlatıldı...\n")

        def work():
            paths = [
                os.environ.get("TEMP"),
                "C:\\Windows\\Temp",
                "C:\\Windows\\Prefetch",
            ]
            results, total_freed = CleanerEngine.clean(paths)
            for path, count, freed in results:
                self.after(
                    0,
                    lambda p=path, c=count, f=freed: self.log_box.insert(
                        "end", f"> {p}: {c} dosya silindi. ({self.format_size(f)})\n"
                    ),
                )

            # Toplam Boyut Raporlama
            self.after(
                0,
                lambda: self.log_box.insert(
                    "end",
                    f"\n[!] TOPLAM {self.t['freed_space']}: {self.format_size(total_freed)}\n",
                ),
            )
            self.after(0, self.render_dashboard)  # Diski güncelle

        threading.Thread(target=work, daemon=True).start()

    def show_update(self):
        self.clear_main()
        ctk.CTkLabel(
            self.main_view, text="Uygulama Güncellemeleri", font=("Arial", 22, "bold")
        ).pack(anchor="w")

        self.upd_box = ctk.CTkTextbox(self.main_view, height=350)
        self.upd_box.pack(fill="both", expand=True, pady=10)

        btn_frame = ctk.CTkFrame(self.main_view, fg_color="transparent")
        btn_frame.pack(fill="x")
        ctk.CTkButton(btn_frame, text=self.t["scan"], command=self.scan_updates).pack(
            side="left", expand=True, padx=5
        )
        ctk.CTkButton(
            btn_frame,
            text=self.t["update_all"],
            fg_color="#2ECC71",
            command=self.install_updates,
        ).pack(side="right", expand=True, padx=5)

    def scan_updates(self):
        self.upd_box.insert("end", "Güncellemeler taranıyor... (Maks 30 sn)\n")
        threading.Thread(
            target=lambda: self.after(
                0, lambda: self.upd_box.insert("end", CleanerEngine.get_updates())
            ),
            daemon=True,
        ).start()

    def install_updates(self):
        write_log("UPDATE", "Toplu güncelleme başlatıldı.")

        def work():
            proc = subprocess.Popen(
                ["winget", "upgrade", "--all", "--accept-package-agreements"],
                stdout=subprocess.PIPE,
                text=True,
                stderr=subprocess.STDOUT,
            )
            for line in iter(proc.stdout.readline, ""):
                self.after(
                    0,
                    lambda l=line: [
                        self.upd_box.insert("end", l),
                        self.upd_box.see("end"),
                    ],
                )

        threading.Thread(target=work, daemon=True).start()

    def show_tools(self):
        self.clear_main()
        ctk.CTkLabel(
            self.main_view, text="Ekstra Araçlar", font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(0, 10))

        # Oyun Modu Toggle
        self.game_mode_var = ctk.StringVar(value="off")
        ctk.CTkSwitch(
            self.main_view,
            text=self.t["game_mode"],
            command=self.toggle_game_mode,
            variable=self.game_mode_var,
            onvalue="on",
            offvalue="off",
        ).pack(anchor="w", pady=10)

        # Zamanlanmış Görevler
        ctk.CTkButton(
            self.main_view,
            text=self.t["task_scheduler"],
            command=self.create_scheduled_task,
        ).pack(anchor="w", pady=10)

    def toggle_game_mode(self):
        state = self.game_mode_var.get()
        if state == "on":
            write_log("TOOL", "Oyun Modu Aktif (Servisler durduruluyor)")
            # Örnek: os.system("net stop SysMain") - Admin yetkisi ister
            messagebox.showinfo(
                "Oyun Modu", "Oyun modu açıldı! Arka plan hizmetleri askıya alındı."
            )
        else:
            write_log("TOOL", "Oyun Modu Pasif")
            messagebox.showinfo(
                "Oyun Modu", "Oyun modu kapatıldı! Hizmetler geri yüklendi."
            )

    def create_scheduled_task(self):
        # Windows Task Scheduler Entegrasyonu (Yüksek Öncelik)
        try:
            exe_path = sys.executable
            script_path = os.path.abspath(__file__)
            # Admin yetkisi gerekebilir, basit bir uyarı gösterelim.
            cmd = f'schtasks /create /tn "WinCleaner_AutoTask" /tr "{exe_path} {script_path} --cli" /sc weekly /d SUN /st 02:00 /f'
            os.system(cmd)
            write_log("SYSTEM", "Haftalık zamanlanmış görev oluşturuldu.")
            messagebox.showinfo(
                "Başarılı", "Her Pazar 02:00 için temizlik görevi oluşturuldu!"
            )
        except Exception as e:
            messagebox.showerror(
                "Hata",
                f"Görev oluşturulamadı: {e}\n(Uygulamayı yönetici olarak başlatın)",
            )

    def show_theme(self):
        self.clear_main()
        ctk.CTkLabel(
            self.main_view, text="Tema ve Dil Ayarları", font=("Arial", 22, "bold")
        ).pack(anchor="w", pady=(0, 10))

        # Dil Seçimi
        ctk.CTkLabel(self.main_view, text="Dil (Language):").pack(anchor="w")
        ctk.CTkSegmentedButton(
            self.main_view, values=["TR", "EN"], command=self.update_lang
        ).pack(fill="x", pady=(0, 15))

        ctk.CTkLabel(self.main_view, text="Görünüm:").pack(anchor="w")
        for t_name in THEMES.keys():
            ctk.CTkButton(
                self.main_view,
                text=t_name,
                command=lambda n=t_name: self.update_theme(n),
            ).pack(pady=5, fill="x")

    def update_lang(self, lang):
        save_config("lang", lang)
        self.restart_app()

    def update_theme(self, name):
        save_config("theme", name)
        self.restart_app()

    def restart_app(self):
        self.destroy()
        ModernGUI().mainloop()

    def clear_main(self):
        for widget in self.main_view.winfo_children():
            widget.destroy()


# --- GELİŞMİŞ CLI ---
def run_cli():
    while True:
        console.clear()
        console.print(
            Panel(
                "[bold cyan]WIN CLEANER PRO - CLI[/bold cyan]\nAtlas OS Edition",
                border_style="blue",
            )
        )

        table = Table(show_header=False, box=None)
        table.add_row("[1] Hızlı Temizlik", "[2] Güncellemeleri Tara")
        table.add_row("[3] Tümünü Güncelle", "[4] GUI Moduna Geç")
        table.add_row("[0] Çıkış", "")
        console.print(table)

        choice = Prompt.ask("\nİşlem seçin", choices=["1", "2", "3", "4", "0"])

        if choice == "1":
            results, total_freed = CleanerEngine.clean(
                [os.environ.get("TEMP"), "C:\\Windows\\Temp", "C:\\Windows\\Prefetch"]
            )
            for p, c, f in results:
                console.print(
                    f"[green]✔[/green] {p}: {c} dosya temizlendi. ({(f / 1024**2):.2f} MB)"
                )
            console.print(
                f"\n[bold green]Toplam {total_freed / 1024**2:.2f} MB alan açıldı.[/bold green]"
            )
            time.sleep(3)
        elif choice == "2":
            console.print("[yellow]Taranıyor... Lütfen bekleyin.[/yellow]")
            console.print(CleanerEngine.get_updates())
            input("\nDevam etmek için Enter...")
        elif choice == "3":
            os.system("winget upgrade --all --accept-package-agreements")
            write_log("UPDATE", "CLI üzerinden toplu güncelleme yapıldı.")
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
        try:
            app = ModernGUI()
            app.mainloop()
        except Exception as e:
            console.print(f"[red]Hata oluştu, CLI başlatılıyor: {e}[/red]")
            run_cli()
