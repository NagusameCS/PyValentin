from tkinter import ttk
import sys

# Detect if running as bundled application
IS_BUNDLED = getattr(sys, 'frozen', False)

def setup_styles():
    """Configure application styles"""
    style = ttk.Style()
    
    style.configure('TButton',
        font=('Helvetica', 12),
        background='#007acc',
        foreground='#ffffff',
        focuscolor='#007acc',
        borderwidth=0,
        highlightthickness=0)
    
    style.configure('TLabel',
        font=('Helvetica', 12),
        background='#1e1e1e',
        foreground='#d4d4d4',
        borderwidth=0,
        highlightthickness=0)
    
    style.configure('TEntry',
        font=('Helvetica', 12),
        fieldbackground='#252526',
        foreground='#d4d4d4',
        borderwidth=1,
        highlightthickness=0,
        selectbackground='#264f78',
        selectforeground='#ffffff')
    
    style.configure('Horizontal.TScale',
        background='#1e1e1e',
        troughcolor='#252526',
        borderwidth=0,
        highlightthickness=0)
