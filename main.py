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
import csv  # Add CSV import
from core.FixCSV import replace_values_in_csv
from core.Ski import process_csv, calculate_distances, calculate_similarity, save_processed_data
import json
from tkinter.scrolledtext import ScrolledText
import sys
from core.PyValentin import SplashScreen
import time
from ui.components import create_file_input, create_quality_slider, create_action_buttons
from core.matching import MatchMaker
from utils.file_handlers import validate_csv_data, process_files
from utils.config import setup_styles, IS_BUNDLED

import numpy as np
from scipy.optimize import linear_sum_assignment
from typing import Dict, Tuple
import platform

# Add this import at the top with other imports
from core.genR.sgluttony.sgluttony_constants import ( # type: ignore
    MAX_GRADE_DIFFERENCE,
    GRADE_PENALTY_FACTOR,
    MIN_MATCH_QUALITY
)

# Detect if running as bundled application
IS_BUNDLED = getattr(sys, 'frozen', False)

# Only import tkinterdnd2 if not IS_BUNDLED
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
    """Purge and recreate the genR folder in core directory"""
    output_dir = os.path.join(os.path.dirname(__file__), "core", "genR")
    if (os.path.exists(output_dir)):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def check_inputs():
    """Check if all required files are selected"""
    files_selected = all(entry.get().strip() for entry in [csv_entry, config_entry, filter_entry, grade_entry])
    files_exist = all(os.path.exists(entry.get()) for entry in [csv_entry, config_entry, filter_entry, grade_entry] if entry.get())
    
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

def select_grade_csv(event=None):
    """Handler for grade CSV file selection"""
    if event:
        file_path = event.data.strip('{}')
    else:
        file_path = filedialog.askopenfilename(filetypes=[("CSV files", "*.csv")])
    if file_path:
        grade_entry.delete(0, tk.END)
        grade_entry.insert(0, file_path)
        status_label.config(text="Grade CSV file selected", foreground='#d4d4d4')
    check_inputs()

def check_gender_preference_match(person1_data, person2_data):
    """Check if two people are compatible based on gender preferences"""
    def preference_accepts_gender(preference, gender):
        # Split preference string if it contains multiple preferences
        preferences = [p.strip() for p in str(preference).split(',')]
        return any([
            p == "5" or  # Accepts both genders
            p == "No Preference" or 
            p == gender
            for p in preferences
        ])
    
    # Check compatibility in both directions
    person1_accepts_person2 = preference_accepts_gender(person1_data["wants"], person2_data["gender"])
    person2_accepts_person1 = preference_accepts_gender(person2_data["wants"], person1_data["gender"])
    
    print(f"Checking compatibility:")
    print(f"  Person1: {person1_data['gender']} wants {person1_data['wants']}")
    print(f"  Person2: {person2_data['gender']} wants {person2_data['wants']}")
    print(f"  Match: {person1_accepts_person2 and person2_accepts_person1}")
    
    return person1_accepts_person2 and person2_accepts_person1

def filter_similarity_list(similarity_file, csv_file, filter_file):
    """Filter matches based on strict gender preferences"""
    print("Starting strict gender/preference filtering")
    
    # Read data files
    with open(similarity_file, 'r') as f:
        similarity_data = [line.strip().split(',') for line in f]
    
    with open(csv_file, 'r') as f:
        reader = csv.reader(f)
        headers = next(reader)
        csv_data = list(reader)
    
    # Create email to data mapping
    email_to_data = {}
    for row in csv_data:
        if len(row) >= 4:
            email = row[1].strip()
            gender = row[2].strip()
            preference = row[3].strip()
            email_to_data[email] = {
                "gender": gender,
                "preference": preference
            }
    
    filtered_similarity = []
    no_matches_users = []
    
    for entry in similarity_data:
        original_email = entry[0]
        original_data = email_to_data.get(original_email)
        if not original_data:
            continue
            
        filtered_entry = [original_email]
        valid_matches = []
        
        for potential_match in entry[1:]:
            if potential_match == "No matches found":
                continue
                
            match_data = email_to_data.get(potential_match)
            if not match_data:
                continue
            
            if check_gender_preference_match(original_data, match_data):
                valid_matches.append(potential_match)
        
        if valid_matches:
            filtered_entry.extend(valid_matches)
        else:
            filtered_entry.append("No matches found")
            no_matches_users.append(original_email)
            
        filtered_similarity.append(filtered_entry)
    
    output_file = os.path.join(os.path.dirname(__file__), "core", "genR", "filtered_similarity_list.csv")
    with open(output_file, 'w') as f:
        for entry in filtered_similarity:
            f.write(','.join(entry) + '\n')
            
    return filtered_similarity, no_matches_users

def handle_edge_cases(no_matches_users, csv_data, filters, email_to_row, filtered_similarity_file):
    print("Handling edge cases")
    edge_cases = []

    edge_cases.append(no_matches_users)

    encapsulating_users = []
    for row in csv_data:
        email = row[1]
        has_eight = str(row[3]).strip() == "8"
        filter_value = str(row[2]).strip()
        if has_eight or (filter_value == "8") or (filter_value in filters and any(
            str(email_to_row[no_match_user][2]).strip() in filters[filter_value] 
            for no_match_user in no_matches_users 
            if no_match_user in email_to_row
        )):
            encapsulating_users.append(email)
    edge_cases.append(encapsulating_users)

    for no_match_email in no_matches_users:
        no_match_row = email_to_row.get(no_match_email)
        no_match_filter_value = str(no_match_row[2]).strip()
        matches = [no_match_email]
        for email in encapsulating_users:
            row = email_to_row.get(email)
            candidate_filter_value = str(row[3]).strip()
            if "8" in (no_match_filter_value, candidate_filter_value) or (
                candidate_filter_value in filters.get(no_match_filter_value, []) and
                str(no_match_row[3]).strip() in filters.get(str(row[2]).strip(), [])
            ):
                matches.append(email)
        edge_cases.append(matches)

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

def validate_csv_data(csv_file):
    """Validate CSV file format and required columns"""
    required_columns = ["Email Address", "What is your gender?", "What gender are you attracted to?"]
    try:
        with open(csv_file, 'r') as f:
            header = f.readline().strip().split(',')
            if not all(col in header for col in required_columns):
                raise ValueError("CSV missing required columns")
            for line in f:
                if len(line.strip().split(',')) != len(header):
                    raise ValueError("Malformed CSV row detected")
        return True
    except Exception as e:
        print(f"CSV validation error: {str(e)}")
        return False

def prefilter_by_preferences(similarity_data, csv_file):
    """Remove incompatible matches using more lenient preference filtering"""
    print("\n=== Starting Preference Filtering ===")
    
    gender_prefs = load_gender_preferences(csv_file)
    print(f"Loaded {len(gender_prefs)} participant preferences")
    
    filtered_data = []
    
    for entry in similarity_data:
        person_email = entry[0]
        person_data = gender_prefs.get(person_email)
        if not person_data:
            continue
            
        filtered_entry = [person_email]
        matches = []
        
        for match_email in entry[1:]:
            if match_email == "No matches found":
                continue
                
            match_data = gender_prefs.get(match_email)
            if not match_data:
                continue
            
            # More lenient compatibility check
            compatible = check_compatibility(person_data, match_data)
            
            if compatible:
                matches.append(match_email)
        
        if matches:
            filtered_entry.extend(matches)
        else:
            filtered_entry.append("No matches found")
            
        filtered_data.append(filtered_entry)
    
    return filtered_data

def check_compatibility(person1, person2):
    """Check if two people are compatible using more lenient rules"""
    # Handle multiple preferences
    def parse_preferences(pref):
        if isinstance(pref, str):
            prefs = [p.strip() for p in pref.split(',')]
            return [p for p in prefs if p]
        return [str(pref)]
    
    person1_wants = parse_preferences(person1["wants"])
    person2_gender = person2["gender"]
    
    # More lenient compatibility rules
    compatible = (
        "No Preference" in person1_wants or
        "5" in person1_wants or  # Accepts both genders
        person2_gender in person1_wants or
        any(p.lower() == person2_gender.lower() for p in person1_wants)
    )
    
    return compatible

def load_gender_preferences(csv_file):
    """Load gender and preference data from CSV"""
    gender_prefs = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        email_idx = headers.index("Email Address")
        gender_idx = headers.index("What is your gender?")
        pref_idx = headers.index("What gender are you attracted to?")
        
        for row in reader:
            if len(row) > max(email_idx, gender_idx, pref_idx):
                email = row[email_idx].strip()
                gender = row[gender_idx].strip()
                # Handle multiple preferences
                preference = row[pref_idx].strip()
                gender_prefs[email] = {
                    "gender": gender,
                    "wants": preference  # Keep full preference string
                }
    return gender_prefs

def create_pairs(similarity_data, quality_weight=0.5):
    """Create pairs from similarity data with preference validation"""
    print("\nStarting pairing process...")
    
    email_matches = {}
    for entry in similarity_data:
        email = entry[0]
        matches = [m for m in entry[1:] if m != "No matches found"]
        if matches:
            email_matches[email] = matches
            print(f"  {email} has {len(matches)} potential matches")
    
    pairs = []
    used_emails = set()
    
    participants = sorted(
        [(email, matches) for email, matches in email_matches.items()],
        key=lambda x: len(x[1])
    )
    
    print(f"\nProcessing {len(participants)} participants...")
    
    for email, potential_matches in participants:
        if email in used_emails:
            continue
            
        print(f"\nProcessing {email}")
        print(f"  Has {len(potential_matches)} potential matches")
        
        best_match = None
        best_score = -1
        
        for match in potential_matches:
            if match in used_emails:
                continue
                
            if match in email_matches and email in email_matches[match]:
                match_score = 1.0 - (potential_matches.index(match) / len(potential_matches))
                reverse_score = 1.0 - (email_matches[match].index(email) / len(email_matches[match]))
                
                score = (match_score + reverse_score) / 2
                print(f"    Checking {match} - mutual match with score {score:.2f}")
                
                if score > best_score:
                    best_score = score
                    best_match = match
            else:
                print(f"    Skipping {match} - not a mutual match")
                
        if best_match:
            print(f"  ✓ Matched with {best_match} (score: {best_score:.2f})")
            pairs.append([email, best_match, best_score])
            used_emails.add(email)
            used_emails.add(best_match)
        else:
            print(f"  ✗ No valid match found")
    
    print(f"\nCreated {len(pairs)} valid pairs")
    return pairs

def create_cost_matrix(similarity_data):
    """Create a cost matrix for the Hungarian algorithm"""
    emails = list(set(entry[0] for entry in similarity_data))
    n = len(emails)
    email_to_idx = {email: i for i, email in enumerate(emails)}
    
    # Initialize with high cost (low similarity)
    cost_matrix = np.full((n, n), 1000.0)
    
    for entry in similarity_data:
        email = entry[0]
        matches = [m for m in entry[1:] if m != "No matches found"]
        i = email_to_idx[email]
        
        for idx, match in enumerate(matches):
            if match in email_to_idx:
                j = email_to_idx[match]
                # Convert similarity to cost (higher similarity = lower cost)
                cost = 1.0 - (1.0 - idx/len(matches))
                cost_matrix[i][j] = cost
    
    return cost_matrix, emails

def create_hungarian_pairs(similarity_data, quality_weight=0.5):
    """Create optimal pairs using modified Hungarian algorithm"""
    print("\nStarting Hungarian matching process...")
    
    # Create a set of all unique emails
    all_emails = set()
    for entry in similarity_data:
        all_emails.add(entry[0])
        all_emails.update(m for m in entry[1:] if m != "No matches found")
    
    emails = sorted(list(all_emails))
    n = len(emails)
    email_to_idx = {email: i for i, email in enumerate(emails)}
    
    # Initialize cost matrix with high costs
    cost_matrix = np.full((n, n), 1000.0)
    
    # Fill in costs based on compatibility
    for entry in similarity_data:
        email1 = entry[0]
        matches = [m for m in entry[1:] if m != "No matches found"]
        i = email_to_idx[email1]
        
        for idx, email2 in enumerate(matches):
            j = email_to_idx[email2]
            # Convert position to cost (earlier positions = lower cost)
            cost = idx / max(len(matches), 1)  # Avoid division by zero
            cost_matrix[i][j] = cost
    
    # Make matrix symmetric
    cost_matrix = np.minimum(cost_matrix, cost_matrix.T)
    
    # Run Hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    # Create pairs
    pairs = []
    used_emails = set()
    
    for i, j in zip(row_ind, col_ind):
        email1, email2 = emails[i], emails[j]
        if (email1 not in used_emails and 
            email2 not in used_emails and 
            cost_matrix[i][j] < 999.0):
            
            quality = 1.0 - cost_matrix[i][j]
            pairs.append([email1, email2, quality])
            used_emails.add(email1)
            used_emails.add(email2)
    
    print(f"Created {len(pairs)} pairs")
    return pairs

RECOMMENDED_GRADE_WEIGHT = 0.7
GRADE_PENALTIES = {
    0: 0.0,    # Same grade
    1: 0.3,    # One grade difference
    2: 0.7,    # Two grades difference
    3: 0.9,    # Three+ grades difference
}

def create_grade_slider(parent):
    """Create slider for grade weight"""
    frame = tk.Frame(parent, bg='#1e1e1e')
    frame.pack(fill='x', pady=5)
    
    label = ttk.Label(frame, text="Grade Weight:", background='#1e1e1e', foreground='#d4d4d4')
    label.pack(side='left', padx=5)
    
    slider = ttk.Scale(frame, from_=0.0, to=1.0, orient='horizontal')
    slider.set(RECOMMENDED_GRADE_WEIGHT)
    slider.pack(side='right', fill='x', expand=True, padx=5)
    
    return slider

def load_grade_data(grade_csv: str) -> Dict[str, int]:
    """Load grade information from CSV"""
    grade_map = {}
    with open(grade_csv, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        next(reader)  # Skip header
        for row in reader:
            if len(row) >= 4:
                email = row[2].strip()
                grade = int(row[3].strip())
                grade_map[email] = grade
    return grade_map

def calculate_grade_penalty(grade1: int, grade2: int) -> float:
    """Calculate penalty for grade difference with stronger penalties"""
    diff = abs(grade1 - grade2)
    penalties = {
        0: 0.0,    # Same grade
        1: 0.3,    # One grade difference
        2: 0.7,    # Two grades difference
        3: 1.0     # Three+ grades difference
    }
    return penalties[min(diff, 3)]

def calculate_grade_difference(grade1: int, grade2: int) -> str:
    """Calculate and format the grade difference between two students"""
    if grade1 is None or grade2 is None:
        return "N/A"
    return str(abs(grade1 - grade2))

def create_grade_sensitive_pairs(similarity_data, grade_data: Dict[str, int], grade_weight: float = RECOMMENDED_GRADE_WEIGHT):
    """Create pairs considering both compatibility and grade"""
    print("\nStarting grade-sensitive Hungarian matching...")
    
    # Create initial sets
    emails = sorted(list(set(entry[0] for entry in similarity_data)))
    n = len(emails)
    email_to_idx = {email: i for i, email in enumerate(emails)}
    
    # Initialize cost matrix with maximum values
    cost_matrix = np.full((n, n), 999999.0)
    
    # Fill cost matrix with combined costs
    for entry in similarity_data:
        email1 = entry[0]
        matches = [m for m in entry[1:] if m != "No matches found"]
        i = email_to_idx[email1]
        
        for idx, email2 in enumerate(matches):
            if email2 not in email_to_idx:
                continue
                
            j = email_to_idx[email2]
            
            # Calculate base compatibility score (inverse of position)
            base_score = 1.0 - (idx / len(matches))
            
            # Calculate grade score
            grade_score = 1.0  # Default if no grade data
            if email1 in grade_data and email2 in grade_data:
                grade_diff = abs(grade_data[email1] - grade_data[email2])
                # Penalize based on grade difference
                if grade_diff == 0:
                    grade_score = 1.0
                elif grade_diff == 1:
                    grade_score = 0.8
                elif grade_diff == 2:
                    grade_score = 0.4
                else:
                    grade_score = 0.0  # Strong penalty for 3+ grade difference
            
            # Combine scores with weights
            combined_score = ((1 - grade_weight) * base_score + 
                            grade_weight * grade_score)
            
            # Convert score to cost (higher score = lower cost)
            cost = 1.0 - combined_score
            
            # Make cost matrix symmetric
            cost_matrix[i][j] = cost
            cost_matrix[j][i] = cost
    
    # Run Hungarian algorithm
    row_ind, col_ind = linear_sum_assignment(cost_matrix)
    
    # Create pairs
    pairs = []
    used_emails = set()
    
    for i, j in zip(row_ind, col_ind):
        email1, email2 = emails[i], emails[j]
        if (email1 not in used_emails and 
            email2 not in used_emails and 
            cost_matrix[i][j] < 999.0):
            
            # Calculate quality score (inverse of cost)
            quality = 1.0 - cost_matrix[i][j]
            
            # Skip pairs with very low quality
            if quality < 0.3:  # Minimum quality threshold
                continue
                
            grade1 = grade_data.get(email1)
            grade2 = grade_data.get(email2)
            grade_diff = calculate_grade_difference(grade1, grade2)
            
            # Skip pairs with too large grade difference
            if grade_diff.isdigit() and int(grade_diff) > 2:
                continue
                
            grade_info = f" (grades: {grade1}, {grade2})"
            
            pairs.append([email1, email2, quality, grade_info, grade_diff])
            used_emails.add(email1)
            used_emails.add(email2)
    
    # Sort pairs by quality
    pairs.sort(key=lambda x: float(x[2]), reverse=True)
    
    print(f"Created {len(pairs)} grade-sensitive pairs")
    return pairs

def create_optimal_pairs(filtered_similarity_file, csv_file, grade_csv, quality_weight=0.5, grade_weight=RECOMMENDED_GRADE_WEIGHT):
    """Create optimal pairs using both algorithms with grade consideration"""
    print("Creating optimal pairs using multiple algorithms...")
    
    # Create algorithm-specific output directories
    algorithm_dirs = {
        'greed': os.path.join(os.path.dirname(__file__), "core", "genR", "greed"),
        'gluttony': os.path.join(os.path.dirname(__file__), "core", "genR", "gluttony"),
        'sgreed': os.path.join(os.path.dirname(__file__), "core", "genR", "sgreed"),
        'sgluttony': os.path.join(os.path.dirname(__file__), "core", "genR", "sgluttony")
    }
    
    # Create directories if they don't exist
    for dir_path in algorithm_dirs.values():
        os.makedirs(dir_path, exist_ok=True)
    
    with open(filtered_similarity_file, 'r') as f:
        similarity_data = [line.strip().split(',') for line in f]
    
    print(f"Read {len(similarity_data)} entries from similarity file")
    
    # Generate pairs using both methods
    greedy_pairs = create_pairs(similarity_data, quality_weight)
    hungarian_pairs = create_hungarian_pairs(similarity_data, quality_weight)
    
    # Load grade data
    grade_data = load_grade_data(grade_csv)
    
    # Create grade-sensitive pairs
    grade_greedy_pairs = create_pairs(similarity_data, quality_weight)  # You could modify this too
    grade_hungarian_pairs = create_grade_sensitive_pairs(similarity_data, grade_data, grade_weight)
    
    # Modify the regular pairs to include grade differences
    enhanced_greedy_pairs = []
    enhanced_hungarian_pairs = []
    
    for pair in greedy_pairs:
        email1, email2, quality = pair
        grade1 = grade_data.get(email1)
        grade2 = grade_data.get(email2)
        grade_diff = calculate_grade_difference(grade1, grade2)
        enhanced_greedy_pairs.append([email1, email2, quality, grade_diff])
    
    for pair in hungarian_pairs:
        email1, email2, quality = pair
        grade1 = grade_data.get(email1)
        grade2 = grade_data.get(email2)
        grade_diff = calculate_grade_difference(grade1, grade2)
        enhanced_hungarian_pairs.append([email1, email2, quality, grade_diff])
    
    # Save regular pairs with grade differences
    greedy_file = os.path.join(algorithm_dirs['greed'], "optimal_pairs.csv")
    with open(greedy_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Person 1", "Person 2", "Match Quality", "Grade Difference"])
        writer.writerows(enhanced_greedy_pairs)
    
    hungarian_file = os.path.join(algorithm_dirs['gluttony'], "optimal_pairs.csv")
    with open(hungarian_file, 'w', newline='') as f:
        writer = csv.writer(f)
        writer.writerow(["Person 1", "Person 2", "Match Quality", "Grade Difference"])
        writer.writerows(enhanced_hungarian_pairs)
    
    # Save grade-sensitive pairs
    grade_file_paths = {
        'sgreed': os.path.join(algorithm_dirs['sgreed'], "optimal_pairs.csv"),
        'sgluttony': os.path.join(algorithm_dirs['sgluttony'], "optimal_pairs.csv")
    }
    
    for suffix, pairs in [("sgreed", grade_greedy_pairs), ("sgluttony", grade_hungarian_pairs)]:
        output_file = grade_file_paths[suffix]
        with open(output_file, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(["Person 1", "Person 2", "Match Quality", "Grade Info", "Grade Difference"])
            writer.writerows(pairs)
        
        # Create enriched versions
        enrich_optimal_pairs(output_file, csv_file, grade_data, suffix=suffix, include_grades=True)
    
    # Find and save unpaired participants for all algorithms
    for algo, file_path in [
        ('greed', greedy_file),
        ('gluttony', hungarian_file),
        ('sgreed', grade_file_paths['sgreed']),
        ('sgluttony', grade_file_paths['sgluttony'])
    ]:
        unpaired = find_unpaired_participants(file_path, csv_file)
        save_unpaired_info(unpaired, csv_file, suffix=f"_{algo}", output_dir=algorithm_dirs[algo])
    
    # Generate enriched versions for all algorithms
    for algo, file_path in [
        ('greed', greedy_file),
        ('gluttony', hungarian_file),
        ('sgreed', grade_file_paths['sgreed']),
        ('sgluttony', grade_file_paths['sgluttony'])
    ]:
        enrich_optimal_pairs(file_path, csv_file, grade_data, suffix="", output_dir=algorithm_dirs[algo])
    
    return greedy_pairs, hungarian_pairs

def enrich_optimal_pairs(optimal_pairs_file, original_csv_file, grade_data=None, suffix="", include_grades=False, output_dir=None):
    """Add gender, preference, and grade difference information to optimal pairs"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "core", "genR")
    
    with open(original_csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        
        email_idx = headers.index("Email Address")
        gender_idx = headers.index("What is your gender?")
        preference_idx = headers.index("What gender are you attracted to?")
        
        email_data = {}
        for row in reader:
            if len(row) > max(email_idx, gender_idx, preference_idx):
                email = row[email_idx].strip()
                gender = row[gender_idx].strip()
                preference = row[preference_idx].strip()
                email_data[email] = (gender, preference)
    
    pairs_with_info = []
    with open(optimal_pairs_file, 'r') as f:
        reader = csv.reader(f)
        header = next(reader)
        for row in reader:
            email1, email2, quality = row[:3]
            grade_info = row[3] if include_grades and len(row) > 3 else ""
            grade_diff = row[4] if len(row) > 4 else (
                calculate_grade_difference(
                    grade_data.get(email1), grade_data.get(email2)
                ) if grade_data else "N/A"
            )
            
            gender1, pref1 = email_data.get(email1, ('Unknown', 'Unknown'))
            gender2, pref2 = email_data.get(email2, ('Unknown', 'Unknown'))
            
            pairs_with_info.append([
                email1, f"(is: {gender1}, wants: {pref1})",
                email2, f"(is: {gender2}, wants: {pref2})",
                quality, grade_info, grade_diff
            ])

    enriched_file = os.path.join(output_dir, f"optimal_pairs_with_info{suffix}.csv")
    with open(enriched_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Person 1", "Gender & Preference 1", "Person 2", "Gender & Preference 2", 
                        "Match Quality", "Grade Info", "Grade Difference"])
        writer.writerows(pairs_with_info)
    
    print(f"Created enriched optimal pairs file in {output_dir}")

def find_unpaired_participants(optimal_pairs_file, csv_file):
    """Find participants who weren't matched"""
    all_participants = set()
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        email_idx = headers.index("Email Address")
        for row in reader:
            all_participants.add(row[email_idx].strip())
    
    paired_participants = set()
    with open(optimal_pairs_file, 'r') as f:
        reader = csv.reader(f)
        next(reader)
        for row in reader:
            paired_participants.add(row[0])
            paired_participants.add(row[1])
            
    unpaired = all_participants - paired_participants
    print(f"Found {len(unpaired)} unpaired participants")
    return unpaired

def save_unpaired_info(unpaired_participants, csv_file, suffix="", output_dir=None):
    """Create CSV with unpaired participants and their preferences"""
    if output_dir is None:
        output_dir = os.path.join(os.path.dirname(__file__), "core", "genR")
    
    email_to_data = {}
    with open(csv_file, 'r', encoding='utf-8-sig') as f:
        reader = csv.reader(f)
        headers = next(reader)
        email_idx = headers.index("Email Address")
        gender_idx = headers.index("What is your gender?")
        pref_idx = headers.index("What gender are you attracted to?")
        
        for row in reader:
            email = row[email_idx].strip()
            if email in unpaired_participants:
                gender = row[gender_idx].strip()
                preference = row[pref_idx].strip()
                email_to_data[email] = (gender, preference)
    
    output_file = os.path.join(output_dir, f"unpaired_entries{suffix}.csv")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(["Email", "Gender & Preference"])
        for email in sorted(unpaired_participants):
            gender, pref = email_to_data.get(email, ('Unknown', 'Unknown'))
            writer.writerow([email, f"(is: {gender}, wants: {pref})"])

from core.analysis import MatchAnalysis

def process_files():
    """Process files with platform-specific path handling"""
    csv_file = csv_entry.get()
    config_file = config_entry.get()
    filter_file = filter_entry.get()
    grade_csv = grade_entry.get()
    grade_weight = grade_weight_slider.get()
    
    if not all([csv_file, config_file, filter_file, grade_csv]):
        status_label.config(text="All files must be selected", foreground='#ff0000')
        return

    progress['value'] = 0
    root.update()
    
    try:
        # Ensure the genR directory exists
        output_dir = os.path.join(os.path.dirname(__file__), "core", "genR")
        os.makedirs(output_dir, exist_ok=True)
        
        status_label.config(text="Stage 1/5: Initializing and processing CSV...", foreground='#d4d4d4')
        purge_genR_folder()
        output_file = os.path.join(os.path.dirname(__file__), "core", "genR", "modified_csv.csv")
        replace_values_in_csv(csv_file, config_file, output_file)
        progress['value'] = 20
        root.update()
        
        status_label.config(text="Stage 2/5: Calculating distances...", foreground='#d4d4d4')
        data = process_csv(output_file)
        distances = calculate_distances(data)
        save_processed_data(distances, os.path.join(os.path.dirname(__file__), "core", "genR", "processed_distances.csv"))
        progress['value'] = 40
        root.update()
        
        status_label.config(text="Stage 3/5: Computing similarities...", foreground='#d4d4d4')
        similarity = calculate_similarity(distances)
        save_processed_data(similarity, os.path.join(os.path.dirname(__file__), "core", "genR", "similarity_list.csv"))
        progress['value'] = 60
        root.update()
        
        status_label.config(text="Stage 4/5: Pre-filtering matches...", foreground='#d4d4d4')
        similarity_file = os.path.join(os.path.dirname(__file__), "core", "genR", "similarity_list.csv")
        
        print("Reading original similarity data...")
        with open(similarity_file, 'r') as f:
            similarity_data = [line.strip().split(',') for line in f]
        print(f"Found {len(similarity_data)} original entries")
        
        filtered_data = prefilter_by_preferences(similarity_data, csv_file)
        
        filtered_file = os.path.join(os.path.dirname(__file__), "core", "genR", "filtered_similarity_list.csv")
        with open(filtered_file, 'w') as f:
            for entry in filtered_data:
                f.write(','.join(entry) + '\n')
        
        progress['value'] = 80
        root.update()
        
        status_label.config(text="Stage 5/5: Creating optimal pairs...", foreground='#d4d4d4')
        quality_weight = quality_slider.get()
        filtered_similarity_file = os.path.join(os.path.dirname(__file__), "core", "genR", "filtered_similarity_list.csv")
        create_optimal_pairs(filtered_similarity_file, csv_file, grade_csv, quality_weight=quality_weight, grade_weight=grade_weight)
        progress['value'] = 100
        root.update()
        
        status_label.config(text="Final Stage: Analyzing results...", foreground='#d4d4d4')
        analyzer = MatchAnalysis(output_dir)
        analyzer.analyze_all_algorithms()
        
        status_label.config(text="Processing completed! Check core/genR for all Data", foreground='#00ff00')
        
    except Exception as e:
        status_label.config(text=f"Error: {str(e)}", foreground='#ff0000')
        progress['value'] = 0

DEFAULT_PATHS_FILE = os.path.join(os.path.dirname(__file__), "defaults.json")

def load_default_paths():
    """Load default paths from configuration file"""
    try:
        with open(DEFAULT_PATHS_FILE, 'r') as f:
            return json.load(f)
    except Exception as e:
        print(f"Could not load default paths: {e}")
        return {}

def create_ui():
    """Create the main application UI with platform-specific adjustments"""
    global csv_entry, config_entry, filter_entry, grade_entry, quality_slider, grade_weight_slider, progress, status_label, root, process_button

    # Platform-specific window creation
    if platform.system() == 'Darwin':  # macOS
        root = TkinterDnD.Tk() if not IS_BUNDLED else tk.Tk()
        # Set modern macOS window style
        root.tk.call('tk::unsupported::MacWindowStyle', 'style', root._w, 'document', 'moveToActiveSpace')
    else:  # Windows and others
        root = TkinterDnD.Tk() if not IS_BUNDLED else tk.Tk()

    root.title("PyValentin")
    root.geometry("600x700")
    root.configure(bg='#1e1e1e')

    # Platform-specific UI adjustments
    if platform.system() == 'Windows':
        padding = 8  # Windows needs slightly different padding
    else:
        padding = 10  # macOS padding

    # Load default paths
    default_paths = load_default_paths()
    
    main_frame = tk.Frame(root, bg='#1e1e1e', highlightthickness=0)
    main_frame.pack(pady=20, padx=20, fill='both', expand=True)

    input_frame = tk.Frame(main_frame, bg='#1e1e1e')
    input_frame.pack(fill='x', pady=10)
    
    csv_entry = create_file_input(input_frame, "CSV File", "csv_entry", select_csv)
    config_entry = create_file_input(input_frame, "Config File", "config_entry", select_config)
    filter_entry = create_file_input(input_frame, "Filter File", "filter_entry", select_filter)
    grade_entry = create_file_input(input_frame, "Grade CSV", "grade_entry", select_grade_csv)
    
    # Set default paths if available
    if 'config_file' in default_paths and os.path.exists(default_paths['config_file']):
        config_entry.insert(0, default_paths['config_file'])
    
    if 'filter_file' in default_paths and os.path.exists(default_paths['filter_file']):
        filter_entry.insert(0, default_paths['filter_file'])
    
    control_frame = tk.Frame(main_frame, bg='#1e1e1e')
    control_frame.pack(fill='x', pady=10)
    
    quality_slider = create_quality_slider(control_frame)
    grade_weight_slider = create_grade_slider(control_frame)
    progress = ttk.Progressbar(control_frame, orient='horizontal', length=300, mode='determinate')
    progress.pack(fill='x', pady=5)
    
    process_button = create_action_buttons(main_frame, process_files)
    
    status_label = ttk.Label(main_frame, text="Please select all files",
                            background='#1e1e1e', foreground='#ff9900')
    status_label.pack(fill='x', pady=5)

    # Platform-specific key bindings
    if platform.system() == 'Darwin':  # macOS
        root.bind('<Command-v>', select_csv)
        root.bind('<Command-c>', select_config)
        root.bind('<Command-f>', select_filter)
    else:  # Windows and others
        root.bind('<Control-v>', select_csv)
        root.bind('<Control-c>', select_config)
        root.bind('<Control-f>', select_filter)

    for entry in [csv_entry, config_entry, filter_entry, grade_entry]:
            entry.drop_target_register(DND_FILES)
            entry.dnd_bind('<<Drop>>', lambda e, entry=entry: drop(e, entry))

    root.mainloop()

def drop(event, widget):
    if event.data:
        widget.delete(0, tk.END)
        widget.insert(0, event.data.strip('{}'))
        check_inputs()

def main():
    if IS_BUNDLED:
        root = tk.Tk()
    else:
        root = TkinterDnD.Tk()
    root.withdraw()
    
    splash = SplashScreen(root)
    start_time = time.time()
    
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
    
    elapsed_time = time.time() - start_time
    if (elapsed_time < 3):
        time.sleep(3 - elapsed_time)
    
    splash.finish()
    create_ui()

if __name__ == "__main__":
    install_dependencies()
    main()

def check_grade_compatibility(person1_grade, person2_grade):
    """Check if two people's grades are compatible using stricter rules"""
    try:
        grade_diff = abs(int(person1_grade) - int(person2_grade))
        return grade_diff <= MAX_GRADE_DIFFERENCE
    except (ValueError, TypeError):
        return False

def adjust_match_quality(base_quality, grade1, grade2):
    """Adjust match quality based on grade difference"""
    try:
        grade_diff = abs(int(grade1) - int(grade2))
        penalty = grade_diff * GRADE_PENALTY_FACTOR
        adjusted_quality = base_quality * (1 - penalty)
        return max(0, adjusted_quality)
    except (ValueError, TypeError):
        return 0

def create_pairs(similarity_data, preferences_data):
    """Create pairs with stricter grade and quality requirements"""
    pairs = []
    used = set()
    
    # Sort by match quality first 
    sorted_entries = sorted(similarity_data, 
                          key=lambda x: float(x[2]) if len(x) > 2 else 0, 
                          reverse=True)
    
    for entry in sorted_entries:
        if len(entry) < 2:
            continue
            
        person1 = entry[0]
        if person1 in used:
            continue
            
        person1_data = preferences_data.get(person1)
        if not person1_data:
            continue
            
        # Find best available match
        best_match = None
        best_quality = 0
        
        for potential_match in entry[1:]:
            if potential_match in used:
                continue
                
            person2_data = preferences_data.get(potential_match)
            if not person2_data:
                continue
                
            # Check grade compatibility
            if not check_grade_compatibility(person1_data['grade'], 
                                          person2_data['grade']):
                continue
                
            # Calculate adjusted match quality
            base_quality = float(entry[2]) if len(entry) > 2 else 0
            adjusted_quality = adjust_match_quality(
                base_quality,
                person1_data['grade'],
                person2_data['grade']
            )
            
            # Check minimum quality threshold
            if adjusted_quality >= MIN_MATCH_QUALITY:
                best_match = potential_match
                best_quality = adjusted_quality
                break
        
        if best_match:
            pairs.append([person1, best_match, best_quality])
            used.add(person1)
            used.add(best_match)
    
    return pairs

