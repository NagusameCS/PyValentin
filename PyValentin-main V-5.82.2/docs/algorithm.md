# PyValentin Algorithm Documentation

## Current Implementation

### Distance Calculation
For users A and B with n survey responses:
```
D(A,B) = √(Σ(Ai - Bi)²) / n
where i = 1 to n responses
```

### Similarity Score
```
S(A,B) = 1 / (1 + D(A,B))
Range: (0,1] where 1 is perfect match
```

### Match Filtering
Boolean function F(A,B) for gender/preference compatibility:
```
F(A,B) = (A.attracted_to ∈ B.gender_identity AND
          B.attracted_to ∈ A.gender_identity) OR
         (8 ∈ {A.gender_identity, A.attracted_to, B.gender_identity, B.attracted_to})
```

### Current Pair Optimization
For quality weight w ∈ [0,1]:
```
P(A,B) = w * S(A,B) + (1-w) * M(A,B)
where M(A,B) is 1 if creates new pair, 0 otherwise
```

## Proposed Improvements

### 1. Weighted Distance Calculation
Introduce importance weights for each question:
```
Dw(A,B) = √(Σ(wi(Ai - Bi)²)) / √(Σwi)
where wi is importance weight of question i
```

### 2. Multidimensional Compatibility Score
Split questions into k categories (values, lifestyle, goals):
```
Mk(A,B) = Σ(αk * Sk(A,B))
where Sk is similarity in category k
and Σαk = 1
```

### 3. Dynamic Preference Strength
Introduce preference strength parameter λ:
```
P'(A,B) = S(A,B) * (1 - e^(-λ * C(A,B)))
where C(A,B) is preference compatibility score
```

### 4. Global Optimization
Instead of greedy matching, use Hungarian algorithm:
```
maximize Σ P'(Ai,Bj) * xij
subject to:
  Σ xij = 1 for all i
  Σ xij = 1 for all j
  xij ∈ {0,1}
where xij is 1 if i matches with j
```

## Implementation Priorities

1. Weighted questions (Dw) - Highest impact/effort ratio
2. Global optimization - Eliminates local maxima issues
3. Dynamic preference strength - Better gender/preference handling
4. Multidimensional scoring - More nuanced matching
5. Feedback learning - Long-term improvement

## Mathematical Complexity

- Current: O(n²) for n users
- With global optimization: O(n³) worst case
- With feedback learning: O(n³ + m) where m is historical matches

## Space Complexity

- Current: O(n²) for similarity matrix
- Improved: O(n² * k) for k categories
