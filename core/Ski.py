"""
Copyright (c) 2025
This program is part of PyValentin
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.
"""

import csv
import os
import shutil
import subprocess
import sys
import numpy as np
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

# Function to read CSV and process data
def process_csv(file_path):
    data = []
    with open(file_path, newline='') as csvfile:
        reader = csv.reader(csvfile)
        next(reader)  # Skip header row
        for row in reader:
            processed_row = [row[1]] + row[4:]  # Include 0th index before any of the others
            data.append(processed_row)
    return data

# Function to form coordinate pairs and calculate distances
def calculate_distances(data):
    distances = []
    for row in data:
        coordinates = []
        for i in range(1, len(row) - 1, 2):
            x = float(row[i])
            y = float(row[i + 1])
            coordinates.append((x, y))
        midpoint = calculate_midpoint(coordinates)
        row_distances = [calculate_distance(midpoint, point) for point in coordinates]
        distances.append([row[0]] + row_distances)
    return distances

# Function to calculate the midpoint of a set of points
def calculate_midpoint(points):
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    return (sum(x_coords) / len(x_coords), sum(y_coords) / len(y_coords))

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Function to compare each row with every other row to determine a "list of similarity"
def calculate_similarity(data):
    """Calculate cosine similarity between participants"""
    similarity = []
    for i, row1 in enumerate(data):
        similarities = []
        vec1 = np.array(row1[1:], dtype=float)
        vec1_norm = np.linalg.norm(vec1)
        
        for j, row2 in enumerate(data):
            if i != j:
                vec2 = np.array(row2[1:], dtype=float)
                vec2_norm = np.linalg.norm(vec2)
                # Compute cosine similarity
                if vec1_norm and vec2_norm:  # Avoid division by zero
                    cos_sim = np.dot(vec1, vec2) / (vec1_norm * vec2_norm)
                else:
                    cos_sim = 0
                similarities.append((row2[0], cos_sim))
        
        # Sort by similarity score (higher is better)
        similarities.sort(key=lambda x: x[1], reverse=True)
        similarity.append([row1[0]] + [sim[0] for sim in similarities])
    
    return similarity

# Function to save processed data to a CSV file
def save_processed_data(data, filename):
    """Save processed data to a CSV file in core/genR"""
    output_dir = os.path.join(os.path.dirname(__file__), "genR")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    output_csv_path = os.path.join(output_dir, filename)
    with open(output_csv_path, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# Function to select CSV file
def select_csv():
    file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        csv_entry.config(state='normal')
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)
        csv_entry.config(state='readonly')
        process_file()

# Function to process the selected CSV file
def process_file():
    csv_file = csv_entry.get()
    if csv_file:
        purge_genR_folder()
        progress_bar.start()
        root.update_idletasks()
        data = process_csv(csv_file)
        distances = calculate_distances(data)
        save_processed_data(distances, "processed_distances.csv")
        similarity = calculate_similarity(distances)
        save_processed_data(similarity, "similarity_list.csv")
        progress_bar.stop()
        messagebox.showinfo("Success", "Data processing completed. Check the results below.")

# Function to create the UI
def create_ui():
    global root, csv_entry, progress_bar

    root = tk.Tk()
    root.title("Data Processing Tool")
    root.geometry("600x400")
    root.configure(bg='#1e1e1e')

    style = ttk.Style()
    style.configure('TButton', font=('Consolas', 12), padding=10, background='#007acc', foreground='#ffffff')
    style.configure('TLabel', font=('Consolas', 14), background='#1e1e1e', foreground='#d4d4d4')
    style.configure('TEntry', font=('Consolas', 12), padding=10, background='#252526', foreground='#d4d4d4')
    style.configure('TProgressbar', thickness=20)

    tk.Label(root, text="Select CSV File and Process:", bg='#1e1e1e', fg='#d4d4d4').pack(pady=10)
    ttk.Button(root, text="Bowser", command=select_csv).pack(pady=10)

    csv_entry = ttk.Entry(root, width=50, state='readonly')
    csv_entry.pack(pady=10)

    progress_bar = ttk.Progressbar(root, orient='horizontal', mode='determinate', length=400)
    progress_bar.pack(pady=10)

    root.mainloop()

if __name__ == "__main__":
    install_dependencies()
    create_ui()
