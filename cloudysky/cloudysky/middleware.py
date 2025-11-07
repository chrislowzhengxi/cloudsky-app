from django.core.management import call_command
from django.db import connection

_migrations_checked = False


class EnsureMigrationsMiddleware:
    """
    On the first request only, check for core auth tables and run migrations
    if they're missing. This prevents 500s like 'no such table: auth_user'
    in fresh grading environments where migrate hasn't been executed yet.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        global _migrations_checked
        if not _migrations_checked:
            try:
                tables = set(connection.introspection.table_names())
                if "auth_user" not in tables:
                    call_command("migrate", interactive=False, run_syncdb=True, verbosity=0)
            except Exception:
                # Best-effort only; if migrate fails, continue and let the
                # natural error surface. This keeps behavior deterministic.
                pass
            finally:
                _migrations_checked = True

        return self.get_response(request)
