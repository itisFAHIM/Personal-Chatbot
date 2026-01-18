import os

def read_local_file(file_path):
    # Security check: Only allow reading files in your project directory
    base_dir = "F:\\Fahm_Code_Korbi"
    full_path = os.path.join(base_dir, file_path)
    
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            return f.read()
    return "File not found."