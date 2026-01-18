# import ollama
# import re
# from .utils import read_local_file  # Import the tool you made

# def get_korbi_response(user_message, history):
#     # System Prompt
#     system_prompt = {
#         'role': 'system', 
#         'content': """You are FAHIM_Code_Korbi. You are an expert developer.
#         1. When the user shares code from a file (marked with CONTEXT FROM FILES), analyze it strictly.
#         2. Provide full, runnable examples.
#         3. Use triple backticks for code (e.g. ```python).
#         4. Be concise."""
#     }
    
#     # --- TOOL USE LOGIC (The new part) ---
#     # 1. Regex to find patterns like "@read agent/views.py"
#     files_to_read = re.findall(r'@read\s+([\w./\\-]+)', user_message)
    
#     context_injection = ""
#     if files_to_read:
#         for filename in files_to_read:
#             # Call your function from utils.py
#             file_content = read_local_file(filename)
#             context_injection += f"\n\n--- FILE: {filename} ---\n{file_content}\n"
        
#         # Append the file content to the message so Gemma sees it
#         user_message += f"\n\nCONTEXT FROM FILES:\n{context_injection}"
#     # -------------------------------------

#     # Build messages: system + history + new (augmented) user message
#     messages = [system_prompt] + history + [{'role': 'user', 'content': user_message}]

#     try:
#         response = ollama.chat(
#             model='gemma3:4b',
#             messages=messages,
#         )
#         return response['message']['content']
#     except Exception as e:
#         return f"Ollama Error: Make sure Ollama is running! Details: {str(e)}"  

import ollama
import re
from .utils import read_local_file

def get_korbi_response_stream(user_message, history):
    # System Prompt
    system_prompt = {
        'role': 'system', 
        'content': """You are FAHIM_Code_Korbi, an expert developer.
        1. When user shares code, analyze strictly.
        2. Provide full, runnable examples in Markdown.
        3. Be concise."""
    }
    
    # --- TOOL USE LOGIC ---
    files_to_read = re.findall(r'@read\s+([\w./\\-]+)', user_message)
    if files_to_read:
        context_injection = ""
        for filename in files_to_read:
            file_content = read_local_file(filename)
            context_injection += f"\n\n--- FILE: {filename} ---\n{file_content}\n"
        user_message += f"\n\nCONTEXT FROM FILES:\n{context_injection}"
    # ----------------------

    messages = [system_prompt] + history + [{'role': 'user', 'content': user_message}]

    # Enable Streaming
    stream = ollama.chat(
        model='gemma3:4b',
        messages=messages,
        stream=True,  # <--- MAGIC SWITCH
    )

    for chunk in stream:
        yield chunk['message']['content']