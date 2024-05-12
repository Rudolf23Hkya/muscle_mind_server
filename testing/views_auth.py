from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import authenticate

from .models import User,Disease
from .serializers import UserSerializer,UserProfileSerializer
from.api_response_generators import *

#Data validation done in the serializers
@api_view(['POST'])
def register_new_user(request):
    #Registering new user
    try:
        user_serializer = UserSerializer(data=request.data['user'])
        if user_serializer.is_valid():
            user = user_serializer.save()
            user.set_password(user_serializer.validated_data['password'])
            user.save()

            profile_data = {**request.data['user'], 'user': user.pk}
            profile_serializer = UserProfileSerializer(data=profile_data)
            if profile_serializer.is_valid():
                profile = profile_serializer.save()
                
                 # Process disease data from request
                disease_data = request.data.get('disease', {})
                disease_instance = Disease(
                    user=profile,# It s connected to the User table not the auth_user
                    cardiovascular_d=disease_data.get('cardiovascular_d', 'False').lower() == 'true',
                    bad_knee=disease_data.get('bad_knee', 'False').lower() == 'true',
                    asthma=disease_data.get('asthma', 'False').lower() == 'true',
                    osteoporosis=disease_data.get('osteoporosis', 'False').lower() == 'true'
                )
                disease_instance.save()
                
                # Generate tokens
                refresh = RefreshToken.for_user(user)
                access = refresh.access_token
                
                response = generate_full_auth_data(user, profile, refresh, access)
                
                return Response(response,status=status.HTTP_201_CREATED)
            else:
                user.delete()  # Cleanup if profile creation fails
                return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    except:
        return Response(user_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])    
def login_user(request):
    email = request.data.get('email')
    password = request.data.get('password')
    
    if email is None or password is None:
        return Response({'error': 'Please provide both email and password'}, status=status.HTTP_400_BAD_REQUEST)
    
    user = authenticate(username=email, password=password)
    if user is not None:
        # User is authenticated
        refresh = RefreshToken.for_user(user)
        access = refresh.access_token
        
        response = generate_full_auth_data(user, user.profile, refresh, access)
        
        return Response(response, status=status.HTTP_200_OK)
    else:
        return Response({'error': 'Invalid Credentials'}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])       
def login_with_google(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})

@api_view(['GET'])
def get_refresh_token(request):
    token_data = request.data.get('tokens', {})
    refresh_token_str = token_data.get('refresh')

    if not refresh_token_str:
        return Response({'error': 'Refresh token is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        refresh_token = RefreshToken(refresh_token_str)

        # From the refresh token generateing a new access token
        new_access_token = refresh_token.access_token

        response = generate_auth_data(refresh_token_str, str(new_access_token))

        return Response(response, status=status.HTTP_200_OK)

    except Exception as e:
        # If the refresh token is invalid or expired
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)