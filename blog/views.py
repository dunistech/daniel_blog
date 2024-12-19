from django.contrib.auth import authenticate, login, logout
from django.db import IntegrityError
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse

from django.shortcuts import render, redirect, get_object_or_404
from .models import User, Post, Like, Comment, Follow, Chat, Message, PostMedia, Notification
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.http import JsonResponse
import traceback
from datetime import datetime
from django.contrib import messages
from django.db.models import Count
from PIL import Image
from django.db import transaction
from django.db.models import Count
from django.template.loader import render_to_string
from django.db.models import Q
from django.db.models import Max
from django.utils.text import slugify
from .utils import create_notification
import json
import logging
logger = logging.getLogger(__name__)
from django.core.paginator import EmptyPage






def index(request):
   return render(request, "blog/index.html")


def login_view(request):
    if request.method == "POST":

       
        username = request.POST["username"]
        password = request.POST["password"]
        user = authenticate(request, username=username, password=password)

     
        if user is not None:
            login(request, user)
            return HttpResponseRedirect(reverse("story"))
        else:
            return render(request, "blog/login.html", {
                "message": "Invalid username and/or password."
            })
    else:
        return render(request, "blog/login.html")


def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse("index"))


def register(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]

      
        password = request.POST["password"]
        confirmation = request.POST["confirmation"]
        if password != confirmation:
            return render(request, "blog/register.html", {
                "message": "Passwords must match."
            })

     
        try:
            user = User.objects.create_user(username, email, password)
            user.save()
        except IntegrityError:
            return render(request, "blog/register.html", {
                "message": "Username already taken."
            })
        login(request, user)
        return HttpResponseRedirect(reverse("index"))
    else:
        return render(request, "blog/register.html")
    

 
@login_required
def profile(request, username):
    profile_user = get_object_or_404(User, username=username)
    following = Follow.objects.filter(user=request.user, followed_user=profile_user).exists()
    post_id = request.GET.get('post_id')

    follower_count = profile_user.followers.count()
    following_count = profile_user.following.count()

    notifications = request.user.notifications.filter(is_read=False)
    unread_notifications = notifications.filter(is_read=False)  # Filter unread notifications

    # Handle profile update form submission
    if request.method == 'POST' and request.user == profile_user:
        profile_user.avatar = request.FILES.get('avatar') or profile_user.avatar
        profile_user.descr = request.POST.get('descr')
        profile_user.location = request.POST.get('location')
        profile_user.save()
        return redirect('profile', username=username)

    # If post_id is provided, display only that post
    if post_id:
        post = get_object_or_404(Post, id=post_id, user=profile_user)
        posts = [post]
        page_obj = None
    else:
        posts = Post.objects.filter(user=profile_user).order_by('-created_at')
        paginator = Paginator(posts, 4)
        page_number = request.GET.get('page')
        page_obj = paginator.get_page(page_number)

    # Ensure there is a chat for the user and the profile user
    if request.user != profile_user:
        chat = Chat.objects.filter(participants=request.user).filter(participants=profile_user).first()
        if not chat:
            chat = Chat.objects.create()
            chat.participants.add(request.user, profile_user)
    else:
        chat = None

    # Fetch liked posts by the user (including user posts and other users' posts)
    liked_posts = Post.objects.filter(like__user=request.user).order_by('-created_at')
    liked_posts_paginator = Paginator(liked_posts, 4)
    liked_posts_page_number = request.GET.get('likes_page')
    liked_posts_page_obj = liked_posts_paginator.get_page(liked_posts_page_number)

    # Fetch replies (comments) for all posts that the user has replied to
    replied_posts = Post.objects.filter(comments__user=request.user).distinct().order_by('-created_at')
    replies_paginator = Paginator(replied_posts, 4)
    replies_page_number = request.GET.get('replies_page')
    replies_page_obj = replies_paginator.get_page(replies_page_number)

    return render(request, 'blog/profile.html', {
        'profile_user': profile_user,
        'posts': posts,
        'page_obj': page_obj,
        'single_post': bool(post_id),
        'following': following,
        'follower_count': follower_count,
        'following_count': following_count,
        'chat': chat,
        'liked_posts_page_obj': liked_posts_page_obj, 
        'replies_page_obj': replies_page_obj, 
        'notifications': notifications,
        'unread_notifications': unread_notifications
    })

@login_required
def write_post(request):
    notifications = request.user.notifications.filter(is_read=False)

    if request.method == 'POST':
        title = request.POST.get('title', '').strip()  # Get title
        content = request.POST.get('content', '').strip()  # Get content
        images = request.FILES.getlist('images')  # Get image files
        videos = request.FILES.getlist('videos')  # Get video files

        # Validation: Check if we have title or files (images/videos)
        if not title and not (images or videos):
            return render(request, 'blog/write_post.html', {
                'error': 'You must provide at least a title or upload images/videos.',
                'notifications': notifications,
            })

        # Generate slug only if title is provided
        slug = None
        if title:
            base_slug = slugify(title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1

        # Start a transaction to ensure data integrity
        with transaction.atomic():
            # Create the post with or without content
            post = Post.objects.create(
                user=request.user,
                title=title,
                content=content or "",  # Use empty string if content is not provided
                slug=slug  # Use the generated slug
            )

            # Save images if any
            for image in images:
                PostMedia.objects.create(post=post, file=image, file_type='image')

            # Save videos if any
            for video in videos:
                PostMedia.objects.create(post=post, file=video, file_type='video')

            # Notify followers about the new post
            followers = Follow.objects.filter(followed_user=request.user)
            for follower in followers:
                create_notification(
                    recipient=follower.user,
                    sender=request.user,
                    content=f"{request.user.username} created a new post.",
                    url=f"/post/{post.slug or post.id}/",  # Use slug or fallback to id
                )

        # Redirect to story page after creating post
        return redirect('story')

    # Render the write post page
    return render(request, 'blog/write_post.html', {
        'notifications': notifications
    })

    # return render(request, 'blog/write_post.html')


@login_required
def edit_post(request, slug):
    post = get_object_or_404(Post, slug=slug)

    # Ensure the user is the one who created the post
    if post.user != request.user:
        messages.error(request, "You are not authorized to edit this post.")
        return redirect('story')

    if request.method == 'POST':
        # Update title and content
        post.title = request.POST['title']
        post.content = request.POST['content']
        post.save()

        # Handle file removal (if checked in the form)
        remove_images = request.POST.getlist('remove_images')
        remove_videos = request.POST.getlist('remove_videos')

        # Delete selected images and videos
        post.media.filter(id__in=remove_images, file_type='image').delete()
        post.media.filter(id__in=remove_videos, file_type='video').delete()

        # Handle new media uploads (images and videos)
        images = request.FILES.getlist('images')
        videos = request.FILES.getlist('videos')
        for image in images:
            PostMedia.objects.create(post=post, file=image, file_type='image')
        for video in videos:
            PostMedia.objects.create(post=post, file=video, file_type='video')

        messages.success(request, "Post updated successfully.")
        return redirect('post_detail', slug=post.slug)

    # Pass 'is_editing' to the template
    return render(request, 'blog/write_post.html', {'post': post, 'is_editing': True})



@login_required
def story(request):
    posts = Post.objects.annotate(comment_count=Count('comments')).order_by('-created_at')
    paginator = Paginator(posts, 6)
    page_number = request.GET.get('page', 1)

    try:
        page_obj = paginator.page(page_number)
    except EmptyPage:  # If the page doesn't exist
        return JsonResponse({'html': ''})  # Return empty HTML for AJAX

    if request.headers.get('x-requested-with') == 'XMLHttpRequest':  # AJAX request
        html = render_to_string('blog/partials/posts.html', {'page_obj': page_obj})
        return JsonResponse({'html': html})

    notifications = Notification.objects.filter(recipient=request.user, is_read=False).order_by('-timestamp')
    unread_notifications = notifications.filter(is_read=False)  # Filter unread notifications


    return render(request, 'blog/story.html', {
        'page_obj': page_obj,
        'notifications': notifications,
        'unread_notifications': unread_notifications
        
    })


@login_required
def post_detail(request, slug):
    # Get the post and annotate it with comment count
    post = get_object_or_404(Post.objects.annotate(comment_count=Count('comments')), slug=slug)

    # Get top-level comments, ordered by most recent first
    top_level_comments = post.comments.filter(parent__isnull=True).order_by('-created_at')

    # Check if the logged-in user is following the post author
    following = Follow.objects.filter(user=request.user, followed_user=post.user).exists()

    # Fetch unread notifications for the logged-in user
    notifications = request.user.notifications.filter(is_read=False).order_by('-timestamp')
    unread_notifications = notifications.filter(is_read=False)

    # Mark all notifications as read
    for notification in notifications:
        notification.is_read = True
        notification.save()

    context = {
        'post': post,
        'top_level_comments': top_level_comments,
        'liked_by_user': post.like_set.filter(user=request.user).exists() if request.user.is_authenticated else False,
        'following': following,
        'notifications': notifications,
        'unread_notifications': unread_notifications,
    }

    return render(request, 'blog/post_detail.html', context)


@login_required
def redirect_to_slug(request, id):
    print(f"Received request for post with ID: {id}")  # Debugging to check the ID value
    
    # Ensure the ID is passed correctly and a Post exists
    try:
        post = get_object_or_404(Post, id=id)
        print(f"Redirecting to post with slug: {post.slug}")  # Debugging to check the slug
        return redirect('post_detail', slug=post.slug)  # Redirect to the slug-based URL
    except Post.DoesNotExist:
        print("Post not found")
        return redirect('home') 
       
@login_required
def delete_post(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    if post.user == request.user:
        post.delete()
        messages.success(request, "Post deleted successfully.")
        next_page = request.GET.get('next')
        if next_page == 'profile':
            return redirect('profile', username=request.user.username)
        return redirect('story')
    else:
        messages.error(request, "You are not authorized to delete this post.")
        return redirect('story')


@login_required
def delete_comment(request, slug, comment_id):
    # Fetch the comment by its ID (not slug)
    comment = get_object_or_404(Comment, id=comment_id)

    # Check if the logged-in user is the author of the comment
    if comment.user == request.user:
        # Deleting the comment or reply
        comment.delete()
        messages.success(request, "Comment deleted successfully.")
        
        # Determine the next page to redirect to
        next_page = request.GET.get('next', 'post_detail')
        
        if next_page == 'post_detail':
            return redirect('post_detail', slug=comment.post.slug)
        elif next_page == 'profile':
            return redirect('profile', username=request.user.username)
        else:
            # Default to post_detail if 'next' query parameter is missing or invalid
            return redirect('post_detail', slug=comment.post.slug)
    else:
        # User is not authorized to delete the comment
        messages.error(request, "You are not authorized to delete this comment.")
        return redirect('post_detail', slug=comment.post.slug)




@login_required
def like_post(request, post_id):
    if request.method == 'POST':
        post = Post.objects.get(id=post_id)
        user = request.user

        try:
            # Check if the user already liked the post
            like = Like.objects.get(user=user, post=post)
            like.delete()  # Remove the like
            liked = False
        except Like.DoesNotExist:
            # If the user hasn't liked the post, create the like
            Like.objects.create(user=user, post=post)
            liked = True

        # Get the count of likes for the post
        likes_count = post.like_set.count()

        # Notify the post author when someone likes their post
        if liked:
            create_notification(
                recipient=post.user,
                sender=user,
                content=f"{user.username} liked your post: {post.title}",
                url=f"/post/{post.slug}/",  # URL to the post
            )

        return JsonResponse({
            'success': True,
            'liked': liked,
            'likes_count': likes_count,
        })

    return JsonResponse({'success': False})



@login_required
def add_comment(request, slug):
    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        images = request.FILES.getlist('images') 
        videos = request.FILES.getlist('videos') 

        # Ensure at least one of content, images, or videos is provided
        if not content and not images and not videos:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest':  
                return JsonResponse({'success': False, 'error': 'Comment content or media is required.'})
            else:
                messages.error(request, 'Comment content or media is required.')
                return redirect('post_detail', slug=slug)

        post = get_object_or_404(Post, slug=slug)
        try:
            # Create the comment
            comment = Comment.objects.create(post=post, user=request.user, content=content)

            # Notify the post author that someone commented on their post
            create_notification(
                recipient=post.user,
                sender=request.user,
                content=f"{request.user.username} commented on your post: {post.title}",
                url=f"/post/{post.slug}/",
            )

            # Save image uploads
            for image in images:
                PostMedia.objects.create(
                    comment=comment,
                    file=image,
                    file_type='image',
                )

            # Save video uploads
            for video in videos:
                PostMedia.objects.create(
                    comment=comment,
                    file=video,
                    file_type='video',
                )

            if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
                return JsonResponse({
                    'success': True,
                    'comment': {
                        'id': comment.id,
                        'content': comment.content,
                        'username': comment.user.username,
                        'created_at': comment.created_at.strftime('%Y-%m-%d %H:%M:%S'),
                    }
                })
            else:
                messages.success(request, 'Your comment was added successfully!')
                return redirect('post_detail', slug=slug)

        except Exception:
            if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
                return JsonResponse({'success': False, 'error': 'An error occurred while saving the comment.'})
            else:
                messages.error(request, 'An error occurred while saving the comment.')
                return redirect('post_detail', slug=slug)

    # Handle invalid request methods
    if request.headers.get('x-requested-with') == 'XMLHttpRequest': 
        return JsonResponse({'success': False, 'error': 'Invalid request method.'})
    else:
        messages.error(request, 'Invalid request method.')
        return redirect('post_detail', slug=slug)

  

@login_required
def add_reply(request, slug, comment_id):
    post = get_object_or_404(Post, slug=slug)
    comment = get_object_or_404(Comment, id=comment_id)

    if request.method == 'POST':
        content = request.POST.get('content', '').strip()
        image = request.FILES.get('image')
        video = request.FILES.get('video')

        if not content and not image and not video:
            messages.error(request, 'Reply content or media is required.')
            return redirect('post_detail', slug=slug)

        try:
            with transaction.atomic():
                # Create the reply
                reply = Comment.objects.create(
                    user=request.user,
                    post=post,
                    parent=comment,
                    content=content,
                )

                # Send notification to the original comment's author
                if comment.user != request.user:  # Only notify if the reply is not by the comment's author
                    create_notification(
                        recipient=comment.user,
                        sender=request.user,
                        content=f"{request.user.username} replied to your comment on {post.title}.",
                        url=f"/post/{post.slug}/#comment-{comment.id}",  # Link directly to the specific comment thread
                    )

                # Save media files if they exist
                if image:
                    PostMedia.objects.create(comment=reply, file=image, file_type='image')
                if video:
                    PostMedia.objects.create(comment=reply, file=video, file_type='video')

                messages.success(request, 'Your reply was added successfully!')

        except Exception as e:
            messages.error(request, f'An error occurred: {e}')

        return redirect('post_detail', slug=slug)




@login_required
def follow_user(request, username):
    try:
        user_to_follow = get_object_or_404(User, username=username)

        # Check if the user is trying to follow someone other than themselves
        if request.user != user_to_follow:
            # Get or create a Follow relationship
            follow, created = Follow.objects.get_or_create(user=request.user, followed_user=user_to_follow)

            # Prepare response data
            data = {
                "follow": True
            }

            if not created:
                follow.delete()  # Unfollow if already following
                data['follow'] = False
            else:
                # Send notification to the user being followed
                create_notification(
                    recipient=user_to_follow,
                    sender=request.user,
                    content=f"{request.user.username} started following you.",
                    url=f"/profile/{request.user.username}/",  # Link to the user's profile
                )

        return JsonResponse(data)

    except Exception as e:
        traceback.print_exc()
        return JsonResponse({"success": False})
       
    

def followers_and_following_list(request, username):
    profile_user = get_object_or_404(User, username=username)
    followers = Follow.objects.filter(followed_user=profile_user).select_related('user')
    following = Follow.objects.filter(user=profile_user).select_related('followed_user')
    user_following = Follow.objects.filter(user=request.user).values_list('followed_user', flat=True) if request.user.is_authenticated else []
    notifications = request.user.notifications.filter(is_read=False)
    
    context = {
        'profile_user': profile_user,
        'followers': followers,
        'following': following,
        'user_following': User.objects.filter(id__in=user_following),
        'notifications': notifications
    }
    return render(request, 'blog/followers_following.html', context)




@login_required
def chat_list(request):
    # Get all chats where the logged-in user is a participant
    chats = (
        Chat.objects.filter(participants=request.user)
        .annotate(latest_message=Max('messages__created_at'))
        .order_by('-latest_message')
    )

    notifications = request.user.notifications.filter(is_read=False)

    chat_data = []
    for chat in chats:
        # Get the other participant(s)
        other_participant = chat.participants.exclude(id=request.user.id).first()

        # Only include chats where the other participant has actually sent messages
        if chat.messages.filter(sender=other_participant).exists():
            unread_count = chat.messages.filter(sender=other_participant, is_read=False).count()

            # Mark all unread messages as read for the current participant
            chat.messages.filter(sender=other_participant, is_read=False).update(is_read=True)

            # Prepare chat data for template
            chat_data.append({
                'chat': chat,
                'other_user': other_participant.username,
                'other_user_avatar': other_participant.avatar.url if other_participant.avatar else 'path/to/default-avatar.png',
                'unread_count': unread_count,
            })

    return render(request, 'blog/chat_list.html', {'chat_data': chat_data, 'notifications': notifications})



@login_required
def chat_detail(request, chat_id):
    chat = get_object_or_404(Chat, id=chat_id, participants=request.user)
    receiver = chat.participants.exclude(id=request.user.id).first()

    if request.method == 'POST' and request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        try:
            # Handle content and files
            content = request.POST.get('content', '').strip()
            image = request.FILES.get('image')
            video = request.FILES.get('video')

            if not content and not image and not video:
                return JsonResponse({'success': False, 'error': 'Message content or file is required'}, status=400)

            # Create a new message
            new_message = Message.objects.create(
                chat=chat,
                sender=request.user,
                content=content,
                image=image,
                video=video,
            )

            # Notify the receiver
            if receiver:
                create_notification(
                    recipient=receiver,
                    sender=request.user,
                    content=f"{request.user.username} sent you a message.",
                    url=reverse('chat_detail', args=[chat.id]),
                )

            # Prepare response
            message_data = {
                'sender': request.user.username,
                'content': new_message.content,
                'image': new_message.image.url if new_message.image else None,
                'video': new_message.video.url if new_message.video else None,
                'timestamp': new_message.created_at.strftime('%b %d, %Y %I:%M %p'),
            }

            return JsonResponse({'success': True, 'message': message_data})

        except Exception as e:
            return JsonResponse({'success': False, 'error': str(e)}, status=500)

    # Handle GET request
    messages = chat.messages.order_by('created_at')
    return render(request, 'blog/chat_detail.html', {
        'chat': chat,
        'messages': messages,
        'receiver': receiver,
    })






def delete_chat(request, chat_id):
    chat = Chat.objects.filter(id=chat_id, participants=request.user).first()
    if chat:
        chat.participants.remove(request.user)  # Remove user from the chat
        if not chat.participants.exists():     # If no participants left, delete chat
            chat.delete()
    return redirect('chat_list')

@login_required
def notifications(request):
    notifications = request.user.notifications.order_by('-timestamp')
    return render(request, 'notifications.html', {'notifications': notifications})


@login_required
def unread_notifications(request):
    unread_count = request.user.notifications.filter(is_read=False).count()
    return JsonResponse({'unread_count': unread_count})

@login_required
def mark_notification_read(request, notification_id):
    # Get the notification that the user clicked on
    notification = get_object_or_404(request.user.notifications, id=notification_id)

    # Only mark the notification as read
    notification.is_read = True
    notification.save()

    return JsonResponse({"status": "success"})



