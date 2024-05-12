from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model

from .models import User, UserDailyPerformance
from .serializers import UserSerializer,UserProfileSerializer
from .data_processors import *

import datetime
from datetime import timedelta

from rest_framework.authentication import SessionAuthentication, BasicAuthentication
from rest_framework.permissions import IsAuthenticated


def generate_full_auth_data(user, profile, refresh, access):
    response_data = {
        'userData': {
            'email': user.email,
            'password': "",
            'username': user.username,
            'gender': profile.gender,
            'experiencelevel': profile.experiencelevel,
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

@api_view(['GET'])
def get_calories(request):
    #Handlest a reg. request
    user = User.objects.all()
    ser = UserSerializer(user,many=True)
    return JsonResponse({"users":ser.data})
    
    #If the data is valid saves it to the db and responds with OK
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_calories(request):
    user = request.user  # Authenticated user from the JWT token
    # Getting data from request
    calorie_data = request.data.get('calorie_data', {})

    # Checking if necessary calorie data is present
    if not calorie_data.get('calories'):
        return Response({'error': 'Calories count is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # You can adjust the field names based on your actual model
        cal = calorie_data.get('calories')

        # Data operations abstracted
        add_user_d_cal_eaten(user.id,cal)

        # Respond with success and the calorie data as confirmation
        return Response({'message': 'Calorie data posted successfully', 'data': calorie_data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        # If there's an error while saving or processing data
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_burnt_calories(request):
    user = request.user  # Authenticated user from the JWT token
    # Getting data from request
    calorie_data = request.data.get('calorie_data', {})

    # Checking if necessary calorie data is present
    if not calorie_data.get('calories'):
        return Response({'error': 'Calories count is required'}, status=status.HTTP_400_BAD_REQUEST)

    try:
        # You can adjust the field names based on your actual model
        cal = calorie_data.get('calories')

        # Data operations abstracted
        add_user_d_cal_burnt(user.id,cal)

        # Respond with success and the calorie data as confirmation
        return Response({'message': 'Calorie data posted successfully', 'data': calorie_data}, status=status.HTTP_201_CREATED)

    except Exception as e:
        # If there's an error while saving or processing data
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
#This view returns this week s workout data for the user starting with monday
@api_view(['POST'])
def get_stats(request):
    token_data = request.data.get('tokens', {})
    access_token = token_data.get('access')
    
    if not access_token:
        return Response({'error': 'Access token is required'}, status=status.HTTP_400_BAD_REQUEST)
    
    try:
        token = AccessToken(access_token)  
        user_id = token['user_id'] 
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        
        # Parsing date
        year = int(request.data.get('year'))
        month = int(request.data.get('month'))
        day = int(request.data.get('day'))

        # Create the date object
        date_obj = datetime.date(year, month, day)
        prev_monday = find_previous_monday(date_obj)
        
        # Collect data from Monday to Sunday
        week_data = []
        for i in range(7):
            current_date = prev_monday + timedelta(days=i)
            performances = UserDailyPerformance.objects.filter(user=user, date=current_date)
            
            # Format the result for each day
            if performances.exists():
                day_data = list(performances.values())
            else:
                day_data = [{}]  # Empty dictionary for days with no data
            
            week_data.append({
                'date': current_date.isoformat(),
                'data': day_data
            })

        return Response({
            'week_data': week_data
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        # If the token is invalid or expired, or the user does not exist
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)

def find_previous_monday(date_obj):
    # Get the weekday number for the date object (0 = Monday, ..., 6 = Sunday)
    day_of_week = date_obj.weekday()
    
    # Calculate the difference to the previous Monday
    if day_of_week == 0:
        # If it's already Monday, return the same date
        previous_monday = date_obj
    else:
        # Calculate the number of days to subtract to get back to the previous Monday
        previous_monday = date_obj - datetime.timedelta(days=day_of_week)

    return previous_monday