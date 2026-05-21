import tkinter as tk
from tkinter import messagebox
from time import time
from datetime import datetime, timedelta


class Stopwatch:
    def __init__(self, root):
        self.root = root
        self.root.title("Stopwatch")

        # ===============================
        # STATE VARIABLES
        # ===============================
        self.running = False
        self.start_time = 0
        self.elapsed = 0

        self.start_timestamp = None
        self.end_timestamp = None

        # Each record is:
        # {"name": str, "start": datetime, "end": datetime}
        self.records = []

        # ===============================
        # NAME INPUT
        # ===============================
        top_frame = tk.Frame(root)
        top_frame.pack(pady=(30, 0))

        self.name_entry = tk.Entry(top_frame, width=30)
        self.name_entry.grid(row=0, column=0, ipady=4, padx=(0, 10))
        self.name_entry.focus_set()

        self.name_entry.bind("<Control-a>", self.select_all)
        self.name_entry.bind("<Return>", self.start_enter)
        self.name_entry.bind("<Control-v>", self.paste)

        # ===============================
        # TIME DISPLAY
        # ===============================
        self.label = tk.Label(root, text="00:00:00:00", font=("Arial", 15))
        self.label.pack(pady=30)

        # ===============================
        # BUTTONS
        # ===============================
        btn_frame = tk.Frame(root)
        btn_frame.pack()

        self.main_btn = tk.Button(btn_frame, text="Start", width=10, command=self.main_action)
        self.main_btn.grid(row=0, column=0)

        self.stop_btn = tk.Button(btn_frame, text="Stop", width=10, command=self.stop)
        self.stop_btn.grid(row=0, column=1)

        self.reset_btn = tk.Button(btn_frame, text="Reset", width=10, command=self.reset)
        self.reset_btn.grid(row=0, column=2)

        # ===============================
        # SAVED LIST DISPLAY
        # ===============================
        self.textbox = tk.Text(root, width=70, height=10, undo=True)
        self.textbox.pack(pady=10)
        self.textbox.bind("<Control-a>", self.select_all_textbox)
        self.textbox.bind("<Double-Button-1>", self.edit_selected_record)
        self.textbox.bind("<Key>", lambda event: "break")  # prevent manual typing inside the display

        # ===============================
        # RIGHT CLICK MENU
        # ===============================
        self.context_menu = tk.Menu(self.root, tearoff=0)
        self.context_menu.add_command(
            label="Edit selected",
            command=self.edit_selected_record
        )

        self.textbox.bind("<Button-3>", self.show_context_menu)
        self.textbox.bind("<Control-c>", self.copy_selected_textbox)
        self.textbox.bind("<Control-C>", self.copy_selected_textbox)

        # ===============================
        # TOTAL TIME
        # ===============================
        self.total_label = tk.Label(root, text="Total: 00:00:00", font=("Arial", 15))
        self.total_label.pack(pady=10)

        self.update_clock()

    # ===============================
    # BINDS
    # ===============================
    def select_all(self, event):
        event.widget.select_range(0, tk.END)
        event.widget.icursor(tk.END)
        return "break"

    def start_enter(self, _):
        self.main_action()
        return "break"

    def paste(self, event):
        try:
            text = self.root.clipboard_get()
            event.widget.insert(tk.INSERT, text)
        except tk.TclError:
            pass
        return "break"

    def select_all_textbox(self, event):
        event.widget.tag_add(tk.SEL, "1.0", tk.END)
        event.widget.mark_set(tk.INSERT, "1.0")
        return "break"

    def copy_selected_textbox(self, event=None):
        try:
            text = self.textbox.get("sel.first", "sel.last")
        except tk.TclError:
            return "break"  # nothing selected

        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()  # keeps clipboard after app closes
        return "break"


    # ===============================
    # Popup
    # ===============================
    def show_context_menu(self, event):
        try:
            # Move cursor to clicked line
            index = self.textbox.index(f"@{event.x},{event.y}")
            self.textbox.mark_set("insert", index)

            # Show menu
            self.context_menu.tk_popup(event.x_root, event.y_root)
        finally:
            self.context_menu.grab_release()

    # ===============================
    # HELPERS
    # ===============================
    def parse_hhmm(self, value):
        value = value.strip()
        parts = value.split(":")
        if len(parts) != 2:
            raise ValueError("Use HH:MM format.")
        hour = int(parts[0])
        minute = int(parts[1])
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            raise ValueError("Hour must be 0-23 and minute must be 0-59.")
        return hour, minute

    def apply_hhmm(self, dt, hhmm):
        hour, minute = self.parse_hhmm(hhmm)
        return dt.replace(hour=hour, minute=minute, second=0, microsecond=0)

    def record_duration_seconds(self, record):
        delta = record["end"] - record["start"]
        if delta.total_seconds() < 0:
            delta += timedelta(days=1)
        return int(delta.total_seconds())

    def format_duration(self, total_seconds):
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        seconds = total_seconds % 60
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    def format_record(self, record):
        duration = self.format_duration(self.record_duration_seconds(record))
        start_str = record["start"].strftime("%H:%M")
        end_str = record["end"].strftime("%H:%M")
        return f'{record["name"]} → {duration} | {start_str} - {end_str}'

    def refresh_textbox(self):
        self.textbox.config(state="normal")
        self.textbox.delete("1.0", tk.END)

        for record in self.records:
            self.textbox.insert(tk.END, self.format_record(record) + "\n")

        content = self.textbox.get("1.0", tk.END).splitlines()
        if content:
            longest = max(len(line) for line in content)
            self.textbox.config(width=max(70, longest + 1))

        line_count = int(self.textbox.index("end-1c").split(".")[0])
        self.textbox.config(height=max(10, line_count))

    def finish_refresh_textbox(self):
        self.textbox.config(state="normal")
        self.refresh_textbox()

    # ===============================
    # START / SAVE
    # ===============================
    def main_action(self):
        if not self.running:
            self.start_time = time() - self.elapsed
            if self.start_timestamp is None:
                self.start_timestamp = datetime.now()
            self.running = True
            self.main_btn.config(text="Save")
        else:
            self.save()
            self.main_btn.config(text="Start")

    # ===============================
    # RESET CURRENT STOPWATCH
    # ===============================
    def reset(self):
        self.running = False
        self.start_time = 0
        self.elapsed = 0
        self.start_timestamp = None
        self.end_timestamp = None
        self.label.config(text="00:00:00:00")
        self.main_btn.config(text="Start")
        self.update_total()

    # ===============================
    # SAVE CURRENT STOPWATCH
    # ===============================
    def save(self):
        if self.start_timestamp is None:
            return

        if self.running:
            self.elapsed = time() - self.start_time
            self.running = False

        if self.elapsed == 0:
            return

        name = self.name_entry.get().strip()
        end_timestamp = datetime.now()

        record = {
            "name": name,
            "start": self.start_timestamp,
            "end": end_timestamp,
        }
        self.records.append(record)

        self.name_entry.delete(0, tk.END)

        self.start_time = 0
        self.elapsed = 0
        self.start_timestamp = None
        self.end_timestamp = None
        self.label.config(text="00:00:00:00")

        self.refresh_textbox()
        self.textbox.config(state="normal")

        self.update_total()

    # ===============================
    # UPDATE CLOCK LOOP
    # ===============================
    def update_clock(self):
        if self.running:
            self.elapsed = time() - self.start_time

        hours = int(self.elapsed // 3600)
        minutes = int((self.elapsed % 3600) // 60)
        seconds = int(self.elapsed % 60)
        milliseconds = int((self.elapsed % 1) * 100)

        self.label.config(text=f"{hours:02}:{minutes:02}:{seconds:02}:{milliseconds:02}")

        self.update_total()
        self.root.after(65, self.update_clock)

    # ===============================
    # STOP / PAUSE
    # ===============================
    def stop(self):
        if self.running:
            self.elapsed = time() - self.start_time
            self.running = False
            self.main_btn.config(text="Start")
            self.update_total()

    # ===============================
    # TOTAL TIME
    # ===============================
    def update_total(self):
        total_seconds = sum(self.record_duration_seconds(record) for record in self.records)
        total_seconds += int(self.elapsed)

        total_str = self.format_duration(total_seconds)
        self.total_label.config(text=f"Total: {total_str}")

    # ===============================
    # EDIT SAVED RECORD
    # ===============================
    def edit_selected_record(self, event=None):
        if not self.records:
            return

        try:
            if event is not None:
                index = self.textbox.index(f"@{event.x},{event.y}")
                line_no = int(index.split(".")[0]) - 1
            else:
                index = self.textbox.index("insert")
                line_no = int(index.split(".")[0]) - 1
        except Exception:
            return

        if line_no < 0 or line_no >= len(self.records):
            return

        record = self.records[line_no]

        popup = tk.Toplevel(self.root)
        popup.title("Edit stopwatch")
        popup.transient(self.root)
        popup.grab_set()

        # Popup size
        width = 430
        height = 170

        screen_width = popup.winfo_screenwidth()
        screen_height = popup.winfo_screenheight()

        # Center coordinates
        x = (screen_width // 2) - (width // 2)
        y = (screen_height // 2) - (height // 2)

        popup.geometry(f"{width}x{height}+{x}+{y}")

        tk.Label(popup, text="Name:").grid(row=0, column=0, padx=10, pady=(10, 5), sticky="e")
        name_var = tk.StringVar(value=record["name"])
        name_entry = tk.Entry(popup, textvariable=name_var, width=30)
        name_entry.grid(row=0, column=1, padx=10, pady=(10, 5))

        tk.Label(popup, text="Start (HH:MM):").grid(row=1, column=0, padx=10, pady=5, sticky="e")
        start_var = tk.StringVar(value=record["start"].strftime("%H:%M"))
        start_entry = tk.Entry(popup, textvariable=start_var, width=30)
        start_entry.grid(row=1, column=1, padx=10, pady=5)

        tk.Label(popup, text="End (HH:MM):").grid(row=2, column=0, padx=10, pady=5, sticky="e")
        end_var = tk.StringVar(value=record["end"].strftime("%H:%M"))
        end_entry = tk.Entry(popup, textvariable=end_var, width=30)
        end_entry.grid(row=2, column=1, padx=10, pady=5)

        def save_changes():
            try:
                new_name = name_var.get().strip()
                new_start = self.apply_hhmm(record["start"], start_var.get())
                new_end = self.apply_hhmm(record["end"], end_var.get())

                record["name"] = new_name
                record["start"] = new_start
                record["end"] = new_end

                self.refresh_textbox()
                self.textbox.config(state="normal")
                self.update_total()
                popup.destroy()
            except Exception as e:
                messagebox.showerror("Invalid time", str(e), parent=popup)

        btn_frame = tk.Frame(popup)
        btn_frame.grid(row=3, column=0, columnspan=2, pady=10)

        tk.Button(btn_frame, text="Save", width=10, command=save_changes).grid(row=0, column=0, padx=5)
        tk.Button(btn_frame, text="Cancel", width=10, command=popup.destroy).grid(row=0, column=1, padx=5)

        name_entry.focus_set()
        popup.bind("<Return>", lambda _event: save_changes())
        popup.bind("<Escape>", lambda _event: popup.destroy())

# ===============================
# MAIN
# ===============================
root = tk.Tk()
app = Stopwatch(root)
root.mainloop()
