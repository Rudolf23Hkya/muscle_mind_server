from django.http import JsonResponse

from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .models import User
from .serializers import UserSerializer,UserProfileSerializer


def generate_full_auth_data(user, profile, refresh, access):
    response_data = {
        'userData': {
            'email': user.email,
            'username': user.username,
            'gender': profile.gender,
            'experienceLevel': profile.experiencelevel,
            'age': profile.age,
            'weight': profile.weight,
            'height': profile.height,
        },
        'tokens': {
            'refresh': str(refresh),
            'access': str(access)
        }
    }
    return response_data

def generate_auth_data(refresh, access):
    response_data = {
        'tokens': {
            'refresh': str(refresh),
            'access': str(access)
        }
    }
    return response_data


#Data validation done in the serializers

@api_view(['POST'])
def register_new_user(request):
    #Registering new user
    user_serializer = UserSerializer(data=request.data)
    if user_serializer.is_valid():
        user = user_serializer.save()
        user.set_password(user_serializer.validated_data['password'])
        user.save()

        profile_data = {**request.data, 'user': user.pk}
        profile_serializer = UserProfileSerializer(data=profile_data)
        if profile_serializer.is_valid():
            profile = profile_serializer.save()
            
            # Generateing tokens
            refresh = RefreshToken.for_user(user)
            access = refresh.access_token
            
            response = generate_full_auth_data(user, profile, refresh, access)
            
            return Response(response,status=status.HTTP_201_CREATED)
        else:
            user.delete()  # Cleanup if profile creation fails
            return Response(profile_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

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
        
def login_with_google(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})

@api_view(['POST'])
def user_data_with_access_token(request):
    token_data = request.data.get('tokens', {})
    access_token = token_data.get('access')
    
    if not access_token:
        return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
    # Decode the access token
        token = AccessToken(access_token)
        user_id = token['user_id']  # Extract user ID from token payload
        User = get_user_model()
        user = User.objects.get(pk=user_id)  # Retrieve the user based on the token user_id
        # Generate the response (no Refrsh Token)
        response = generate_full_auth_data(user, user.profile, "", access_token)
        return Response(response, status=status.HTTP_200_OK)
    
    except Exception as e:
    # If the token is invalid or expired, or the user does not exist
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
def access_token_with_refresh_token(request):
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

def workout_done(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})

#@api_view('GET')
def get_calories(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
    
def add_calories(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
#@api_view('GET') 
def get_stats(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
