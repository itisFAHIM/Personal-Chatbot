from django.contrib import admin
from django.urls import path, include
from agent.views import chat_home, chat_api, get_chat_sessions, get_session_messages
from django.urls import path
from agent.views import chat_home, chat_api, trigger_indexing, get_chat_sessions, get_session_messages, delete_chat_session


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', chat_home, name='chat_home'),
    path('api/chat/', chat_api, name='chat_api'),
    path('api/sessions/', get_chat_sessions, name='get_sessions'),
    path('api/sessions/<uuid:session_id>/', get_session_messages, name='get_session_messages'),
    
    path('accounts/', include('accounts.urls')),  
    path('api/index-codebase/', trigger_indexing, name='trigger_indexing'),

    path('api/sessions/<uuid:session_id>/delete/', delete_chat_session, name='delete_chat_session'),
]