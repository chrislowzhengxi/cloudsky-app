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
    # HW5: HTML form views
    path('app/new_post/', views.new_post, name='new_post'),
    path('app/new_comment/', views.new_comment, name='new_comment'),
]

