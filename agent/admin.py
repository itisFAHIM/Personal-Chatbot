from django.contrib import admin
from .models import ChatSession, ChatMessage


class ChatMessageInline(admin.TabularInline):
    model = ChatMessage
    extra = 0  # Don't show empty rows
    readonly_fields = ('role', 'content', 'created_at') 
    can_delete = False 

@admin.register(ChatSession)
class ChatSessionAdmin(admin.ModelAdmin):

    list_display = ('title', 'user', 'created_at', 'is_active')
    
    list_filter = ('is_active', 'created_at', 'user')
    

    search_fields = ('title', 'user__username', 'session_id')
    

    inlines = [ChatMessageInline]
    
   
    def get_queryset(self, request):
       
        return super().get_queryset(request)


@admin.register(ChatMessage)
class ChatMessageAdmin(admin.ModelAdmin):
    list_display = ('session', 'role', 'short_content', 'created_at')
    list_filter = ('role', 'created_at')
    
    def short_content(self, obj):
        return obj.content[:50] + "..." if len(obj.content) > 50 else obj.content