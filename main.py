import os
import shutil
import time
import subprocess
import ctypes
import threading
import sys
import json

# --- PRELOAD / PERFORMANS AYARI ---
try:
    import customtkinter as ctk
    from tkinter import messagebox
    from rich.console import Console
    from rich.panel import Panel
    from rich.prompt import Prompt
    from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
    from rich.table import Table
    from rich.text import Text
    import rich.box as box
except ImportError as e:
    print(f"Hata: Eksik kütüphane tespit edildi! Lütfen terminalde çalıştırın: pip install customtkinter rich")
    sys.exit(1)

console = Console()
CONFIG_FILE = "cleaner_config.json"

# Windows'ta CMD penceresinin anlık açılıp kapanmasını engellemek için
CREATE_NO_WINDOW = 0x08000000 if os.name == 'nt' else 0

# --- TEMA SİSTEMİ ---
THEMES = {
    "Sistem Varsayılanı": {"mode": "System", "color": "blue"},
    "Gece Mavisi": {"mode": "Dark", "color": "blue"},
    "Orman Yeşili": {"mode": "Dark", "color": "green"},
    "Siberpunk": {"mode": "Dark", "color": "dark-blue"},
    "Aydınlık Mavi": {"mode": "Light", "color": "blue"}
}

def load_config():
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass
    return {"theme": "Sistem Varsayılanı"}

def save_config(theme_name):
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        json.dump({"theme": theme_name}, f, indent=4)

# Uygulama başlamadan önce temayı yükle
current_config = load_config()
selected_theme = current_config.get("theme", "Sistem Varsayılanı")
if selected_theme not in THEMES:
    selected_theme = "Sistem Varsayılanı"

ctk.set_appearance_mode(THEMES[selected_theme]["mode"])
ctk.set_default_color_theme(THEMES[selected_theme]["color"])

# --- YARDIMCI FONKSİYONLAR ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_size_format(b, factor=1024, suffix="B"):
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor: return f"{b:.2f} {unit}{suffix}"
        b /= factor
    return f"{b:.2f} Y{suffix}"

# --- ÇEKİRDEK MANTIK ---
class CleaningCore:
    def __init__(self):
        self.targets = {
            "User Temp": {"path": os.environ.get('TEMP'), "active": True},
            "System Temp": {"path": r"C:\Windows\Temp", "active": False},
            "Prefetch": {"path": r"C:\Windows\Prefetch", "active": False}
        }

    def scan_system(self):
        files_to_clean, total_size = [], 0
        for name, data in self.targets.items():
            if not data["active"]: continue
            folder = data["path"]
            if not os.path.exists(folder): continue
            try:
                for item in os.listdir(folder):
                    item_path = os.path.join(folder, item)
                    files_to_clean.append(item_path)
                    try:
                        if os.path.isfile(item_path) or os.path.islink(item_path):
                            total_size += os.path.getsize(item_path)
                        elif os.path.isdir(item_path):
                            total_size += sum(os.path.getsize(os.path.join(dirpath, filename)) 
                                              for dirpath, _, filenames in os.walk(item_path) 
                                              for filename in filenames)
                    except Exception: pass
            except PermissionError: pass
        return files_to_clean, total_size

    @staticmethod
    def run_defrag_logic():
        try:
            subprocess.run(["dfrgui.exe"], check=True, creationflags=CREATE_NO_WINDOW)
            return "SUCCESS"
        except OSError as e:
            if getattr(e, 'winerror', None) == 740: return "ADMIN_REQUIRED"
            return f"ERROR: {e}"

    @staticmethod
    def check_updates():
        """Winget kullanarak Atlas OS'a uygun (sadece app/driver) güncellemeleri tarar."""
        try:
            result = subprocess.run(["winget", "upgrade"], capture_output=True, text=True, creationflags=CREATE_NO_WINDOW)
            return result.stdout if result.stdout else "Güncellenecek paket bulunamadı veya Winget yüklü değil."
        except Exception as e:
            return f"Hata: {e}\n(Winget sisteminizde yüklü olmayabilir)"

    @staticmethod
    def install_updates():
        """Tüm uygun uygulamaları günceller."""
        try:
            subprocess.run(["winget", "upgrade", "--all", "--accept-source-agreements", "--accept-package-agreements"], creationflags=CREATE_NO_WINDOW)
            return True
        except Exception:
            return False

core = CleaningCore()

# --- GUI SINIFI ---
class CleanerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows Cleaner Pro - Atlas OS Edition")
        self.geometry("750x600")
        self.resizable(False, False)
        
        self.setup_ui()

    def setup_ui(self):
        # Sol Menü (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=160, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="WinCleaner\nPRO", font=ctk.CTkFont(size=22, weight="bold"))
        self.logo_label.pack(pady=20, padx=20)
        
        self.status_label = ctk.CTkLabel(self.sidebar, text=f"Admin: {'✅' if is_admin() else '❌'}", font=ctk.CTkFont(weight="bold"))
        self.status_label.pack(pady=10)

        self.freed_space_label = ctk.CTkLabel(self.sidebar, text="Kazanılan Alan\n0.00 B", font=ctk.CTkFont(size=14), text_color="#2FA572")
        self.freed_space_label.pack(side="bottom", pady=20)

        # Ana İçerik Alanı
        self.main_frame = ctk.CTkFrame(self)
        self.main_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Sekmeler
        self.tabview = ctk.CTkTabview(self.main_frame)
        self.tabview.pack(fill="both", expand=True)
        self.tab_clean = self.tabview.add("Temizlik")
        self.tab_update = self.tabview.add("Güncellemeler")
        self.tab_settings = self.tabview.add("Ayarlar")
        self.tab_logs = self.tabview.add("Loglar")

        self.setup_clean_tab()
        self.setup_update_tab()
        self.setup_settings_tab()
        self.setup_logs_tab()

    def setup_clean_tab(self):
        self.lbl_targets = ctk.CTkLabel(self.tab_clean, text="Temizlenecek Alanları Seçin:", font=ctk.CTkFont(weight="bold"))
        self.lbl_targets.pack(anchor="w", pady=(10, 5), padx=10)

        self.switch_user_temp = ctk.CTkSwitch(self.tab_clean, text="Kullanıcı Temp Klasörü", command=self.update_targets)
        self.switch_user_temp.select()
        self.switch_user_temp.pack(anchor="w", pady=5, padx=20)

        self.switch_sys_temp = ctk.CTkSwitch(self.tab_clean, text="Sistem Temp Klasörü", command=self.update_targets)
        self.switch_sys_temp.pack(anchor="w", pady=5, padx=20)

        self.switch_prefetch = ctk.CTkSwitch(self.tab_clean, text="Prefetch (Yönetici İzni Gerekir)", command=self.update_targets)
        self.switch_prefetch.pack(anchor="w", pady=5, padx=20)

        self.btn_analyze = ctk.CTkButton(self.tab_clean, text="Sistemi Analiz Et", fg_color="#E67E22", hover_color="#D35400", command=self.analyze_system)
        self.btn_analyze.pack(fill="x", pady=(20, 10), padx=20)

        self.btn_clean = ctk.CTkButton(self.tab_clean, text="SEÇİLİ ALANLARI TEMİZLE", height=40, font=ctk.CTkFont(weight="bold"), fg_color="#C2185B", hover_color="#880E4F", command=self.start_clean)
        self.btn_clean.pack(fill="x", pady=10, padx=20)

        self.btn_defrag = ctk.CTkButton(self.tab_clean, text="Disk Birleştiriciyi Aç", command=self.start_defrag)
        self.btn_defrag.pack(fill="x", pady=10, padx=20)

        self.progress_bar = ctk.CTkProgressBar(self.tab_clean)
        self.progress_bar.pack(fill="x", pady=20, padx=20)
        self.progress_bar.set(0)

    def setup_update_tab(self):
        info_text = ("⚡ ATLAS OS MODU AKTİF ⚡\n"
                     "Sistem hizmetlerini bozmamak için Windows OS güncellemeleri atlanır.\n"
                     "Sadece Uygulamalar, Paketler ve bağımsız Sürücüler aranır.")
        self.lbl_update_info = ctk.CTkLabel(self.tab_update, text=info_text, font=ctk.CTkFont(weight="bold"), text_color="#E67E22")
        self.lbl_update_info.pack(pady=(10, 10))

        self.update_box = ctk.CTkTextbox(self.tab_update, height=200, font=ctk.CTkFont(family="Consolas", size=11))
        self.update_box.pack(fill="both", expand=True, padx=10, pady=5)
        self.update_box.insert("end", "Güncellemeleri görmek için 'Sistemi Tara' butonuna basın.\n")
        self.update_box.configure(state="disabled")

        self.btn_check_update = ctk.CTkButton(self.tab_update, text="Sistemi Tara (Winget)", command=self.start_update_scan)
        self.btn_check_update.pack(side="left", fill="x", expand=True, padx=10, pady=10)

        self.btn_install_update = ctk.CTkButton(self.tab_update, text="Tümünü Güncelle", fg_color="#2FA572", hover_color="#1E7A52", command=self.start_update_install)
        self.btn_install_update.pack(side="right", fill="x", expand=True, padx=10, pady=10)

    def setup_settings_tab(self):
        self.lbl_theme = ctk.CTkLabel(self.tab_settings, text="Arayüz Teması Seçin:", font=ctk.CTkFont(weight="bold"))
        self.lbl_theme.pack(anchor="w", pady=(20, 5), padx=20)

        self.theme_var = ctk.StringVar(value=selected_theme)
        self.theme_menu = ctk.CTkOptionMenu(self.tab_settings, values=list(THEMES.keys()), variable=self.theme_var, command=self.change_theme)
        self.theme_menu.pack(anchor="w", padx=20, pady=5)

        self.lbl_theme_info = ctk.CTkLabel(self.tab_settings, text="* Renk teması değişikliklerinin (örn: Mavi -> Yeşil)\ntam etkili olması için uygulamayı yeniden başlatın.", text_color="gray", justify="left")
        self.lbl_theme_info.pack(anchor="w", padx=20, pady=10)

    def setup_logs_tab(self):
        self.log_box = ctk.CTkTextbox(self.tab_logs, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)
        self.log("Sistem hazır. Modülleri seçip işleme başlayabilirsiniz.")

    # --- İşlevler ---
    def update_targets(self):
        core.targets["User Temp"]["active"] = self.switch_user_temp.get() == 1
        core.targets["System Temp"]["active"] = self.switch_sys_temp.get() == 1
        core.targets["Prefetch"]["active"] = self.switch_prefetch.get() == 1

    def change_theme(self, choice):
        save_config(choice)
        mode = THEMES[choice]["mode"]
        ctk.set_appearance_mode(mode)
        # Renk teması anında değişmez, restart ister ama aydınlık/karanlık anında değişir
        self.log(f"Tema '{choice}' olarak kaydedildi. Uygulama bir sonraki açılışta bu renklerle başlayacak.")

    def log(self, message):
        def append_text():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", f"[{time.strftime('%H:%M:%S')}] {message}\n")
            self.log_box.see("end")
            self.log_box.configure(state="disabled")
        self.after(0, append_text)

    def analyze_system(self):
        self.log("Sistem analiz ediliyor...")
        self.btn_analyze.configure(state="disabled")
        def task():
            files, size = core.scan_system()
            size_str = get_size_format(size)
            self.log(f"Analiz tamamlandı. Bulunan dosya: {len(files)}, Toplam Boyut: {size_str}")
            self.after(0, lambda: self.btn_analyze.configure(state="normal", text=f"Analiz Edildi: {size_str}"))
        threading.Thread(target=task, daemon=True).start()

    def start_clean(self):
        self.btn_clean.configure(state="disabled")
        self.btn_analyze.configure(state="disabled")
        self.tabview.set("Loglar")
        threading.Thread(target=self._clean_task, daemon=True).start()

    def _clean_task(self):
        self.log("--- Temizlik Başlatıldı ---")
        files, total_size = core.scan_system()
        total, success, fail = len(files), 0, 0

        for i, f_path in enumerate(files):
            try:
                if os.path.isfile(f_path) or os.path.islink(f_path): os.unlink(f_path)
                elif os.path.isdir(f_path): shutil.rmtree(f_path)
                success += 1
            except: fail += 1
            if total > 0: self.after(0, lambda v=(i+1)/total: self.progress_bar.set(v))
        
        size_str = get_size_format(total_size if success > 0 else 0)
        self.log(f"Bitti! Silinen: {success}, Atlanan: {fail} | Kazanılan: {size_str}")
        self.after(0, lambda: self.freed_space_label.configure(text=f"Kazanılan Alan\n{size_str}"))
        self.after(0, lambda: [self.btn_clean.configure(state="normal"), self.btn_analyze.configure(state="normal", text="Sistemi Analiz Et"), self.progress_bar.set(0)])

    def start_defrag(self):
        res = core.run_defrag_logic()
        if res == "ADMIN_REQUIRED":
            if messagebox.askyesno("Yetki Gerekli", "Yönetici izni gerekiyor. Verilsin mi?"):
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "dfrgui.exe", "", None, 1)
        elif res == "SUCCESS": self.log("Defragmenter başlatıldı.")

    def start_update_scan(self):
        self.btn_check_update.configure(state="disabled")
        self.update_box.configure(state="normal")
        self.update_box.delete("1.0", "end")
        self.update_box.insert("end", "Güncellemeler taranıyor... Lütfen bekleyin...\n")
        self.update_box.configure(state="disabled")
        
        def task():
            output = core.check_updates()
            self.after(0, lambda: self._update_scan_done(output))
        threading.Thread(target=task, daemon=True).start()

    def _update_scan_done(self, output):
        self.update_box.configure(state="normal")
        self.update_box.delete("1.0", "end")
        self.update_box.insert("end", output)
        self.update_box.configure(state="disabled")
        self.btn_check_update.configure(state="normal")

    def start_update_install(self):
        cevap = messagebox.askyesno("Güncelleme", "Listelenen tüm uygulamalar arka planda güncellenecek. Onaylıyor musunuz?")
        if not cevap: return
        self.log("Uygulama/Sürücü güncellemeleri arka planda başlatıldı...")
        threading.Thread(target=core.install_updates, daemon=True).start()

# --- CLI MANTIK ---
def draw_cli_menu():
    console.clear()
    console.print(Text("\n ⚡ WINDOWS CLEANER PRO (ATLAS OS Modu) ⚡\n", style="bold bright_cyan justify center"))
    
    info_table = Table(show_header=False, box=box.ROUNDED, border_style="dim")
    info_table.add_row("İşletim Sistemi", "[blue]Atlas OS (Optimize Windows)[/blue]")
    info_table.add_row("Yönetici İzni", "[green]Aktif[/green]" if is_admin() else "[red]Yok (Sınırlı)[/red]")
    info_table.add_row("Seçili Tema", f"[magenta]{current_config.get('theme', 'Varsayılan')}[/magenta]")
    console.print(info_table)
    
    console.print(Panel(
        "[1] Sistemi Temizle\n"
        "[2] Güncellemeleri Yönet (Atlas OS Güvenli)\n"
        "[3] Temayı Değiştir\n"
        "[4] GUI (Arayüz) Moduna Geç\n"
        "[5] Çıkış", 
        title="Ana Menü", border_style="bright_blue"
    ))

def run_cli():
    while True:
        draw_cli_menu()
        choice = Prompt.ask("Seçiminiz", choices=["1", "2", "3", "4", "5"])

        if choice == "1":
            console.print("\n[yellow]Sistem Analiz Ediliyor...[/yellow]")
            files, total_size = core.scan_system()
            if not files:
                console.print("[yellow]Temizlenecek dosya yok.[/yellow]")
                Prompt.ask("\nDevam etmek için Enter...")
                continue

            console.print(f"Hedeflenen Dosya Sayısı: [cyan]{len(files)}[/cyan] | Kazanç: [green]{get_size_format(total_size)}[/green]")
            if Prompt.ask("Temizliğe başlansın mı?", choices=["e", "h"], default="e") == "e":
                success, fail = 0, 0
                with Progress(SpinnerColumn(), TextColumn("[progress.description]{task.description}"), BarColumn(), TaskProgressColumn(), console=console) as progress:
                    task = progress.add_task("[cyan]Temizleniyor...", total=len(files))
                    for f in files:
                        try:
                            if os.path.isfile(f) or os.path.islink(f): os.unlink(f)
                            elif os.path.isdir(f): shutil.rmtree(f)
                            success += 1
                        except: fail += 1
                        progress.update(task, advance=1)
                console.print(f"\n[bold green]✅ Temizlik Tamamlandı![/bold green] Silinen: {success} | Atlanan: {fail}")
            Prompt.ask("\nDevam etmek için Enter...")

        elif choice == "2":
            console.print("\n[bold yellow]Atlas OS Modu: Windows güncellemeleri atlanıyor. Paketler (Winget) aranıyor...[/bold yellow]")
            output = core.check_updates()
            console.print(Panel(output, title="Bulunan Güncellemeler"))
            if "winget" in output.lower() or "hata" in output.lower():
                pass # Winget yok veya hata var
            else:
                if Prompt.ask("Tümünü kurmak ister misiniz?", choices=["e", "h"], default="h") == "e":
                    console.print("[yellow]Arka planda güncelleniyor, lütfen bekleyin...[/yellow]")
                    core.install_updates()
                    console.print("[green]İşlem komutu gönderildi![/green]")
            Prompt.ask("\nDevam etmek için Enter...")

        elif choice == "3":
            console.print("\n[bold]Hangi temayı seçmek istersiniz? (GUI için)[/bold]")
            keys = list(THEMES.keys())
            for i, k in enumerate(keys, 1):
                console.print(f"[{i}] {k}")
            c = Prompt.ask("Seçim", choices=[str(i) for i in range(1, len(keys)+1)])
            selected = keys[int(c)-1]
            save_config(selected)
            current_config["theme"] = selected
            console.print(f"[green]Tema '{selected}' olarak güncellendi![/green]")
            Prompt.ask("\nDevam etmek için Enter...")

        elif choice == "4":
            console.print("[bold magenta]GUI Başlatılıyor...[/bold magenta]")
            time.sleep(0.5)
            app = CleanerGUI()
            app.mainloop()
            break

        elif choice == "5":
            break

if __name__ == "__main__":
    if "--gui" in sys.argv:
        app = CleanerGUI()
        app.mainloop()
    else:
        run_cli()