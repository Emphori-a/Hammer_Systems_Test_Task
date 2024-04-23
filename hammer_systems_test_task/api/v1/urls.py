from django.urls import path

from .views import AuthView, LoginView, UserProfileView

urlpatterns = [
    path('login/', LoginView.as_view(), name='login'),
    path('auth/', AuthView.as_view(), name='auth'),
    path('profile/', UserProfileView.as_view(), name='profile'),
]
