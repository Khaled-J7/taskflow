from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

app_name = 'accounts'  # This creates a namespace for our app URLs

urlpatterns = [
    # Authentication URLs
    
    path('login/', views.login_view, name='login'),
    
    # The next_page='home' parameter tells Django to redirect users to the home page after they log out.
    path('logout/', auth_views.LogoutView.as_view(next_page='home'), name='logout'),
    
    path('register/', views.register, name='register'),
    
]