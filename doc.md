# 🛠 WinCleaner Pro - Teknik Dökümantasyon

WinCleaner Pro, **Atlas OS** ve optimize edilmiş Windows sistemleri için geliştirilmiş, Python tabanlı bir sistem bakım ve temizlik aracıdır. Hem modern bir Grafik Kullanıcı Arayüzü (GUI) hem de hız tutkunları için Gelişmiş Komut Satırı Arayüzü (CLI) sunar.

## 🚀 Temel Özellikler
- **Hibrit Yapı:** `--gui` veya `--cli` parametreleriyle istenilen modda başlatılabilir.
- **Akıllı Temizlik:** Kullanıcı ve sistem geçici dosyalarını (Temp) güvenli bir şekilde temizler.
- **Winget Entegrasyonu:** Sistemdeki tüm uygulamaları ve sürücüleri `winget` üzerinden anlık olarak tarar ve günceller.
- **Dinamik Tema Motoru:** Uygulamayı kapatmaya gerek kalmadan anlık tema değişimi (Glassmorphism esintili).
- **C-Backend Derleme:** Nuitka kullanılarak C diline dönüştürülmüş, yüksek performanslı EXE çıktısı.

## 📂 Teknik Yapı
- **Dil:** Python 3.12+
- **Arayüz:** `customtkinter` (Modern UI bileşenleri)
- **Terminal:** `rich` (Renkli tablolar, canlı ilerleme çubukları ve paneller)
- **Paket Yönetimi:** `subprocess` üzerinden Windows Package Manager (winget) erişimi.

## 🛠 Kurulum ve Derleme
Proje bağımlılıklarını yüklemek için:
```bash
pip install -r requirements.txt