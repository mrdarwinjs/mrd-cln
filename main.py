import os
import shutil
import time
import subprocess
import ctypes
import threading
import sys

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

# --- YARDIMCI FONKSİYONLAR ---
def is_admin():
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def get_size_format(b, factor=1024, suffix="B"):
    """Bayt cinsinden boyutu okunabilir formata çevirir (MB, GB vb.)"""
    for unit in ["", "K", "M", "G", "T", "P", "E", "Z"]:
        if b < factor:
            return f"{b:.2f} {unit}{suffix}"
        b /= factor
    return f"{b:.2f} Y{suffix}"

# --- ÇEKİRDEK MANTIK (CORE LOGIC) ---
class CleaningCore:
    def __init__(self):
        self.targets = {
            "User Temp": {"path": os.environ.get('TEMP'), "active": True},
            "System Temp": {"path": r"C:\Windows\Temp", "active": False},
            "Prefetch": {"path": r"C:\Windows\Prefetch", "active": False}
        }

    def scan_system(self):
        """Aktif hedefleri tarar, dosya listesini ve toplam boyutu döndürür."""
        files_to_clean = []
        total_size = 0

        for name, data in self.targets.items():
            if not data["active"]:
                continue
            
            folder = data["path"]
            if not os.path.exists(folder):
                continue
                
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
                    except Exception:
                        pass
            except PermissionError:
                pass # Yönetici izni yoksa atla
                
        return files_to_clean, total_size

    @staticmethod
    def run_defrag_logic():
        try:
            subprocess.run(["dfrgui.exe"], check=True)
            return "SUCCESS"
        except OSError as e:
            if getattr(e, 'winerror', None) == 740:
                return "ADMIN_REQUIRED"
            return f"ERROR: {e}"

# Global Core Instance
core = CleaningCore()

# --- GUI SINIFI ---
class CleanerGUI(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Windows Cleaner Pro")
        self.geometry("650x550")
        self.resizable(False, False)
        
        ctk.set_appearance_mode("System")
        ctk.set_default_color_theme("blue")

        self._osName = "Windows"
        self._programVersion = "1.0 (Pro GUI)"
        
        self.setup_ui()

    def setup_ui(self):
        # Sol Menü (Sidebar)
        self.sidebar = ctk.CTkFrame(self, width=150, corner_radius=0)
        self.sidebar.pack(side="left", fill="y")
        
        self.logo_label = ctk.CTkLabel(self.sidebar, text="WinCleaner\nPRO", font=ctk.CTkFont(size=20, weight="bold"))
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
        self.tab_logs = self.tabview.add("Loglar")

        # --- Temizlik Sekmesi İçeriği ---
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

        # --- Loglar Sekmesi İçeriği ---
        self.log_box = ctk.CTkTextbox(self.tab_logs, state="disabled")
        self.log_box.pack(fill="both", expand=True, padx=10, pady=10)

        self.log("Sistem hazır. Modülleri seçip temizliğe başlayabilirsiniz.")

    def update_targets(self):
        core.targets["User Temp"]["active"] = self.switch_user_temp.get() == 1
        core.targets["System Temp"]["active"] = self.switch_sys_temp.get() == 1
        core.targets["Prefetch"]["active"] = self.switch_prefetch.get() == 1

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
        self.log("--- Temizlik İşlemi Başlatıldı ---")
        files, total_size = core.scan_system()
        total = len(files)
        success, fail = 0, 0

        for i, f_path in enumerate(files):
            try:
                if os.path.isfile(f_path) or os.path.islink(f_path): os.unlink(f_path)
                elif os.path.isdir(f_path): shutil.rmtree(f_path)
                success += 1
            except: fail += 1
            if total > 0: self.after(0, lambda v=(i+1)/total: self.progress_bar.set(v))
        
        size_str = get_size_format(total_size if success > 0 else 0)
        self.log(f"Temizlik Bitti! Silinen: {success}, Atlanan: {fail}")
        self.log(f"Kazanılan Toplam Alan: {size_str}")
        
        self.after(0, lambda: self.freed_space_label.configure(text=f"Kazanılan Alan\n{size_str}"))
        self.after(0, lambda: self.btn_clean.configure(state="normal"))
        self.after(0, lambda: self.btn_analyze.configure(state="normal", text="Sistemi Analiz Et"))
        self.after(0, lambda: self.progress_bar.set(0))

    def start_defrag(self):
        res = core.run_defrag_logic()
        if res == "ADMIN_REQUIRED":
            cevap = messagebox.askyesno("Yetki Gerekli", "Disk birleştirici için yönetici izni gerekiyor. Verilsin mi?")
            if cevap: ctypes.windll.shell32.ShellExecuteW(None, "runas", "dfrgui.exe", "", None, 1)
        elif res == "SUCCESS": 
            self.log("Defragmenter başlatıldı.")

# --- CLI MANTIK ---
def draw_cli_menu():
    console.clear()
    console.print(Text("\n ⚡ WINDOWS CLEANER PRO (CLI Mode) ⚡\n", style="bold bright_cyan justify center"))
    
    # Bilgi Tablosu
    info_table = Table(show_header=False, box=box.ROUNDED, border_style="dim")
    info_table.add_row("İşletim Sistemi", "Windows")
    info_table.add_row("Yönetici İzni", "[green]Aktif[/green]" if is_admin() else "[red]Yok (Sınırlı Temizlik)[/red]")
    console.print(info_table)

    # Hedef Durum Tablosu
    target_table = Table(title="Aktif Temizlik Hedefleri", box=box.SIMPLE_HEAD)
    target_table.add_column("Bölge", style="cyan")
    target_table.add_column("Durum", justify="center")
    
    for name, data in core.targets.items():
        status = "[green]Açık[/green]" if data["active"] else "[red]Kapalı[/red]"
        target_table.add_row(name, status)
    
    console.print(target_table)
    
    console.print(Panel(
        "[1] Seçili Alanları Temizle\n"
        "[2] Ayarları Değiştir (Aç/Kapat)\n"
        "[3] Disk Defragmenter Başlat\n"
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
            size_str = get_size_format(total_size)
            
            if len(files) == 0:
                console.print("[yellow]Temizlenecek dosya bulunamadı veya yetki yok.[/yellow]")
                Prompt.ask("\nDevam etmek için Enter...")
                continue

            console.print(f"Hedeflenen Dosya Sayısı: [cyan]{len(files)}[/cyan] | Beklenen Kazanç: [green]{size_str}[/green]")
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
                        time.sleep(0.002) # Efekt için
                
                console.print(f"\n[bold green]✅ Temizlik Tamamlandı![/bold green]")
                console.print(f"Silinen: {success} | Atlanan: {fail} | Kazanılan Alan: {size_str}")
            Prompt.ask("\nDevam etmek için Enter...")

        elif choice == "2":
            console.print("\n[bold]Hangi ayarı değiştirmek istersiniz?[/bold]")
            keys = list(core.targets.keys())
            for i, k in enumerate(keys, 1):
                durum = "Açık" if core.targets[k]["active"] else "Kapalı"
                console.print(f"[{i}] {k} (Şu an: {durum})")
            
            c = Prompt.ask("Seçim (İptal için Enter)", default="")
            if c.isdigit() and 1 <= int(c) <= len(keys):
                selected_key = keys[int(c)-1]
                core.targets[selected_key]["active"] = not core.targets[selected_key]["active"]
                console.print(f"[green]{selected_key} durumu değiştirildi.[/green]")
                time.sleep(1)

        elif choice == "3":
            res = core.run_defrag_logic()
            if res == "ADMIN_REQUIRED":
                console.print("[yellow]Uyarı: Defrag için UAC onayı bekleniyor...[/yellow]")
                ctypes.windll.shell32.ShellExecuteW(None, "runas", "dfrgui.exe", "", None, 1)
            Prompt.ask("\nDevam etmek için Enter...")

        elif choice == "4":
            console.print("[bold magenta]GUI Başlatılıyor...[/bold magenta]")
            time.sleep(0.5)
            app = CleanerGUI()
            app.mainloop()
            break

        elif choice == "5":
            console.print("[bold red]Çıkış yapılıyor...[/bold red]")
            break

# --- ANA GİRİŞ NOKTASI ---
if __name__ == "__main__":
    if "--gui" in sys.argv:
        app = CleanerGUI()
        app.mainloop()
    else:
        run_cli()