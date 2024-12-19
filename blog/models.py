from django.db import models
from django.contrib.auth.models import AbstractUser
from .utils import resize_image, validate_video_size
from django.utils.text import slugify

class User(AbstractUser):
    descr = models.TextField(blank=True, null=True)  # Optional bio field
    avatar = models.ImageField(upload_to='images/avatar', blank=True, null=True)  # Optional profile picture
    location = models.CharField(max_length=100, blank=True, null=True)  # Optional location field
    join_date = models.DateTimeField(auto_now_add=True)  # Track when the user joined

    def __str__(self):
        return self.username
    
class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    title = models.CharField(max_length=255, blank=True, null=True)
    content = models.TextField(blank=True, null=True) 
    slug = models.SlugField(unique=True, max_length=255, null=True)
    created_at = models.DateTimeField(auto_now_add=True,  db_index=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


    def __str__(self):
        return self.title
    
    # def save(self, *args, **kwargs):
    #     # Save the post first to access the file paths
    #     super().save(*args, **kwargs)

    #     # Resize image if present
    #     if self.images:
    #         resize_image(self.images.path, max_width=200, max_height=100)

    #     # Validate video size
    #     if self.videos:
    #         validate_video_size(self.videos)


 

    
class Like(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)

    
class Comment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name="replies")
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # def save(self, *args, **kwargs):
    #     # Save the comment first to access the file paths
    #     super().save(*args, **kwargs)

    #     # Resize image if present
    #     if self.images:
    #         resize_image(self.image.path, max_width=200, max_height=100)

    #     # Validate video size
    #     if self.videos:
    #         validate_video_size(self.video)



class Follow(models.Model):
    user = models.ForeignKey(User, related_name= 'following', on_delete=models.CASCADE)
    followed_user = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)



class Chat(models.Model):
    participants = models.ManyToManyField(User, related_name='chats')
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Chat between: {', '.join([user.username for user in self.participants.all()])}"

class Message(models.Model):
    chat = models.ForeignKey(Chat, related_name='messages', on_delete=models.CASCADE)
    sender = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField(blank=True, null=True)
    image = models.ImageField(upload_to='chat/images/', blank=True, null=True)
    video = models.FileField(upload_to='chat/videos/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)


class PostMedia(models.Model):
    post = models.ForeignKey(Post, related_name='media', null=True, blank=True, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, related_name='media', null=True, blank=True, on_delete=models.CASCADE)
    file = models.FileField(upload_to='post_media/')
    file_type = models.CharField(max_length=10, choices=[('image', 'Image'), ('video', 'Video')])

class Notification(models.Model):
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='notifications')
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_notifications')
    content = models.CharField(max_length=255)
    url = models.URLField()  # Link to the related resource
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification for {self.recipient.username} from {self.sender.username}"



