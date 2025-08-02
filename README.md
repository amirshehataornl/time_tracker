# Time Tracker
This is a simple application designed to keep track of time spent at work or other tasks.

- Click "Start Work" when you want to start recording your work time
- Click "End Work" when you want to end recording  your work time
- You can repeat multiple time during the day
- Click "Show Work Log" to display a nicely formatted window of your work log
- Click "Generate Report" to dump the log into a text file
- Click "Remaining Time" to show the amount of remaining time based on a 40 hour work week

# Cross compile to Windows from Linux
The following procedure assumes debian distribution.

- Install wine
- Download python3 for windows from https://www.python.org/downloads/
- run the windows python installation via wine: `wine <python.exe>` ex: `wine python-3.13.5-amd64.exe`
- install `pyinstaller` ex: `wine ~/.wine/drive_c/users/<user>/Local\ Settings/Application\ Data/Programs/Python/Python313/Scripts/pip3.exe install pyinstaller`
- cross compile: `wine ~/.wine/drive_c/users/<user>/Local\ Settings/Application\ Data/Programs/Python/Python313/Scripts/pyinstaller.exe --noconsole --onefile time_tracker.py`
