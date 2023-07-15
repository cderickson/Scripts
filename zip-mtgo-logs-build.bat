pyinstaller -w --onefile -i "icon_1.png" zip-mtgo-logs.py
rmdir build /s /q
del zip-mtgo-logs.spec