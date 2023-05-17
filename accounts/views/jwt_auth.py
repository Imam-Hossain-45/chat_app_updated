from rest_framework import status
from rest_framework.response import Response
from rest_framework_simplejwt.views import (
    TokenViewBase as BaseTokenViewBase,
    TokenObtainPairView as BaseTokenObtainPairView
)
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from django.contrib.auth.models import User
from accounts.serializers import UserSerializer


class TokenViewBase(BaseTokenViewBase):
    """
    Author: A.G.M. Imam Hossain
    Date: May 17, 2023,
    Purpose: override jwt post function
    """

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        response_data = serializer.validated_data.copy()
        try:
            user = User.objects.get(username=request.data['username'])
            user_data = UserSerializer(user).data
            response_data['user'] = user_data
        except Exception as e:
            print(e.__str__())
        return Response(response_data, status=status.HTTP_200_OK)


class TokenObtainPairView(BaseTokenObtainPairView, TokenViewBase):
    pass


token_obtain_pair = TokenObtainPairView.as_view()
