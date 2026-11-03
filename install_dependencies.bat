@echo off
rem Installs the Python library used by reaper_to_wwise.py
py -m pip install -r "%~dp0requirements.txt" || python -m pip install -r "%~dp0requirements.txt"
pause
