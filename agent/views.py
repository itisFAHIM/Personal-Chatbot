# from django.shortcuts import render
# from django.http import JsonResponse
# from django.contrib.auth.decorators import login_required
# from .ai_logic import get_korbi_response
# from .models import ChatSession, ChatMessage
# import json

# @login_required
# def chat_home(request):
#     return render(request, 'agent/index.html')

# @login_required
# def chat_api(request):
#     if request.method == "POST":
#         data = json.loads(request.body)
#         user_message = data.get('message')
#         session_id = data.get('session_id')
        
#         # 1. Try to get an EXISTING session belonging to THIS USER
#         session = None
#         if session_id:
#             try:
#                 session = ChatSession.objects.get(session_id=session_id, user=request.user)
#             except ChatSession.DoesNotExist:
#                 session = None

#         # 2. If no valid session found, create a NEW one for THIS USER
#         if not session:
#             session = ChatSession.objects.create(user=request.user) # <--- Critical Change
        
#         # Get conversation history
#         messages = session.messages.all()
#         history = [{'role': msg.role, 'content': msg.content} for msg in messages]
        
#         # Get AI response
#         bot_response = get_korbi_response(user_message, history)
        
#         # Save messages
#         ChatMessage.objects.create(session=session, role='user', content=user_message)
#         ChatMessage.objects.create(session=session, role='assistant', content=bot_response)
        
#         # Generate title for new chats
#         if session.title == "New Chat" and len(history) == 0:
#             title = ' '.join(user_message.split()[:5])
#             if len(user_message.split()) > 5:
#                 title += "..."
#             session.title = title
#             session.save()
        
#         return JsonResponse({
#             'response': bot_response,
#             'session_id': str(session.session_id),
#             'title': session.title
#         })

# @login_required
# def get_chat_sessions(request):
#     """API endpoint to get sessions ONLY for the current user"""
#     # Filter by user=request.user so they can't see others' chats
#     sessions = ChatSession.objects.filter(user=request.user) 
    
#     sessions_data = [
#         {
#             'session_id': str(session.session_id),
#             'title': session.title,
#             'updated_at': session.updated_at.isoformat()
#         }
#         for session in sessions
#     ]
#     return JsonResponse({'sessions': sessions_data})

# @login_required
# def get_session_messages(request, session_id):
#     """API endpoint to get messages for a specific session"""
#     try:
#         # Ensure the session belongs to the user
#         session = ChatSession.objects.get(session_id=session_id, user=request.user)
#         messages = session.messages.all()
#         messages_data = [
#             {
#                 'role': msg.role,
#                 'content': msg.content,
#                 'created_at': msg.created_at.isoformat()
#             }
#             for msg in messages
#         ]
#         return JsonResponse({
#             'session_id': str(session.session_id),
#             'title': session.title,
#             'messages': messages_data
#         })
#     except ChatSession.DoesNotExist:
#         return JsonResponse({'error': 'Session not found or access denied'}, status=404)

from django.shortcuts import render
from django.http import StreamingHttpResponse, JsonResponse
from django.contrib.auth.decorators import login_required
from .ai_logic import get_korbi_response_stream
from .models import ChatSession, ChatMessage
import json

@login_required
def chat_home(request):
    """
    Renders the main chat interface. 
    Protected by @login_required so only logged-in users can see it.
    """
    return render(request, 'agent/index.html')

@login_required
def chat_api(request):
    """
    Handles the chat logic with Streaming Response.
    """
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get('message')
        session_id = data.get('session_id')
        
        # 1. Get/Create Session
        session = None
        if session_id:
            try:
                session = ChatSession.objects.get(session_id=session_id, user=request.user)
            except ChatSession.DoesNotExist:
                session = None
        
        if not session:
            # Create new session linked to the current user
            session = ChatSession.objects.create(user=request.user)

        # 2. Save User Message immediately
        ChatMessage.objects.create(session=session, role='user', content=user_message)

        # 3. Get History
        messages = session.messages.all()
        history = [{'role': msg.role, 'content': msg.content} for msg in messages]

        # 4. Generate Title if new
        if session.title == "New Chat":
            title = ' '.join(user_message.split()[:5])
            if len(user_message.split()) > 5: title += "..."
            session.title = title
            session.save()

        # 5. Define the Streaming Generator
        def stream_response():
            full_response = ""
            # Yield the session ID first so the frontend knows where we are
            yield json.dumps({'session_id': str(session.session_id), 'title': session.title}) + "\n"
            
            # Stream the AI content
            for chunk in get_korbi_response_stream(user_message, history):
                full_response += chunk
                yield chunk # Send chunk to browser
            
            # 6. Save AI Message to DB after stream ends
            ChatMessage.objects.create(session=session, role='assistant', content=full_response)

        return StreamingHttpResponse(stream_response(), content_type='text/plain')

    return JsonResponse({'error': 'Invalid request'}, status=400)
# Add these endpoints if you haven't already, so the sidebar works:

@login_required
def get_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user)
    sessions_data = [
        {
            'session_id': str(session.session_id),
            'title': session.title,
            'updated_at': session.updated_at.isoformat()
        }
        for session in sessions
    ]
    return JsonResponse({'sessions': sessions_data})

@login_required
def get_session_messages(request, session_id):
    try:
        session = ChatSession.objects.get(session_id=session_id, user=request.user)
        messages = session.messages.all()
        messages_data = [
            {
                'role': msg.role,
                'content': msg.content,
                'created_at': msg.created_at.isoformat()
            }
            for msg in messages
        ]
        return JsonResponse({
            'session_id': str(session.session_id),
            'title': session.title,
            'messages': messages_data
        })
    except ChatSession.DoesNotExist:
        return JsonResponse({'error': 'Session not found'}, status=404)