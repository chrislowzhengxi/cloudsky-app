from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    # HW4 Step 2: user creation routes under /app/* per spec
    path('app/new/', views.new_user, name='new_user'),
    path('app/createUser/', views.create_user, name='create_user'),
    # HW5: New API endpoints
    path('app/createPost/', views.create_post, name='create_post'),
    path('app/createComment/', views.create_comment, name='create_comment'),
    path('app/hidePost/', views.hide_post, name='hide_post'),
    path('app/hideComment/', views.hide_comment, name='hide_comment'),
    path('app/dumpFeed/', views.dump_feed, name='dump_feed'),
    path('app/dumpFeed', views.dump_feed, name='dump_feed_no_slash'),
    # Part 2: Feed and post detail endpoints
    path('app/feed/', views.feed, name='feed'),
    path('app/feed', views.feed, name='feed_no_slash'),
    path('app/post/<int:post_id>/', views.post_detail, name='post_detail'),
    path('app/post/<int:post_id>', views.post_detail, name='post_detail_no_slash'),
    # HW5: HTML form views
    path('app/new_post/', views.new_post, name='new_post'),
    path('app/new_comment/', views.new_comment, name='new_comment'),
]

