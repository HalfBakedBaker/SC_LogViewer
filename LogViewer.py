""" Realtime log viewer for Star Citizen """
from tkinter import messagebox, filedialog, simpledialog, colorchooser, Toplevel, Menu
import re
import threading
import json
import os
import tkinter as tk
import time
import pyautogui
import webbrowser
import sys
import datetime
import pygame.mixer
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.widgets import Button
from play_time_calculator import PlayTimeCalculator

from tkinter import messagebox
from tkinter import ttk
from tkinter import filedialog  
import time
from pynput import keyboard, mouse
import tkinter as tk
import os 

print("########################################################################################################")
print("LogViewer")
print("Build: 0.2.9.3")
print("30 June 2024")
print("################################################ START ##################################################")

root = tk.Tk()


# Webbrowser Urls

URLS = ["https://issue-council.robertsspaceindustries.com/projects/STAR-CITIZEN",
        "https://robertsspaceindustries.com/spectrum/community/SC/lobby/38230",
        "https://robertsspaceindustries.com/spectrum/community/AVOCADO/lobby/1355241",
        "https://robertsspaceindustries.com/spectrum/community/SC/forum/190048?page=1&sort=newest",
        "https://robertsspaceindustries.com/account/settings",
        "https://robertsspaceindustries.com/galactapedia",
        "https://robertsspaceindustries.com/spectrum/community/SC/forum/190048?page=1&sort=newest",
        "https://robertsspaceindustries.com/spectrum/community/AVOCADO/search?member&page=1&q=&range=year&role=67971&scopes=op%2Creply%2Cchat&sort=latest&visibility=nonerased",
        "https://robertsspaceindustries.com/spectrum/community/SC/search?member&page=1&q=&range=year&role=2&scopes=op%2Creply%2Cchat&sort=latest&visibility=nonerased"]

KEY = ["Issue Council","SC Testing", "Avocado", "Spectrum", "Account", "Galactapedia", "Patchnotes","Evo Latest","SC Testing Latest"]




class LogViewer(threading.Thread):
    """LogViewer class that monitors the log file and displays the log in a tkinter window."""
    def __init__(self,logviewer):
        """Initializes the LogViewer class."""
        threading.Thread.__init__(self,None,daemon=True)
        print("SC Log Monitor Starting...")
        if not os.path.exists("mp3"):
            os.makedirs("mp3")
            self.mp3_folder = os.path.abspath("mp3")
        else:
            self.mp3_folder = os.path.abspath("mp3")
        pygame.mixer.init()

        mp3_files = [f for f in os.listdir(self.mp3_folder) if f.endswith(".mp3")]
        if mp3_files:

            mp3_file = mp3_files[0]
            mp3_file_path = os.path.join(self.mp3_folder, mp3_file)
            print("Playing:", mp3_file_path)

            pygame.mixer.music.load(mp3_file_path)

            pygame.mixer.music.play()
        else:
            print("No mp3 files found in:", self.mp3_folder)


        self.is_minimized = False

        self.logviewer = logviewer

        self.topmost_var = tk.BooleanVar(value=True)

        SliderFrame = tk.Frame(self.logviewer,bg="#1E1E1E")
        SliderFrame.pack(side="top",fill=tk.BOTH, expand=False)

        self.frame = tk.Frame(self.logviewer,bg="black")
        self.frame.pack(fill=tk.BOTH, expand=True)

        logviewer.attributes('-topmost', 1) 
        logviewer.overrideredirect(True)
        logviewer.geometry("705x950")
        logviewer.title("SC LogViewer")

        screen_width = logviewer.winfo_screenwidth()
        screen_height = logviewer.winfo_screenheight()
        x = (screen_width / 2) - (705 / 2)
        y = (screen_height / 2) - (950 / 2)
        logviewer.geometry("705x950+%d+%d" % (x, y))
        
        logviewer.bind("<ButtonPress-3>", self.start_move)
        logviewer.bind("<ButtonRelease-3>", self.stop_move)
        logviewer.bind("<B3-Motion>", self.on_move)

        self.font_scale_var = tk.DoubleVar(value=1.0)


        self.btn_win_mode = tk.Button(self.frame, text="", command=self.toggle_window, fg="white", bg="#1E1E1E") 
        self.btn_win_mode.pack(side="top", fill="x", padx=5, pady=1)
        DefaultSliderValueOpac = 1
        self.slider_opacity = tk.Scale(
            SliderFrame, from_=0.2, to=1, resolution=0.1, width=10, length=250,
            orient="horizontal", label="", showvalue=False, command=self.set_transparency,
            bg="#1E1E1E", fg="#FFFFFF", troughcolor="#565656", highlightbackground="#1E1E1E",
            bd=0, font=("Arial", 10, "bold")
        )
        self.slider_opacity.set(DefaultSliderValueOpac)  
        self.slider_opacity.pack(side="right", fill="x", padx=5, pady=1)

        DefaultSliderValueFont = 1
        self.slider_font_size = tk.Scale(
            SliderFrame, from_=0.2, to=2, resolution=0.01, width=10, length=250,
            orient="horizontal", label="", showvalue=False, command=self.Set_FontSize,
            bg="#1E1E1E", fg="#FFFFFF", troughcolor="#565656", highlightbackground="#1E1E1E",
            bd=0, font=("Arial", 10, "bold")
        )

        self.slider_font_size.set(DefaultSliderValueFont)  
        self.slider_font_size.pack(side="left", fill="x", padx=5, pady=1)
        self.scrollbar = tk.Scrollbar(self.frame)
        self.scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.scrollbar.pack_forget()  

        self.log_text = tk.Text(self.frame, wrap=tk.WORD, yscrollcommand=self.scrollbar.set, fg="white", bg="black")
        self.log_text.pack(fill=tk.BOTH, expand=True)
        self.log_text.config(insertbackground='white', insertwidth=2)
        self.log_text.focus_set()

        self.configure_text_tags()

        height = 1
        self.start_monitor_text = "Start"
        self.pause_monitor_text = "Pause"
        self.stop_monitor_text = "Stop"
        self.resume_monitor_text = "Resume"
        quit_text = "Quit"
        to_top_text = "⬆"
        to_bottom_text = "⬇"
        clear_log_text = "Clear"
        window_mode_text = "Window"
        toggle_file_menu_text = "File"

        toggle_search_menu_text = "Words"

        self.btn_monitor = tk.Button(self.frame, text=self.start_monitor_text, command=self.start_stop, fg="white", bg="green", height=height)
        self.btn_monitor.pack(side="left", padx=5)
        self.btn_pause_monitor = tk.Button(self.frame, text=self.pause_monitor_text, command=self.pause_monitor, fg="white", bg="green", height=height)
        self.btn_pause_monitor.pack(side="left", padx=5)

        self.btn_hide_log_view = tk.Button(self.frame, text=quit_text, command=self.Quit_LV, fg="white", bg="#b30404", height=height)
        self.btn_hide_log_view.pack(side="right", padx=5)

        self.btn_to_top = tk.Button(self.frame, text=to_top_text, command=self.ToTop, fg="white", bg="#333333", height=height,font=("Helvetica", 8))
        self.btn_to_top.pack(side="left", padx=5)

        self.btn_to_bottom = tk.Button(self.frame, text=to_bottom_text, command=self.ToBottom, fg="white", bg="#333333", height=height,font=("Helvetica", 8))
        self.btn_to_bottom.pack(side="left", padx=5)

        self.btn_clear_log_mon = tk.Button(self.frame, text=clear_log_text, command=self.ClearLog, fg="white", bg="#ce723c", height=height)
        self.btn_clear_log_mon.pack(side="left", padx=5)

        self.btn_win_mode = tk.Button(self.frame, text=window_mode_text, command=self.toggle_mode, fg="white", bg="#333333", height=height)
        self.btn_win_mode.pack(side="right", padx=5)

        self.btn_toggle_file_menu= tk.Button(self.frame, text=toggle_file_menu_text, command=self.show_file_menu, fg="white", bg="#333333", height=height)
        self.btn_toggle_file_menu.pack(side="right", padx=5)

        self.btn_toggle_search_menu = tk.Button(self.frame, text=toggle_search_menu_text, command=self.toggle_word_menu, fg="white", bg="#333333", height=height)
        self.btn_toggle_search_menu.pack(side="left", padx=5)

        self.btn_print_stats = tk.Button(self.frame, text="Stats", command=self.print_stats, fg="white", bg="#333333", height=height)
        self.btn_print_stats.pack(side="left", padx=5)

        self.btn_start_stop_chart = tk.Button(self.frame, text="Chart", command=self.start_stop_chart, fg="white", bg="#333333", height=height)
        self.btn_start_stop_chart.pack(side="left", padx=5)

        self.log_text.bind("<FocusOut>", self.on_focus_out)
        self.log_text.bind("<FocusIn>", self.on_focus_in)

        self.logviewer.attributes("-alpha", 0.7)
        self.logviewer.configure(bg="black")

        self.monitor_log_process = False
        self.is_borderless = True
        self.start_stop_chart_bool = False
        self.timer = None
        self.inside_physics_instance = False

        self.search_win = None
        self.pause_monitor = False

        self.is_search_mode = True




        self.menu_bar = tk.Menu(logviewer)

        self.file_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.file_menu.add_command(label="Select LIVE", command=self.save_live_json)

        self.file_menu.add_command(label="Open txt", command=self.open_file)
        self.file_menu.add_command(label="Save txt", command=self.save_file)
        self.file_menu.add_separator()
        self.file_menu.add_command(label="Exit", command=self.Quit_LV)

        self.add_word_menu = tk.Menu(self.file_menu, tearoff=0)
        self.add_word_menu.add_command(label="Word Menu", command=self.toggle_word_menu)


        self.notifications_menu = tk.Menu(self.file_menu, tearoff=0)
        self.notifications_menu.add_command(label="Enable Notifications", command=self.enable_notifications)
        self.notifications_menu.add_command(label="Disable Notifications", command=self.disable_notifications)

        self.monitor_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.monitor_menu.add_command(label=self.start_monitor_text, command=self.start_monitor)
        self.monitor_menu.add_command(label=self.pause_monitor_text, command=self.pause_monitor)
        self.monitor_menu.add_command(label="Stop Monitor", command=self.stop_monitor)
        self.monitor_menu.add_command(label="Clear Log", command=self.ClearLog)
        self.monitor_menu.add_command(label="Top", command=self.ToTop)
        self.monitor_menu.add_command(label="Bottom", command=self.ToBottom)

        self.view_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.view_menu.add_command(label="Toggle Window Mode", command=self.toggle_mode)
        self.view_menu.add_command(label="Toggle Topmost", command=self.toggle_force_front)
        self.view_menu.add_command(label="Toggle Buttons", command=self.toggle_buttons)

        self.menu_bar.add_cascade(label="File", menu=self.file_menu)
        self.menu_bar.add_cascade(label="Words", menu=self.add_word_menu)
        self.menu_bar.add_cascade(label="Notifications", menu=self.notifications_menu)
        self.menu_bar.add_cascade(label="Monitor", menu=self.monitor_menu)
        self.menu_bar.add_cascade(label="View", menu=self.view_menu)


        self.links_menu = tk.Menu(self.menu_bar, tearoff=0)


        for key, url in zip(KEY, URLS):
            self.links_menu.add_command(label=key, command=lambda url=url: webbrowser.open(url))


        self.menu_bar.add_cascade(label="Links", menu=self.links_menu)

        self.extras_menu = tk.Menu(self.menu_bar, tearoff=0)
        self.extras_menu.add_command(label="Idle Monitor", command=self.run_play_time_app)

        self.menu_bar.add_cascade(label="Extras", menu=self.extras_menu)

        logviewer.config(menu=self.menu_bar)




        self.search_list = []
        self.mute_notifications = False


        """Opens the search menu for adding, removing, and coloring persistant search words."""
        self.search_win = Toplevel(self.logviewer)
        self.search_win.title("Search Menu")
        self.search_win.attributes("-topmost", 1) 
        self.search_win.configure(bg="black")
        self.search_win.geometry("300x500")
 
        parent_x = self.logviewer.winfo_x()
        parent_y = self.logviewer.winfo_y()
        parent_width = self.logviewer.winfo_width()
        parent_height = self.logviewer.winfo_height()


        x = parent_x + (parent_width / 2) - (300 / 2)
        y = parent_y + (parent_height / 2) - (500 / 2)


        self.search_win.geometry(f'300x500+{int(x)}+{int(y)}')

        self.search_win.overrideredirect(True)

        self.btn_toggle_search_menu.config(bg="#333333")

        self.search_win.withdraw()



        def move_window(event):
            """Move the window when the left mouse button is dragged."""
            self.search_win.geometry(f'+{event.x_root - dx}+{event.y_root - dy}')


        def on_right_click(event):
            """Store the initial x and y coordinates when the right mouse button is clicked."""
            nonlocal dx, dy
            dx = event.x
            dy = event.y

        def resize_window(event):
            if resizing:
                self.search_win.geometry(f'{event.x_root}x{event.y_root}')


        def on_right_click_resize(event):
            nonlocal resizing
            edge_thickness = 10
            if (event.x > self.search_win.winfo_width() - edge_thickness) or (event.y > self.search_win.winfo_height() - edge_thickness):
                resizing = True
            else:
                resizing = False


        dx, dy = 0, 0

        resizing = False


        self.search_win.bind('<Button-3>', on_right_click)
        self.search_win.bind('<B3-Motion>', move_window)
        self.search_win.bind('<Button-1>', on_right_click_resize)
        self.search_win.bind('<B1-Motion>', resize_window)
            
        self.log_text.bind("<Button-1>", self.on_left_click)




        def add_word():
            """adds word when inside of the search menu/ word manager"""
            try:
                search_word = self.log_text.selection_get()
            except tk.TclError:
                search_word = ""

            if not search_word:

                screen_width = self.search_win.winfo_screenwidth()
                screen_height = self.search_win.winfo_screenheight()
                x = (screen_width / 2) - (300 / 2)
                y = (screen_height / 2) - (500 / 2)
                self.search_win.geometry(f"300x500+{int(x)}+{int(y)}")

                search_word = simpledialog.askstring("Add Word", "Enter a word to search and highlight:", parent=self.search_win)

            if search_word:
                color = colorchooser.askcolor(parent=self.search_win)[1]
                if color:
      


                    notify = messagebox.askyesno("Notify", "Do you want to be notified when the word is found?")
                    self.search_list.append({"word": search_word, "color": color, "count": 0, "notify": notify})
                    self.search_and_highlight_words()
                    update_word_list()



        def hotkey_add_word():
            """Adds a word to the search menu/ word manager using a hotkey, default notify = false."""
            try:
                search_word = self.log_text.selection_get()
            except tk.TclError:
                search_word = None
                print("No text selected.")

            if search_word:
                color = colorchooser.askcolor(parent=self.search_win)[1]
                if color:
                    notify = messagebox.askyesno("Notify", "Do you want to be notified when the word is found?")
                    self.search_list.append({"word": search_word, "color": color, "count": 0, "notify": notify})
                    self.search_and_highlight_words()
                    update_word_list()

        def remove_selected_words():
            """Remove the selected words from the listbox."""
            selected_items = listbox.curselection()
            for item in reversed(selected_items):
                word = self.search_list[item]["word"]
                del self.search_list[item]
                clear_selected_highlights(word)

            update_word_list()

        def remove_all_words():
            """Remove all words from the listbox."""

            def confirm_remove():
                root = tk.Tk()
                root.withdraw()
                return messagebox.askyesno("Confirm Remove", "Do you want to remove all words?")

            if confirm_remove():
                clear_all_highlights()
                self.search_list = []
                update_word_list()
            else:
                print("The operation was cancelled. The words were not removed.")

        def clear_all_highlights():
            """Clear all highlights from the log text widget."""
            for item in self.search_list:
                word = item["word"]
                self.log_text.tag_remove(word, 1.0, tk.END)
                self.log_text.tag_configure(word, foreground="white", background="")

        def clear_selected_highlights(removed_word):
            """Clear the highlights of the removed word."""
            self.log_text.tag_remove(removed_word, 1.0, tk.END)
            self.log_text.tag_configure(removed_word, foreground="white", background="")

        def update_word_list():
            """Update the word list in the listbox."""
            listbox.delete(0, tk.END)
            for idx, item in enumerate(self.search_list):
                word = item["word"]
                color = item["color"]
                listbox.insert(tk.END, word)
                listbox.itemconfig(idx, fg="black", bg=color)

        def color_word():
            """Color the selected words in the listbox."""

            selected_items = listbox.curselection()
            color = colorchooser.askcolor(parent=self.search_win)[1]
            if color:
                for item in selected_items:
                    self.search_list[item]["color"] = color
            update_word_list()
            self.search_and_highlight_words()

        def change_notification_state_for_selected_words():
            """Change the notification state of the selected word in the listbox."""
            selected_items = listbox.curselection()
            # ask the user once if they want to notify when the selected words are found
            notify = messagebox.askyesno("Notify", "Do you want to be notified when the selected words are found?")
            for item in selected_items:
                self.search_list[item]["notify"] = notify


        def default_save_word():
            """Save the current words to the default words file."""

            def confirm_overwrite():
                """Ask the user if they want to overwrite the default words."""
                root = tk.Tk()
                root.withdraw()
                return messagebox.askyesno("Confirm Overwrite", "Do you want to overwrite the default with current words?")

            file_path = "defaultwords.json"
            if file_path:

                if confirm_overwrite():
                    with open(file_path, "w") as file:
                        json.dump(self.search_list, file)
                else:
                    print("The operation was cancelled. The default words were not overwritten.")

        def default_load_word():
            """Load the default words from the default words file."""
            file_path = "defaultwords.json"
            if os.path.exists(file_path):
                with open(file_path, "r") as file:
                    self.search_list = json.load(file)
                self.search_and_highlight_words()
                update_word_list()

        def on_app_close():
            """Handle the close event of the search menu."""

            self.Quit_LV()

        def save_word():
            """Save the current words to a file."""
            file_path = filedialog.asksaveasfilename(defaultextension=".json", filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if file_path:
                with open(file_path, "w") as file:
                    json.dump(self.search_list, file)

        def load_word():
            """Load the words from a file."""
            file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json"), ("All files", "*.*")])
            if file_path:
                with open(file_path, "r") as file:
                    self.search_list = json.load(file)
                self.search_and_highlight_words()
                update_word_list()

        def toggle_highlight():
            """Toggle the highlight of the words in the listbox."""
            self.highlight = not self.highlight
            if self.highlight:
                highlight_button.config(text="Highlight", bg="green", fg="white")
            else:
                highlight_button.config(text="Highlight", bg="black", fg="white")
            self.search_and_highlight_words()


        self.logviewer.protocol("WM_DELETE_WINDOW", on_app_close)

        xpadval = 1
        button_properties = [
            {"frame": "bottom", "text": "Add Word", "command": add_word, "fg": "white", "bg": "#003a96"},

            {"frame": "bottom", "text": "Remove", "command": remove_selected_words, "fg": "white", "bg": "#c73018"},
            {"frame": "bottom", "text": "Remove All", "command": remove_all_words, "fg": "white", "bg": "#7a1d0e"},
            {"frame": "bottom", "text": "Color", "command": color_word, "fg": "white", "bg": "#7809a0"},
        ]

        button_frame_top = tk.Frame(self.search_win, bg="black")
        button_frame_top.pack(side="top", pady=xpadval)

        button_frame_bottom = tk.Frame(self.search_win, bg="black")
        button_frame_bottom.pack(side="bottom")

        frames = {"top": button_frame_top, "bottom": button_frame_bottom}

        for properties in button_properties:
            btn = tk.Button(frames[properties["frame"]], text=properties["text"], command=properties["command"], fg=properties["fg"], bg=properties["bg"])
            btn.pack(side="left", padx=xpadval)

        listbox = tk.Listbox(self.search_win, selectmode=tk.MULTIPLE, fg="white", bg="black")
        listbox.pack(fill=tk.BOTH, expand=True)
        update_word_list()

        self.highlight = False
        highlight_button = tk.Button(
            button_frame_bottom,
            text="Highlight",
            command=toggle_highlight,
            fg="white",
            bg="black",
            activebackground="black",
            activeforeground="white",
        )
        highlight_button.pack(side="left", padx=xpadval)


        menu_bar = tk.Menu(self.search_win)


        file_menu = tk.Menu(menu_bar, tearoff=0)
        file_menu.add_command(label="Save Words", command=save_word)
        file_menu.add_command(label="Load Words", command=load_word)
        file_menu.add_command(label="Save Default", command=default_save_word)
        file_menu.add_command(label="Load Default", command=default_load_word)

        menu_bar.add_cascade(label="File", menu=file_menu)

        words_menu = tk.Menu(menu_bar, tearoff=0)
        words_menu.add_command(label="Add Word", command=add_word)
        words_menu.add_command(label="Remove", command=remove_selected_words)
        words_menu.add_command(label="Remove All", command=remove_all_words)
        menu_bar.add_cascade(label="Words", menu=words_menu)


        highlight_menu = tk.Menu(menu_bar, tearoff=0)
        highlight_menu.add_command(label="Toggle", command=toggle_highlight)
        highlight_menu.add_command(label="New Color", command=color_word)
        menu_bar.add_cascade(label="Highlight Color", menu=highlight_menu)

        # notification menu
        notification_menu = tk.Menu(menu_bar, tearoff=0)
        notification_menu.add_command(label="Change Selected", command=change_notification_state_for_selected_words)
        menu_bar.add_cascade(label="Notify", menu=notification_menu)

        menu_bar.add_command(label="Close", command=self.close_search_menu)

        self.search_win.config(menu=menu_bar)

        #keybinds
        # bind ctrl w to open word menu
        self.logviewer.bind("<Control-e>", lambda event: self.toggle_word_menu())

        # bind  ctrl f to call new function named "search_and_count"
        self.logviewer.bind("<Control-f>", lambda event: self.search_and_count_handler())

        # bind  ctrl q to call new function named "start stop chart"
        self.logviewer.bind("<Control-q>", lambda event: self.start_stop_chart())

        # bind ctrl a to call the keybind word function
        self.logviewer.bind("<Control-w>", lambda event: hotkey_add_word())

        default_load_word()

    def on_focus_out(self, event):

        try:
            start_index, end_index = self.log_text.tag_ranges(tk.SEL)
            if start_index and end_index:

                self.log_text.tag_add("persist_highlight", start_index, end_index)
                self.log_text.tag_configure("persist_highlight", background="gray")
        except ValueError:
            pass  
    
    def on_focus_in(self, event):

        self.log_text.tag_remove("persist_highlight", 1.0, tk.END)
    
    def on_left_click(self, event):

        self.log_text.tag_remove("persist_highlight", 1.0, tk.END)
  
    def search_and_count_handler(self):
        """Handle the search and count operation."""
        if self.is_search_mode:
            self.start_search_and_count()
        else:
            self.finish_search_and_count()

    def start_search_and_count(self): 

        self.is_search_mode = False

        try:
            self.search_word = self.log_text.selection_get()
        except tk.TclError:
            self.search_word = ""

        if not self.search_word:
           

            print("no text selected")
        if self.search_word:

            index = 1.0
            count = 0
            while index:
                index = self.log_text.search(self.search_word, index, stopindex=tk.END, nocase=False)
                if index:
                    count += 1
                    end_index = f"{index}+{len(self.search_word)}c"
                    self.log_text.tag_add(self.search_word, index, end_index)
                    self.log_text.tag_configure(self.search_word, background="yellow", foreground="black")
                    index = end_index
                else:
                    break


            self.notification = Toplevel(self.logviewer)
            self.notification.title("Search and Count")
            self.notification.attributes("-topmost", 1)  
            self.notification.configure(bg="black")

            min_width = 100
            width_multiplier = 10


            calculated_width = len(self.search_word) * width_multiplier


            final_width = max(calculated_width, min_width)


            self.notification.geometry(f"{final_width}x25")



            label = tk.Label(self.notification, text=f"{self.search_word} : {count}", fg="yellow", bg="black", font=("Arial", 12))
            label.pack()

            self.notification.overrideredirect(True)


            x, y = pyautogui.position()
            self.notification.geometry(f"+{x}+{y}")

    def finish_search_and_count(self):
        """Finish the search and count operation by removing the temporary highlights."""

        self.is_search_mode = True
        try:
            self.log_text.tag_remove(self.search_word, 1.0, tk.END)
            self.log_text.tag_configure(self.search_word, foreground="white", background="")


            self.notification.destroy()
            self.search_and_highlight_words()

        except AttributeError:
            pass

    def toggle_buttons(self):
        """Toggles the visibility of the UI buttons in the logviewer window"""
        if self.btn_monitor.winfo_ismapped():
            self.hide_buttons()
        else:
            self.show_buttons()

    def hide_buttons(self):
        """Hides the UI buttons in the logviewer window"""
        self.btn_monitor.pack_forget()
        self.btn_pause_monitor.pack_forget()
        self.btn_hide_log_view.pack_forget()
        self.btn_to_top.pack_forget()
        self.btn_to_bottom.pack_forget()
        self.btn_clear_log_mon.pack_forget()
        self.btn_win_mode.pack_forget()
        self.btn_toggle_file_menu.pack_forget()
        self.btn_toggle_search_menu.pack_forget()
        self.btn_print_stats.pack_forget()
        self.btn_start_stop_chart.pack_forget()
        
    def show_buttons(self):
        """Shows the UI buttons in the logviewer window"""
        self.btn_monitor.pack(side="left", padx=5)
        self.btn_pause_monitor.pack(side="left", padx=5)
        self.btn_hide_log_view.pack(side="right", padx=5)
        self.btn_to_top.pack(side="left", padx=5)
        self.btn_to_bottom.pack(side="left", padx=5)
        self.btn_clear_log_mon.pack(side="left", padx=5)
        self.btn_win_mode.pack(side="right", padx=5)
        self.btn_toggle_file_menu.pack(side="right", padx=5)
        self.btn_toggle_search_menu.pack(side="left", padx=5)
        self.btn_print_stats.pack(side="left", padx=5)
        self.btn_start_stop_chart.pack(side="left", padx=5)

    def show_file_menu(self):
        """Shows a dropdown menu with options"""
        menu = tk.Menu(self.logviewer, tearoff=0, bg="#3f0554", fg="#FFFFFF")

        # Button 1: Select LIVE
        menu.add_command(label="Select LIVE", command=self.save_live_json)

        # Button 2: Open txt
        menu.add_command(label="Open txt", command=self.open_file)

        # Button 3: Save txt
        menu.add_command(label="Save txt", command=self.save_file)
        menu.post(self.btn_toggle_file_menu.winfo_rootx(), self.btn_toggle_file_menu.winfo_rooty())

    def open_file(self):
        """opens a file dialog to select a file and reads the content of the file into the log text widget so the user can read and edit."""
        file_path = filedialog.askopenfilename(filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            with open(file_path, "r", encoding="utf-8") as file:
                content = file.read()
                self.log_text.delete(1.0, tk.END)
                self.log_text.insert(tk.INSERT, content)

    def save_file(self):
        """saves the content of the variable self.log_text to a file. allowing user to modify the log, make notes and save it to a file."""
        file_path = filedialog.asksaveasfilename(defaultextension=".txt", filetypes=[("Text files", "*.txt"), ("All files", "*.*")])
        if file_path:
            content = self.log_text.get(1.0, tk.END)
            with open(file_path, "w") as file:
                file.write(content)

    def toggle_word_menu(self):
        """Toggle the search menu on and off showing the search words and highlighting them in the log text."""
        if self.search_win is not None and self.search_win.winfo_viewable():
            self.close_search_menu()
            print("Search Menu Closed")
        else:
            self.open_search_menu()
            print("Search Menu Opened")

    def open_search_menu(self):
        """Opens the search menu"""
        print("Open search menu called")



        self.search_win.deiconify()


        parent_x = self.logviewer.winfo_x()
        parent_y = self.logviewer.winfo_y()
        parent_width = self.logviewer.winfo_width()
        parent_height = self.logviewer.winfo_height()


        x = parent_x + (parent_width / 2) - (300 / 2)
        y = parent_y + (parent_height / 2) - (500 / 2)


        self.search_win.geometry(f'300x500+{int(x)}+{int(y)}')

        self.search_win.attributes("-topmost", 1)

        self.btn_toggle_search_menu.config(bg="green")

    def close_search_menu(self):
        """Closes the search menu"""
        print("Close search menu called")
        if self.search_win:
            self.search_win.withdraw()


            self.btn_toggle_search_menu.config(bg="#333333")

    def enable_notifications(self):
        """Enable notifications for the search words self.mute_notifications = False"""
        print("Enable notifications called")
        self.mute_notifications = False

    def disable_notifications(self):
        """Disable notifications for the search words self.mute_notifications = True"""
        print("Disable notifications called")
        self.mute_notifications = True

    def toggle_force_front(self):
        """Toggle the topmost attribute of the logviewer window to keep it on top of all other windows."""
        if self.topmost_var.get():
            self.logviewer.attributes("-topmost", 0)

        else:
            self.logviewer.attributes("-topmost", 1)

        self.topmost_var.set(not self.topmost_var.get())

        self.logviewer.lift()

    def highlight_new_line(self, line, start_index):
        """Highlight the new line that was added to the log text."""

        for item in self.search_list:
            word = item["word"]
            color = item["color"]
            index = start_index

            while index:
                index = self.log_text.search(word, index, stopindex=tk.END, nocase=True)
                if index:
                    end_index = f"{index}+{len(word)}c"
                    self.log_text.tag_add(word, index, end_index)
                    if self.highlight:
                        self.log_text.tag_configure(word, background=color, foreground="black")
                    else:
                        self.log_text.tag_configure(word, foreground=color, background="")  
                    index = end_index
                    item["count"] += 1
                else:
                    break

    def load_default_words(self):
        """Load the default words from the defaultwords.json file."""
        file_path = "defaultwords.json"
        if os.path.exists(file_path):
            with open(file_path, "r") as file:
                self.search_list = json.load(file)
            self.search_and_highlight_words()
            self.update_word_list()

    def search_and_highlight_words(self):
        """Search for the words in the search list and highlight them in the log text."""
        for item in self.search_list:
            word = item["word"]
            color = item["color"]
            self.log_text.tag_remove(word, 1.0, tk.END)

        content = self.log_text.get(1.0, tk.END)

        for item in self.search_list:
            word = item["word"]
            color = item["color"]
            index = 1.0
            item["count"] = 0
            while index:
                index = self.log_text.search(word, index, stopindex=tk.END, nocase=False)  
                if index:
                    end_index = f"{index}+{len(word)}c"
                    self.log_text.tag_add(word, index, end_index)
                    if self.highlight:
                        self.log_text.tag_configure(word, background=color, foreground="black")
                    else:
                        self.log_text.tag_configure(word, foreground=color, background="") 
                    index = end_index
                    item["count"] += 1

    def count_words(self):
        """Count the occurrences of each word in the log text."""

        content = self.log_text.get(1.0, tk.END)
        words = content.split()  


        word_counts = {}
        for word in words:
            if word not in word_counts:
                word_counts[word] = 1
            else:
                word_counts[word] += 1


        for item in self.search_list:
            word = item["word"]
            if word in word_counts:
                item["count"] = word_counts[word]
            else:
                item["count"] = 0

    def print_stats(self):
        print("Printing stats...")
        """Print the statistics of the search words to the console."""
        print("____________________________________Word Count____________________________________________")
        
        self.log_text.insert(tk.END, "____________________________________Word Count____________________________________________\n", "yellow")
        for item in self.search_list:
            word = item["word"]
            count = item["count"]
            print(f"{word}: {count}")

            
            self.log_text.insert(tk.END, f"{word}: {count}\n", "yellow")
            self.log_text.see(tk.END)
        print("__________________________________________________________________________________________")
        self.log_text.insert(tk.END, f"__________________________________________________________________________________________\n", "yellow")

    def print_to_console_and_text_widget(self, message):
        """Print a message to the console and the log text widget."""
        print(message)
        self.log_text.insert(tk.END, message + '\n', 'white')
        self.log_text.see(tk.END)

    def start_stop_chart(self):
        """Start or stop the charting of the search word counts."""
        if self.start_stop_chart_bool:
            print("Stopping chart...")
            self.start_stop_chart_bool = False

            self.btn_start_stop_chart.config(bg="#333333")
            self.remove_chart()
        else:
            print("Starting chart...")
            self.start_stop_chart_bool = True

            self.btn_start_stop_chart.config(bg="green")
            self.plot_graph()
 
    def remove_chart(self):
        """Remove the chart from the log text widget."""

        self.btn_start_stop_chart.config(bg="#333333")
        self.start_stop_chart_bool = False
        print("Removing chart...")
        plt.close()

    def plot_graph(self):
        print("Plotting graph...")
        words = [item["word"] for item in self.search_list]
        counts = [item["count"] for item in self.search_list]
        colors = [item["color"] for item in self.search_list]

        plt.style.use('dark_background')
        fig, ax = plt.subplots()
        plt.subplots_adjust(bottom=0.2)
        plt.subplots_adjust(left=0.3)
        plt.subplots_adjust(right=0.97)

        ax.barh(words, counts, color=colors)
        self.set_plot_style(ax)

        button_ax = fig.add_axes([0.81, 0.05, 0.1, 0.075]) 

        button = Button(button_ax, 'Refresh', color='darkgrey', hovercolor='lightgrey')



        button.on_clicked(lambda event: self.refresh_chart(fig, ax))


        fig.canvas.mpl_connect('close_event', lambda event: self.remove_chart())




        plt.show()

    def refresh_chart(self, fig, ax):
        print("Refreshing plot...")
        words = [item["word"] for item in self.search_list]
        counts = [item["count"] for item in self.search_list]
        colors = [item["color"] for item in self.search_list]

        ax.clear()
        ax.barh(words, counts, color=colors)
        self.set_plot_style(ax)
        plt.draw()

    def set_plot_style(self, ax):
        ax.set_title("Search Word Counts", color='white')
        ax.set_xlabel("Counts", color='white')
        ax.set_ylabel("Words", color='white')
        ax.tick_params(axis='x', colors='white')
        ax.tick_params(axis='y', colors='white')

    def print_rsi_launcher_json(self):
        """Print the value of the RSI Launcher directory from the config file to the console and log text widget."""
        script_directory = os.path.abspath('.')
        config_file_path = os.path.join(script_directory, "config.json")
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            message = "SC RSI Launcher Directory : " + config["SC_RSI_directory"]
            self.print_to_console_and_text_widget(message)

    def print_live_json(self):
        """Print the value of the LIVE directory from the config file to the console and log text widget."""
        script_directory = os.path.abspath('.')
        config_file_path = os.path.join(script_directory, "config.json")
        with open(config_file_path, "r") as config_file:
            config = json.load(config_file)
            message = "SC LIVE Launcher Directory : " + config["SC_LIVE_directory"]
            self.print_to_console_and_text_widget(message)

    def save_live_json(self):
        """Save the selected LIVE directory to the config file."""
        root = tk.Tk()
        root.withdraw()
        selected_directory = filedialog.askdirectory()
        if not selected_directory:  
            return

        config = {}

        script_directory = os.path.abspath('.')

        config_file_path = os.path.join(script_directory, "config.json")


        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as config_file:
                config = json.load(config_file)


        config["SC_LIVE_directory"] = selected_directory


        with open(config_file_path, "w") as config_file:
            json.dump(config, config_file)

        self.print_live_json()

    def save_rsi_json(self):
        """Save the selected RSI directory to the config file."""
        root = tk.Tk()
        root.withdraw()
        selected_directory = filedialog.askdirectory()
        if not selected_directory:  
            return

        config = {}
        script_directory = os.path.abspath('.')
        config_file_path = os.path.join(script_directory, "config.json")


        if os.path.exists(config_file_path):
            with open(config_file_path, "r") as config_file:
                config = json.load(config_file)


        config["SC_RSI_directory"] = selected_directory


        with open(config_file_path, "w") as config_file:
            json.dump(config, config_file)

        self.print_rsi_launcher_json()

    def configure_text_tags(self):
        """Configure the text tags used to style the log text. may allow customisation of text tags in the future."""
        small_font_size = 10
        large_font_size = 10
        small_font = ("Helvetica", small_font_size)
        large_font = ("Helvetica", large_font_size)
        self.log_text.configure(font=large_font)
        self.log_text.tag_configure('larger_font', font=large_font)
        self.log_text.tag_configure('Instace_Stats', font=large_font, foreground='#df0eff')

        self.log_text.tag_configure('smaller_font', font=small_font, foreground='#17940c')

    def pause_monitor(self):
        """Pause the monitoring of the log file."""


        pause_bool = self.pause_monitor

        if pause_bool is False:
            print("Monitoring paused...")
            self.pause_monitor = True
            self.btn_pause_monitor.config(text=self.resume_monitor_text, bg="orange")
        else:
            print("Monitoring Resumed...")
            self.pause_monitor = False
            self.btn_pause_monitor.config(text=self.pause_monitor_text, bg="green")

    def start_monitor(self):
        """Start monitoring the log file."""
        for item in self.search_list:
            item["count"] = 0
        self.count_words()
        print("Monitoring started...")

        try:
            with open("config.json", "r") as f:
                config = json.load(f)
                scdir = os.path.join(config["SC_LIVE_directory"], "Game.log")
        except (FileNotFoundError, KeyError):
            print("Error: LIVE directory path not set in config file.")
            print("Please Select Live Directory")
            self.save_live_json()
            self.start_monitor()
            return

        if not self.monitor_log_process:
            self.monitor_log_process = True
            self.monitor_log_thread = threading.Thread(target=self.monitor_log, args=(scdir,),daemon=True)
            self.monitor_log_thread.start()

    def stop_monitor(self):
        """Stop monitoring the log file. there is an issue with the counting being broken when stopping and starting the monitor which is why the count is not working correctly."""
        self.monitor_log_process = False 
        self.btn_monitor.config(text=self.start_monitor_text, bg="green")
        self.btn_pause_monitor.config(text=self.pause_monitor_text, bg="green")
        self.pause_monitor = False
        print("Monitoring stopped...")

    def start_stop(self):
        """Start or stop the monitoring of the log file."""
        if self.btn_monitor["text"] == self.start_monitor_text:
            self.ClearLog()
            self.start_monitor()
            self.btn_monitor.config(text=self.stop_monitor_text, bg="red")
        else:
            self.stop_monitor()
            self.btn_monitor.config(text=self.start_monitor_text, bg="green")

    def process_line(self, line):
        """Process a line of text and insert it into the text widget."""
        current_tag = 'white'


        if "PHYSICS INSTANCE STATS BEGIN" in line:
            self.inside_physics_instance = True

        elif "PHYSICS INSTANCE STATS END" in line:
            self.inside_physics_instance = False
            current_tag = 'Instace_Stats'


        if self.inside_physics_instance:

            current_tag = 'Instace_Stats'

        parts = re.findall(r'(\<\d{4}\-\d{2}\-\d{2}T\d{2}\:\d{2}\:\d{2}\.\d{3}Z\>)(.*$)', line) 


        for part in parts:
            if part[0]:
                self.log_text.insert(tk.END, part[0], 'smaller_font')
                self.log_text.insert(tk.END, part[1], current_tag)
            else:
                self.log_text.insert(tk.END, line, current_tag)

        self.log_text.insert(tk.END, '\n', current_tag)
        self.log_text.see(tk.END)

    def monitor_log(self, file_path):
        self.inside_physics_instance = False 

        """Monitor the log file for changes and update the text widget."""
        if not file_path:
            print("No path set")
            return
        try:
            with open(file_path, "r") as f:
                should_highlight = False
                while self.monitor_log_process:
                    if not self.pause_monitor:  
                        where = f.tell()
                        line = f.readline()
                        if not line:
                            time.sleep(0.1)
                            f.seek(where)
                        else:
                            start_index = self.log_text.index(tk.END + "-1c linestart")
                            self.process_line(line)
                            if self.has_match(line):
                                
                                should_highlight = True
                            if line.endswith('\n') and should_highlight:
                                self.highlight_new_line(line, start_index)
                                should_highlight = False
                    else:
                        time.sleep(0.1)  
        except FileNotFoundError:
            print("File not found:", file_path)

    def has_match(self, line):
        
        for item in self.search_list:
            if item["word"].lower() in line.lower():
            
                if bool(item["notify"]) and not self.mute_notifications:

                    self.mp3_notification()
                return True
        return False

    def mp3_notification(self):
        """Play a notification sound."""

        pygame.mixer.music.play()



        print("mp3_notification")

    def LogStats(self):
        """Log the stats to the console. Not currently used may re implement later."""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"######################### {current_time} ##################################")
        headers = ["Count", "Type"]

       
        data = [(item["count"], item["word"]) for item in self.search_list]


         
        if not data:
            print("No data to print.")
            return


        data.sort(key=lambda x: int(x[0]), reverse=True)

        
        col_widths = [max(len(str(row[i])) for row in data) for i in range(len(headers))]
        row_text = f"######################### {current_time} ##################################"
        self.log_text.insert(tk.END, row_text + "\n")

        
        header_text = ""
        for i in range(len(headers)):
            header_text += headers[i].ljust(col_widths[i]) + "\t"
        print(header_text)
        
        separator_text = "-" * sum(col_widths)
        print(separator_text)
        
        for row in data:
            row_text = ""
            for i in range(len(row)):
                row_text += str(row[i]).ljust(col_widths[i]) + "\t"
            print(row_text)
            
        print("################################ END ###########################################" + "\n")

    def start_move(self, event):
        """Start moving the log viewer window."""
        self.x = event.x
        self.y = event.y
    def stop_move(self, event):
        """Stop moving the log viewer window."""
        self.x = None
        self.y = None
    def on_move(self, event):
        """Move the log viewer window."""
        deltax = event.x - self.x
        deltay = event.y - self.y
        x = self.logviewer.winfo_x() + deltax
        y = self.logviewer.winfo_y() + deltay
        self.logviewer.geometry(f"+{x}+{y}")
    def toggle_window(self):
        """Toggle the log viewer window between minimized and maximized states."""
        if self.is_minimized:
            print("Maximize Log View Window")
            self.logviewer.geometry(f"{self.logviewer.winfo_width()}x950")

            self.is_minimized = False
        else:
            print("Minimize Log View Window")
            self.logviewer.geometry(f"{self.logviewer.winfo_width()}x150")
            
            self.logviewer.after(100, self.ToBottom)

            self.is_minimized = True
    def set_transparency(self, value):
        """Set the transparency of the log viewer window."""
        self.logviewer.attributes('-alpha', float(value))
    def toggle_mode(self):  
        """Toggle the log viewer window between borderless and bordered states."""
        self.is_borderless = not self.is_borderless
        if self.is_borderless:
            print("is borderless True")
            self.logviewer.overrideredirect(True)
        else:
            print("is borderless False")
            self.logviewer.overrideredirect(False)

    def save_to_txt(self):
        """Save the log text to a text file are there two of these?!?."""
        current_time = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
        filename = f"log_{current_time}.txt"
        file_path = tk.filedialog.asksaveasfilename(initialfile=filename, defaultextension=".txt")
        if file_path: 
            with open(file_path, "w", encoding="utf-8") as file:
                file.write(self.log_text.get("1.0", tk.END))
                
    def ClearLog(self):
        """Clear the log text widget."""
        
        print("Stopping Monitor")

        self.btn_monitor.config(text=self.start_monitor_text, bg="green")


        self.log_text.delete("1.0", tk.END)
        
        for item in self.search_list:
            item["count"] = 0

        print("LogCleared")

    def Set_FontSize(self, value):
        """Set the font size of the log text widget."""
        small_font_size = int(float(value) * 10)
        large_font_size = int(float(value) * 10) 
        small_font = ("Helvetica", small_font_size)
        large_font = ("Helvetica", large_font_size)

        self.log_text.tag_configure('white', font=large_font)
        self.log_text.tag_configure('larger_font', font=large_font)
        self.log_text.tag_configure('Blue_font', font=large_font) 
        self.log_text.tag_configure('Yellow_font', font=large_font)
        self.log_text.tag_configure('Purple_font', font=large_font)
        self.log_text.tag_configure('Red_font', font=large_font)
        self.log_text.tag_configure('Orange_font', font=large_font)
        self.log_text.tag_configure('LightGreen_font', font=large_font)

        self.log_text.tag_configure('smaller_font', font=small_font, foreground='#17940c')
        self.log_text.tag_configure('Instace_Stats', font=large_font, foreground='#df0eff')

    def ToTop(self):
        """Scroll the log text widget to the top."""
        self.log_text.see('1.0')

    def ToBottom(self):
        """Scroll the log text widget to the bottom."""
        self.log_text.see(tk.END)

    def Log_View_Vis(self):
        """Toggle the visibility of the log viewer window."""
        if self.logviewer.state() == 'normal':
            print("Log View Hidden")
            self.logviewer.withdraw()
        else:
            print("Log View Visible")
            self.logviewer.deiconify()

    def Quit_LV(self):
        """Quit the log viewer."""
      
        self.stop_monitor()
        self.logviewer.destroy()
        sys.exit()

    def run_play_time_app(self):
        """Run the PlayTimeCalculator application."""
        


        play_time_app = PlayTimeCalculator()
        
        keyboard_listener = keyboard.Listener(on_press=play_time_app.on_press)
        mouse_listener = mouse.Listener(on_click=play_time_app.on_click, on_move=play_time_app.on_move_listener)
        keyboard_listener.start()
        mouse_listener.start()
        play_time_app.mainloop()
        
        keyboard_listener.stop()
        mouse_listener.stop()


LogView = LogViewer(root)


