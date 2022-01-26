from rest_framework import generics

from user.serializers import UserSerializer


class CreateUserView(generics.CreateAPIView):
    # crear nuevo usuario en el sistema
    serializer_class = UserSerializer