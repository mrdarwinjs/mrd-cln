@echo off
setlocal enabledelayedexpansion
title mrd-cln Loader - Debug Mode
color 0B

echo ======================================================
echo           mrd-cln SYSTEM OPTIMIZER LOADER
echo ======================================================
echo.

:: 1. GIT KONTROLU
where git >nul 2>nul
if %errorlevel% neq 0 (
    echo [HATA] Git bulunamadi! Lutfen Git'in kurulu ve PATH'e ekli oldugundan emin olun.
    pause
    exit /b
)

:: 2. REPO VE DOSYA KONTROLU
if exist "mrd-cln" (
    echo [+] Proje klasoru mevcut. Guncellemeler denetleniyor...
    cd /d "%~dp0mrd-cln"
    
    if not exist "main.py" (
        echo [!] main.py bulunamadi! Klasor hatali gorunuyor.
        echo Yeniden indiriliyor...
        cd ..
        rd /s /q "mrd-cln"
        goto :CLONE
    )

    git fetch origin
    git pull origin main
) else (
    :CLONE
    echo [+] Proje bulunamadi. Github'dan indiriliyor...
    git clone https://github.com/mrdarwinjs/mrd-cln.git
    if %errorlevel% neq 0 (
        echo [HATA] Repo indirilemedi. internet baglantinizi kontrol edin.
        pause
        exit /b
    )
    cd /d "%~dp0mrd-cln"
)

:: 3. PYTHON VE CALISTIRMA KONTROLU
echo.
echo [+] Uygulama baslatiliyor...
echo.

:: Python'un calisip calismadigini kesinlestirelim
python --version >nul 2>nul
if %errorlevel% equ 0 (
    python main.py
) else (
    py --version >nul 2>nul
    if %errorlevel% equ 0 (
        py main.py
    ) else (
        echo [HATA] Python komutu calismiyor! 
        echo Python yuklu mu? Yukluyse 'Add to PATH' secenegini isaretlediniz mi?
    )
)

echo.
echo ======================================================
echo Islem tamamlandi veya durduruldu.
echo ======================================================
pause