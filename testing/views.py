from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import authenticate
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from .models import UserDailyPerformance,UserWorkout
from .serializers import UserSerializer,WorkoutSerializer,UserWorkoutSerializer
from .data_processors import *
from.api_response_generators import *

import datetime
from datetime import timedelta

from rest_framework.permissions import IsAuthenticated


def generic_api_handler(request, data_processor):
    """
    General function for handling API calls, including authentication,
    data processing, and basic error handling.

    Args:
        request: The HTTP request object.
        data_processor: A function responsible for processing the request data,
                        and raising an exception if an error occurs.

    Returns:
        Response: The REST response, which may contain success or error information.
    """

    # Calling the data processing function
    try:
        result = data_processor(request)
        return Response({'message': 'Success', 'data': result}, status=status.HTTP_200_OK)

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def get_user_data(request):
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
    return generic_api_handler(request, add_eaten_calorie_data)
    
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_workout_data(request):
    return generic_api_handler(request, process_wourout_done)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_recom_workouts(request):
    user_id = request.user.id
    
    weightlifting = request.GET.get('weightlifting')
    trx = request.GET.get('trx')
    
    workouts = get_best_3_workout(user_id,weightlifting,trx)
        
    # Serializeing the data and respond
    serializer = WorkoutSerializer(workouts, many=True)
    return JsonResponse(serializer.data, safe=False)
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_user_workout(request):
    user_id = request.user.id
    
    try:
        workout_id = int(request.data.get('workout').get('workoutid'))
        do_weekly = int(request.data.get('do_weekly', 0))

        # Checkig if the workout exists in the database
        weights = calculate_weights(workout_id,user_id)
        
        if weights and user_id:
            # Saving the posted UserWorkout
            UserWorkout.objects.create(
                user=UserProfile.objects.get(user=user_id),
                workout=Workout.objects.get(workoutid=workout_id),
                weights=weights,
                do_weekly=do_weekly
            )
        
        # Válasz vissza a létrehozott bejegyzés adataival
        return Response({'workoutid': workout_id, 'do_weekly': do_weekly}, status=status.HTTP_201_CREATED)
    
    except (ValueError, AttributeError, Workout.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_workout(request):
    user_id = request.user.id
    user_profile = UserProfile.objects.get(user=user_id)
    user_workouts = UserWorkout.objects.filter(user=user_profile)
    serializer = UserWorkoutSerializer(user_workouts, many=True)
    return Response(serializer.data)

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