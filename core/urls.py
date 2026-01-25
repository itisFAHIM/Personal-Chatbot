from django.contrib import admin
from django.urls import path, include
from django.urls import path
from agent.views import chat_home, chat_api, trigger_indexing, get_chat_sessions, get_session_messages, delete_chat_session

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static



urlpatterns = [
    path('admin/', admin.site.urls),
    path('', chat_home, name='home'),
    path('accounts/', include('django.contrib.auth.urls')),
    path('api/chat/', chat_api, name='chat_api'),
    path('api/sessions/', get_chat_sessions, name='get_chat_sessions'),
    path('api/sessions/<uuid:session_id>/', get_session_messages, name='get_session_messages'),
    path('api/sessions/<uuid:session_id>/delete/', delete_chat_session, name='delete_chat_session'),
    path('api/index-codebase/', trigger_indexing, name='trigger_indexing'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)