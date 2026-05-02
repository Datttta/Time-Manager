import tkinter as tk
from time import time
from datetime import datetime

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
        self.total_elapsed = 0
        self.rows = 0

        self.start_timestamp = None
        self.end_timestamp = None

        # Store saved stopwatches
        self.records = []

        # ===============================
        # NAME INPUT 
        # ===============================
        top_frame = tk.Frame(root)
        top_frame.pack(pady=(30, 0))
        
        # Entry
        self.name_entry = tk.Entry(top_frame, width=30)
        self.name_entry.grid(row=0, column=0, ipady=4, padx=(0, 10))
        self.name_entry.insert(0, "")
        self.name_entry.focus_set()

        ##Binds
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

        # ===============================
        # Total time
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
        event.widget.tag_add(tk.SEL, "1.0", tk.END)  # select all text
        event.widget.mark_set(tk.INSERT, "1.0")      # move cursor to the beginning
        return "break"

    # ===============================
    # START/SAVE
    # ===============================
    def main_action(self):
        if not self.running:
            self.start_time = time() - self.elapsed
            self.start_timestamp = datetime.now()
            self.running = True
            self.main_btn.config(text="")
        else:
            self.save()
            self.main_btn.config(text="Start")

    # ===============================
    # RESET
    # ===============================
    def reset(self):
        self.running = False
        self.elapsed = 0
        self.total_elapsed = 0
        self.label.config(text="00:00:00:00")
        self.start_timestamp = None
        self.end_timestamp = None
        self.main_btn.config(text="")

    # ===============================
    # SAVE CURRENT STOPWATCH
    # ===============================
    def save(self):
        if self.elapsed == 0:
            return  # avoid saving empty stopwatch

        name = self.name_entry.get()

        self.rows += 1

        #print("Row added:", self.rows)

        # Format time elapsed
        hours = int(self.elapsed // 3600)
        minutes = int((self.elapsed % 3600) // 60)
        seconds = int(self.elapsed % 60)

        time_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.end_timestamp = datetime.now()

        # Format timestamps
        start_str = self.start_timestamp.strftime("%H:%M") if self.start_timestamp else "N/A"
        end_str = self.end_timestamp.strftime("%H:%M") if self.end_timestamp else "Running"

        # Save as tuple (name, time)
        record = (name, self.elapsed)
        self.records.append(record)
        
        # Show in textbox
        self.textbox.insert(tk.END, f"{name} → {time_str} | {start_str} - {end_str}\n")

        # Change width based of length stopwatch name 
        content = self.textbox.get("1.0", tk.END).splitlines()

        if content:
            longest = max(len(line) for line in content)
            self.textbox.config(width=max(70, longest))  # keep minimum width

        # Adjust height to number of lines
        line_count = int(self.textbox.index('end-1c').split('.')[0])
        self.textbox.config(height=max(10, line_count))

        self.name_entry.delete(0, tk.END)

        # Reset
        self.reset()

        # Update total time
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

        self.label.config(
            text=f"{hours:02}:{minutes:02}:{seconds:02}:{milliseconds:02}"
        )

        self.root.after(65, self.update_clock)

        self.update_total()

    # ===============================
    # STOP
    # ===============================
    def stop(self):
        if self.running:
            self.running = False
            self.main_btn.config(text="")

    # ===============================
    # Total time
    # ===============================
    def update_total(self):

        if self.running:
            self.total_elapsed = time() - self.start_time

        total_seconds = sum(record[1] for record in self.records) + self.total_elapsed


        hours = int(total_seconds // 3600)
        minutes = int((total_seconds % 3600) // 60)
        seconds = int(total_seconds % 60)

        total_str = f"{hours:02}:{minutes:02}:{seconds:02}"

        self.total_label.config(text=f"Total: {total_str}")

# ===============================
# MAIN
# ===============================
root = tk.Tk()
app = Stopwatch(root)
root.mainloop()
