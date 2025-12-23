@echo off
echo Iniciando Agente WhatsApp de Cortes...
echo.
cd /d "%~dp0"
call venv\Scripts\activate
python run.py
pause
