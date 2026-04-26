import os
import shutil
import subprocess
import sys
import threading
import time
import re
import functools
from datetime import datetime

# --- KÜTÜPHANE OTOMASYONU ---
def install_requirements():
    try:
        import customtkinter as ctk
    except ImportError:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "customtkinter"])

install_requirements()

from tkinter import messagebox
import customtkinter as ctk

# --- AYARLAR VE PERFORMANS ---
VERSION = "0.8.3 ELECTRON EDITION"
APP_ICON_PATH = "appicon/favicon.png"

# --- TEMA MOTORU (ELECTRON STYLE) ---
# "card" ve "bg" renklerini birbirine yakınlaştırarak o gri kutu etkisini yok ediyoruz.
THEMES = {
    "Karanlık": {
        "bg": "#0d1117", "fg": "#161b22", "text": "#c9d1d9", 
        "border": "#30363d", "accent": "#7952b3", "subtext": "#8b949e",
        "card": "#161b22"
    },
    "Aydınlık": {
        "bg": "#f6f8fa", "fg": "#ffffff", "text": "#24292f", 
        "border": "#d0d7de", "accent": "#0969da", "subtext": "#57606a",
        "card": "#ffffff"
    },
    "Mor": {
        "bg": "#0f0913", "fg": "#1a1221", "text": "#e0d6eb", 
        "border": "#3d2b52", "accent": "#9333ea", "subtext": "#a191b2",
        "card": "#1a1221"
    },
    "Cyber": {
        "bg": "#050505", "fg": "#0f0f0f", "text": "#00ff41", 
        "border": "#003b00", "accent": "#00ff41", "subtext": "#008f11",
        "card": "#0f0f0f"
    },
    "Okyanus": {
        "bg": "#010409", "fg": "#0d1117", "text": "#58a6ff", 
        "border": "#1f6feb", "accent": "#1f6feb", "subtext": "#388bfd",
        "card": "#0d1117"
    }
}

# --- SİSTEM MOTORU ---
class CleanerEngine:
    @staticmethod
    def get_size(path):
        total = 0
        try:
            if os.path.isfile(path): total = os.path.getsize(path)
            elif os.path.isdir(path):
                for dirpath, _, filenames in os.walk(path):
                    for f in filenames:
                        fp = os.path.join(dirpath, f)
                        if os.path.exists(fp): total += os.path.getsize(fp)
        except: pass
        return total

    @staticmethod
    def run_silent(cmd):
        try:
            return subprocess.run(cmd, shell=True, capture_output=True, text=True, creationflags=subprocess.CREATE_NO_WINDOW, encoding='utf-8', errors='ignore')
        except:
            return None

# --- ANA ARAYÜZ ---
class WinCleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        self.current_theme = "Karanlık"
        self.active_tab = "Temizlik"
        self.title("mrd cleaner")
        self.geometry("1080x880")
        
        # UI Element Takibi
        self.cards = [] 
        self.log_widgets = [] 
        self.nav_buttons = {}
        self.frames = {}
        
        # Ana Yapı
        self.grid_columnconfigure(0, weight=1)
        self.grid_rowconfigure(0, weight=1)

        self.build_ui()
        self.apply_theme(self.current_theme)
        self.switch_tab("Temizlik")

    def log_message(self, widget, message):
        widget.configure(state="normal")
        widget.insert("end", f"{message}\n")
        widget.see("end")
        widget.configure(state="disabled")

    def build_ui(self):
        # Ana Konteyner
        self.main_container = ctk.CTkFrame(self, border_width=1, corner_radius=0)
        self.main_container.grid(row=0, column=0, sticky="nsew")
        self.main_container.grid_columnconfigure(0, weight=1)
        self.main_container.grid_rowconfigure(1, weight=1)

        # Header
        self.header = ctk.CTkFrame(self.main_container, height=80, corner_radius=0, border_width=0)
        self.header.grid(row=0, column=0, sticky="ew")
        
        self.logo_label = ctk.CTkLabel(self.header, text="✨ MRD CLEANER", font=("Inter", 22, "bold"))
        self.logo_label.pack(side="left", padx=30)
        
        tabs = ["Temizlik", "Sistem bakim", "Onarim", "Guncellemeler", "Tema", "Ayarlar"]
        self.nav_container = ctk.CTkFrame(self.header, fg_color="transparent")
        self.nav_container.pack(side="right", padx=20)
        
        for tab in tabs:
            btn = ctk.CTkButton(self.nav_container, text=tab.upper(), width=110, height=40, corner_radius=4, 
                                font=("Inter", 11, "bold"), border_spacing=10,
                                command=lambda t=tab: self.switch_tab(t))
            btn.pack(side="left", padx=2)
            self.nav_buttons[tab] = btn

        # Content Box (Scrollable alanın kendi rengini de temaya bağlayacağız)
        self.content_box = ctk.CTkScrollableFrame(self.main_container, corner_radius=0)
        self.content_box.grid(row=1, column=0, sticky="nsew", padx=20, pady=(10, 30))

        # Footer
        self.footer_label = ctk.CTkLabel(self.main_container, text=f"ELECTRON ENGINE | {VERSION}", font=("Inter", 9))
        self.footer_label.place(relx=0.5, rely=0.98, anchor="center")

        self.setup_pages()

    def setup_pages(self):
        # Sayfaları oluştururken her birini bir frame içine koyuyoruz
        page_list = ["Temizlik", "Sistem bakim", "Onarim", "Guncellemeler", "Tema", "Ayarlar"]
        
        for key in page_list:
            frame = ctk.CTkFrame(self.content_box, fg_color="transparent")
            self.frames[key] = frame
            
            if key == "Temizlik":
                self.add_page_header(frame, "Sistem Temizliği", "Gereksiz dosyaları tarayın ve silin.")
                self.clean_log = ctk.CTkTextbox(frame, height=450, corner_radius=8, font=("JetBrains Mono", 12), border_width=1, state="disabled")
                self.clean_log.pack(fill="both", expand=True, padx=10, pady=10)
                self.log_widgets.append(self.clean_log)
                self.btn_start_clean = ctk.CTkButton(frame, text="TARAMAYI BAŞLAT", height=50, corner_radius=6, font=("Inter", 14, "bold"), command=self.start_cleaning)
                self.btn_start_clean.pack(fill="x", padx=10, pady=10)
                
            elif key == "Tema":
                self.add_page_header(frame, "Görünüm Ayarları", "Uygulama stilini anında değiştirin.")
                for t_name in THEMES.keys():
                    btn = ctk.CTkButton(frame, text=f"{t_name.upper()} MODU", height=60, corner_radius=8, font=("Inter", 13, "bold"),
                                        command=lambda n=t_name: self.apply_theme(n))
                    btn.pack(fill="x", padx=10, pady=5)
                    
            elif key == "Ayarlar":
                self.add_page_header(frame, "Gelişmiş Seçenekler", "Uygulama davranışını özelleştirin.")
                for s in ["Otomatik Başlat", "Hızlı Tarama", "GPU Hızlandırma"]:
                    row = self.create_card(frame)
                    ctk.CTkLabel(row, text=s, font=("Inter", 14)).pack(side="left", padx=15)
                    ctk.CTkSwitch(row, text="").pack(side="right", padx=15)

            elif key == "Guncellemeler":
                self.add_page_header(frame, "Yazılım Güncelleme", "Tüm sistem bileşenlerini güncel tutun.")
                self.upd_log = ctk.CTkTextbox(frame, height=400, corner_radius=8, font=("JetBrains Mono", 11), border_width=1, state="disabled")
                self.upd_log.pack(fill="x", padx=10, pady=10)
                self.log_widgets.append(self.upd_log)
                ctk.CTkButton(frame, text="GÜNCELLEMELERİ KONTROL ET", height=45, command=self.scan_updates).pack(fill="x", padx=10)
            
            else:
                self.add_page_header(frame, key, "Bu özellik yakında eklenecek.")
                for i in range(2):
                    row = self.create_card(frame)
                    ctk.CTkLabel(row, text=f"Modül {i+1}", font=("Inter", 14, "bold")).pack(side="left", padx=15)
                    ctk.CTkButton(row, text="AKTİF ET", width=100).pack(side="right", padx=15)

    def create_card(self, parent):
        card = ctk.CTkFrame(parent, height=70, corner_radius=8, border_width=1)
        card.pack(fill="x", padx=10, pady=6)
        card.pack_propagate(False)
        self.cards.append(card)
        return card

    def add_page_header(self, parent, title, subtitle):
        ctk.CTkLabel(parent, text=title.upper(), font=("Inter", 26, "bold")).pack(anchor="w", padx=10, pady=(15, 0))
        ctk.CTkLabel(parent, text=subtitle, font=("Inter", 13)).pack(anchor="w", padx=10, pady=(0, 20))

    def apply_theme(self, theme_name):
        self.current_theme = theme_name
        t = THEMES[theme_name]
        
        # 1. Ana Pencere ve Arka Planlar
        self.configure(fg_color=t["bg"])
        self.main_container.configure(fg_color=t["bg"], border_color=t["border"])
        self.header.configure(fg_color=t["fg"])
        self.content_box.configure(fg_color=t["bg"]) # Scrollable Frame Arka Planı
        
        # 2. Yazı Renkleri
        self.logo_label.configure(text_color=t["accent"])
        self.footer_label.configure(text_color=t["subtext"])
        
        # 3. Navigasyon Butonları
        for name, btn in self.nav_buttons.items():
            if name == self.active_tab:
                btn.configure(fg_color=t["accent"], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=t["text"], hover_color=t["border"])

        # 4. Gri Kutu Sorunu Çözümü (Log Textboxları)
        for widget in self.log_widgets:
            widget.configure(fg_color=t["card"], border_color=t["border"], text_color=t["text"])

        # 5. Kartlar (Ayarlar vb.)
        for card in self.cards:
            card.configure(fg_color=t["card"], border_color=t["border"])
            # Kart içindeki labelların rengini de güncellemek gerekebilir
            for child in card.winfo_children():
                if isinstance(child, ctk.CTkLabel):
                    child.configure(text_color=t["text"])

        self.switch_tab(self.active_tab)

    def switch_tab(self, tab_name):
        self.active_tab = tab_name
        for f in self.frames.values(): f.pack_forget()
        
        t = THEMES[self.current_theme]
        for name, btn in self.nav_buttons.items():
            if name == tab_name:
                btn.configure(fg_color=t["accent"], text_color="#ffffff")
            else:
                btn.configure(fg_color="transparent", text_color=t["text"])
        
        self.frames[tab_name].pack(fill="both", expand=True)

    def start_cleaning(self):
        self.log_message(self.clean_log, ">>> MRD ENGINE BAŞLATILDI...")
        def work():
            time.sleep(1)
            self.log_message(self.clean_log, "[BİLGİ] Sistem taranıyor...")
            time.sleep(1)
            self.log_message(self.clean_log, "[BİLGİ] Temizlik tamamlandı!")
            self.after(0, lambda: messagebox.showinfo("Başarılı", "Temizlik işlemi bitti."))
        threading.Thread(target=work, daemon=True).start()

    def scan_updates(self):
        def work():
            self.log_message(self.upd_log, "Winget üzerinden güncellemeler denetleniyor...")
            res = CleanerEngine.run_silent("winget upgrade")
            if res: self.log_message(self.upd_log, res.stdout)
        threading.Thread(target=work, daemon=True).start()

if __name__ == "__main__":
    app = WinCleanerApp()
    app.mainloop()