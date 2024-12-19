from django.contrib import admin
from .models import Post, Comment, Like, Follow, User, Chat, Message, PostMedia  # Import your models


class PostAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("title",)}

admin.site.register(Post, PostAdmin)
admin.site.register(Comment)
admin.site.register(Like)
admin.site.register(Follow)
admin.site.register(User)
admin.site.register(Chat)
admin.site.register(Message)
admin.site.register(PostMedia)
