# PyValentin - Advanced Matchmaking System

## Overview
PyValentin is a sophisticated matchmaking system that uses multi-dimensional distance calculations and compatibility filtering to create optimal pairs from survey responses. The system processes raw survey data through several stages, applying mathematical models to quantify compatibility.

## Table of Contents
1. [Features](#features)
2. [Setup](#setup)
3. [Usage](#usage)
4. [The Beautiful Beautifly Simple Math Behind PyValentin](#the-mathematics-behind-pyvalentin)
5. [File Structure](#file-structure)
6. [Configuration](#configuration)
7. [Input Format](#input-format)
8. [Output Files](#output-files)
9. [Customization Guide](#customization-guide)
10. [Technical Details](#technical-details)
11. [Troubleshooting](#troubleshooting)
12. [Contact & Support](#contact--support)
13. [License](#license)

## Features
- Multi-dimensional compatibility analysis
- Customizable gender/preference filtering
- Quality vs. quantity optimization
- Interactive GUI with progress tracking
- Drag-and-drop file support
- Comprehensive results output

## Setup
1. Ensure Python 3.8+ is installed
2. Install dependencies:
    ```bash
    pip install tkinterdnd2 numpy
    ```
3. Place your survey data in CSV format
4. Configure your Config.json and Filter.json files

## Usage
1. Launch the application:
    ```bash
    python main.py
    ```
2. Select your input files:
    - Survey responses (CSV)
    - Configuration file (JSON)
    - Filter rules (JSON)
3. Adjust the quality-quantity slider
4. Click "Process Files"
5. Check the genR folder for results

## The Mathematics Behind PyValentin

### 1. Data Normalization
Before processing, all categorical survey responses are converted to numerical values using the Config.json mapping. This creates a consistent numerical space for calculations.

### 2. Distance Calculation
For each pair of users (i,j), we calculate a multi-dimensional Euclidean distance:

```
distance(i,j) = √(Σ(xi,k - xj,k)²)
where k represents each survey question
```

This produces a distance matrix D where D[i,j] represents how different two users are across all responses.

### 3. Similarity Transformation
The distance matrix is transformed into a similarity matrix using:

```
similarity(i,j) = 1 / (1 + distance(i,j))
```

This creates a normalized similarity score where:
- 1.0 = perfect match
- 0.0 = complete mismatch

### 4. Preference Filtering
The system applies a boolean matrix F where:
```
F[i,j] = 1 if preferences match
F[i,j] = 0 if preferences conflict
```

The final compatibility score becomes:
```
compatibility(i,j) = similarity(i,j) × F[i,j]
```

### 5. Optimal Pairing Algorithm
The system uses a modified stable marriage algorithm with the following steps:

1. Sort users by number of potential matches
2. For each user i:
    - Find top N matches based on quality weight
    - Select best available match j
    - Remove both i and j from available pool

Quality weight affects match selection:
- High (>0.5): Selects from top 25% of matches
- Low (<0.5): Considers up to 75% of matches

### 6. Second Pass Optimization
For remaining unmatched users:
1. Create a graph of mutual matches
2. Find maximal matching using a greedy algorithm
3. Optimize for global satisfaction using local improvements

## File Structure
```
PyValentin/
├── main.py           # Main application
├── FixCSV.py        # Data preprocessing
├── Ski.py           # Core algorithms
├── genR/            # Generated results
├── ASF Specific/    # Configuration files
└── README.md        # Documentation
```

## Configuration

### Config.json
Defines mappings from survey responses to numerical values:
```json
{
     "Response Text": "Numerical Value",
     // ... more mappings
}
```

### Filter.json
Defines preference matching rules:
```json
{
     "filterables": {
          "1": "Male",
          "2": "Female",

     },
     "filters": {
          "5": ["1", "2", "3"],  
          "4": ["1", "2"],      

     }
}
```

## Input Format
Required CSV columns:
1. Timestamp
2. Email
3. Gender (a)
4. Attracted to (b)
5. Question responses...

Example:
```csv
Timestamp,Email,Gender,Attracted To,Q1,Q2,...
2024-01-01,user@example.com,Male,Female,Response1,Response2,...
```

## Output Files
- modified_csv.csv: Normalized survey data
- processed_distances.csv: Distance matrix
- similarity_list.csv: Similarity scores
- filtered_similarity_list.csv: Filtered matches
- optimal_pairs.csv: Final pairings
- unpaired_entries.csv: Unmatched users

## Customization Guide

### Modifying Match Criteria
1. Update `Config.json` with new response mappings
2. Modify `Filter.JSON` matching rules
3. Adjust weights in `Ski.py` calculate_distances() function

### Adding New Questions
1. Add response mappings to `Config.json`
2. Update CSV processing in `FixCSV.py` if needed
3. Modify distance calculation in `Ski.py`

### Custom Filtering Rules
Modify `Filter.JSON`:
```json
{
    "filterables": {
        "value": "label"
    },
    "filters": {
        "seeker_value": ["acceptable_values"]
    }
}
```

## Technical Details

### Distance Calculation
- Uses normalized Euclidean distance
- Configurable weights per question
- Range: 0 (identical) to 1 (maximum difference)

### Matching Algorithm
1. Converts responses to numerical values
2. Calculates distance matrix
3. Generates similarity scores
4. Applies filtering rules
5. Handles edge cases

### Performance
- O(n²) complexity for n participants
- Memory usage: ~100MB for 1000 participants
- Processing time: ~1-2 seconds per 100 participants

## Troubleshooting

### Common Issues
1. **Missing dependencies**
   - Run `pip install tkinterdnd2 numpy`
   - Check Python version (3.8+ required)

2. **File format errors**
   - Verify CSV column order
   - Check JSON syntax
   - Ensure UTF-8 encoding

3. **No matches found**
   - Verify filter rules
   - Check response mappings
   - Confirm gender/attraction values

### Debug Mode
Add debug logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contact & Support
Contact me for info on this project at:
Oharawil123@asf.edu.mx

## License
This project is licensed under the GNU General Public License v3.0 - see below for details:

```
This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program. If not, see <https://www.gnu.org/licenses/>.
```
