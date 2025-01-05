# main.py
from gui.gui_main import UserInterface
import tkinter as tk

if __name__ == '__main__':
    root = tk.Tk()
    app = UserInterface(root)
    root.mainloop()
