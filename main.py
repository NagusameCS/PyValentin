"""
Copyright (c) 2025
This program is part of PyValentin
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.
"""

import tkinter as tk
import sys
from tkinter import filedialog, ttk
import os
import shutil
import subprocess
from FixCSV import replace_values_in_csv
from Ski import process_csv, calculate_distances, calculate_similarity, save_processed_data
import json
from tkinter.scrolledtext import ScrolledText
import sys
from PyValentin import SplashScreen
import time

# Detect if running as bundled application
IS_BUNDLED = getattr(sys, 'frozen', False)

# Only import tkinterdnd2 if not bundled
if not IS_BUNDLED:
    from tkinterdnd2 import DND_FILES, TkinterDnD

def install_dependencies():
    required_packages = ["tkinterdnd2", "numpy"]
    for package in required_packages:
        try:
            __import__(package)
        except ImportError:
            subprocess.check_call([sys.executable, "-m", "pip", "install", package]) #Honestly not 100% sure if this work 

def purge_genR_folder():
    output_dir = os.path.join(os.path.dirname(__file__), "genR")
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def check_inputs():
    """Check if all required files are selected"""
    files_selected = all(entry.get().strip() for entry in [csv_entry, config_entry, filter_entry])
    files_exist = all(os.path.exists(entry.get()) for entry in [csv_entry, config_entry, filter_entry] if entry.get())
    
    if files_selected and files_exist:
        status_label.config(text="Ready to process", foreground='#00ff00')
        process_button['state'] = 'normal'
    else:
        status_label.config(text="Please select all required files", foreground='#ff9900')
        process_button['state'] = 'disabled'

def select_csv(event=None):
    if event:
        file_path = event.data.strip('{}')
    else:
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        csv_entry.delete(0, tk.END)
        csv_entry.insert(0, file_path)
        status_label.config(text="CSV file selected", foreground='#d4d4d4')
    check_inputs()

def select_config(event=None):
    if event:
        file_path = event.data.strip('{}')
    else:
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        config_entry.delete(0, tk.END)
        config_entry.insert(0, file_path)
        status_label.config(text="Config file selected", foreground='#d4d4d4')
    check_inputs()

def select_filter(event=None):
    if event:
        file_path = event.data.strip('{}')
    else:
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
    if file_path:
        filter_entry.delete(0, tk.END)
        filter_entry.insert(0, file_path)
        status_label.config(text="Filter file selected", foreground='#d4d4d4')
    check_inputs()

def filter_similarity_list(similarity_file, csv_file, filter_file):
    print("Starting filter_similarity_list function")
    print(f"Reading similarity file: {similarity_file}")
    with open(similarity_file, 'r') as sim_file:
        similarity_data = [line.strip().split(',') for line in sim_file]

    print(f"Reading CSV file: {csv_file}")
    with open(csv_file, 'r') as csv_file:
        csv_data = [line.strip().split(',') for line in csv_file]
    print("CSV Data: " + str(csv_data))  # Debugging statement to verify CSV data

    print(f"Reading filter file: {filter_file}")
    with open(filter_file, 'r') as f_file:
        filters = json.load(f_file)

    filterables = filters["filterables"]
    filters = filters["filters"]

    # Create a mapping from email to row index
    email_to_row = {row[1]: row for row in csv_data}

    filtered_similarity = []
    no_matches_users = []

    for entry in similarity_data:
        original_email = entry[0]
        original_row = email_to_row.get(original_email)
        if not original_row:
            print(f"Email {original_email} not found in CSV data")
            continue

        original_filter_value = str(original_row[2]).strip()  # Use index 2 for 'a'
        original_allowed_filterables = filters.get(original_filter_value, [])
        print(f"Processing {original_email} with filter value {original_filter_value} and allowed filterables {original_allowed_filterables}")

        filtered_entry = [original_email]
        for email in entry[1:]:
            row = email_to_row.get(email)
            if not row:
                print(f"Email {email} not found in CSV data")
                continue

            candidate_filter_value = str(row[3]).strip()  # Use index 3 for 'b'
            candidate_allowed_filterables = filters.get(candidate_filter_value, [])

            print(f"Checking match: {original_email} ({original_filter_value}) - {email} ({candidate_filter_value})")
            print(f"Filter {original_filter_value} allows: {original_allowed_filterables}")
            print(f"Filter {candidate_filter_value} allows: {candidate_allowed_filterables}")
            print(f"Match condition: {'8' in (original_filter_value, candidate_filter_value)} or ({original_filter_value in candidate_allowed_filterables} and {candidate_filter_value in original_allowed_filterables}) or ({original_filter_value == '3' and candidate_filter_value == '8'}) or ({original_filter_value == '8' and candidate_filter_value == '3'})")
            if "8" in (original_filter_value, candidate_filter_value) or (
                original_filter_value in candidate_allowed_filterables and candidate_filter_value in original_allowed_filterables
            ) or (original_filter_value == "3" and candidate_filter_value == "8") or (original_filter_value == "8" and candidate_filter_value == "3"):
                print(f"Match found: {original_email} ({original_filter_value}) y {email} ({candidate_filter_value})")
                filtered_entry.append(email)
            else:
                print(f"No match: {original_email} ({original_filter_value}) x {email} ({candidate_filter_value})")

        if len(filtered_entry) == 1:
            print(f"No matches found for {original_email}")
            filtered_entry.append("No matches found")
            no_matches_users.append(original_email)

        filtered_similarity.append(filtered_entry)

    # Analyze users with no matches
    print("Analyzing users with no matches found:")
    for email in no_matches_users:
        row = email_to_row.get(email)
        if row:
            print(f"User: {email}, Gender: {row[2]}, Attracted to: {row[3]}")

    output_file = os.path.join(os.path.dirname(__file__), "genR", "filtered_similarity_list.csv")
    print(f"Saving filtered similarity list to: {output_file}")
    with open(output_file, 'w') as out_file:
        for entry in filtered_similarity:
            out_file.write(','.join(entry) + '\n')
    print("Filtered similarity list saved successfully")

    # New step to handle edge cases
    handle_edge_cases(no_matches_users, csv_data, filters, email_to_row, output_file)

def handle_edge_cases(no_matches_users, csv_data, filters, email_to_row, filtered_similarity_file):
    print("Handling edge cases")
    edge_cases = []

    # First entry: users with no matches found
    edge_cases.append(no_matches_users)

    # Second entry: users with filters that should encapsulate those in the first entry
    encapsulating_users = []
    for row in csv_data:
        email = row[1]
        # Check specifically in the attraction field (index 3) for "8"
        has_eight = str(row[3]).strip() == "8"
        filter_value = str(row[2]).strip()  # Gender value
        if has_eight or (filter_value == "8") or (filter_value in filters and any(
            str(email_to_row[no_match_user][2]).strip() in filters[filter_value] 
            for no_match_user in no_matches_users 
            if no_match_user in email_to_row
        )):
            encapsulating_users.append(email)
    edge_cases.append(encapsulating_users)

    # Following entries: determine matches
    for no_match_email in no_matches_users:
        no_match_row = email_to_row.get(no_match_email)
        no_match_filter_value = str(no_match_row[2]).strip()  # Gender value
        matches = [no_match_email]
        for email in encapsulating_users:
            row = email_to_row.get(email)
            candidate_filter_value = str(row[3]).strip()  # Attraction value
            # Match if either has "8" or they match each other's preferences
            if "8" in (no_match_filter_value, candidate_filter_value) or (
                candidate_filter_value in filters.get(no_match_filter_value, []) and
                str(no_match_row[3]).strip() in filters.get(str(row[2]).strip(), [])
            ):
                matches.append(email)
        edge_cases.append(matches)

    # Commenting out the edge cases CSV saving part
    # Save edge cases to CSV
    # edge_cases_file = os.path.join(os.path.dirname(__file__), "genR", "edge_cases.csv")
    # print(f"Saving edge cases to: {edge_cases_file}")
    # with open(edge_cases_file, 'w') as out_file:
    #     for entry in edge_cases:
    #         out_file.write(','.join(entry) + '\n')
    # print("Edge cases saved successfully")

    # Update original filtered similarity list with new indices
    update_filtered_similarity_list(filtered_similarity_file, edge_cases)

def update_filtered_similarity_list(filtered_similarity_file, edge_cases):
    print("Updating filtered similarity list with edge cases")
    with open(filtered_similarity_file, 'r') as in_file:
        filtered_similarity = [line.strip().split(',') for line in in_file]

    for matches in edge_cases[2:]:
        original_email = matches[0]
        for entry in filtered_similarity:
            if entry[0] == original_email:
                entry.extend(matches[1:])

    with open(filtered_similarity_file, 'w') as out_file:
        for entry in filtered_similarity:
            out_file.write(','.join(entry) + '\n')
    print("Filtered similarity list updated successfully")

def create_optimal_pairs(filtered_similarity_file, quality_weight=0.5):
    print(f"Creating optimal pairs with quality weight: {quality_weight}")
    pairs = []
    unpaired = []
    used_emails = set()

    with open(filtered_similarity_file, 'r') as f:
        similarity_data = [line.strip().split(',') for line in f]
    
    # Sort entries by number of potential matches (more matches = more flexibility)
    similarity_data.sort(key=lambda x: len(x[1:]) if x[1] != "No matches found" else 0, 
                        reverse=True if quality_weight < 0.5 else False)
    
    # First pass - match pairs based on quality weight
    for entry in similarity_data:
        email = entry[0]
        if email in used_emails:
            continue
        
        if len(entry) <= 2 and entry[1] == "No matches found":
            unpaired.append(email)
            continue

        available_matches = [e for e in entry[1:] if e not in used_emails]
        
        if available_matches:
            if quality_weight > 0.5:
                # Prioritize best matches
                best_match = available_matches[0]
            else:
                # Consider later matches to increase total pairs
                match_index = int((len(available_matches) - 1) * (1 - quality_weight) * 2)
                best_match = available_matches[min(match_index, len(available_matches) - 1)]
            
            pairs.append([email, best_match])
            used_emails.add(email)
            used_emails.add(best_match)
        else:
            unpaired.append(email)

    # Second pass with remaining singles
    if unpaired and quality_weight < 0.8:  # Skip second pass if high quality priority
        print(f"Second pass optimization for {len(unpaired)} unpaired entries...")
        retry_unpaired = unpaired.copy()
        unpaired = []
        
        available_matches_map = {}
        for email in retry_unpaired:
            for entry in similarity_data:
                if entry[0] == email:
                    available_matches_map[email] = [e for e in entry[1:] if e != "No matches found"]
                    break

        while retry_unpaired:
            current_email = retry_unpaired.pop(0)
            potential_matches = available_matches_map.get(current_email, [])
            
            best_match = None
            for match in potential_matches:
                if match in retry_unpaired:
                    match_potentials = available_matches_map.get(match, [])
                    if current_email in match_potentials:
                        best_match = match
                        break
            
            if best_match:
                pairs.append([current_email, best_match])
                retry_unpaired.remove(best_match)
                used_emails.add(current_email)
                used_emails.add(best_match)
            else:
                unpaired.append(current_email)

    # Save results
    output_file = os.path.join(os.path.dirname(__file__), "genR", "optimal_pairs.csv")
    with open(output_file, 'w') as f:
        for pair in pairs:
            f.write(f"{pair[0]},{pair[1]}\n")
    print(f"Saved {len(pairs)} optimal pairs")

    if unpaired:
        unpaired_file = os.path.join(os.path.dirname(__file__), "genR", "unpaired_entries.csv")
        with open(unpaired_file, 'w') as f:
            for email in unpaired:
                f.write(f"{email}\n")
        print(f"Saved {len(unpaired)} unpaired entries after optimization")

def process_files():
    csv_file = csv_entry.get()
    config_file = config_entry.get()
    filter_file = filter_entry.get()
    
    if csv_file and config_file and filter_file:
        progress['value'] = 0
        root.update()
        
        try:
            # Stage 1: Initial setup and CSV processing (20%)
            status_label.config(text="Stage 1/5: Initializing and processing CSV...", foreground='#d4d4d4')
            purge_genR_folder()
            output_file = os.path.join(os.path.dirname(__file__), "genR", "modified_csv.csv")
            replace_values_in_csv(csv_file, config_file, output_file)
            progress['value'] = 20
            root.update()
            
            # Stage 2: Data processing and distance calculation (40%)
            status_label.config(text="Stage 2/5: Calculating distances...", foreground='#d4d4d4')
            data = process_csv(output_file)
            distances = calculate_distances(data)
            save_processed_data(distances, os.path.join(os.path.dirname(__file__), "genR", "processed_distances.csv"))
            progress['value'] = 40
            root.update()
            
            # Stage 3: Similarity calculation (60%)
            status_label.config(text="Stage 3/5: Computing similarities...", foreground='#d4d4d4')
            similarity = calculate_similarity(distances)
            save_processed_data(similarity, os.path.join(os.path.dirname(__file__), "genR", "similarity_list.csv"))
            progress['value'] = 60
            root.update()
            
            # Stage 4: Filter similarity list (80%)
            status_label.config(text="Stage 4/5: Filtering matches...", foreground='#d4d4d4')
            filter_similarity_list(
                os.path.join(os.path.dirname(__file__), "genR", "similarity_list.csv"),
                output_file,
                filter_file
            )
            progress['value'] = 80
            root.update()
            
            # Stage 5: Create optimal pairs (100%)
            status_label.config(text="Stage 5/5: Creating optimal pairs...", foreground='#d4d4d4')
            quality_weight = quality_slider.get()
            filtered_similarity_file = os.path.join(os.path.dirname(__file__), "genR", "filtered_similarity_list.csv")
            create_optimal_pairs(filtered_similarity_file, quality_weight)
            progress['value'] = 100
            root.update()
            
            # Show completion message with success color
            status_label.config(text="Processing completed successfully! Check the genR Folder for all the Data", foreground='#00ff00')
            
        except Exception as e:
            # Show error message with error color
            status_label.config(text=f"Error: {str(e)}", foreground='#ff0000')
            progress['value'] = 0

def create_ui():
    global csv_entry, config_entry, filter_entry, quality_slider, progress, status_label, root, process_button

    # Create appropriate root window based on whether we're bundled
    if IS_BUNDLED:
        root = tk.Tk()
    else:
        root = TkinterDnD.Tk()

    root.title("PyValentin")
    root.geometry("600x550")  # Reduced height since we removed console
    root.configure(bg='#1e1e1e')

    style = ttk.Style()
    
    # Configure styles with proper background and highlight colors
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

    # Create and configure main frame
    main_frame = tk.Frame(root, bg='#1e1e1e', highlightthickness=0)
    main_frame.pack(pady=20, padx=20, fill='both', expand=True)

    # File input sections with browse buttons
    for label_text, entry_var, command in [
        ("CSV File", "csv_entry", select_csv),
        ("Config File", "config_entry", select_config),
        ("Filter File", "filter_entry", select_filter)
    ]:
        frame = tk.Frame(main_frame, bg='#1e1e1e', highlightthickness=0)
        frame.pack(fill='x', pady=10)
        
        ttk.Label(frame, text=label_text).pack(anchor='w')
        
        entry_frame = tk.Frame(frame, bg='#1e1e1e')
        entry_frame.pack(fill='x', pady=(5,0))
        
        entry = ttk.Entry(entry_frame, width=40)
        entry.pack(side='left', fill='x', expand=True)
        globals()[entry_var] = entry
        
        browse_btn = ttk.Button(entry_frame, text="Browse", command=command)
        browse_btn.pack(side='right', padx=(5,0))

    # Quality slider section with improved visuals
    slider_frame = tk.Frame(main_frame, bg='#1e1e1e', highlightthickness=0)
    slider_frame.pack(fill='x', pady=20)
    
    ttk.Label(slider_frame, text="Quality vs Quantity Balance").pack(anchor='w')
    
    quality_slider = ttk.Scale(slider_frame, from_=0.0, to=1.0, orient='horizontal')
    quality_slider.set(0.5)
    quality_slider.pack(fill='x', pady=(5,0))
    
    label_frame = tk.Frame(slider_frame, bg='#1e1e1e', highlightthickness=0)
    label_frame.pack(fill='x', pady=(5,0))
    
    ttk.Label(label_frame, text="Quantity Priority", style='Small.TLabel').pack(side='left')
    ttk.Label(label_frame, text="Quality Priority", style='Small.TLabel').pack(side='right')

    # Add progress bar
    progress_frame = tk.Frame(main_frame, bg='#1e1e1e', highlightthickness=0)
    progress_frame.pack(fill='x', pady=20)
    
    progress = ttk.Progressbar(
        progress_frame,
        orient='horizontal',
        length=300,
        mode='determinate'
    )
    progress.pack(fill='x', pady=(5,0))

    # Add status label
    status_label = ttk.Label(
        progress_frame,
        text="Please select all required files",
        background='#1e1e1e',
        foreground='#ff9900',
        anchor='center'
    )
    status_label.pack(fill='x', pady=(5,0))

    # Add process button (disabled by default)
    process_button = ttk.Button(main_frame, text="Process Files", command=process_files, state='disabled')
    process_button.pack(pady=20)

    # Bind events
    root.bind('<Control-v>', select_csv)
    root.bind('<Control-c>', select_config)
    root.bind('<Control-f>', select_filter)

    # Only setup drag and drop if not bundled
    if not IS_BUNDLED:
        for entry in [csv_entry, config_entry, filter_entry]:
            entry.drop_target_register(DND_FILES)
            entry.dnd_bind('<<Drop>>', lambda e, entry=entry: drop(e, entry))

    root.mainloop()

def drop(event, widget):
    if event.data:
        widget.delete(0, tk.END)
        widget.insert(0, event.data.strip('{}'))
        check_inputs()  # Add check after drop

def main():
    # Create root window but don't show it yet
    if IS_BUNDLED:
        root = tk.Tk()
    else:
        root = TkinterDnD.Tk()
    root.withdraw()  # Hide the root window
    
    # Create and show splash screen
    splash = SplashScreen(root)
    start_time = time.time()
    
    # Simulate loading steps
    steps = [
        "Checking dependencies...",
        "Initializing interface...",
        "Loading components...",
        "Starting PyValentin..."
    ]
    
    for i, step in enumerate(steps):
        splash.loading_label.config(text=step)
        splash.update_progress((i + 1) * 25)
        time.sleep(0.5)
    
    # Ensure splash screen stays visible for at least 3 seconds
    elapsed_time = time.time() - start_time
    if elapsed_time < 3:
        time.sleep(3 - elapsed_time)
    
    # Close splash and show main application
    splash.finish()
    create_ui()

if __name__ == "__main__":
    install_dependencies()
    main()
