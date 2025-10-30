from django.db import models
from django.contrib.auth.models import User

# User + Profile 
class Profile(models.Model):
    # Instructions: Start with the UserType tables and specify those in Django.
    USER_TYPE_SERF = 'SERF'
    USER_TYPE_ADMIN = 'ADMIN'
    USER_TYPE_CHOICES = [
        (USER_TYPE_SERF, 'Serf'),
        (USER_TYPE_ADMIN, 'Administrator'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    
    user_type = models.CharField(
        max_length=10,
        choices=USER_TYPE_CHOICES,
        default=USER_TYPE_SERF
    )
    bio = models.TextField(blank=True, null=True)
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} ({self.get_user_type_display()})"

    @property
    def is_admin(self):
        return self.user_type == self.USER_TYPE_ADMIN


# Then, think about Posts and Comments and moderation. You may need multiple tables here.
# Moderation
class ModerationReason(models.Model):
    reason_text = models.CharField(max_length=255, unique=True)

    def __str__(self):
        return self.reason_text


# Post + Comment
class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    is_hidden = models.BooleanField(default=False)
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True, 
        blank=True,
        related_name='moderated_posts'
    )
    moderation_reason = models.ForeignKey(
        ModerationReason,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Post {self.id} by {self.author.username}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments')
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Same logic as Post for moderation
    is_hidden = models.BooleanField(default=False)
    moderator = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='moderated_comments'
    )
    moderation_reason = models.ForeignKey(
        ModerationReason,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    def __str__(self):
        return f"Comment by {self.author.username} on {self.post}"


# Finally think about Media, both how they will be created and uploaded.
# Media
class Media(models.Model):
    uploader = models.ForeignKey(User, on_delete=models.CASCADE, related_name='media')
    file = models.FileField(upload_to='media_attachments/')
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # A file can be attached to a post OR a comment.
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='media'
    )
    comment = models.ForeignKey(
        Comment,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        related_name='media'
    )

    def __str__(self):
        return self.file.name