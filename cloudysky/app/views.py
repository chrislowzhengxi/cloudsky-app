from django.shortcuts import render
from django.utils import timezone
from django.http import HttpResponse, JsonResponse
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.views.decorators.csrf import csrf_exempt


def index(request):
    """
    Render homepage with: Current time string and Access to request.user
    """
    # Use Django timezone (respects USE_TZ)
    now = timezone.localtime()
    time_str = now.strftime("%A, %B %d, %Y at %I:%M %p %Z")

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
