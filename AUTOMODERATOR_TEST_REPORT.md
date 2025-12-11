````markdown
# CloudySky Automoderator – Test Report and Verification Guide

## Overview

This document describes how to set up test data, run the automoderator script, and verify that it correctly hides violating content and respects access control in the CloudySky application.

---

## Part 1: Setup

### Prerequisites

- CloudySky Django project
- Python 3.8+ with `requests` installed
- Django dev server running on `http://localhost:8000`

### Step 1: Apply Migrations

```bash
cd /path/to/project2-yacl/cloudysky
python manage.py migrate --no-input
````

Expected output (or similar):

```text
Operations to perform:
  Apply all migrations: admin, app, auth, contenttypes, sessions
Running migrations:
  No migrations to apply.
```

### Step 2: Create Admin User

```bash
cd /path/to/project2-yacl/cloudysky
python manage.py shell << 'EOF'
from django.contrib.auth.models import User

if User.objects.filter(username='admin').exists():
    print("Admin user already exists")
else:
    User.objects.create_superuser('admin', 'admin@test.com', 'admin')
    print("Admin user created")
EOF
```

Example output:

```text
11 objects imported automatically (use -v 2 for details)
Admin user created
```

(or `Admin user already exists` on later runs)

### Step 3: Create Test Data

```bash
cd /path/to/project2-yacl/cloudysky
python manage.py shell << 'EOF'
from django.contrib.auth.models import User
from app.models import Post, Comment

admin_user = User.objects.get(username='admin')
regular_user, created = User.objects.get_or_create(
    username='testuser',
    defaults={'email': 'test@test.com', 'is_staff': False}
)
if created:
    regular_user.set_password('testpass')
    regular_user.save()

Post.objects.all().delete()
Comment.objects.all().delete()

posts = [
    {
        'author': admin_user,
        'title': 'Clean Post About Technology',
        'content': 'This is a clean post discussing modern web frameworks and best practices.',
    },
    {
        'author': regular_user,
        'title': 'Spam Alert',
        'content': 'This post contains spam and should be hidden by the automoderator.',
    },
    {
        'author': admin_user,
        'title': 'Community Harassment Discussion',
        'content': 'We need to discuss online harassment and how to prevent it.',
    },
    {
        'author': regular_user,
        'title': 'Abuse Report',
        'content': 'This is inappropriate and contains abuse that violates our rules.',
    },
]

created_posts = []
for post_data in posts:
    post = Post.objects.create(**post_data)
    created_posts.append(post)
    print(f"Created post {post.id}: {post.title}")

comments = [
    {
        'post': created_posts[0],
        'author': regular_user,
        'content': 'Great article! I agree with your points about frameworks.',
    },
    {
        'post': created_posts[0],
        'author': admin_user,
        'content': 'This comment contains harassment and should be removed.',
    },
    {
        'post': created_posts[1],
        'author': admin_user,
        'content': 'This is spam marketing content that should be hidden.',
    },
    {
        'post': created_posts[2],
        'author': regular_user,
        'content': 'I found this abuse in the forums - it needs removal.',
    },
]

for comment_data in comments:
    comment = Comment.objects.create(**comment_data)
    print(f"Created comment {comment.id} on post {comment.post.id}: {comment.content[:50]}...")

print("\nAll test data created successfully")
EOF
```

Example output (IDs may differ):

```text
Created post 2: Clean Post About Technology
Created post 3: Spam Alert
Created post 4: Community Harassment Discussion
Created post 5: Abuse Report
Created comment 2 on post 2: Great article! I agree with your points about fram...
Created comment 3 on post 2: This comment contains harassment and should be rem...
Created comment 4 on post 3: This is spam marketing content that should be hidd...
Created comment 5 on post 4: I found this abuse in the forums - it needs remova...

All test data created successfully
```

### Step 4: Start Django Development Server

```bash
cd /path/to/project2-yacl/cloudysky
python manage.py runserver 0.0.0.0:8000
```

---

## Part 2: Running the Automoderator

In a separate terminal:

```bash
cd /path/to/project2-yacl
python automoderator.py --url http://localhost:8000 --username admin --password admin
```

Example console output:

```text
======================================================================
CloudySky Automoderator
======================================================================
Server: http://localhost:8000
User: admin
Banlist size: 5 term(s)

[*] Logging in...
[+] Login successful

[*] Starting moderation scan...
[*] Fetching feed...
[*] Feed contains 4 posts
[!] Hiding post 5 by testuser: Contains banned word/phrase: 'abuse'
[!] Hiding post 4 by admin: Contains banned word/phrase: 'harassment'
[!] Hiding comment 5 by testuser: Contains banned word/phrase: 'abuse'
[!] Hiding post 3 by testuser: Contains banned word/phrase: 'spam'
[!] Hiding comment 4 by admin: Contains banned word/phrase: 'spam'
[!] Hiding comment 3 by admin: Contains banned word/phrase: 'harassment'

======================================================================
MODERATION SUMMARY
======================================================================
STATISTICS:
  Posts scanned:       4
  Posts hidden:        3
  Comments scanned:    4
  Comments hidden:     3
...
======================================================================
```

---

## Part 3: Verification

### A. Database Status

```bash
cd /path/to/project2-yacl/cloudysky
python manage.py shell << 'EOF'
from app.models import Post, Comment

print("=" * 70)
print("VERIFICATION: Hidden Content Status in Database")
print("=" * 70)

print("\nPOSTS:")
for post in Post.objects.all().order_by('id'):
    hidden_status = "HIDDEN" if getattr(post, "is_hidden", False) else "VISIBLE"
    mod_reason = f" (Reason: {post.moderation_reason})" if getattr(post, "moderation_reason", None) else ""
    print(f"  Post {post.id}: {post.title}")
    print(f"    Status: {hidden_status}{mod_reason}")
    print(f"    Author: {post.author.username}")
    print()

print("\nCOMMENTS:")
for comment in Comment.objects.all().order_by('id'):
    hidden_status = "HIDDEN" if getattr(comment, "is_hidden", False) else "VISIBLE"
    mod_reason = f" (Reason: {comment.moderation_reason})" if getattr(comment, "moderation_reason", None) else ""
    print(f"  Comment {comment.id}: {comment.content[:40]}...")
    print(f"    Status: {hidden_status}{mod_reason}")
    print(f"    Author: {comment.author.username}")
    print(f"    On Post: {comment.post.id}")
    print()

hidden_posts = Post.objects.filter(is_hidden=True).count()
total_posts = Post.objects.count()
hidden_comments = Comment.objects.filter(is_hidden=True).count()
total_comments = Comment.objects.count()

print("=" * 70)
print("SUMMARY")
print("=" * 70)
print(f"Posts: {hidden_posts}/{total_posts} hidden")
print(f"Comments: {hidden_comments}/{total_comments} hidden")
EOF
```

You should see 3 of 4 posts hidden and 3 of 4 comments hidden, with reasons matching the banned terms.

### B. Access Control (Admin vs Regular User)

```bash
cd /path/to/project2-yacl && python << 'EOF'
import requests

session_admin = requests.Session()
session_user = requests.Session()

login_url = 'http://localhost:8000/accounts/login/'

print("=" * 70)
print("ADMIN SESSION")
print("=" * 70)

resp = session_admin.get(login_url)
csrf_token = session_admin.cookies.get('csrftoken')
session_admin.post(login_url, data={'username': 'admin', 'password': 'admin', 'csrfmiddlewaretoken': csrf_token})
admin_feed = session_admin.get('http://localhost:8000/app/dumpFeed/').json()

print(f"\nAdmin sees {len(admin_feed)} posts total\n")
for post in admin_feed:
    print(f"  Post {post['id']}: {post['title']}")
    if post.get('comments'):
        for comment in post['comments']:
            print(f"    Comment {comment['id']}: {comment['content'][:40]}...")

print("\n" + "=" * 70)
print("REGULAR USER SESSION (testuser)")
print("=" * 70)

resp = session_user.get(login_url)
csrf_token = session_user.cookies.get('csrftoken')
session_user.post(login_url, data={'username': 'testuser', 'password': 'testpass', 'csrfmiddlewaretoken': csrf_token})
user_feed = session_user.get('http://localhost:8000/app/dumpFeed/').json()

print(f"\nRegular user sees {len(user_feed)} posts\n")
for post in user_feed:
    print(f"  Post {post['id']}: {post['title']}")
    if post.get('comments'):
        for comment in post['comments']:
            print(f"    Comment {comment['id']}: {comment['content'][:40]}...")
EOF
```

Expected behavior:

* Admin sees all posts and comments, including hidden ones.
* Regular user should only see the clean post and its clean comment.

---

## Part 4: Customizing the Automoderator

### Banlist

In `automoderator.py`:

```python
BANLIST = [
    "spam",
    "abuse",
    "harassment",
    "inappropriate",
    "banned",
]
```

You can add more terms as needed.

### Server Settings

Also in `automoderator.py`:

```python
SETTINGS = {
    "base_url": "http://localhost:8000",
    "admin_username": "admin",
    "admin_password": "admin",
    "timeout": 10,
}
```

Update these if you deploy elsewhere.

---

## Summary

This test flow:

* sets up an admin and test user,
* creates a mix of clean and violating posts/comments,
* runs the automoderator script,
* verifies that violating content is hidden with reasons recorded, and
* confirms that admins see all content while regular users do not see hidden items.

```
```
