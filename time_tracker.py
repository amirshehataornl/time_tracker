import json
import os
import datetime
import tkinter as tk
from tkinter import messagebox

# File to store work log
LOG_FILE = "work_log.json"

STATE_IDLE = 0
STATE_STARTED = 1
STATE_ENDED = 2

g_state = STATE_IDLE

def load_log():
	"""Load work log from JSON file."""
	if os.path.exists(LOG_FILE):
		with open(LOG_FILE, 'r') as f:
			return json.load(f)
	return {}

def save_log(log):
	"""Save work log to JSON file."""
	with open(LOG_FILE, 'w') as f:
		json.dump(log, f, indent=4)

def get_week_number(date):
	"""Get ISO week number for a given date."""
	return date.isocalendar()[1]

def log_start_time():
	global g_state

	"""Log the start time of work."""
	now = datetime.datetime.now()
	date_str = now.strftime("%Y-%m-%d")
	log = load_log()

	if g_state == STATE_STARTED:
		messagebox.showwarning("Time Tracker", "Work already started today!")
		return

	if date_str not in log:
		log[date_str] = []

	time_started = now.strftime("%I:%M:%S %p")
	log[date_str].append({"start": time_started, "end": None})
	save_log(log)
	messagebox.showinfo("Time Tracker", f"Work started at {time_started}")
	g_state = STATE_STARTED

def log_end_time():
	global g_state

	if g_state != STATE_STARTED:
		if g_state == STATE_ENDED:
			messagebox.showwarning("Time Tracker", f"Work has already ended. Start again")
		elif g_state == STATE_IDLE:
			messagebox.showwarning("Time Tracker", f"Work has not started yet")
		return

	"""Log the end time of work."""
	now = datetime.datetime.now()
	date_str = now.strftime("%Y-%m-%d")
	log = load_log()

	if date_str not in log:
		ebox.showwarning("Time Tracker", f"Work surpassed an entire day. Did you really work for more than 24 hours straight?")
		g_state = STATE_IDLE
		return

	end_time = now.strftime("%I:%M:%S %p")
	log[date_str][-1]["end"] = end_time
	save_log(log)
	messagebox.showinfo("Time Tracker", f"Work ended at {end_time}")
	g_state = STATE_ENDED

def calculate_remaining_time():
	"""Generate a weekly report of work hours."""
	log = load_log()
	now = datetime.datetime.now()
	current_week = get_week_number(now)

	report = f"Weekly Work Report (Week {current_week})\n"
	report += "=" * 30 + "\n"
	total_hours = 0

	for date_str, times in log.items():
		date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
		if get_week_number(date) == current_week:
			for time in times:
				if time["start"] and time["end"]:
					start_time = datetime.datetime.strptime(f"{date_str} {time['start']}", "%Y-%m-%d %I:%M:%S %p")
					end_time = datetime.datetime.strptime(f"{date_str} {time['end']}", "%Y-%m-%d %I:%M:%S %p")
					hours = (end_time - start_time).total_seconds() / 3600
					total_hours += hours

	messagebox.showinfo("Remaining Time", f"For week {current_week} is {40 - total_hours}")

def generate_report():
	"""Generate a weekly report of work hours."""
	log = load_log()
	now = datetime.datetime.now()
	current_week = get_week_number(now)

	report = f"Weekly Work Report (Week {current_week})\n"
	report += "=" * 30 + "\n"
	total_hours = 0

	for date_str, times in log.items():
		date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
		if get_week_number(date) == current_week:
			for time in times:
				if time["start"] and time["end"]:
					start_time = datetime.datetime.strptime(f"{date_str} {time['start']}", "%Y-%m-%d %I:%M:%S %p")
					end_time = datetime.datetime.strptime(f"{date_str} {time['end']}", "%Y-%m-%d %I:%M:%S %p")
					hours = (end_time - start_time).total_seconds() / 3600
					total_hours += hours
					report += f"{date_str}: {time['start']} - {time['end']} ({hours:.2f} hours)\n"

	report += f"\nTotal Hours: {total_hours:.2f}\n"

	# Save report to file
	report_file = f"weekly_report_week_{current_week}.txt"
	with open(report_file, 'w') as f:
		f.write(report)

	messagebox.showinfo("Time Tracker", f"Report generated: {report_file}")

def create_window():
	"""Create the main Tkinter window."""
	window = tk.Tk()
	window.title("Time Tracker")
	window.geometry("300x200")

	# Add buttons
	tk.Button(window, text="Start Work", command=log_start_time, width=20).pack(pady=10)
	tk.Button(window, text="End Work", command=log_end_time, width=20).pack(pady=10)
	tk.Button(window, text="Generate Report", command=generate_report, width=20).pack(pady=10)
	tk.Button(window, text="Remaining Time", command=calculate_remaining_time, width=20).pack(pady=10)

	# Handle window close event
	window.protocol("WM_DELETE_WINDOW", window.quit)

	return window

if __name__ == "__main__":
	# Create and run the window
	app = create_window()
	app.mainloop()

