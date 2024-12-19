from django.urls import path
from . import views

from .views import post_detail, redirect_to_slug

urlpatterns = [
    path("", views.index, name="index"),
    path("login", views.login_view, name="login"),
    path("logout", views.logout_view, name="logout"),
    path("register", views.register, name="register"),
    path('profile/<str:username>/', views.profile, name='profile'),
    path('write/', views.write_post, name='write_post'),
    path('story/', views.story, name='story'),
    path('post/<slug:slug>/', post_detail, name='post_detail'),
    path('post/<int:post_id>/delete/', views.delete_post, name='delete_post'),
    path('post/<slug:slug>/delete_comment/<int:comment_id>/', views.delete_comment, name='delete_comment'),
    path('like/<int:post_id>/', views.like_post, name='like_post'),
    path('post/<slug:slug>/add_comment/', views.add_comment, name='add_comment'),
    path('post/<slug:slug>/comment/<int:comment_id>/reply/', views.add_reply, name='add_reply'),
    path('follow/<str:username>/', views.follow_user, name='follow_user'),
    path('profile/<str:username>/connections/', views.followers_and_following_list, name='followers_following_list'),
    path('chats/<int:chat_id>/', views.chat_detail, name='chat_detail'),
    path('chats/', views.chat_list, name='chat_list'),
    path('chat/delete/<int:chat_id>/', views.delete_chat, name='delete_chat'),
    path('post/<int:id>/', redirect_to_slug, name='redirect_to_slug'),
    path('post/<slug:slug>/edit/', views.edit_post, name='edit_post'),  # Uncomment this line
    path('notifications/', views.notifications, name='notifications'),
    path('notifications/unread/', views.unread_notifications, name='unread_notifications'),
    path('notifications/mark-read/<int:notification_id>/', views.mark_notification_read, name='mark_notification_read'),
]
