# accounts/urls.py
from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from .views import RegisterView, LoginView, MeView, ProOnlyView, ProApplyView, ProMyApplicationView
from .social import GoogleLoginView, AppleLoginView

urlpatterns = [
    path("register/", RegisterView.as_view()),
    path("login/",    LoginView.as_view()),
    path("token/refresh/", TokenRefreshView.as_view()),
    path("me/",       MeView.as_view()),
    path("google/",   GoogleLoginView.as_view()),
    path("apple/",    AppleLoginView.as_view()),
    path("pro/only/", ProOnlyView.as_view()),
    path("pro/apply/", ProApplyView.as_view()),          # POST (multipart) ile başvuru/yenileme
    path("pro/application/", ProMyApplicationView.as_view()),  # GET: kendi başvurunu gör
]
