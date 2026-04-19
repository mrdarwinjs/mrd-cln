@echo off
title Nuitka Pro Compiler - Atlas OS
setlocal enabledelayedexpansion

:: Yonetici Izni Kontrolu
openfiles >nul 2>&1
if %errorlevel% neq 0 (
    echo [X] HATA: Lutfen bu dosyayi SAG TIKLAYIP 'Yonetici Olarak Calistir' deyin.
    pause
    exit /b
)

echo [+] Gereksinimler Kontrol Ediliyor...
python -m pip install --upgrade pip
pip install nuitka customtkinter rich

echo.
echo [!] Derleme Basliyor (C Backend)...
echo.

:: --standalone ve --onefile parametreleri bazen cakistigi icin
:: Atlas OS uzerinde en stabil yontem budur:
python -m Nuitka ^
    --onefile ^
    --standalone ^
    --windows-disable-console ^
    --plugin-enable=tk-inter ^
    --follow-imports ^
    --output-dir=derlenmis_program ^
    --remove-output ^
    --assume-yes-for-downloads ^
    main.py

if %ERRORLEVEL% EQU 0 (
    echo.
    echo [OK] Derleme Tamam! Dosya: derlenmis_program\main.exe
    start "" "derlenmis_program\main.exe"
) else (
    echo.
    echo [X] HATA: Derleme basarisiz. Python'un resmi sitesinden kurulduguna emin olun.
    pause
)