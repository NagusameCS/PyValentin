"""Constants for grade-sensitive Hungarian algorithm"""

# Maximum allowed difference in grades between matched pairs
MAX_GRADE_DIFFERENCE = 2

# Factor by which match quality is reduced per grade difference
GRADE_PENALTY_FACTOR = 0.2

# Minimum acceptable match quality after grade penalties
MIN_MATCH_QUALITY = 0.3
