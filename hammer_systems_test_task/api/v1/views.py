import random
import time

from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.shortcuts import get_object_or_404
from drf_yasg import openapi
from drf_yasg.utils import swagger_auto_schema
from rest_framework import status
from rest_framework.generics import RetrieveUpdateAPIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import AccessToken

from .serializers import AuthSerializer, LoginSerializer, UserProfileSerializer
from .utils import (get_invite_code, get_verification_code,
                    save_verification_code)

User = get_user_model()


class LoginView(APIView):
    """Представление для регистрации пользователя."""

    queryset = User.objects.all()
    serializer_class = LoginSerializer

    @swagger_auto_schema(
        request_body=LoginSerializer,
        responses={200: 'Код авторизации отправлен.'})
    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']

        User.objects.get_or_create(phone=phone)

        verification_code = get_verification_code()
        cache.set(phone, verification_code, timeout=120)
        time.sleep(random.uniform(1, 2))

        # эмуляция отправки смс
        save_verification_code(phone, verification_code)

        return Response({'detail': 'Код авторизации отправлен.'},
                        status=status.HTTP_200_OK)


class AuthView(APIView):
    """Представление для авторизации пользователя по токену из смс."""

    @swagger_auto_schema(
        request_body=AuthSerializer,
        responses={200: 'Пользователь успешно авторизован',
                   400: 'Неверный код авторизации'}
    )
    def post(self, request):
        serializer = AuthSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        phone = serializer.validated_data['phone']
        verification_code = serializer.validated_data['verification_code']
        saved_verification_code = str(cache.get(phone))

        if (saved_verification_code
                and saved_verification_code == verification_code):
            user = get_object_or_404(User, phone=phone)
            user.is_verified = True
            user.my_invite_code = get_invite_code()
            user.save()
            cache.delete(phone)

            return Response({'detail': 'Пользователь успешно авторизован',
                             'Ваш код приглашения': f'{user.my_invite_code}',
                             'token': str(AccessToken.for_user(user))},
                            status=status.HTTP_200_OK)

        return Response({'detail': 'Неверный код авторизации'},
                        status=status.HTTP_400_BAD_REQUEST)


class UserProfileView(RetrieveUpdateAPIView):
    """Представление для работы с профилем пользователя."""

    serializer_class = UserProfileSerializer
    permission_classes = (IsAuthenticated, )
    http_method_names = ('get', 'patch')

    def get_object(self):
        return self.request.user

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER,
                              description="Bearer token",
                              type=openapi.TYPE_STRING, required=True)
        ]
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('Authorization', openapi.IN_HEADER,
                              description="Bearer token",
                              type=openapi.TYPE_STRING, required=True)
        ]
    )
    def patch(self, request, *args, **kwargs):
        return super().patch(request, *args, **kwargs)
