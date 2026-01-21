# from django.db import models
# from django.contrib.auth.models import User
# import uuid

# class ChatSession(models.Model):
#     user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')

#     session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
#     title = models.CharField(max_length=200, default="New Chat")
#     created_at = models.DateTimeField(auto_now_add=True)
#     updated_at = models.DateTimeField(auto_now=True)
    
#     class Meta:
#         ordering = ['-updated_at']
    
#     def __str__(self):
#         return f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

# class ChatMessage(models.Model):
#     session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
#     role = models.CharField(max_length=20)   
#     content = models.TextField()
#     created_at = models.DateTimeField(auto_now_add=True)
    
#     class Meta:
#         ordering = ['created_at']
    
#     def __str__(self):
#         return f"{self.role}: {self.content[:50]}"
    
from django.db import models
from django.contrib.auth.models import User
import uuid

class ChatSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='chat_sessions')
    session_id = models.UUIDField(default=uuid.uuid4, unique=True, editable=False)
    title = models.CharField(max_length=200, default="New Chat")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # Controls visibility Field
    is_active = models.BooleanField(default=True) 

    class Meta:
        ordering = ['-updated_at']
    
    def __str__(self):
        return f"{self.title} - {self.created_at.strftime('%Y-%m-%d %H:%M')}"

class ChatMessage(models.Model):
    session = models.ForeignKey(ChatSession, on_delete=models.CASCADE, related_name='messages')
    role = models.CharField(max_length=20)   
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['created_at']
    
    def __str__(self):
        return f"{self.role}: {self.content[:50]}"