import os
import shutil
import subprocess
import ctypes
import threading
import customtkinter as ctk
from tkinter import messagebox

# CustomTkinter genel ayarları
ctk.set_appearance_mode("System")  # "Dark", "Light" veya "System"
ctk.set_default_color_theme("blue")  # "blue", "green", "dark-blue"

class CleanerApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Pencere ayarları
        self.title("Windows Cleaner GUI")
        self.geometry("550x500")
        self.resizable(False, False)

        self._osName = "Windows 11"
        self._programVersion = "0.4 (GUI Edition)"

        self.setup_ui()

    def setup_ui(self):
        # Başlık ve Bilgi Alanı
        self.header_label = ctk.CTkLabel(self, text="Windows Cleaner", font=ctk.CTkFont(size=24, weight="bold"))
        self.header_label.pack(pady=(20, 5))

        self.info_label = ctk.CTkLabel(self, text=f"OS: {self._osName} | Versiyon: {self._programVersion}", font=ctk.CTkFont(size=12, slant="italic"))
        self.info_label.pack(pady=(0, 20))

        # Butonlar
        self.btn_frame = ctk.CTkFrame(self)
        self.btn_frame.pack(pady=10, padx=20, fill="x")

        self.btn_full = ctk.CTkButton(self.btn_frame, text="Full Clean Up (Temp + Defrag)", command=self.start_full_clean, fg_color="#C2185B", hover_color="#880E4F")
        self.btn_full.pack(side="left", padx=10, pady=10, expand=True, fill="x")

        self.btn_light = ctk.CTkButton(self.btn_frame, text="Light Clean Up (Sadece Temp)", command=self.start_light_clean)
        self.btn_light.pack(side="right", padx=10, pady=10, expand=True, fill="x")

        # İlerleme Çubuğu (Progress Bar)
        self.progress_bar = ctk.CTkProgressBar(self)
        self.progress_bar.pack(pady=10, padx=20, fill="x")
        self.progress_bar.set(0)

        # Log (Bilgi) Ekranı
        self.log_box = ctk.CTkTextbox(self, height=150, state="disabled")
        self.log_box.pack(pady=10, padx=20, fill="both", expand=True)

    def log(self, message):
        """Log ekranına thread-safe (güvenli) şekilde mesaj yazar."""
        def append_text():
            self.log_box.configure(state="normal")
            self.log_box.insert("end", message + "\n")
            self.log_box.see("end")  # Otomatik olarak en aşağı kaydır
            self.log_box.configure(state="disabled")
        
        self.after(0, append_text)

    def update_progress(self, value):
        """İlerleme çubuğunu günceller."""
        self.after(0, lambda: self.progress_bar.set(value))

    def set_buttons_state(self, state):
        """İşlem sırasında butonları kilitler veya açar."""
        self.after(0, lambda: self.btn_full.configure(state=state))
        self.after(0, lambda: self.btn_light.configure(state=state))

    def get_temp_files(self):
        temp_folder = os.environ.get('TEMP')
        try:
            return [os.path.join(temp_folder, f) for f in os.listdir(temp_folder)]
        except Exception as e:
            self.log(f"[!] Hata: Temp dizini okunamadı! {e}")
            return []

    def clean_files(self, file_list):
        success_count = 0
        fail_count = 0
        total_files = len(file_list)

        self.update_progress(0)

        for i, file_path in enumerate(file_list):
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
                success_count += 1
            except Exception:
                fail_count += 1
            
            # Progress bar'ı güncelle
            if total_files > 0:
                self.update_progress((i + 1) / total_files)

        return success_count, fail_count

    def run_defragmenter_as_admin(self):
        self.log("Disk birleştiricisi başlatılıyor...")
        try:
            # Önce standart yolla açmayı dener
            subprocess.run(["dfrgui.exe"], check=True)
        except OSError as e:
            # 740 hatası: Yönetici izni gerekli
            if getattr(e, 'winerror', None) == 740:
                # GUI içinde kullanıcıya sor
                cevap = messagebox.askyesno(
                    "Yönetici İzni Gerekli", 
                    "Disk birleştirici aracını başlatmak için Yönetici izni gerekiyor.\n\nYetki vermek istiyor musunuz?",
                    parent=self
                )
                
                if cevap:
                    try:
                        ctypes.windll.shell32.ShellExecuteW(None, "runas", "dfrgui.exe", "", None, 1)
                        self.log("Disk birleştirici ayrı bir pencerede yönetici olarak başlatıldı.")
                    except Exception as ex:
                        self.log(f"[!] Yönetici olarak başlatılırken hata: {ex}")
                else:
                    self.log("Disk birleştirme işlemi kullanıcı tarafından atlandı.")
            else:
                self.log(f"[!] Disk birleştiricisi başlatılamadı: {e}")
        except Exception as e:
            self.log(f"[!] Beklenmeyen hata: {e}")

    # --- THREADING (Arka Plan İşlemleri) ---

    def start_light_clean(self):
        self.set_buttons_state("disabled")
        self.log("--- LIGHT CLEAN UP Başlatıldı ---")
        # Arayüzün donmaması için işlemi ayrı bir Thread'de başlatıyoruz
        threading.Thread(target=self._light_clean_task, daemon=True).start()

    def _light_clean_task(self):
        files = self.get_temp_files()
        s, f = self.clean_files(files)
        self.log(f"Hızlı Temizlik Tamamlandı! Silinen: {s}, Atlanan: {f}")
        self.set_buttons_state("normal")

    def start_full_clean(self):
        self.set_buttons_state("disabled")
        self.log("--- FULL CLEAN UP Başlatıldı ---")
        threading.Thread(target=self._full_clean_task, daemon=True).start()

    def _full_clean_task(self):
        files = self.get_temp_files()
        s, f = self.clean_files(files)
        self.log(f"Temp temizliği bitti (Silinen: {s}, Atlanan: {f}).")
        
        self.run_defragmenter_as_admin()
        
        self.log("Full Clean Up Başarıyla Tamamlandı!")
        self.set_buttons_state("normal")

if __name__ == "__main__":
    app = CleanerApp()
    app.mainloop()