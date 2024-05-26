from django.contrib.auth.backends import BaseBackend
from django.contrib.auth import get_user_model

# This authentication method should only be used with Google authentication
# The password validation is done by google

class GoogleBackend(BaseBackend):
    def authenticate(self, request, email=None, **kwargs):
        UserModel = get_user_model()
        try:
            user = UserModel.objects.get(email=email)
            return user
        except UserModel.DoesNotExist:
            return None

    def get_user(self, user_id):
        UserModel = get_user_model()
        try:
            return UserModel.objects.get(pk=user_id)
        except UserModel.DoesNotExist:
            return None