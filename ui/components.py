import tkinter as tk
from tkinter import ttk
import os
import subprocess
import sys
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

def create_action_buttons(parent, process_callback):
    """Create action buttons for the UI"""
    button_frame = tk.Frame(parent, bg='#1e1e1e')
    button_frame.pack(fill='x', pady=10)
    
    process_button = ttk.Button(
        button_frame,
        text="Process Files",
        command=process_callback,
        state='disabled'
    )
    process_button.pack(fill='x', pady=5)
    
    return process_button

def open_folder(path):
    """Open folder in file explorer (cross-platform)"""
    abs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), path))
    if os.path.exists(abs_path):
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', abs_path])
        elif sys.platform == 'win32':  # Windows
            os.startfile(abs_path)
        else:  # Linux and others
            subprocess.run(['xdg-open', abs_path])

def open_file(path):
    """Open file with default application (cross-platform)"""
    abs_path = os.path.abspath(os.path.join(os.path.dirname(os.path.dirname(__file__)), path))
    if os.path.exists(abs_path):
        if sys.platform == 'darwin':  # macOS
            subprocess.run(['open', abs_path])
        elif sys.platform == 'win32':  # Windows
            os.startfile(abs_path)
        else:  # Linux and others
            subprocess.run(['xdg-open', abs_path])
