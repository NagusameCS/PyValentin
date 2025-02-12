import tkinter as tk
from tkinter import ttk
import os
import subprocess
from utils.file_handlers import process_files

def create_file_input(parent, label_text, entry_var, command):
    """Create a file input component with label and browse button"""
    frame = tk.Frame(parent, bg='#1e1e1e', highlightthickness=0)
    frame.pack(fill='x', pady=10)
    
    ttk.Label(frame, text=label_text).pack(anchor='w')
    
    entry_frame = tk.Frame(frame, bg='#1e1e1e')
    entry_frame.pack(fill='x', pady=(5,0))
    
    entry = ttk.Entry(entry_frame, width=40)
    entry.pack(side='left', fill='x', expand=True)
    
    browse_btn = ttk.Button(entry_frame, text="Browse", command=command)
    browse_btn.pack(side='right', padx=(5,0))
    
    return entry

def create_quality_slider(parent):
    """Create the quality vs quantity slider component"""
    frame = tk.Frame(parent, bg='#1e1e1e', highlightthickness=0)
    frame.pack(fill='x', pady=20)
    
    ttk.Label(frame, text="Quality vs Quantity Balance").pack(anchor='w')
    
    slider = ttk.Scale(frame, from_=0.0, to=1.0, orient='horizontal')
    slider.set(0.5)
    slider.pack(fill='x', pady=(5,0))
    
    label_frame = tk.Frame(frame, bg='#1e1e1e')
    label_frame.pack(fill='x', pady=(5,0))
    
    ttk.Label(label_frame, text="Quantity Priority", style='Small.TLabel').pack(side='left')
    ttk.Label(label_frame, text="Quality Priority", style='Small.TLabel').pack(side='right')
    
    return slider

def create_action_buttons(parent, process_handler):
    """Create a frame with action buttons"""
    frame = tk.Frame(parent, bg='#1e1e1e', highlightthickness=0)
    frame.pack(fill='x', pady=10)
    
    # Create inner frame for button grid
    button_frame = tk.Frame(frame, bg='#1e1e1e')
    button_frame.pack()
    
    # Create buttons in a 2x2 grid
    buttons = [
        ("Open GenR", lambda: open_folder("core/genR")),
        ("Open OP", lambda: open_file("core/genR/optimal_pairs_with_info.csv")),
        ("Open Unp", lambda: open_file("core/genR/unpaired_entries.csv")),
        ("Process", process_handler)
    ]
    
    for i, (text, command) in enumerate(buttons):
        row = i // 2
        col = i % 2
        btn = ttk.Button(button_frame, text=text, command=command, width=15)
        btn.grid(row=row, column=col, padx=5, pady=5)
        
        if text == "Process":
            return btn  # Return process button for state management

def open_folder(path):
    """Open folder in file explorer"""
    abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), path)
    if os.path.exists(abs_path):
        os.startfile(abs_path) if os.name == 'nt' else subprocess.run(['open', abs_path])

def open_file(path):
    """Open file with default application"""
    abs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), path)
    if os.path.exists(abs_path):
        os.startfile(abs_path) if os.name == 'nt' else subprocess.run(['open', abs_path])
