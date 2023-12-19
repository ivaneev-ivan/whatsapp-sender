@echo off
chcp 65001

rem ------------ ИМЯ ИСХОДНОГО ФАЙЛА  ---- МЕНЯТЬ ТУТ
Set infile=send_messages

rd /s /q "__pycache__"
rd /s /q "build"
rd /s /q "dist"
del /q *.spec
del /q *.exe

pyi-makespec %infile%.py --onefile --add-data "adb-cmd;." --name %infile%

pyinstaller --clean %infile%.spec

pause

move .\dist\%infile%.exe .\%infile%.exe

rd /s /q "__pycache__"
rd /s /q "build"
rd /s /q "dist"
del /q *.spec
del /q .\protectmod.py

