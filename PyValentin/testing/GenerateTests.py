"""
Copyright (c) 2025
This program is part of PyValentin
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License.
"""

import random
import csv
from datetime import datetime, timedelta

# Gender and preference mapping
gender_options = ["1", "2", "3"]
preference_options = ["1", "2", "3", "4", "5", "6", "7", "8"]

# Other possible answers for survey questions
responses = { 
    "Are you an introvert or extrovert?": ["1", "2"],
    "What's your ideal first date?": ["1", "2", "3", "4"],
    "What type of sense of humor attracts you most?": ["1", "2", "3", "4"],
    "Which hobby would you love to share with your partner?": ["1", "2", "3", "4"],
    "Do you think communication is important?": ["1", "2", "3", "4"],
    "What kind of lifestyle matches yours?": ["1", "2", "3", "4"],
    "What’s your take on PDA (Public Displays of Affection)?": ["1", "2", "3", "4"],
    "What kind of music speaks to your soul?": ["1", "2", "3", "4"],
    "How do you show love to your partner?": ["1", "2", "3", "4"],
    "If you could cook dinner for someone, what would you cook?": ["1", "2", "3", "4"],
    "How do you handle leadership roles?": ["1", "2", "3", "4"],
    "How do you express your needs and opinions?": ["1", "2", "3", "4"],
    "How do you handle stressful situations?": ["1", "2", "3", "4"],
    "How do you collaborate in group projects?": ["1", "2", "3", "4"],
    "How motivated are you to achieve your goals?": ["1", "2", "3", "4"],
    "When you have a project due, how do you approach it?": ["1", "2", "3", "4"],
    "How do you typically spend your free time?": ["1", "2", "3", "4"],
    "How do you feel in large social gatherings?": ["1", "2", "3", "4"],
    "How do you respond to someone needing help?": ["1", "2", "3", "4"],
    "How often do you feel anxious or stressed?": ["1", "2", "3", "4"],
}

# Generate timestamps for new entries
base_time = datetime.strptime("2/5/2025 10:00:00", "%m/%d/%Y %H:%M:%S")

# File path
import os
output_file = os.path.join(os.path.dirname(__file__), "test_users_700.csv")

# Generate 10,000 test users
with open(output_file, mode="w", newline="") as file:
    writer = csv.writer(file)
    header = [
        "Timestamp", "Email Address", "What is your gender?", "What gender are you attracted to?",
        "Are you an introvert or extrovert?", "What's your ideal first date?", "What type of sense of humor attracts you most?",
        "Which hobby would you love to share with your partner?", "Do you think communication is important?",
        "What kind of lifestyle matches yours?", "What’s your take on PDA (Public Displays of Affection)?",
        "What kind of music speaks to your soul?", "How do you show love to your partner?",
        "If you could cook dinner for someone, what would you cook?", "How do you handle leadership roles?",
        "How do you express your needs and opinions?", "How do you handle stressful situations?",
        "How do you collaborate in group projects?", "How motivated are you to achieve your goals?",
        "When you have a project due, how do you approach it?", "How do you typically spend your free time?",
        "How do you feel in large social gatherings?", "How do you respond to someone needing help?",
        "How often do you feel anxious or stressed?", "Column 24"
    ]
    writer.writerow(header)
    
    for i in range(700):
        timestamp = base_time + timedelta(minutes=random.randint(1, 500000))
        email = f"user{i+1}@test.com"
        gender = random.choice(gender_options)
        preference = random.choice(preference_options)
        
        entry = [
            timestamp.strftime("%m/%d/%Y %H:%M:%S"),
            email,
            gender,
            preference,
        ] + [random.choice(responses[q]) for q in responses]
        
        writer.writerow(entry)

print(f"Generated {output_file} with 10,000 entries.")
