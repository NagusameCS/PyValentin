"""
Copyright (c) 2025
This program is part of PyValentin
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.
"""

import csv
import json
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from tkinter import ttk

def install_dependencies():
    required_packages = ["tkinterdnd2", "numpy"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def purge_genR_folder():
    output_dir = os.path.join(os.path.dirname(__file__), "genR")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def replace_values_in_csv(csv_file, config_file, output_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        replacements = json.load(f)
    
    output_dir = os.path.join(os.path.dirname(__file__), "genR")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_file = os.path.join(output_dir, "modified_csv.csv")
    
    with open(csv_file, 'r', encoding='utf-8') as infile, open(output_file, 'w', encoding='utf-8', newline='') as outfile:
        reader = csv.reader(infile)
        writer = csv.writer(outfile)
        
        for row in reader:
            new_row = [replacements.get(cell, cell) for cell in row]
            writer.writerow(new_row)
    
    print("CSV processing completed successfully")

def select_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    csv_entry.delete(0, tk.END)
    csv_entry.insert(0, file_path)

def select_config():
    file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    config_entry.delete(0, tk.END)
    config_entry.insert(0, file_path)

def process_files():
    csv_file = csv_entry.get()
    config_file = config_entry.get()
    if csv_file and config_file:
        purge_genR_folder()
        replace_values_in_csv(csv_file, config_file, "modified_csv.csv")

def create_ui():
    root = tk.Tk()
    root.title("CSV Value Replacer")
    root.geometry("600x400")
    root.configure(bg='#1e1e1e')

    style = ttk.Style()
    style.configure('TButton', font=('Consolas', 12), padding=10, background='#007acc', foreground='#ffffff')
    style.configure('TLabel', font=('Consolas', 14), background='#1e1e1e', foreground='#d4d4d4')
    style.configure('TEntry', font=('Consolas', 12), padding=10, background='#252526', foreground='#d4d4d4')

    global csv_entry, config_entry

    ttk.Label(root, text="Select CSV File:", background='#1e1e1e', foreground='#d4d4d4').pack(pady=10)
    csv_entry = ttk.Entry(root, width=50)
    csv_entry.pack(pady=5)
    ttk.Button(root, text="Browse", command=select_csv).pack(pady=5)

    ttk.Label(root, text="Select Config File:", background='#1e1e1e', foreground='#d4d4d4').pack(pady=10)
    config_entry = ttk.Entry(root, width=50)
    config_entry.pack(pady=5)
    ttk.Button(root, text="Browse", command=select_config).pack(pady=5)

    ttk.Button(root, text="Process Files", command=process_files).pack(pady=20)

    root.mainloop()

if __name__ == "__main__":
    install_dependencies()
    create_ui()
