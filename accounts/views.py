from django.shortcuts import render

# Create your views here.

from rest_framework import generics, permissions
from rest_framework.permissions import AllowAny
from .serializadores import RegisterSerializer, LoginSerializer
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]

class LoginView(TokenObtainPairView):
    serializer_class = LoginSerializer

class RefreshView(TokenRefreshView):
    permission_classes = [permissions.AllowAny]

