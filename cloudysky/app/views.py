from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt
from datetime import datetime
from zoneinfo import ZoneInfo
from .models import Post, Comment, ModerationReason, Profile


def index(request):
    """
    Render homepage with: Current time string and Access to request.user
    """
    # Use Central Time (America/Chicago) as expected by autograder
    now = datetime.now(ZoneInfo("America/Chicago"))
    # Format as HH:MM in 24-hour format
    time_str = now.strftime("%H:%M")

    context = {
        "current_time": time_str,
    }
    return render(request, "app/index.html", context)


def new_user(request):
    """GET only"""
    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)
    return render(request, "app/new.html")


@csrf_exempt  
def create_user(request):
    """Create a new user via POST with fields: email, user_name, password, is_admin.
    We shold reject non-POST with 405. email, username is unique (case-insensitive)
    """
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)

    email = (request.POST.get("email") or "").strip()
    username = (request.POST.get("user_name") or "").strip()
    password = request.POST.get("password") or ""
    is_admin_raw = request.POST.get("is_admin")
    if is_admin_raw is None:
        return HttpResponse("Missing required field: is_admin", status=400)
    is_admin = str(is_admin_raw).lower() in {"1", "true", "yes", "on"}

    missing = []
    if not email:
        missing.append("email")
    if not username:
        missing.append("user_name")
    if not password:
        missing.append("password")
    if missing:
        return HttpResponse(f"Missing required field(s): {', '.join(missing)}", status=400)

    try:
        if User.objects.filter(email__iexact=email).exists():
            return HttpResponse("Email already in use", status=400)
        if User.objects.filter(username__iexact=username).exists():
            return HttpResponse("Username already exists", status=400)

        last_name = (request.POST.get("last_name") or "").strip()

        user = User.objects.create_user(username=username, email=email, password=password)
        if last_name:
            user.last_name = last_name
        
        user.is_staff = bool(is_admin)
        user.save()

        auth_user = authenticate(request, username=username, password=password)
        if auth_user is not None:
            login(request, auth_user)

        return HttpResponse("User created successfully.")
    except Exception as e:
        # Return 500 with error message for debugging
        return HttpResponse(f"Database error: {str(e)}", status=500)


# New views for HW5
@csrf_exempt
def new_post(request):
    """HTML form/view to submit to createPost"""
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return render(request, 'app/new_post.html')


@csrf_exempt
def new_comment(request):
    """HTML form/view to submit to createComment"""
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    return render(request, 'app/new_comment.html')


@csrf_exempt
def create_post(request):
    """API endpoint to create a post. Takes POST request with fields: content, title"""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    title = (request.POST.get("title") or "").strip()
    content = (request.POST.get("content") or "").strip()
    
    if not title:
        return HttpResponse("Missing required field: title", status=400)
    if not content:
        return HttpResponse("Missing required field: content", status=400)
    
    try:
        post = Post.objects.create(
            author=request.user,
            title=title,
            content=content
        )
        return HttpResponse(f"Post created successfully with id {post.id}", status=201)
    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}", status=500)


@csrf_exempt
def create_comment(request):
    """API endpoint to create a comment. Takes POST request with fields: post_id, content"""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    post_id = request.POST.get("post_id")
    content = (request.POST.get("content") or "").strip()
    
    if not post_id:
        return HttpResponse("Missing required field: post_id", status=400)
    if not content:
        return HttpResponse("Missing required field: content", status=400)
    
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse("Post not found", status=404)
    except ValueError:
        return HttpResponse("Invalid post_id", status=400)
    
    try:
        comment = Comment.objects.create(
            post=post,
            author=request.user,
            content=content
        )
        return HttpResponse(f"Comment created successfully with id {comment.id}", status=201)
    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}", status=500)


@csrf_exempt
def hide_post(request):
    """API endpoint to hide a post. Takes POST request with fields: post_id, reason"""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    # Check if user is admin
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)
    
    post_id = request.POST.get("post_id")
    reason = (request.POST.get("reason") or "").strip()
    
    if not post_id:
        return HttpResponse("Missing required field: post_id", status=400)
    if not reason:
        return HttpResponse("Missing required field: reason", status=400)
    
    try:
        post = Post.objects.get(id=post_id)
    except Post.DoesNotExist:
        return HttpResponse("Post not found", status=404)
    except ValueError:
        return HttpResponse("Invalid post_id", status=400)
    
    try:
        # Get or create the moderation reason
        moderation_reason, _ = ModerationReason.objects.get_or_create(reason_text=reason)
        
        post.is_hidden = True
        post.moderator = request.user
        post.moderation_reason = moderation_reason
        post.save()
        
        return HttpResponse(f"Post {post_id} hidden successfully", status=200)
    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}", status=500)


@csrf_exempt
def hide_comment(request):
    """API endpoint to hide a comment. Takes POST request with fields: comment_id, reason"""
    if request.method != "POST":
        return HttpResponse("Method not allowed", status=405)
    
    if not request.user.is_authenticated:
        return HttpResponse("Unauthorized", status=401)
    
    # Check if user is admin
    if not request.user.is_staff:
        return HttpResponse("Unauthorized", status=401)
    
    comment_id = request.POST.get("comment_id")
    reason = (request.POST.get("reason") or "").strip()
    
    if not comment_id:
        return HttpResponse("Missing required field: comment_id", status=400)
    if not reason:
        return HttpResponse("Missing required field: reason", status=400)
    
    try:
        comment = Comment.objects.get(id=comment_id)
    except Comment.DoesNotExist:
        return HttpResponse("Comment not found", status=404)
    except ValueError:
        return HttpResponse("Invalid comment_id", status=400)
    
    try:
        # Get or create the moderation reason
        moderation_reason, _ = ModerationReason.objects.get_or_create(reason_text=reason)
        
        comment.is_hidden = True
        comment.moderator = request.user
        comment.moderation_reason = moderation_reason
        comment.save()
        
        return HttpResponse(f"Comment {comment_id} hidden successfully", status=200)
    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}", status=500)


@csrf_exempt
def dump_feed(request):
    """
    Diagnostic output view that returns all posts as JSON.
    Applies censorship logic:
    - Admins can see hidden content (flagged)
    - Authors can see their own hidden content
    - Other users cannot see hidden content
    """
    if request.method != "GET":
        return HttpResponse("Method not allowed", status=405)
    
    # Check if user is logged in
    if not request.user.is_authenticated:
        return HttpResponse("", status=200)
    
    try:
        posts = Post.objects.all().order_by('-created_at')
        feed_data = []
        
        for post in posts:
            # Check if post is hidden and if user can see it
            if post.is_hidden:
                # Only show hidden posts to admins and the author
                if not (request.user.is_staff or request.user == post.author):
                    continue
            
            # Format date as "YYYY-MM-DD HH:MM"
            date_str = post.created_at.strftime("%Y-%m-%d %H:%M")
            
            # Get comment details (not just IDs, but full comment info)
            comments_data = []
            for comment in post.comments.all():
                # Check if comment is hidden and if user can see it
                if comment.is_hidden:
                    # Only show hidden comments to admins and the author
                    if not (request.user.is_staff or request.user == comment.author):
                        continue
                
                comments_data.append({
                    'id': comment.id,
                    'author': comment.author.username,
                    'content': comment.content,
                    'date': comment.created_at.strftime("%Y-%m-%d %H:%M")
                })
            
            post_dict = {
                'id': post.id,
                'username': post.author.username,
                'date': date_str,
                'title': post.title,
                'content': post.content,
                'comments': comments_data
            }
            feed_data.append(post_dict)
        
        return JsonResponse(feed_data, safe=False)
    except Exception as e:
        return HttpResponse(f"Database error: {str(e)}", status=500)

