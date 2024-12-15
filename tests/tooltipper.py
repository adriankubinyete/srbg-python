import tkinter as tk
import threading
import time

class Tooltipper:
    def __init__(self, root):
        self.root = root
        
        self.tooltips = {}
        
        self.SHOW_TOOLTIP = True;
        
        # counters
        self.counters = {
            "update": 0,
            "make": 0,
        }
        
    def toggle(self):
        self.SHOW_TOOLTIP = not self.SHOW_TOOLTIP
        return self
    
    # internal method, do not use
    def __make(self, name, x, y, title=""):
        """Creates a tooltip in absolute x,y, and stores in self.tooltips"""
        self.counters["make"] += 1
        
        print('creating window')
        # create tooltip window
        tooltip_window = tk.Toplevel(self.root)
        tooltip_window.geometry(f"5x5+{x}+{y}")  # Initial size as 5x5, posiiton (x, y)
        tooltip_window.overrideredirect(True)  # Remove borders and title bars
        tooltip_window.config(bg="white", bd=1, relief="solid")
        tooltip_window.attributes('-topmost', True) # Above other windows
        tooltip_window.withdraw() 
        
        print('creating label')
        # create label inside tooltip
        label = tk.Label(tooltip_window, text=title, bg="white", anchor="center", justify="center")
        label.pack(padx=0, pady=0) # internal space around text
        
        print('updating sizes')
        # update width and height of tooltip immediately
        tooltip_window.update_idletasks()  # process the changes
        label_width = label.winfo_width()  # gets label width
        label_height = label.winfo_height()  # gets label height
        tooltip_window.geometry(f"{label_width+10}x{label_height+10}+{x}+{y}")  # update tooltip geometry with additional space
        
        print('registering')
        # register to tooltips
        self.tooltips[name] = {
            'title': title,
            'x': x,
            'y': y,
            'window': tooltip_window,  # window reference
            'label': label  # label reference to update later
        }
        
    def __update(self, name, x, y, text=""):
        self.counters["update"] += 1
        tooltip = self.tooltips[name]
        
        # what do we update?
        
        if text != "" and tooltip['label'].cget("text") != text:
            # text, size and pos
            tooltip['label'].config(text=text)
            width = tooltip['label'].winfo_width()
            height = tooltip['label'].winfo_height()
            tooltip['window'].geometry(f"{width}x{height}+{x}+{y}") # size and pos
            
        elif text  != "":
            # size and pos
            width = tooltip['label'].winfo_width()
            height = tooltip['label'].winfo_height()
            tooltip['window'].geometry(f"{width}x{height}+{x}+{y}") # size and pos
            
        else:
            # pos
            tooltip['window'].geometry(f"5x5+{x}+{y}") # pos only, size fixed at 5x5
            
    def tooltip(self, name, x, y, text=""):
        """Creates a tooltip, or updates it if it already exists (based on name parameter)."""
        
        if name not in self.tooltips:
            self.__make(name, x, y, text)
        else:
            self.__update(name, x, y, text)
            
        return