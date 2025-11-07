from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('index.html', views.index, name='index_html'),
    # HW4 Step 2: user creation routes under /app/* per spec
    path('app/new', views.new_user, name='new_user'),
    path('app/createUser', views.create_user, name='create_user'),
]
