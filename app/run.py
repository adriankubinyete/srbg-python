import tkinter as tk
from application import Application

if __name__ == "__main__":
    root = tk.Tk()
    app = Application(root)
    root.protocol("WM_DELETE_WINDOW", app.on_gui_close)
    root.mainloop()