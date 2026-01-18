import os
from django.conf import settings

def read_file_content(filename):
    """
    Reads a file from the project root.
    Security: Prevents escaping the project directory.
    """
    # Base directory is where manage.py is
    base_dir = settings.BASE_DIR
    
    # Clean the filename to remove any leading slash or whitespace
    filename = filename.strip().lstrip('/')
    
    # Create the full path
    file_path = os.path.join(base_dir, filename)
    
    # SECURITY: Ensure the path is actually inside our project folder
    # This prevents users from typing "@read ../../../windows/system32/..."
    if not os.path.abspath(file_path).startswith(str(base_dir)):
        return f"[System Error]: Access denied. You can only read files inside {base_dir}"

    if os.path.exists(file_path):
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                return f"--- START OF FILE: {filename} ---\n{content}\n--- END OF FILE ---"
        except Exception as e:
            return f"[System Error]: Could not read file. {str(e)}"
    else:
        return f"[System Error]: File '{filename}' not found."