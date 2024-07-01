
from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog  
import time
from pynput import keyboard, mouse
import tkinter as tk
import os 

class PlayTimeCalculator(tk.Tk):
    """Application for calculating play time."""
    def __init__(self):
        """Initialise the application."""
        super().__init__()

        self.title("Play Timer")
    
        self.window_geometry="575x180"
        self.geometry(self.window_geometry)
        self.resizable(False, False)
        self.configure(bg="black")
        self.attributes("-topmost", True)
        self.overrideredirect(True)

        self.attributes("-alpha", 0.75)


        self.time_idle = 0
        self.total_time = 0
        self.actual_play_time_label = 0
        self.paused = False
        self.last_input = time.time()

        self.create_widgets()
        self.bind_all("<Key>", self.on_input)  
        self.bind_all("<Motion>", self.on_input)  
        # For moving the window
        self.bind("<Button-3>", self.start_move)  
        self.bind("<B3-Motion>", self.on_window_move) 
        self.bind("<ButtonRelease-3>", self.stop_move) 

        self._drag_data = {"x": 0, "y": 0}  
        self.window_minimised = False
        

    def start_move(self, event):
        """Begin the drag operation."""
        self._drag_data["x"] = event.x
        self._drag_data["y"] = event.y


    def on_window_move(self, event):
        """Handle dragging of the window."""
        delta_x = event.x - self._drag_data["x"]
        delta_y = event.y - self._drag_data["y"]
        x = self.winfo_x() + delta_x
        y = self.winfo_y() + delta_y
        self.geometry(f"+{x}+{y}")


    def stop_move(self, event):
        """End the drag operation."""
        self._drag_data["x"] = 0
        self._drag_data["y"] = 0

    def on_press(self, key):
        """Update the last input time."""
        self.on_input(None)

    def on_click(self, x, y, button, pressed):
        """Update the last input time."""
        self.on_input(None)

    def on_move_listener(self, x, y):
        """Update the last input time."""
        self.on_input(None)

    def toggle_window(self):#
        """Toggle the window between minimised and normal size."""
        if self.window_minimised:
            
            self.window_minimised = False
            
            self.geometry(self.window_geometry)

        else:
            
            self.window_minimised = True
            self.geometry("575x35")
        
    def create_widgets(self):
        """Create the widgets for the application."""
        
        pad = 0

        self.start_button = ttk.Button(self, text="Start", command=self.start_timer)
        self.start_button.grid(row=0, column=0, padx=pad, pady=pad, sticky="ew") 

        self.stop_button = ttk.Button(self, text="Pause", command=self.stop_timer)
        self.stop_button.grid(row=0, column=1, padx=pad, pady=pad, sticky="ew")
        self.stop_button["state"] = "disabled"

        self.reset_button = ttk.Button(self, text="Reset", command=self.reset_timer)
        self.reset_button.grid(row=0, column=2, padx=pad, pady=pad, sticky="ew") 


        self.save_button = ttk.Button(self, text="Save", command=self.save_timer)
        self.save_button.grid(row=0, column=3, padx=pad, pady=pad, sticky="ew")  

        self.exit_button = ttk.Button(self, text="Exit", command=self.on_close)
        self.exit_button.grid(row=0, column=4, padx=pad, pady=pad, sticky="ew")  

        self.toggle_button = ttk.Button(self, text="Toggle", command=self.toggle_window)
        self.toggle_button.grid(row=0, column=5, padx=pad, pady=pad, sticky="ew") 



        self.active_idle_indicator_color = "Black" 

        self.active_idle_indicator = tk.Canvas(self, width=500, height=10,bg=self.active_idle_indicator_color, highlightthickness=0)
        self.active_idle_indicator.grid(row=1, column=0, columnspan=6, padx=pad, pady=pad, sticky="ew")   



        font_name = "Arial"
        font_size = 15

        self.idle_percentage_label = ttk.Label(self, text="Idle Percentage: 0%", font=(font_name, font_size, "bold"), foreground="white", background="black")
        self.idle_percentage_label.grid(row=2, column=0, columnspan=3, padx=10, pady=10, sticky="ew")  # Idle Percentage label

        self.active_percentage_label = ttk.Label(self, text="Active Percentage: 0%", font=(font_name, font_size, "bold"), foreground="white", background="black")
        self.active_percentage_label.grid(row=2, column=3, columnspan=3, padx=10, pady=10, sticky="ew")  # Active Percentage label

        self.time_idle_label = ttk.Label(self, text="Time Idle: 00:00:00", font=(font_name, font_size, "bold"), foreground="white", background="black")
        self.time_idle_label.grid(row=3, column=0, columnspan=3, padx=10, pady=10, sticky="ew")  # Time Idle label

        self.actual_play_time_label = ttk.Label(self, text="Actual Play Time: 00:00:00", font=(font_name, font_size, "bold"), foreground="white", background="black")
        self.actual_play_time_label.grid(row=3, column=3, columnspan=3, padx=10, pady=10, sticky="ew")  # Actual Play Time label

        self.total_time_label = ttk.Label(self, text="Total Time: 00:00:00", font=(font_name, font_size, "bold"), foreground="white", background="black")
        self.total_time_label.grid(row=4, column=2, columnspan=6, padx=10, pady=10, sticky="ew")  # Total Time at the bottom center

        self.grid_columnconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)
        self.grid_columnconfigure(2, weight=1)
        self.grid_columnconfigure(3, weight=1)
        self.grid_columnconfigure(4, weight=1)
        self.reset_timer()


    def seconds_to_hms(self, seconds):
        """Convert seconds to hours, minutes, and seconds."""
        hours = seconds // 3600
        minutes = (seconds % 3600) // 60
        seconds = seconds % 60
        return f"{hours:02d}:{minutes:02d}:{seconds:02d}"
    
    def save_timer(self):  
        """Save the times to a text file."""
        time_idle = self.time_idle_label["text"]
        total_time = self.total_time_label["text"]
        actual_play_time = self.actual_play_time_label["text"]

        idle_percentage = self.idle_percentage_label["text"]
        active_percentage = self.active_percentage_label["text"]



        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt")])
        if file_path:
            with open(file_path, "w") as file:
                file.write(f"Time Idle: {time_idle}\n")
                file.write(f"Total Time: {total_time}\n")
                file.write(f"Actual Play Time: {actual_play_time}\n")
                file.write(f"{idle_percentage}\n")
                file.write(f"{active_percentage}\n")


            messagebox.showinfo("Save", "Times saved successfully")




    def update_percentages(self):
        """Update the idle and active percentages on the screen."""
        if self.total_time == 0:
            idle_percentage = 0
            active_percentage = 0
        else:
            idle_percentage = (self.time_idle / self.total_time) * 100
            active_percentage = 100 - idle_percentage

        self.idle_percentage_label["text"] = f"Idle Percentage: {idle_percentage:.2f}%"
        self.active_percentage_label["text"] = f"Active Percentage: {active_percentage:.2f}%"

    def update_time(self):  
        """Update the time on the screen."""
        if self.paused:
            return  
        current_time = time.time()
        if current_time - self.last_input >= 1:
            self.time_idle += 1
            self.active_idle_indicator_color = "Red"
            self.active_idle_indicator.configure(bg=self.active_idle_indicator_color) 
            
        else:
            self.active_idle_indicator_color = "Green"
            self.active_idle_indicator.configure(bg=self.active_idle_indicator_color)  
            
        self.total_time += 1

        formatted_time_idle = self.seconds_to_hms(self.time_idle)
        formatted_total_time = self.seconds_to_hms(self.total_time)
        
        actual_play_time = self.total_time - self.time_idle
        formatted_play_time_actual = self.seconds_to_hms(actual_play_time)
        
        self.time_idle_label["text"] = f"Time Idle: {formatted_time_idle}"
        self.total_time_label["text"] = f"Total Time: {formatted_total_time}"
        self.actual_play_time_label["text"] = f"Actual Play Time: {formatted_play_time_actual}"
        
        self.update_percentages()  

        self.after(1000, self.update_time)  
    
    def start_timer(self):
        """Start the timer."""
        if not self.paused:  
            return  
        print("Start Timer")
        self.paused = False
        self.start_button["state"] = "disabled"
        self.stop_button["state"] = "normal"
        self.update_time()  
      
    
    def stop_timer(self):
        """Stop the timer."""
        print("Stop Timer")
        self.paused = True
        self.start_button["state"] = "normal"
        self.stop_button["state"] = "disabled"
        self.active_idle_indicator_color = "Black"
        self.active_idle_indicator.configure(bg=self.active_idle_indicator_color)  
    
    def reset_timer(self):
        """Reset the timer to zero."""
        self.stop_timer()  
        print("Reset Timer")
        self.time_idle = 0
        self.total_time = 0
        self.actual_play_time = 0
        self.time_idle_label["text"] = "Time Idle: 00:00:00"
        self.total_time_label["text"] = "Total Time: 00:00:00"
        self.actual_play_time_label["text"] = "Actual Play Time: 00:00:00"
        self.idle_percentage_label["text"] = "Idle Percentage: 0%"
        self.active_percentage_label["text"] = "Active Percentage: 0%"
       
        self.active_idle_indicator_color = "Black"
        self.active_idle_indicator.configure(bg=self.active_idle_indicator_color)


    def on_input(self, event):
        """Update the last input time."""
        self.last_input = time.time()  

    def on_close(self):
        """Close the application."""
        if messagebox.askokcancel("Quit", "Do you want to quit?"):
            self.destroy()

if __name__ == "__main__":
    app = PlayTimeCalculator()

    keyboard_listener = keyboard.Listener(on_press=app.on_press)
    mouse_listener = mouse.Listener(on_click=app.on_click, on_move=app.on_move_listener)
    keyboard_listener.start()
    mouse_listener.start()
    app.mainloop()

    keyboard_listener.stop()
    mouse_listener.stop()

    