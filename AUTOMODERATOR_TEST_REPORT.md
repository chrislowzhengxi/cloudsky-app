# CloudySky Automoderator – Test Summary

## Overview

The automoderator is a standalone Python script that logs in as an admin, fetches the CloudySky feed, scans content for banned terms, and hides any violating posts or comments using the existing moderation endpoints. It does not modify the Django codebase and interacts with the app only through HTTP requests.

---

## Setup

1. Apply migrations:
```

python manage.py migrate

````

2. Ensure an admin user exists:
```python
from django.contrib.auth.models import User
User.objects.create_superuser("admin", "admin@test.com", "admin")
````

3. Create a regular user and a small set of test posts/comments (some clean, some containing banned terms such as “spam”, “harassment”, or “abuse”).
   This ensures the automoderator has both positive and negative cases to process.

4. Start the development server:

   ```
   python manage.py runserver 0.0.0.0:8000
   ```

---

## Running the Automoderator

In a separate terminal:

```
python automoderator.py --url http://localhost:8000 --username admin --password admin
```

The script will:

* authenticate as the admin user,
* fetch the entire feed,
* detect content containing any banned terms,
* call the appropriate hide endpoints, and
* print a short report showing what was scanned and what was hidden.

A typical run hides three of the four sample posts and several comments, matching the banned terms included in the test data.

---

## Verifying Results

### Database

You can quickly confirm which items were hidden by checking the `is_hidden` and `moderation_reason` fields:

```python
from app.models import Post, Comment
Post.objects.values("id", "is_hidden", "moderation_reason")
Comment.objects.values("id", "is_hidden", "moderation_reason")
```

Hidden items should show the reason inserted by the automoderator.

### Access Control

* **Admin users** should see all posts and comments, including hidden items.
* **Regular users** should only see content that is not hidden.

Testing this with two sessions (admin and regular user) confirms that the suppression logic behaves as expected.

---

## Customizing the Script

* Update banned terms by editing the `BANLIST` list.
* Update server URL, credentials, and timeouts in the `SETTINGS` dictionary.
* The checking functions can be extended to include more advanced logic if needed.

---

## Summary

The automoderator successfully:

* logs in using session authentication,
* retrieves the feed,
* identifies violating content,
* records suppression reasons, and
* respects the visibility rules for different user types.

This optional tool demonstrates how CloudySky's API supports automated moderation workflows while remaining fully separate from the core application.

