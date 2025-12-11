#!/usr/bin/env python3
"""
CloudySky Automoderator
=======================

A standalone script that automatically moderates posts and comments on the CloudySky
Django social platform by scanning for banned words and hidden content violations.

Features:
- Session-based login as admin user
- Fetches feed from /api/dumpFeed endpoint
- Scans posts and comments against configurable BANLIST
- Automatically hides violating content with reason
- And, most importantly, provides detailed summary report

Usage:
    python automoderator.py [--url BASE_URL] [--username ADMIN_USER] [--password PASSWORD]

Default values can be configured in the SETTINGS dict below.
"""

import requests
import json
import sys
import argparse
from typing import Dict, List, Tuple, Optional
from dataclasses import dataclass
from datetime import datetime


# ============================================================================
# CONFIGURATION SECTION (Change if you want to customize)
# ============================================================================
BANLIST = [
    "spam",
    "abuse",
    "harassment",
    "inappropriate",
    "banned",
]

SETTINGS = {
    "base_url": "http://localhost:8000",
    "admin_username": "admin",
    "admin_password": "admin",
    "timeout": 10,  # seconds for HTTP requests
}


# ============================================================================
# DATA CLASSES
# ============================================================================

@dataclass
class ModerationAction:
    """Represents a single moderation action taken."""
    action_type: str  # "post_hidden" or "comment_hidden"
    content_id: int
    content_type: str  # "post" or "comment"
    reason: str
    original_content: str
    author: str


@dataclass
class ModerationSummary:
    """Summary statistics for a moderation run."""
    posts_scanned: int
    comments_scanned: int
    posts_hidden: int
    comments_hidden: int
    actions: List[ModerationAction]
    errors: List[str]


# ============================================================================
# CONTENT CHECKING LOGIC
# ============================================================================

def contains_banned_content(text: str, banlist: List[str]) -> Tuple[bool, Optional[str]]:
    """
    Check if text contains any banned words/phrases.
    
    Args:
        text: Text content to check
        banlist: List of banned words/phrases
        
    Returns:
        Tuple of (is_banned, reason_string)
    """
    if not text:
        return False, None
    
    text_lower = text.lower()
    for banned_term in banlist:
        if banned_term.lower() in text_lower:
            return True, f"Contains banned word/phrase: '{banned_term}'"
    
    return False, None


def check_post(post: Dict) -> Tuple[bool, Optional[str]]:
    """
    Check if a post violates moderation rules.
    
    Args:
        post: Post dict from dumpFeed response
        
    Returns:
        Tuple of (should_hide, reason)
    """
    # Check title
    is_banned, reason = contains_banned_content(post.get("title", ""), BANLIST)
    if is_banned:
        return True, reason
    
    # Check content
    is_banned, reason = contains_banned_content(post.get("content", ""), BANLIST)
    if is_banned:
        return True, reason
    
    return False, None


def check_comment(comment: Dict) -> Tuple[bool, Optional[str]]:
    """
    Check if a comment violates moderation rules.
    
    Args:
        comment: Comment dict from a post's comments array
        
    Returns:
        Tuple of (should_hide, reason)
    """
    is_banned, reason = contains_banned_content(comment.get("content", ""), BANLIST)
    if is_banned:
        return True, reason
    
    return False, None


# ============================================================================
# API COMMUNICATION
# ============================================================================
class CloudySkyClient:
    """Client for interacting with the CloudySky API."""
    
    def __init__(self, base_url: str, timeout: int = 10):
        """
        Initialize the API client.
        
        Args:
            base_url: Base URL of the CloudySky server (e.g., http://localhost:8000)
            timeout: Timeout for HTTP requests in seconds
        """
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.session = requests.Session()
    
    def login(self, username: str, password: str) -> bool:
        """
        Log in as admin user using session-based authentication.
        
        Args:
            username: Admin username
            password: Admin password
            
        Returns:
            True if login successful, False otherwise
        """
        try:
            login_url = f"{self.base_url}/accounts/login/"
            response = self.session.get(login_url, timeout=self.timeout)
            
            csrf_token = self.session.cookies.get('csrftoken')
            
            login_data = {
                'username': username,
                'password': password,
                'csrfmiddlewaretoken': csrf_token or '',
            }
            
            response = self.session.post(login_url, data=login_data, timeout=self.timeout)
            
            # Test authentication by accessing the dumpFeed endpoint
            feed_url = f"{self.base_url}/app/dumpFeed/"
            response = self.session.get(feed_url, timeout=self.timeout)
            
            if response.status_code == 200:
                return True
            
            print(f"[ERROR] Login failed: dumpFeed returned {response.status_code}")
            return False
            
        except requests.RequestException as e:
            print(f"[ERROR] Login request failed: {e}")
            return False
    
    def get_feed(self) -> Optional[List[Dict]]:
        """
        Fetch the feed from dumpFeed endpoint.
        
        Returns:
            List of post dictionaries, or None if request failed
        """
        try:
            feed_url = f"{self.base_url}/app/dumpFeed/"
            response = self.session.get(feed_url, timeout=self.timeout)
            
            if response.status_code != 200:
                print(f"[ERROR] Failed to fetch feed: HTTP {response.status_code}")
                return None
            
            return response.json()
            
        except requests.RequestException as e:
            print(f"[ERROR] Feed request failed: {e}")
            return None
        except json.JSONDecodeError as e:
            print(f"[ERROR] Failed to parse feed JSON: {e}")
            return None
    
    def hide_post(self, post_id: int, reason: str) -> bool:
        """
        Hide a post via the hidePost endpoint.
        
        Args:
            post_id: ID of the post to hide
            reason: Reason for hiding
            
        Returns:
            True if successful, False otherwise
        """
        try:
            hide_url = f"{self.base_url}/app/hidePost/"
            data = {
                'post_id': post_id,
                'reason': reason,
            }
            
            response = self.session.post(hide_url, data=data, timeout=self.timeout)
            
            if response.status_code not in (200, 201):
                print(f"[WARNING] Failed to hide post {post_id}: HTTP {response.status_code}")
                return False
            
            return True
            
        except requests.RequestException as e:
            print(f"[ERROR] Hide post request failed: {e}")
            return False
    
    def hide_comment(self, comment_id: int, reason: str) -> bool:
        """
        Hide a comment via the hideComment endpoint.
            
        Returns:
            True if successful, False otherwise
        """
        try:
            hide_url = f"{self.base_url}/app/hideComment/"
            data = {
                'comment_id': comment_id,
                'reason': reason,
            }
            
            response = self.session.post(hide_url, data=data, timeout=self.timeout)
            
            if response.status_code not in (200, 201):
                print(f"[WARNING] Failed to hide comment {comment_id}: HTTP {response.status_code}")
                return False
            
            return True
            
        except requests.RequestException as e:
            print(f"[ERROR] Hide comment request failed: {e}")
            return False


# ============================================================================
# MODERATION ENGINE
# ============================================================================

class ModerationEngine:
    """Orchestrates the moderation of feed content."""
    
    def __init__(self, client: CloudySkyClient, banlist: List[str]):
        """
        Initialize the moderation engine.
        """
        self.client = client
        self.banlist = banlist
        self.summary = ModerationSummary(
            posts_scanned=0,
            comments_scanned=0,
            posts_hidden=0,
            comments_hidden=0,
            actions=[],
            errors=[]
        )
    
    def moderate_feed(self) -> ModerationSummary:
        """
        Fetch the feed and moderate all posts and comments.
        """
        print("[*] Fetching feed...")
        feed = self.client.get_feed()
        
        if feed is None:
            self.summary.errors.append("Failed to fetch feed")
            return self.summary
        
        if not isinstance(feed, list):
            self.summary.errors.append("Feed response is not a list")
            return self.summary
        
        print(f"[*] Feed contains {len(feed)} posts")
        
        for post in feed:
            self._moderate_post(post)
        
        return self.summary
    
    def _moderate_post(self, post: Dict) -> None:
        """
        Moderate a single post and its comments.
        """
        try:
            post_id = post.get('id')
            if post_id is None:
                self.summary.errors.append("Post missing 'id' field")
                return
            
            self.summary.posts_scanned += 1
            
            should_hide, reason = check_post(post)
            
            if should_hide:
                author = post.get('username', 'unknown')
                content_preview = post.get('title', post.get('content', ''))[:50]
                
                print(f"[!] Hiding post {post_id} by {author}: {reason}")
                
                if self.client.hide_post(post_id, reason):
                    self.summary.posts_hidden += 1
                    self.summary.actions.append(ModerationAction(
                        action_type="post_hidden",
                        content_id=post_id,
                        content_type="post",
                        reason=reason,
                        original_content=content_preview,
                        author=author
                    ))
            
            comments = post.get('comments', [])
            if isinstance(comments, list):
                for comment in comments:
                    self._moderate_comment(post_id, comment)
        
        except Exception as e:
            self.summary.errors.append(f"Error moderating post {post.get('id', 'unknown')}: {e}")
    
    def _moderate_comment(self, post_id: int, comment: Dict) -> None:
        """
        Moderate a single comment.
        """
        try:
            comment_id = comment.get('id')
            if comment_id is None:
                self.summary.errors.append(f"Comment on post {post_id} missing 'id' field")
                return
            
            self.summary.comments_scanned += 1
            
            should_hide, reason = check_comment(comment)
            
            if should_hide:
                author = comment.get('author', 'unknown')
                content_preview = comment.get('content', '')[:50]
                
                print(f"[!] Hiding comment {comment_id} by {author}: {reason}")
                
                if self.client.hide_comment(comment_id, reason):
                    self.summary.comments_hidden += 1
                    self.summary.actions.append(ModerationAction(
                        action_type="comment_hidden",
                        content_id=comment_id,
                        content_type="comment",
                        reason=reason,
                        original_content=content_preview,
                        author=author
                    ))
        
        except Exception as e:
            self.summary.errors.append(f"Error moderating comment {comment.get('id', 'unknown')}: {e}")


# ============================================================================
# REPORTING
# ============================================================================
def print_summary(summary: ModerationSummary) -> None:
    """
    Print a formatted summary of the moderation run.
    """
    print("\n" + "=" * 70)
    print("MODERATION SUMMARY")
    print("=" * 70)
    print(f"Timestamp: {datetime.now().isoformat()}")
    print()
    
    print("STATISTICS:")
    print(f"  Posts scanned:       {summary.posts_scanned}")
    print(f"  Posts hidden:        {summary.posts_hidden}")
    print(f"  Comments scanned:    {summary.comments_scanned}")
    print(f"  Comments hidden:     {summary.comments_hidden}")
    print()
    
    if summary.actions:
        print("ACTIONS TAKEN:")
        for i, action in enumerate(summary.actions, 1):
            print(f"\n  {i}. {action.action_type.replace('_', ' ').upper()}")
            print(f"     ID: {action.content_id}")
            print(f"     Author: {action.author}")
            print(f"     Reason: {action.reason}")
            print(f"     Content: {action.original_content}...")
    else:
        print("ACTIONS TAKEN: None")
    
    print()
    
    if summary.errors:
        print("ERRORS ENCOUNTERED:")
        for i, error in enumerate(summary.errors, 1):
            print(f"  {i}. {error}")
        print()
    
    print("=" * 70)


# ============================================================================
# MAIN ENTRY POINT
# ============================================================================

def main():
    """Main entry point for the automoderator script."""
    parser = argparse.ArgumentParser(
        description="CloudySky Automoderator - Automatic content moderation"
    )
    parser.add_argument(
        "--url",
        default=SETTINGS["base_url"],
        help=f"Base URL of CloudySky server (default: {SETTINGS['base_url']})"
    )
    parser.add_argument(
        "--username",
        default=SETTINGS["admin_username"],
        help=f"Admin username (default: {SETTINGS['admin_username']})"
    )
    parser.add_argument(
        "--password",
        default=SETTINGS["admin_password"],
        help="Admin password (default: from SETTINGS)"
    )
    parser.add_argument(
        "--timeout",
        type=int,
        default=SETTINGS["timeout"],
        help=f"HTTP request timeout in seconds (default: {SETTINGS['timeout']})"
    )
    
    args = parser.parse_args()
    
    print("=" * 70)
    print("CloudySky Automoderator")
    print("=" * 70)
    print(f"Server: {args.url}")
    print(f"User: {args.username}")
    print(f"Banlist size: {len(BANLIST)} term(s)")
    print()
    
    client = CloudySkyClient(args.url, timeout=args.timeout)
    
    print("[*] Logging in...")
    if not client.login(args.username, args.password):
        print("[ERROR] Failed to log in. Exiting.")
        return 1
    print("[+] Login successful")
    print()
    
    print("[*] Starting moderation scan...")
    engine = ModerationEngine(client, BANLIST)
    summary = engine.moderate_feed()
    
    print_summary(summary)
    
    if summary.errors:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
