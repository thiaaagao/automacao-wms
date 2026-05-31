@echo off
title Instalando Automacao WMS
echo ============================================
echo   Instalacao - Automacao WMS
echo ============================================
echo.

REM Verifica se Python esta instalado
python --version >nul 2>&1
if %errorlevel% neq 0 (
    echo [ERRO] Python nao encontrado!
    echo Baixe e instale de: https://python.org
    echo (marque "Add Python to PATH" na instalacao)
    echo.
    pause
    exit /b 1
)

echo [OK] Python encontrado
python --version

echo.
echo Instalando dependencias...
pip install -r "%~dp0requirements.txt"
if %errorlevel% neq 0 (
    echo [ERRO] Falha ao instalar dependencias
    pause
    exit /b 1
)

echo.
echo ============================================
echo   Instalacao concluida com sucesso!
echo ============================================
echo.
echo Proximos passos:
echo   1. Abra o WMS na tela de Monitoracao
echo   2. Execute: executar.bat --calibrar
echo   3. Atualize as coordenadas no script
echo   4. Execute: executar.bat --teste
echo   5. Execute: executar.bat
echo.
pause
