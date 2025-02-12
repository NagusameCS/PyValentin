# PyValentin Documentation

## Quick Links
- [GitHub Repository](https://github.com/NagusameCS/PyValentin)
- [Installation Guide](#installation)
- [Usage Guide](#usage)
- [Understanding Outputs](#outputs)
- [Mathematical Foundation](#math)

## Overview

PyValentin is a sophisticated matchmaking system that combines multiple algorithms to create optimal pairings based on survey responses, grade levels, and preferences. The system now features both a traditional GUI and a modern Pygame interface.

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/NagusameCS/PyValentin.git
   ```

2. Install dependencies:
   ```bash
   python update_dependencies.py
   ```

3. Required Python version: 3.8+

## Usage

### GUI Options

1. **Traditional Interface**:
   ```bash
   python main.py
   ```

2. **Modern Pygame Interface**:
   ```bash
   python pygameMain.py
   ```

### File Requirements

1. **Survey CSV**
   - Contains participant responses
   - Required columns:
     - Email Address
     - Gender
     - Attracted To
     - Survey responses

2. **Config JSON**
   - Maps text responses to numerical values
   ```json
   {
     "Response Text": "Numerical Value"
   }
   ```

3. **Filter JSON**
   - Defines gender/preference matching rules
   ```json
   {
     "filterables": {
       "1": "Male",
       "2": "Female"
     },
     "filters": {
       "5": ["1", "2"]
     }
   }
   ```

4. **Grade CSV**
   - Contains participant grade levels
   - Required format:
     ```csv
     Email,Grade
     user@example.com,9
     ```

## Outputs

All outputs are generated in the `core/genR` folder:

### 1. modified_csv.csv
- Normalized survey data
- Numerical values for all responses
- Used for distance calculations

### 2. processed_distances.csv
- Distance matrix between all participants
- Format: CSV with participant emails as rows/columns
- Values: 0-1 (0 = identical, 1 = maximum difference)

### 3. similarity_list.csv
- Ranked similarity scores
- Format: `email1,email2,score`
- Higher scores indicate better matches

### 4. filtered_similarity_list.csv
- Gender/preference filtered matches
- Excludes incompatible pairs
- Format: `email1,matches...`

### 5. Optimal Pairs Files
- **optimal_pairs_greed.csv**: Greedy algorithm matches
- **optimal_pairs_gluttony.csv**: Hungarian algorithm matches
- **optimal_pairs_sGreed.csv**: Grade-sensitive greedy matches
- **optimal_pairs_sGluttony.csv**: Grade-sensitive Hungarian matches

### 6. Enriched Output Files
- **optimal_pairs_with_info_*.csv**: Detailed match information
- Includes gender, preferences, and grade differences
- Format:
  ```csv
  Person 1,Gender & Pref 1,Person 2,Gender & Pref 2,Quality,Grade Info
  ```

## Mathematical Foundation {#math}

### Distance Calculation

The system uses a weighted Euclidean distance in n-dimensional space:

$$d(x,y) = \sqrt{\sum_{i=1}^{n} w_i(x_i - y_i)^2}$$

Where:
- $x_i, y_i$ are normalized response values
- $w_i$ are question weights
- $n$ is the number of questions

### Similarity Transform

Raw distances are converted to similarity scores:

$$s(x,y) = \frac{1}{1 + d(x,y)}$$

This creates a similarity score between 0 and 1.

### Grade Weighting

Grade differences affect final scores:

$$\text{final\_score} = (1-w_g)s(x,y) + w_g(1-p_g)$$

Where:
- $w_g$ is the grade weight (0-1)
- $p_g$ is the grade penalty:
  ```python
  penalties = {
      0: 0.0,  # Same grade
      1: 0.3,  # One grade apart
      2: 0.7,  # Two grades apart
      3: 0.9   # Three+ grades apart
  }
  ```

### Hungarian Algorithm

For optimal matching, we use the Hungarian algorithm with a cost matrix $C$ where:

$$C_{ij} = 1 - s(i,j)$$

This minimizes the total cost of all matches.

## Configuration

### Quality vs Quantity Slider
- 0.0: Maximize number of matches
- 1.0: Maximize match quality
- Default: 0.5 (balanced)

### Grade Weight Slider
- 0.0: Ignore grades
- 1.0: Prioritize grade matching
- Recommended: 0.7

## Tips

1. **Preprocessing**
   - Clean survey data
   - Remove duplicate entries
   - Verify email formats

2. **Grade Matching**
   - Use consistent grade format
   - Include all participants
   - Verify grade range

3. **Performance**
   - Typical processing time: 1-2s per 100 participants
   - Memory usage: ~100MB for 1000 participants

## Troubleshooting

### Common Issues

1. **File Format Errors**
   ```python
   Error: CSV missing required columns
   ```
   - Verify CSV column names
   - Check for extra commas

2. **No Matches Found**
   - Verify filter rules
   - Check gender/preference data
   - Confirm grade data format

### Debug Mode

Enable detailed logging:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Submit a pull request

## License

GNU General Public License v3.0
