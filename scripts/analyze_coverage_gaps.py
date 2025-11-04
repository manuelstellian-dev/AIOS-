import json
import os

def load_coverage_data(coverage_file):
    with open(coverage_file, 'r') as file:
        coverage_data = json.load(file)
    return coverage_data

def analyze_coverage(coverage_data):
    coverage_gaps = []
    for module, data in coverage_data.items():
        if data['coverage'] < 80:  # Assuming 80% coverage is the threshold
            coverage_gaps.append({
                'module': module,
                'coverage': data['coverage'],
                'missing_tests': data['missing_tests']
            })
    return coverage_gaps

def prioritize_files(coverage_gaps):
    priorities = {'quick_wins': [], 'core_modules': [], 'security': [], 'high_impact': []}
    for gap in coverage_gaps:
        if gap['module'].startswith('core'):
            priorities['core_modules'].append(gap)
        elif gap['module'].startswith('security'):
            priorities['security'].append(gap)
        else:
            priorities['quick_wins'].append(gap)
    
    # Assume high impact based on certain criteria
    priorities['high_impact'] = [g for g in coverage_gaps if g['coverage'] < 50]  # Example condition

    return priorities

def generate_report(prioritized_files):
    for priority, files in prioritized_files.items():
        print(f"{priority}:")
        for file in files:
            print(f" - Module: {file['module']}, Coverage: {file['coverage']}%")

if __name__ == '__main__':
    coverage_file_path = 'coverage.json'  # Specify the path to coverage.json
    coverage_data = load_coverage_data(coverage_file_path)
    coverage_gaps = analyze_coverage(coverage_data)
    prioritized_files = prioritize_files(coverage_gaps)
    generate_report(prioritized_files)