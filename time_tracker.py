import json
import os
import datetime
import tkinter as tk
from tkinter import messagebox
from tkinter import ttk

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

def format_date_with_suffix(date_str):
	"""Convert date from YYYY-MM-DD to 'Month DDth, YYYY' format."""
	# Parse the input date string
	date_obj = datetime.datetime.strptime(date_str, "%Y-%m-%d")

	# Get day number to determine suffix
	day = date_obj.day
	if 10 <= day % 100 <= 20:
		suffix = "th"  # 11th, 12th, 13th, etc.
	else:
		suffix = {1: "st", 2: "nd", 3: "rd"}.get(day % 10, "th")

	# Format the date with month name, day, suffix, and year
	formatted_date = date_obj.strftime(f"%B {day}{suffix}, %Y")
	return formatted_date

def display_work_log(parent, json_data):
	"""Display work log data in a formatted Tkinter table in a new window."""
	# Create a new top-level window for the table
	table_window = tk.Toplevel(parent)
	table_window.title("Work Time Records")
	table_window.geometry("700x450")
	table_window.configure(bg="#f5f6f5")

	# Function to format seconds into HH:MM:SS
	def format_duration(seconds):
		hours, remainder = divmod(seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

	# Function to calculate time difference in seconds
	def calculate_duration(start, end, date):
		start_dt = datetime.datetime.strptime(f"{date} {start}", "%Y-%m-%d %I:%M:%S %p")
		end_dt = datetime.datetime.strptime(f"{date} {end}", "%Y-%m-%d %I:%M:%S %p")
		return int((end_dt - start_dt).total_seconds())

	# Header frame for title
	header_frame = tk.Frame(table_window, bg="#4a90e2")
	header_frame.pack(fill="x", padx=10, pady=(10, 5))
	title_label = tk.Label(
		header_frame,
		text="Work Time Records",
		font=("Helvetica", 16, "bold"),
		bg="#4a90e2",
		fg="white",
		pady=10
	)
	title_label.pack()

	# Create a frame for the table
	table_frame = tk.Frame(table_window, bg="#f5f6f5")
	table_frame.pack(padx=10, pady=5, fill="both", expand=True)

	# Define column headers
	columns = ("Work Date", "Start Time", "End Time", "Total Time")
	tree = ttk.Treeview(table_frame, columns=columns, show="headings", height=10)
	tree.pack(side="left", fill="both", expand=True)

	# Configure Treeview style
	style = ttk.Style()
	style.theme_use("clam")
	style.configure(
		"Treeview",
		font=("Helvetica", 10),
		rowheight=30,
		background="#ffffff",
		foreground="#333333",
		fieldbackground="#ffffff"
	)
	style.configure(
		"Treeview.Heading",
		font=("Helvetica", 11, "bold"),
		background="#4a90e2",
		foreground="white"
	)
	style.map("Treeview", background=[("selected", "#0078d7")])

	# Set column headings and configure alignment
	for col in columns:
		tree.heading(col, text=col, anchor="center")
		tree.column(col, width=150, anchor="center")

	# Add scrollbars
	vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
	vsb.pack(side="right", fill="y")
	tree.configure(yscrollcommand=vsb.set)

	# Process JSON data and populate the table
	day_total_seconds = 0
	try:
		dates = list(json_data.keys())
		j = 0
		for date in dates:
			tree.insert(
				"",
				tk.END,
				values=(format_date_with_suffix(date), "", "", ""),
				tags=("header",)
			)
			for i, entry in enumerate(json_data[date]):
				start = entry["start"]
				end = entry["end"]
				if end:
					total_time = calculate_duration(start, end, date)
					day_total_seconds += total_time
				else:
					total_time = 0
				tree.insert(
					"",
					tk.END,
					values=(date, start, end, format_duration(total_time)),
					tags=("even" if j % 2 == 0 else "odd",)
				)
				j += 1
	except (KeyError, ValueError, IndexError) as e:
		error_label = tk.Label(
			table_window,
			text="Error: Invalid JSON data format",
			font=("Helvetica", 12, "bold"),
			bg="#f5f6f5",
			fg="red"
		)
		error_label.pack(pady=10)
		return

	# Configure alternating row colors
	tree.tag_configure("even", background="#f0f0f0", font=("Helvetica", 10, "bold"), foreground="red")
	tree.tag_configure("odd", background="#ffffff", font=("Helvetica", 10, "bold"))
	tree.tag_configure("header", background="#add8e6", font=("Helvetica", 12, "bold"))

	# Display day total time
	day_total_label = tk.Label(
		table_window,
		text=f"Total Time: {format_duration(day_total_seconds)}",
		font=("Helvetica", 12, "bold"),
		bg="#f5f6f5",
		fg="#333333",
		pady=10
	)
	day_total_label.pack()

def log_start_time():
	global g_state

	log = load_log()

	if 'g_state' in log:
		g_state = log['g_state']

	"""Log the start time of work."""
	now = datetime.datetime.now()
	date_str = now.strftime("%Y-%m-%d")

	if g_state == STATE_STARTED:
		messagebox.showwarning("Time Tracker", "Work already started today!")
		return

	if date_str not in log:
		log[date_str] = []

	time_started = now.strftime("%I:%M:%S %p")
	log[date_str].append({"start": time_started, "end": None})
	g_state = STATE_STARTED
	log['g_state'] = g_state
	save_log(log)
	messagebox.showinfo("Time Tracker", f"Work started at {time_started}")

def log_end_time():
	global g_state

	log = load_log()

	if 'g_state' in log:
		g_state = log['g_state']

	if g_state != STATE_STARTED:
		if g_state == STATE_ENDED:
			messagebox.showwarning("Time Tracker", f"Work has already ended. Start again")
		elif g_state == STATE_IDLE:
			messagebox.showwarning("Time Tracker", f"Work has not started yet")
		return

	"""Log the end time of work."""
	now = datetime.datetime.now()
	date_str = now.strftime("%Y-%m-%d")

	if date_str not in log:
		ebox.showwarning("Time Tracker", f"Work surpassed an entire day. Did you really work for more than 24 hours straight?")
		g_state = STATE_IDLE
		return

	end_time = now.strftime("%I:%M:%S %p")
	log[date_str][-1]["end"] = end_time
	g_state = STATE_ENDED
	log['g_state'] = g_state
	save_log(log)
	messagebox.showinfo("Time Tracker", f"Work ended at {end_time}")

def calculate_time(inreport=''):
	log = load_log()
	now = datetime.datetime.now()
	current_week = get_week_number(now)
	total_hours = 0
	total_day_hours = 0

	if 'g_state' in log:
		del(log['g_state'])

	report = inreport

	for date_str, times in log.items():
		date = datetime.datetime.strptime(date_str, "%Y-%m-%d")
		if get_week_number(date) == current_week:
			for time in times:
				if time["start"] and time["end"]:
					start_time = datetime.datetime.strptime(f"{date_str} {time['start']}", "%Y-%m-%d %I:%M:%S %p")
					end_time = datetime.datetime.strptime(f"{date_str} {time['end']}", "%Y-%m-%d %I:%M:%S %p")
					hours = (end_time - start_time).total_seconds() / 3600
					total_hours += hours
					total_day_hours += hours
					if inreport:
						report += f"{date_str}: {time['start']} - {time['end']} ({hours:.2f} hours)\n"
			if inreport:
				report += f"Total hours for {date_str}: {total_day_hours:.2f}\n"
			total_day_hours = 0

	return total_hours, report

def calculate_remaining_time():
	"""Generate a weekly report of work hours."""
	now = datetime.datetime.now()
	current_week = get_week_number(now)

	total_hours, report = calculate_time()

	messagebox.showinfo("Remaining Time", f"For week {current_week} is {40 - total_hours}")

def generate_report():
	"""Generate a weekly report of work hours."""
	now = datetime.datetime.now()
	current_week = get_week_number(now)
	report = f"Weekly Work Report (Week {current_week})\n"
	report += "=" * 30 + "\n"

	total_hours, report = calculate_time(inreport=report)

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

	def show_work_log():
		if not os.path.exists("work_log.json"):
			messagebox.showwarning("Time Tracker", "No work to show")
		log = load_log()
		if 'g_state' in log:
			del(log['g_state'])
		display_work_log(window, log)

	# Create a temporary button to measure its height
	temp_button = tk.Button(window, text="Test", font=("Helvetica", 15), width=20)
	temp_button.pack(pady=10)
	button_height = temp_button.winfo_reqheight()
	temp_button.destroy()

	# Calculate total height
	num_buttons = 5
	pady_per_button = 20
	total_button_height = num_buttons * button_height
	total_pady = (num_buttons - 1) * pady_per_button + 10
	border_and_title = 40
	total_height = total_button_height + total_pady + border_and_title

	# Set window geometry with calculated height
	window.geometry(f"300x{total_height}")

	# Add buttons
	tk.Button(window, text="Start Work", font=("Helvetica", 15), command=log_start_time, width=20).pack(pady=10)
	tk.Button(window, text="End Work", font=("Helvetica", 15), command=log_end_time, width=20).pack(pady=10)
	tk.Button(window, text="Generate Report", font=("Helvetica", 15), command=generate_report, width=20).pack(pady=10)
	tk.Button(window, text="Show Work Log", font=("Helvetica", 15), command=show_work_log, width=20).pack(pady=10)
	tk.Button(window, text="Remaining Time", font=("Helvetica", 15), command=calculate_remaining_time, width=20).pack(pady=10)

	# Handle window close event
	window.protocol("WM_DELETE_WINDOW", window.quit)

	return window

if __name__ == "__main__":
	# Create and run the window
	app = create_window()
	app.mainloop()

