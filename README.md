Bu proje **GNU General Public License v3.0 (GPL-3.0)** altında lisanslanmıştır.

- **Özgürlük:** Bu yazılımı kopyalayabilir, dağıtabilir ve değiştirebilirsiniz.
- **Açık Kaynak Zorunluluğu:** Bu kodun kullanıldığı veya modifiye edildiği tüm projelerin de GPL-3.0 ile açık kaynak olarak paylaşılması **zorunludur**.
- **Sorumluluk:** Yazılım "olduğu gibi" sunulur, herhangi bir garanti verilmez.

Detaylı bilgi için [LICENSE](LICENSE) dosyasına göz atın.

# 🚀 mrdarwin clean (v0.0.7) - Atlas OS & Pro Edition

Windows işletim sistemini temizlemek, hızlandırmak ve optimize etmek için Python ile geliştirilmiş, **Atlas OS** dostu, hafif ve güçlü bir sistem düzenleyicidir. Geleneksel temizleyicilerin aksine, modern paket yöneticileriyle entegre çalışarak sisteminizi sadece temizlemez, aynı zamanda güncel tutar.

---

## 🛠️ Yeni Nesil Özellikler

* **🌓 Hibrit Arayüz:** `--gui` parametresi ile modern "Glassmorphism" esintili bir pencere deneyimi, `--cli` ile hız tutkunları için terminal üzerinden yönetim.
* **🧹 Akıllı Temizlik:** Atlas OS servis yapısına uygun, sadece güvenli `Temp` ve sistem artıklarını temizleyen özel algoritma.
* **📦 Uygulama & Sürücü Güncelleyici:** `Winget` entegrasyonu sayesinde tüm üçüncü taraf uygulamaları ve sürücüleri tek tuşla, arka planda güncelleyin.
* **🎨 Dinamik Tema Motoru:** Uygulamayı kapatmaya gerek kalmadan anlık tema değişimi ve tercih edilen temanın otomatik kaydedilmesi.
* **⚙️ Nuitka Derleme:** Python kodunu C-Backend ile makine diline derleyerek mermi hızında EXE performansı.
* **🛡️ Güvenli Mod:** Kritik Windows bileşenlerine ve Update servislerine dokunmadan, sistem stabilitesini bozmadan temizlik yapar.

---

## 🚀 Kurulum ve Çalıştırma

### Gereksinimler
- **Python 3.12+** (Resmi [python.org](https://www.python.org/downloads/) sürümü önerilir).
- **Yönetici (Administrator) Yetkileri** (Dosya silme ve sistem güncellemeleri için gereklidir).
- **Winget** (Windows Paket Yöneticisi - Genelde Windows ile yerleşik gelir).

### Hızlı Başlangıç

1.  **Projeyi Klonlayın:**
    ```bash
    git clone [https://github.com/mrdarwinjs/mrd-cln.git](https://github.com/mrdarwinjs/mrd-cln.git)
    cd mrd-cln
    ```

2.  **Bağımlılıkları Yükleyin:**
    ```bash
    pip install -r requirements.txt
    ```

3.  **Uygulamayı Çalıştırın:**
    ```bash
    # Grafik arayüzü (GUI) ile başlatmak için:
    python main.py --gui

    # Komut satırı (CLI) modunda başlatmak için:
    python main.py --cli
    ```

---

## 🏗️ Derleme (EXE Yapma)

Kodunuzu performanslı bir EXE dosyasına dönüştürmek ve tüm kütüphaneleri içine gömmek için projedeki `nuitka_derle.bat` dosyasını kullanabilir veya şu komutu manuel çalıştırabilirsiniz:

```bash
python -m nuitka --onefile --standalone --windows-disable-console --plugin-enable=tk-inter main.py




