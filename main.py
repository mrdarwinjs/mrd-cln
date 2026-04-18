import os
import shutil
import time
import subprocess
import ctypes
import tkinter as tk
from tkinter import messagebox
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TaskProgressColumn
from rich.table import Table
from rich.text import Text

# Console nesnesi
console = Console()

def get_temp_files():
    temp_folder = os.environ.get('TEMP')
    try:
        return [os.path.join(temp_folder, f) for f in os.listdir(temp_folder)], temp_folder
    except Exception as e:
        console.print(f"[red]Hata: Temp dizini okunamadı! {e}[/red]")
        return [], None

def clean_files_with_progress(file_list, description="Temizleniyor"):
    success_count = 0
    fail_count = 0
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console
    ) as progress:
        task = progress.add_task(description, total=len(file_list))
        
        for file_path in file_list:
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                success_count += 1
            except Exception:
                fail_count += 1
            
            progress.update(task, advance=1)
            time.sleep(0.01)
            
    return success_count, fail_count

def run_defragmenter_as_admin():
    """Disk birleştiriciyi yönetici yetkisi isteyerek çalıştırır."""
    try:
        # Önce standart yolla açmayı dener
        subprocess.run(["dfrgui.exe"], check=True)
    except OSError as e:
        # 740 hatası: Yönetici izni gerekli
        if e.winerror == 740:
            # Tkinter arayüzünü gizli olarak başlat
            root = tk.Tk()
            root.withdraw()
            root.attributes('-topmost', True) # Pop-up'ın en önde görünmesini sağlar
            
            # Kullanıcıya sor
            cevap = messagebox.askyesno(
                "Yönetici İzni Gerekli", 
                "Disk birleştirici aracını başlatmak için Yönetici izni gerekiyor.\n\nYetki vermek istiyor musunuz?",
                parent=root
            )
            
            if cevap:
                try:
                    # Windows UAC (Kullanıcı Hesabı Denetimi) tetiklenir
                    ctypes.windll.shell32.ShellExecuteW(None, "runas", "dfrgui.exe", "", None, 1)
                    console.print("[yellow]Disk birleştirici ayrı bir pencerede yönetici olarak başlatıldı.[/yellow]")
                except Exception as ex:
                    console.print(f"[red]Yönetici olarak başlatılırken hata oluştu: {ex}[/red]")
            else:
                console.print("[yellow]Disk birleştirme işlemi kullanıcı tarafından atlandı.[/yellow]")
            
            root.destroy()
        else:
            console.print(f"[red]Disk birleştiricisi başlatılamadı: {e}[/red]")

def full_clean_up():
    console.print("[bold yellow]FULL CLEAN UP Başlatıldı...[/bold yellow]")
    
    files, path = get_temp_files()
    s, f = clean_files_with_progress(files, description="[cyan]Temp Dosyaları Siliniyor")
    
    console.print(f"[green]Temp temizliği bitti ({s} silindi, {f} atlandı).[/green]\n")
    
    console.print(Panel("[bold white]Windows Disk Birleştiricisi açılıyor...\nLütfen işlem bitince pencereyi kapatın.[/bold white]", border_style="magenta"))
    
    # Yeni eklenen yönetici fonksiyonunu çağırıyoruz
    run_defragmenter_as_admin()

    console.print(Panel("[bold green]Full Clean Up Başarıyla Tamamlandı![/bold green]", border_style="green"))

def light_clean_up():
    console.print("[bold yellow]LIGHT CLEAN UP Başlatıldı...[/bold yellow]")
    
    files, path = get_temp_files()
    s, f = clean_files_with_progress(files, description="[cyan]Hızlı Temizlik Yapılıyor")
    
    console.print(Panel(
        f"[bold green]Hızlı Temizlik Tamamlandı![/bold green]\n\n"
        f"Silinen: [cyan]{s}[/cyan]\n"
        f"Atlanan: [red]{f}[/red]",
        title="Sonuç", border_style="green"
    ))

def clean():
    console.clear()

def main():
    _osName = "Windows 11"
    _programVersion = "0.4 (Admin Pop-Up Edition)"

    logo_text = Text("""
    __      __                _             
   / /_  __/ /_  _______ _   / /_  __  ____ 
  / __ \/ __  / / ___/| | /| / / / / / __ \\
 / /_/ / /_/ / / /    | |/ |/ / / / / / / /
/_.___/\__,_/_/_/     |__/|__/_/_/_/_/ /_/ 
    """, style="bold cyan")

    while True:
        clean()
        
        table = Table(show_header=False, header_style="bold magenta", border_style="dim")
        table.add_row("İşletim Sistemi", f"[bold yellow]{_osName}[/bold yellow]")
        table.add_row("Versiyon", f"[bold blue]{_programVersion}[/bold blue]")
        
        console.print(logo_text)
        console.print(table)
        
        console.print(Panel(
            "[bold cyan][1][/bold cyan] Full Clean Up (Temp + Disk Defragmenter)\n"
            "[bold cyan][2][/bold cyan] Light Clean Up (Sadece Temp)\n"
            "[bold red][3][/bold red] Çıkış",
            title="Ana Menü", border_style="bright_blue"
        ))

        try:
            choice = Prompt.ask("Seçim", choices=["1", "2", "3"], default="1")

            if choice == "1":
                clean()
                full_clean_up()
                Prompt.ask("\nAna menüye dönmek için [bold]Enter[/bold]'a basın...")
            
            elif choice == "2":
                clean()
                light_clean_up()
                Prompt.ask("\nAna menüye dönmek için [bold]Enter[/bold]'a basın...")
            
            elif choice == "3":
                console.print("[bold red]Güle güle![/bold red]")
                time.sleep(1)
                break

        except KeyboardInterrupt:
            break

if __name__ == "__main__":
    main()