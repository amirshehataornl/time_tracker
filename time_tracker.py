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
	"""Display work log data in a formatted Tkinter table with separate Delete and Edit columns."""
	# Create a new top-level window for the table
	table_window = tk.Toplevel(parent)
	table_window.title("Work Time Records")
	table_window.geometry("900x450")  # Increased width for two action columns
	table_window.configure(bg="#f5f6f5")

	# Function to format seconds into HH:MM:SS
	def format_duration(seconds):
		hours, remainder = divmod(seconds, 3600)
		minutes, seconds = divmod(remainder, 60)
		return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

	# Function to calculate time difference in seconds
	def calculate_duration(start, end, date):
		try:
			start_dt = datetime.datetime.strptime(f"{date} {start}", "%Y-%m-%d %I:%M:%S %p")
			end_dt = datetime.datetime.strptime(f"{date} {end}", "%Y-%m-%d %I:%M:%S %p")
			return int((end_dt - start_dt).total_seconds())
		except ValueError:
			return 0

	# Function to delete an entry and update JSON
	def delete_entry(entry_index, date):
		try:
			# Create a copy of json_data to modify
			log = json_data.copy()
			# Preserve g_state if it exists
			g_state_temp = log.get('g_state')
			if g_state_temp is not None:
				del log['g_state']
			# Remove the entry
			if date in log and 0 <= entry_index < len(log[date]):
				del log[date][entry_index]
				# Remove date if no entries remain
				if not log[date]:
					del log[date]
				# Restore g_state
				if g_state_temp is not None:
					log['g_state'] = g_state_temp
				# Save to file
				save_log(log)
				# Refresh the table
				table_window.destroy()
				if log:
					display_work_log(parent, log)
				else:
					empty_window = tk.Toplevel(parent)
					empty_window.title("Work Time Records")
					empty_window.geometry("300x100")
					empty_window.configure(bg="#f5f6f5")
					tk.Label(
						empty_window,
						text="No work log entries to display",
						font=("Helvetica", 12),
						bg="#f5f6f5",
						fg="#333333",
						pady=20
					).pack()
		except Exception as e:
			messagebox.showerror("Error", f"Failed to delete entry: {str(e)}")

	# Function to edit an entry
	def edit_entry(entry_index, date):
		try:
			log = json_data.copy()
			g_state_temp = log.get('g_state')
			if g_state_temp is not None:
				del log['g_state']
			entry = log[date][entry_index]
			start = entry["start"]
			end = entry["end"]

			# Create edit dialog
			edit_window = tk.Toplevel(table_window)
			edit_window.title("Edit Work Entry")
			edit_window.geometry("300x200")
			edit_window.configure(bg="#f5f6f5")

			tk.Label(edit_window, text="Start Time (HH:MM:SS AM/PM):", bg="#f5f6f5").pack(pady=5)
			start_entry = tk.Entry(edit_window, width=20)
			start_entry.insert(0, start)
			start_entry.pack(pady=5)

			tk.Label(edit_window, text="End Time (HH:MM:SS AM/PM):", bg="#f5f6f5").pack(pady=5)
			end_entry = tk.Entry(edit_window, width=20)
			end_entry.insert(0, end if end else "")
			end_entry.pack(pady=5)

			def save_changes():
				new_start = start_entry.get()
				new_end = end_entry.get()
				try:
					# Validate time format
					start_dt = datetime.datetime.strptime(f"{date} {new_start}", "%Y-%m-%d %I:%M:%S %p")
					new_start = start_dt.strftime("%I:%M:%S %p")
					if new_end:
						end_dt = datetime.datetime.strptime(f"{date} {new_end}", "%Y-%m-%d %I:%M:%S %p")
						new_end = end_dt.strftime("%I:%M:%S %p")
					# Update entry
					log[date][entry_index]["start"] = new_start
					log[date][entry_index]["end"] = new_end
					# Restore g_state
					if g_state_temp is not None:
						log['g_state'] = g_state_temp
					# Save to file
					save_log(log)
					# Refresh table
					table_window.destroy()
					display_work_log(parent, log)
					edit_window.destroy()
				except ValueError:
					messagebox.showerror("Error", "Invalid time format. Use HH:MM:SS AM/PM")
				except Exception as e:
					messagebox.showerror("Error", f"Failed to save changes: {str(e)}")

			tk.Button(
				edit_window,
				text="Save",
				command=save_changes,
				width=10,
				bg="#4a90e2",
				fg="white"
			).pack(pady=10)

		except Exception as e:
			messagebox.showerror("Error", f"Failed to edit entry: {str(e)}")

	# Function to add a new entry
	def add_entry(date):
		try:
			log = json_data.copy()
			g_state_temp = log.get('g_state')
			if g_state_temp is not None:
				del log['g_state']

			add_window = tk.Toplevel(table_window)
			add_window.title("Add Work Entry")
			add_window.geometry("300x200")
			add_window.configure(bg="#f5f6f5")

			tk.Label(add_window, text="Start Time (HH:MM:SS AM/PM):", bg="#f5f6f5").pack(pady=5)
			start_entry = tk.Entry(add_window, width=20)
			start_entry.pack(pady=5)

			tk.Label(add_window, text="End Time (HH:MM:SS AM/PM):", bg="#f5f6f5").pack(pady=5)
			end_entry = tk.Entry(add_window, width=20)
			end_entry.pack(pady=5)

			def save_new_entry():
				new_start = start_entry.get()
				new_end = end_entry.get()
				try:
					start_dt = datetime.datetime.strptime(f"{date} {new_start}", "%Y-%m-%d %I:%M:%S %p")
					new_start = start_dt.strftime("%I:%M:%S %p")
					if new_end:
						end_dt = datetime.datetime.strptime(f"{date} {new_end}", "%Y-%m-%d %I:%M:%S %p")
						new_end = end_dt.strftime("%I:%M:%S %p")
					if date not in log:
						log[date] = []
					log[date].append({"start": new_start, "end": new_end if new_end else None})
					# Sort entries by start time
					log[date].sort(key=lambda x: datetime.datetime.strptime(f"{date} {x['start']}", "%Y-%m-%d %I:%M:%S %p"))
					if g_state_temp is not None:
						log['g_state'] = g_state_temp
					save_log(log)
					table_window.destroy()
					display_work_log(parent, log)
					add_window.destroy()
				except ValueError:
					messagebox.showerror("Error", "Invalid time format. Use HH:MM:SS AM/PM")
				except Exception as e:
					messagebox.showerror("Error", f"Failed to add entry: {str(e)}")

			tk.Button(
				add_window,
				text="Save",
				command=save_new_entry,
				width=10,
				bg="#4a90e2",
				fg="white"
			).pack(pady=10)

		except Exception as e:
			messagebox.showerror("Error", f"Failed to add entry: {str(e)}")

	# Function to handle click events on Delete, Edit, and Add columns
	def on_tree_click(event):
		# Identify the clicked item and column
		item = tree.identify_row(event.y)
		column = tree.identify_column(event.x)
		if not item or column not in ("#5", "#6"):  # Delete (#5) or Edit (#6) columns
			return
		# Get the tags to determine if it's a header row
		tags = tree.item(item, "tags")
		if column == "#5" and "header" not in tags:  # Delete action
			for tag in tags:
				if tag.startswith("entry_"):
					_, date, idx = tag.split("_")
					delete_entry(int(idx), date)
		elif column == "#6":  # Edit or Add action
			if "header" in tags:
				# Add action for header row
				for tag in tags:
					if tag.startswith("date_"):
						date = tag.split("_")[1]
						add_entry(date)
			else:
				# Edit action for data row
				for tag in tags:
					if tag.startswith("entry_"):
						_, date, idx = tag.split("_")
						edit_entry(int(idx), date)

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
	columns = ("Work Date", "Start Time", "End Time", "Total Time", "Delete", "Edit")
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
		tree.column(col, width=150 if col not in ("Delete", "Edit") else 40, anchor="center")

	# Add scrollbars
	vsb = ttk.Scrollbar(table_frame, orient="vertical", command=tree.yview)
	vsb.pack(side="right", fill="y")
	tree.configure(yscrollcommand=vsb.set)

	# Bind click event to the Treeview
	tree.bind("<Button-1>", on_tree_click)

	# Process JSON data and populate the table
	total_seconds = 0
	try:
		dates = list(json_data.keys())
		j = 0
		for date in dates:
			day_total_seconds = 0
			header_id = tree.insert(
				"",
				tk.END,
				values=(format_date_with_suffix(date), "", "", "", "", ""),
				tags=("header", f"date_{date}")
			)
			for i, entry in enumerate(json_data[date]):
				start = entry["start"]
				end = entry["end"]
				total_time = calculate_duration(start, end, date) if end else 0
				total_seconds += total_time
				day_total_seconds += total_time
				# Add action text and unique tag for the entry
				tree.insert(
					"",
					tk.END,
					values=(format_date_with_suffix(date), start, end if end else "N/A", format_duration(total_time), "\u274C", "\U0000270E"),
					tags=("even" if j % 2 == 0 else "odd", f"entry_{date}_{i}")
				)
				j += 1
			tree.item(header_id, values=(format_date_with_suffix(date), "", "", format_duration(day_total_seconds), "", "\u2795"))
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

	# Configure alternating row colors and action column styles
	tree.tag_configure("even", background="#f0f0f0", font=("Helvetica", 10, "bold"), foreground="blue")
	tree.tag_configure("odd", background="#ffffff", font=("Helvetica", 10, "bold"))
	tree.tag_configure("header", background="#add8e6", font=("Helvetica", 12, "bold"))
	# Apply action column styles to non-header rows
	for item in tree.get_children():
		tags = tree.item(item, "tags")
		if "header" not in tags:
			tree.item(item, tags=tags + ("delete_cell", "edit_cell"))

	# Display day total time
	day_total_label = tk.Label(
		table_window,
		text=f"Total Time: {format_duration(total_seconds)}",
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
	tk.Button(window, text="Start Work", font=("Helvetica", 15), bg="green", fg="white", command=log_start_time, width=20).pack(pady=10)
	tk.Button(window, text="End Work", font=("Helvetica", 15), bg="red", fg="white", command=log_end_time, width=20).pack(pady=10)
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

