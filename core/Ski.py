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
    """Calculate distances between all possible overlapping pairs of responses"""
    distances = []
    for row in data:
        email = row[0]
        # Convert all numeric values, excluding email
        values = [float(x) for x in row[1:]]
        coordinates = []
        
        # Create ALL possible overlapping pairs
        for i in range(len(values)):
            for j in range(i + 1, len(values)):
                coordinates.append((values[i], values[j]))
        
        # Calculate midpoint of all coordinates
        midpoint = calculate_midpoint(coordinates)
        
        # Calculate distances from midpoint to each coordinate pair
        row_distances = [calculate_distance(midpoint, point) for point in coordinates]
        distances.append([email] + row_distances)
        
        # Debug print
        print(f"Email: {email}")
        print(f"Number of pairs: {len(coordinates)}")
        print(f"Coordinates: {coordinates[:5]}...")  # Print first 5 pairs
        print(f"Number of distances: {len(row_distances)}\n")
    
    return distances

# Function to calculate the midpoint of a set of points
def calculate_midpoint(points):
    """Calculate the midpoint of a set of points"""
    if not points:
        return (0, 0)
    x_coords = [p[0] for p in points]
    y_coords = [p[1] for p in points]
    return (sum(x_coords) / len(points), sum(y_coords) / len(points))

# Function to calculate the distance between two points
def calculate_distance(point1, point2):
    return np.sqrt((point1[0] - point2[0]) ** 2 + (point1[1] - point2[1]) ** 2)

# Function to compare each row with every other row to determine a "list of similarity"
def calculate_similarity(data):
    """Calculate normalized similarity scores between users"""
    similarity = []
    print(f"\nProcessing similarity for {len(data)} entries")
    
    for i, row1 in enumerate(data):
        email1 = row1[0]
        values1 = [float(x) for x in row1[1:]]
        
        print(f"\nProcessing {email1}")
        print(f"Number of values: {len(values1)}")
        
        # Calculate similarities with all other users
        similarities = []
        for j, row2 in enumerate(data):
            if i != j:
                email2 = row2[0]
                values2 = [float(x) for x in row2[1:]]
                
                # Calculate normalized Euclidean distance
                squared_diff_sum = 0
                for v1, v2 in zip(values1, values2):
                    squared_diff_sum += (v1 - v2) ** 2
                euclidean_dist = np.sqrt(squared_diff_sum)
                
                # Convert distance to similarity score (inverse relationship)
                # Using exponential decay for better scaling
                similarity_score = np.exp(-euclidean_dist)
                
                similarities.append((email2, similarity_score))
        
        # Normalize similarity scores to 0-1 range
        if similarities:
            max_score = max(s[1] for s in similarities)
            min_score = min(s[1] for s in similarities)
            score_range = max_score - min_score if max_score != min_score else 1
            
            normalized_similarities = [
                (email, (score - min_score) / score_range)
                for email, score in similarities
            ]
            
            # Sort by normalized similarity score (higher is better)
            sorted_similarities = sorted(normalized_similarities, 
                                      key=lambda x: x[1], 
                                      reverse=True)
            
            # Create list of sorted emails
            sorted_emails = [sim[0] for sim in sorted_similarities]
        else:
            sorted_emails = ["No matches found"]
            
        # Debug info
        print(f"Top 3 matches for {email1}:")
        for idx, email in enumerate(sorted_emails[:3], 1):
            print(f"{idx}. {email}")
        
        # Add original email followed by sorted similar emails
        similarity.append([email1] + sorted_emails)
    
    return similarity

# Function to save processed data to a CSV file
def save_processed_data(data, filename):
    """Save processed data with verification"""
    output_dir = os.path.join(os.path.dirname(__file__), "genR")
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
    
    output_path = os.path.join(output_dir, os.path.basename(filename))
    
    try:
        with open(output_path, mode='w', newline='') as file:
            writer = csv.writer(file)
            writer.writerows(data)
        
        # Verify the save
        with open(output_path, 'r') as file:
            saved_data = list(csv.reader(file))
            print(f"\nSaved {len(saved_data)} rows to {output_path}")
            print(f"First row length: {len(saved_data[0])} elements")
    except Exception as e:
        print(f"Error saving/verifying data: {str(e)}")

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
