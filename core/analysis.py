import csv
import os
from typing import List, Dict, Tuple

class MatchAnalysis:
    def __init__(self, genR_path: str):
        self.genR_path = genR_path
        self.summary_data = {}
    
    def analyze_all_algorithms(self):
        """Analyze results from all matching algorithms"""
        algorithms = {
            'Greedy': ('greed', 'optimal_pairs.csv'),
            'Hungarian': ('gluttony', 'optimal_pairs.csv'),
            'Grade-Sensitive Greedy': ('sgreed', 'optimal_pairs.csv'),
            'Grade-Sensitive Hungarian': ('sgluttony', 'optimal_pairs.csv')
        }
        
        results = {}
        for algo_name, (subdir, filename) in algorithms.items():
            filepath = os.path.join(self.genR_path, subdir, filename)
            if os.path.exists(filepath):
                results[algo_name] = self.analyze_matches(filepath)
        
        self.generate_summary(results)
    
    def analyze_matches(self, filepath: str) -> Dict:
        """Analyze a single matching file"""
        stats = {
            'total_pairs': 0,
            'avg_match_quality': 0.0,
            'grade_differences': {},
            'same_grade_pairs': 0,
            'different_grade_pairs': 0,
            'missing_grade_info': 0
        }
        
        with open(filepath, 'r', newline='') as f:
            reader = csv.reader(f)
            next(reader)  # Skip header
            
            for row in reader:
                stats['total_pairs'] += 1
                quality = float(row[2])
                stats['avg_match_quality'] += quality
                
                # Handle grade differences if present
                if len(row) > 3:
                    grade_diff = row[-1]  # Last column is grade difference
                    if grade_diff == 'N/A':
                        stats['missing_grade_info'] += 1
                    else:
                        diff = int(grade_diff)
                        stats['grade_differences'][diff] = stats['grade_differences'].get(diff, 0) + 1
                        if diff == 0:
                            stats['same_grade_pairs'] += 1
                        else:
                            stats['different_grade_pairs'] += 1
        
        if stats['total_pairs'] > 0:
            stats['avg_match_quality'] /= stats['total_pairs']
        
        return stats
    
    def generate_summary(self, results: Dict):
        """Generate and save analysis summary"""
        output_path = os.path.join(self.genR_path, 'matching_analysis.txt')
        
        with open(output_path, 'w') as f:
            f.write("=== PyValentin Matching Analysis ===\n\n")
            
            for algo_name, stats in results.items():
                f.write(f"\n{algo_name} Algorithm Results:\n")
                f.write("-" * 30 + "\n")
                f.write(f"Total Pairs: {stats['total_pairs']}\n")
                
                # Check for division by zero
                if stats['total_pairs'] > 0:
                    f.write(f"Average Match Quality: {stats['avg_match_quality']:.2%}\n")
                else:
                    f.write("Average Match Quality: N/A (no pairs)\n")
                
                if stats.get('grade_differences'):
                    f.write("\nGrade Distribution:\n")
                    total_graded = stats['same_grade_pairs'] + stats['different_grade_pairs']
                    
                    if total_graded > 0:
                        same_grade_pct = (stats['same_grade_pairs']/total_graded * 100) if total_graded > 0 else 0
                        diff_grade_pct = (stats['different_grade_pairs']/total_graded * 100) if total_graded > 0 else 0
                        
                        f.write(f"Same Grade: {stats['same_grade_pairs']} ({same_grade_pct:.1f}%)\n")
                        f.write(f"Different Grade: {stats['different_grade_pairs']} ({diff_grade_pct:.1f}%)\n")
                        
                        f.write("\nGrade Differences:\n")
                        for diff, count in sorted(stats['grade_differences'].items()):
                            diff_pct = (count/total_graded * 100) if total_graded > 0 else 0
                            f.write(f"{diff} grade(s) apart: {count} pairs ({diff_pct:.1f}%)\n")
                    else:
                        f.write("No grade comparison data available\n")
                    
                    if stats['missing_grade_info'] > 0:
                        missing_pct = (stats['missing_grade_info']/stats['total_pairs'] * 100) if stats['total_pairs'] > 0 else 0
                        f.write(f"\nPairs missing grade info: {stats['missing_grade_info']} ({missing_pct:.1f}%)\n")
                
                f.write("\n" + "="*50 + "\n")
            
            f.write("\nComparative Analysis:\n")
            f.write("-" * 30 + "\n")
            
            # Only compare if there are results
            if results:
                best_quality = max(results.items(), key=lambda x: x[1]['avg_match_quality'])
                f.write(f"Best average match quality: {best_quality[0]} ({best_quality[1]['avg_match_quality']:.2%})\n")
            else:
                f.write("No algorithm results available for comparison\n")
