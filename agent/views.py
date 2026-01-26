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
from .rag import index_project_code
from django.shortcuts import get_object_or_404, redirect  
import json
from django.utils import timezone
import base64
import uuid
from django.core.files.base import ContentFile
from django.contrib.auth import login                            
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect


@login_required
def trigger_indexing(request):
    if request.method == "POST":
        status = index_project_code()
        return JsonResponse({'status': status})
    return JsonResponse({'status': 'Invalid request'})

@login_required
def chat_home(request):
    """
    Renders the main chat interface. 
    Protected by @login_required so only logged-in users can see it.
    """
    return render(request, 'agent/index.html')

@login_required
def chat_api(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user_message = data.get('message', '')
        session_id = data.get('session_id')
        image_data = data.get('image', None) 

        # (Session Creation Logic - Keep this the same)
        if not session_id:
            session = ChatSession.objects.create(user=request.user, title=user_message[:30])
            session_id = str(session.session_id)
        else:
            session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)

        # --- SAVE USER MESSAGE (WITH IMAGE) ---
        msg = ChatMessage.objects.create(session=session, role='user', content=user_message)
        
        if image_data:
            try:
                # Decode the Base64 image and save it to the file system
                format, imgstr = image_data.split(';base64,') if ';base64,' in image_data else (None, image_data)
                ext = 'png' # Default to png
                data = ContentFile(base64.b64decode(imgstr), name=f'{session.session_id}_{uuid.uuid4()}.{ext}')
                msg.image = data
                msg.save()
            except Exception as e:
                print(f"Error saving image: {e}")

        # Retrieve History (Same as before)
        history = [{'role': msg.role, 'content': msg.content} for msg in session.messages.all().order_by('created_at')[:10]]

        def event_stream():
            yield json.dumps({'session_id': session_id}) + "\n"
            full_response = ""
            
            # Use get_korbi_response_stream (Make sure to import it!)
            for chunk in get_korbi_response_stream(user_message, history, image_data):
                full_response += chunk
                yield chunk
            
            # Save Assistant Response
            ChatMessage.objects.create(session=session, role='assistant', content=full_response)
            session.updated_at = timezone.now()
            session.save()

        return StreamingHttpResponse(event_stream(), content_type='text/event-stream')

@login_required
def get_chat_sessions(request):
    sessions = ChatSession.objects.filter(user=request.user, is_active=True).order_by('-updated_at')
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
def delete_chat_session(request, session_id):
    if request.method == "POST":
        
        session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)
        
        session.is_active = False
        session.save()
        
        return JsonResponse({'status': 'success', 'message': 'Chat deleted successfully'})
    return JsonResponse({'error': 'Invalid method'}, status=400)

@login_required
def get_session_messages(request, session_id):
    session = get_object_or_404(ChatSession, session_id=session_id, user=request.user)
    messages_data = [
        {
            'role': msg.role, 
            'content': msg.content,
            'image_url': msg.image.url if msg.image else None # SEND IMAGE URL TO FRONTEND
        } 
        for msg in session.messages.all()
    ]
    return JsonResponse({'messages': messages_data})

def signup(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log user in immediately
            return redirect('home')
    else:
        form = UserCreationForm()
    return render(request, 'registration/signup.html', {'form': form})