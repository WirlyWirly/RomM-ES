rem This Windows wrapper script can be used to first call 'GameImporter.py' and then start ES-DE. This process is basically the same as a "Scan on Startup" option for ES-DE

rem First perform a RomM import by calling GameImporter.py
"C:\path\to\python.exe" "C:\path\to\GameImporter.py"

rem After the process completes, start ES-DE 
start "" "C:\path\to\ES-DE.exe"
