import os
import shutil
import subprocess
import sys


def run_command(command):
    """Komutları terminale canlı çıktı verecek şekilde çalıştırır."""
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        shell=True,
        text=True,
        encoding="utf-8",
        errors="ignore",
    )
    for line in iter(process.stdout.readline, ""):
        print(line, end="")
    process.stdout.close()
    return process.wait()


def build():
    print("🚀 mrd-cln Builder Başlatılıyor...")

    # 1. Gereksinim Kontrolü
    print("\n[1/3] Kütüphaneler kontrol ediliyor...")
    modules = ["nuitka", "customtkinter", "rich"]
    for mod in modules:
        run_command(f"{sys.executable} -m pip install {mod}")

    # 2. Microsoft Store Python Kontrolü (Uyarı)
    if "WindowsApps" in sys.executable:
        print("\n" + "!" * 50)
        print("UYARI: Microsoft Store Python'u kullanıyorsunuz!")
        print("Bu sürüm Nuitka derlemesinde 'Access Denied' hatası verebilir.")
        print("Eğer hata alırsanız python.org'dan resmi sürümü kurun.")
        print("!" * 50 + "\n")

    # 3. İkon Yolu Kontrolü
    icon_path = os.path.join("appicon", "favicon.ico")
    icon_param = ""
    if os.path.exists(icon_path):
        print(f"✨ İkon bulundu: {icon_path}")
        icon_param = f"--windows-icon-from-ico={icon_path}"
    else:
        print(f"⚠️ UYARI: {icon_path} bulunamadı, ikon eklenmeden derlenecek.")

    # 4. Nuitka Derleme Komutu
    dist_dir = "derlenmis_program"
    main_file = "main.py"

    if not os.path.exists(main_file):
        print(f"❌ HATA: {main_file} bulunamadı!")
        return

    print(f"\n[2/3] Nuitka derlemesi başlıyor (C Backend)...")

    # Komut listesi
    cmd = [
        sys.executable,
        "-m",
        "nuitka",
        "--onefile",
        "--standalone",
        "--windows-disable-console",
        "--plugin-enable=tk-inter",
        "--follow-imports",
        f"--output-dir={dist_dir}",
        "--remove-output",
        "--assume-yes-for-downloads",
    ]

    # İkon varsa komuta ekle
    if icon_param:
        cmd.append(icon_param)

    # Ana dosyayı en sona ekle
    cmd.append(main_file)

    # Komutu çalıştır
    exit_code = run_command(" ".join(cmd))

    # 5. Sonuç
    if exit_code == 0:
        print(f"\n✅ [BAŞARILI] Program derlendi: {dist_dir}/")
        exe_path = os.path.join(dist_dir, main_file.replace(".py", ".exe"))
        if os.path.exists(exe_path):
            print(f"🚀 Çalıştırılıyor: {exe_path}")
            os.startfile(exe_path)
    else:
        print("\n❌ [HATA] Derleme başarısız oldu.")


if __name__ == "__main__":
    try:
        is_admin = os.getuid() == 0
    except AttributeError:
        import ctypes

        is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

    if not is_admin:
        print("⚠️ UYARI: Builder'ı 'Yönetici Olarak' çalıştırmanız önerilir.")

    build()
