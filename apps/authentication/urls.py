from django.urls import path

from .views import (
    RegisterView,
    LoginView,
    MyTokenRefreshView,
    LogoutView,
)


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', MyTokenRefreshView.as_view(), name='token_refresh'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
