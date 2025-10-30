

# app/models.py
from django.conf import settings
from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType

User = settings.AUTH_USER_MODEL

class Profile(models.Model):
    class Role(models.TextChoices):
        SERF = "serf", "Serf"
        ADMIN = "admin", "Administrator"

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile")
    role = models.CharField(max_length=10, choices=Role.choices, default=Role.SERF)
    bio = models.TextField(blank=True)
    # Store avatar as a Media row too if you prefer. Keeping a direct FileField is simplest.
    avatar = models.ImageField(upload_to="avatars/", blank=True, null=True)
    avatar_bytes = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"{self.user} ({self.role})"


class ModerationReason(models.Model):
    """Vetted reasons shown in the pull-down."""
    code = models.SlugField(unique=True, max_length=50)
    label = models.CharField(max_length=200)

    def __str__(self):
        return self.label


class Post(models.Model):
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="posts")
    title = models.CharField(max_length=200)
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Suppression state
    is_suppressed = models.BooleanField(default=False)
    suppressed_at = models.DateTimeField(blank=True, null=True)
    suppressed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="suppressed_posts"
    )
    suppression_reason = models.ForeignKey(
        ModerationReason, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Cached byte totals for dashboard
    body_bytes = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"Post #{self.id} by {self.author}"


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name="comments")
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name="comments")
    body = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    # Suppression state
    is_suppressed = models.BooleanField(default=False)
    suppressed_at = models.DateTimeField(blank=True, null=True)
    suppressed_by = models.ForeignKey(
        User, on_delete=models.SET_NULL, null=True, blank=True, related_name="suppressed_comments"
    )
    suppression_reason = models.ForeignKey(
        ModerationReason, on_delete=models.SET_NULL, null=True, blank=True
    )

    # Cache for dashboard
    body_bytes = models.PositiveBigIntegerField(default=0)

    def __str__(self):
        return f"Comment #{self.id} on Post #{self.post_id}"


class ModerationAction(models.Model):
    """
    Immutable audit trail for suppress and unsuppress actions.
    """
    class Action(models.TextChoices):
        SUPPRESS = "suppress", "Suppress"
        UNSUPPRESS = "unsuppress", "Unsuppress"

    actor = models.ForeignKey(User, on_delete=models.CASCADE, related_name="moderation_actions")
    action = models.CharField(max_length=20, choices=Action.choices)

    # Generic target: Post or Comment
    target_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    target_object_id = models.PositiveIntegerField()
    target = GenericForeignKey("target_content_type", "target_object_id")

    reason = models.ForeignKey(ModerationReason, on_delete=models.SET_NULL, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)


class Media(models.Model):
    """
    Media that can belong to a Post or a Comment.
    Also usable for avatars if you want a single pipeline.
    """
    uploaded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name="media")
    file = models.FileField(upload_to="media/")
    mime_type = models.CharField(max_length=100, blank=True)
    num_bytes = models.PositiveBigIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    # Generic attachment to Post or Comment
    owner_content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    owner_object_id = models.PositiveIntegerField()
    owner = GenericForeignKey("owner_content_type", "owner_object_id")

    # Optional flags for display control
    is_inline_display_allowed = models.BooleanField(default=True)

    def __str__(self):
        return f"Media #{self.id} ({self.mime_type}, {self.num_bytes} bytes)"
