import os
import shutil
import time
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from rich.status import Status
from rich.table import Table
from rich.text import Text

# Console nesnesini başlatalım
console = Console()

def full_clean_up():
    # Rich status ile çok daha şık bir yükleme animasyonu
    with console.status("[bold green]Geçici dosyalar taranıyor ve siliniyor...", spinner="dots"):
        temp_folder = os.environ.get('TEMP')
        time.sleep(1.5) # Görsellik için kısa bir bekleme
        
        success_count = 0
        fail_count = 0

        for filename in os.listdir(temp_folder):
            file_path = os.path.join(temp_folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                success_count += 1
            except Exception:
                fail_count += 1
        
    console.print(Panel(
        f"[bold green]Temizlik Tamamlandı![/bold green]\n\n"
        f"Başarıyla Silinen: [cyan]{success_count}[/cyan]\n"
        f"Atlanan (Kullanımda): [red]{fail_count}[/red]",
        title="Sonuç", border_style="green"
    ))

def clean():
    console.clear()

def main():
    _osName = "Windows 11"
    _programVersion = "0.2 (Rich Edition)"

    # Logo ve Başlık
    logo_text = Text("""
    __      __                _             
   / /_  __/ /_  _______ _   / /_  __  ____ 
  / __ \/ __  / / ___/| | /| / / / / / __ \\
 / /_/ / /_/ / / /    | |/ |/ / / / / / / /
/_.___/\__,_/_/_/     |__/|__/_/_/_/_/ /_/ 
    """, style="bold cyan")

    while True:
        clean()
        
        # Bilgi Tablosu
        table = Table(show_header=False, header_style="bold magenta", border_style="dim")
        table.add_row("İşletim Sistemi", f"[bold yellow]{_osName}[/bold yellow]")
        table.add_row("Versiyon", f"[bold blue]{_programVersion}[/bold blue]")
        
        console.print(logo_text)
        console.print(table)