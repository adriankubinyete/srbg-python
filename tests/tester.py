import tkinter as tk
from tooltipper import Tooltipper as t
import time

def movement():
    for i in range(1, 1000):
        if i % 100 == 0:
            t.tooltip('moving_tip'. i, 100, "hello world")
            time.sleep(0.01)
    

# alguma magica aqui pra preparar o root
root = tk.Tk()
root.withdraw()
t = t(root)

root.mainloop()
