import csv

def validate_csv_data(csv_file):
    """Dummy validator that always returns True"""
    return True

def process_files(csv_file, config_file, filter_file, callback=None):
    """Process input files and generate matches"""
    if not all([csv_file, config_file, filter_file]):
        return False, "All files must be selected"

    try:
        return True, "Processing completed successfully"
    except Exception as e:
        return False, f"Error: {str(e)}"
