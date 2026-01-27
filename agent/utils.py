import os
from django.conf import settings

def read_local_file(file_path):
    # Security check: Only allow reading files in the project directory
    base_dir = settings.BASE_DIR
    full_path = os.path.join(base_dir, file_path)
    
    if os.path.exists(full_path):
        with open(full_path, 'r') as f:
            return f.read()
    return "File not found."