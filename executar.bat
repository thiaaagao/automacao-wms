@echo off
title Automacao WMS
python "%~dp0automacao_wms.py" %*
if %errorlevel% neq 0 (
    echo.
    echo Script finalizado com erro(s).
    pause
)
