# gui/styles.py
from tkinter import ttk

def setup_styles():
    style = ttk.Style()
    style.configure('Tile.TLabelframe', background='#2E2E2E', padding=10)
    style.configure('Tile.TLabelframe.Label', font=('Arial', 14, 'bold'), foreground='white', background='#2E2E2E')
    style.configure('TileHeader.TLabel', font=('Arial', 18), background='#2E2E2E', foreground='#ADD8E6')
    style.configure('TileValue.TLabel', font=('JetBrains Mono', 16, 'bold'), background='#2E2E2E', foreground='#90EE90')
    style.configure('Tile.TButton', font=('JetBrains Mono', 16, 'bold'), padding=15, background='#404040', foreground='white')
