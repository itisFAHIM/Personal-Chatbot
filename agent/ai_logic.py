# import ollama
# import re
# from .utils import read_local_file
# from .rag import search_codebase

# def get_korbi_response_stream(user_message, history):
    
#     files_to_read = re.findall(r'@read\s+([\w./\\-]+)', user_message)
#     manual_context = ""
#     if files_to_read:
#         for filename in files_to_read:
#             manual_context += f"\n\n--- FILE: {filename} ---\n{read_local_file(filename)}\n"

    
#     rag_context = ""
#     if not files_to_read and len(user_message) > 15:
#         try:
            
#             search_results = search_codebase(user_message, n_results=2)
#             if search_results:
#                 rag_context = f"\n\n=== BACKGROUND CONTEXT FROM PROJECT FILES ===\n{search_results}\n=============================================\n"
#         except Exception as e:
#             print(f"RAG Error: {e}")

    
#     full_context = manual_context + rag_context
    
#     # --- SMARTER SYSTEM PROMPT ---
#     system_instruction = """You are FAHIM_Code_Korbi, an expert AI developer.
    
#     RULES FOR USING CONTEXT:
#     1. You have access to project files in the 'BACKGROUND CONTEXT' section below.
#     2. IF the user asks about the project (e.g., "how does login work?", "where is views.py?"), USE the context.
#     3. IF the user asks a GENERAL question (e.g., "write hello world in C", "explain bubble sort"), IGNORE the context completely and use your general knowledge.
#     4. NEVER just output the context code unless specifically asked to "show me the file".
    
#     Answer concisely and accurately."""

#     if full_context:
        
#         final_user_message = f"{full_context}\n\nUSER QUESTION:\n{user_message}"
#     else:
#         final_user_message = user_message

#     messages = [
#         {'role': 'system', 'content': system_instruction}
#     ] + history + [{'role': 'user', 'content': final_user_message}]

   
#     stream = ollama.chat(model='gemma3:4b', messages=messages, stream=True)
#     for chunk in stream:
#         yield chunk['message']['content']        

import ollama
import re
from .utils import read_local_file
from .rag import search_codebase

def get_korbi_response_stream(user_message, history, image_data=None):
    # --- 1. SETUP CONTEXT ---
    files_to_read = re.findall(r'@read\s+([\w./\\-]+)', user_message)
    manual_context = ""
    if files_to_read:
        for filename in files_to_read:
            manual_context += f"\n\n--- FILE: {filename} ---\n{read_local_file(filename)}\n"

    # Only do RAG search if it's text-only (LLaVA focuses on the image)
    rag_context = ""
    if not image_data and not files_to_read and len(user_message) > 15:
        try:
            search_results = search_codebase(user_message, n_results=2)
            if search_results:
                rag_context = f"\n\n=== PROJECT CONTEXT ===\n{search_results}\n"
        except Exception:
            pass

    full_context = manual_context + rag_context
    final_user_message = f"{full_context}\n\nUSER QUESTION:\n{user_message}" if full_context else user_message

    # --- 2. MODEL SWITCHING LOGIC ---
    if image_data:
        # VISION MODE
        model_name = 'llava:7b'
        system_instruction = """You are FAHIM_Code_Korbi, an expert AI developer.
    
    RULES FOR USING CONTEXT:
    1. You have access to project files in the 'BACKGROUND CONTEXT' section below.
    2. IF the user asks about the project (e.g., "how does login work?", "where is views.py?"), USE the context.
    3. IF the user asks a GENERAL question (e.g., "write hello world in C", "explain bubble sort"), IGNORE the context completely and use your general knowledge.
    4. NEVER just output the context code unless specifically asked to "show me the file".
    
    Answer concisely and accurately."""
        
        # LLaVA needs the message format specifically for images
        user_msg_payload = {
            'role': 'user', 
            'content': final_user_message, 
            'images': [image_data] # Pass the Base64 image
        }
    else:
        # CODING MODE
        model_name = 'gemma:4b' # Or 'gemma3:4b' if that is what you use
        system_instruction = """You are FAHIM_Code_Korbi, an expert AI developer.
    
    RULES FOR USING CONTEXT:
    1. You have access to project files in the 'BACKGROUND CONTEXT' section below.
    2. IF the user asks about the project (e.g., "how does login work?", "where is views.py?"), USE the context.
    3. IF the user asks a GENERAL question (e.g., "write hello world in C", "explain bubble sort"), IGNORE the context completely and use your general knowledge.
    4. NEVER just output the context code unless specifically asked to "show me the file".
    
    Answer concisely and accurately."""
        user_msg_payload = {'role': 'user', 'content': final_user_message}

    messages = [{'role': 'system', 'content': system_instruction}] + history + [user_msg_payload]

    # --- 3. STREAM RESPONSE ---
    stream = ollama.chat(model=model_name, messages=messages, stream=True)
    for chunk in stream:
        yield chunk['message']['content']