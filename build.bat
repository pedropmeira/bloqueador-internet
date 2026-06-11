@echo off
title Build — Bloqueador Praxedes
cd /d "%~dp0"
echo.
echo  [1/3] Verificando dependencias...

pip show pillow >nul 2>&1
if %errorlevel% neq 0 (
    echo  Instalando Pillow...
    pip install pillow
)

pip show pyinstaller >nul 2>&1
if %errorlevel% neq 0 (
    echo  Instalando PyInstaller...
    pip install pyinstaller
)

echo.
echo  [2/3] Gerando icone...
python create_icon.py
if not exist icon.ico (
    echo  AVISO: icone nao gerado, continuando sem ele.
)

echo.
echo  [3/3] Compilando executavel...
echo.

if exist icon.ico (
    pyinstaller --onefile --windowed --name "BloqueadorPraxedes" --icon "icon.ico" buscador_executaveis.py
) else (
    pyinstaller --onefile --windowed --name "BloqueadorPraxedes" buscador_executaveis.py
)

if exist "dist\BloqueadorPraxedes.exe" (
    echo.
    echo  =========================================
    echo   Executavel gerado com sucesso!
    echo   Local: dist\BloqueadorPraxedes.exe
    echo  =========================================
    echo.
    explorer dist
) else (
    echo.
    echo  ERRO: Build falhou. Verifique os logs acima.
    echo.
)

pause
