# import ollama

# def get_korbi_response(user_message, history):
#     # This System Prompt is what makes it a CODING agent
#     system_prompt = {
#         'role': 'system', 
#         'content': """You are FAHIM_Code_Korbi. You are an expert developer. Provide clean code and concise explanations.
#         1. You are an expert software developer.
#         2. When asked for code, provide full, runnable examples.
#         3. Use triple backticks with the language name (e.g. ```python).
#         4. Explain your logic briefly after the code block."""
#     }
    
#     # Combine system prompt, history, and the new message
#     messages = [system_prompt] + history + [{'role': 'user', 'content': user_message}]

#     # try:
#     #     response = ollama.chat(
#     #         model='gemma3:4b',
#     #         messages=messages,
#     #     )
#     #     return response['message']['content']
#     # except Exception as e:
#     #     return f"Ollama Error: Make sure Ollama is running! Details: {str(e)}"
#     response = ollama.chat(model='gemma3:4b', messages=messages)
#     return response['message']['content']
    
import ollama

def get_korbi_response(user_message, history):
    # System Prompt
    system_prompt = {
        'role': 'system', 
        'content': """You are FAHIM_Code_Korbi. You are an expert developer. Provide clean code and concise explanations.
        1. You are an expert software developer.
        2. When asked for code, provide full, runnable examples.
        3. Use triple backticks with the language name (e.g. ```python).
        4. Explain your logic briefly after the code block."""
    }
    
    # Build messages: system + history + new user message
    # Don't duplicate the user message - it's not in history yet
    messages = [system_prompt] + history + [{'role': 'user', 'content': user_message}]

    try:
        response = ollama.chat(
            model='gemma3:4b',
            messages=messages,
        )
        return response['message']['content']
    except Exception as e:
        return f"Ollama Error: Make sure Ollama is running! Details: {str(e)}"