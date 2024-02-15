@echo off
:start
call animenewep\Scripts\activate.bat
python.exe animekimiget.py
timeout /t 1800 /nobreak
goto start
