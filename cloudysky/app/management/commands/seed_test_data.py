from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from app.models import Post, Comment


class Command(BaseCommand):
    help = 'Seed database with test fixtures for testing'

    def handle(self, *args, **options):
        # Create admin user if doesn't exist
        admin, created = User.objects.get_or_create(
            username='Autograder Admin',
            defaults={
                'email': 'autograder_test@test.org',
                'is_staff': True,
                'is_superuser': True
            }
        )
        if created:
            admin.set_password('Password123')
            admin.save()
            self.stdout.write(self.style.SUCCESS(f'Created admin user: {admin.username}'))
        
        # Create regular user if doesn't exist
        user, created = User.objects.get_or_create(
            username='Tester Student',
            defaults={
                'email': 'user_test@test.org',
                'is_staff': False
            }
        )
        if created:
            user.set_password('Password123')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created regular user: {user.username}'))
        
        # Create a test post with id=1 if it doesn't exist
        if not Post.objects.filter(id=1).exists():
            post = Post.objects.create(
                id=1,
                author=admin,
                title='Test Post for Comments',
                content='This is a test post that can be used for creating comments'
            )
            self.stdout.write(self.style.SUCCESS(f'Created test post with id=1'))
        
        # Create a test comment with id=1 if it doesn't exist
        if not Comment.objects.filter(id=1).exists():
            post = Post.objects.get(id=1)
            comment = Comment.objects.create(
                id=1,
                post=post,
                author=user,
                content='This is a test comment for testing hide functionality'
            )
            self.stdout.write(self.style.SUCCESS(f'Created test comment with id=1'))
        
        self.stdout.write(self.style.SUCCESS('Database seeded successfully!'))
