from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken

from django.contrib.auth import authenticate
from django.utils import timezone
from django.contrib.auth.models import User

from .models import Disease
from .serializers import UserSerializer,UserProfileSerializer
from.api_response_generators import *

def extract_error_messages(errors):
    error_messages = []
    for field, error_list in errors.items():
        for error in error_list:
            if isinstance(error, dict) and 'string' in error:
                error_messages.append(error['string'])
            else:
                error_messages.append(str(error))
    return error_messages

#Data validation done in the serializers
@api_view(['POST'])
def register_new_user(request):
    try:
        user_created = False
        user_serializer = UserSerializer(data=request.data.get('userData'))
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(user_serializer.validated_data['password'])
            user.save()
            user_created = True
            
            profile_data = {**request.data['userData'], 'user': user.pk}
            profile_serializer = UserProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()

                # Process disease data from request
                disease_data = request.data.get('disease', {})
                disease_instance = Disease(
                    user=profile,  # It's connected to the UserProfile table not the auth_user
                    cardiovascular_d=disease_data.get('cardiovascular_d', False),
                    bad_knee=disease_data.get('bad_knee', False),
                    asthma=disease_data.get('asthma', False),
                    osteoporosis=disease_data.get('osteoporosis', False)
                )
                disease_instance.save()

                # Generate tokens
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token

                response = generate_full_auth_data(user, profile, refresh, access)

                return Response(response, status=status.HTTP_201_CREATED)
            else:
                user.delete()  # Cleanup if profile creation fails
                return Response({'error': str(profile_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': str(user_serializer.errors)}, status=status.HTTP_400_BAD_REQUEST)
    except Exception as e:
        if(user_created):
            user.delete()  # Cleanup if profile creation fails
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])    
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=email, password=password)

    if user is not None and not user.is_superuser:
        # Updating the last login s value
        user.last_login = timezone.now()
        user.save(update_fields=['last_login'])
        
        # User is authenticated
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        response = generate_full_auth_data(user, user.profile, refresh, access)
        
        return Response(response, status=status.HTTP_200_OK)
    elif user is not None:
        return Response({'error': 'Superuser have no access to the app!'}, status=status.HTTP_401_UNAUTHORIZED)
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])       
def login_with_google(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})

# This function is POST not GET for security reasons
@api_view(['POST'])
def get_access_token(request):
    refresh_token_str = request.data.get('refresh')

    if not refresh_token_str:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh_token = RefreshToken(refresh_token_str)

        # From the refresh token generating a new access token
        new_access_token = refresh_token.access_token

        response = generate_auth_data(refresh_token_str, str(new_access_token))

        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        # If the refresh token is invalid or expired
        return Response({'error': str(extract_error_messages(e))}, status=status.HTTP_401_UNAUTHORIZED)