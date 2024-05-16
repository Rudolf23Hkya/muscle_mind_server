from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.tokens import AccessToken
from django.contrib.auth import get_user_model
from django.contrib.auth.models import User

from .models import UserDailyPerformance,UserWorkout
from .serializers import UserSerializer,WorkoutSerializer,UserWorkoutSerializer
from .data_processors import *
from.api_response_generators import *

from rest_framework.permissions import IsAuthenticated


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

# With this view we can see how much calory was consumed today by the user
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_calories(request):
    try:
        user_id = request.user.id
        obj, _ = get_or_create_user_daily_performance(user_id)
        cal = obj.calorie_intake
        
        return Response({'message': 'Success', 'Cal': cal}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    
# With this view calories can be added to the daily stat
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_calories(request):
    try:
        cal = request.data.get('calorie_data').get('calories')
        
        if cal and cal > 0:
            add_cal_eaten(request.user.id,cal)
            return Response({'message': 'Success', 'Cal': cal}, status=status.HTTP_201_CREATED)
        else:
            raise ValueError('Invalid calorie count!')

    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# This view saves workout statistics and modify weights based on rating
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def workout_done(request):
    try:
        user_id = request.user.id
        user_workout_id = request.data.get("user_workout_id")
        done_exercises = request.data.get("exercises")
        
        handle_workout_done(user_id,user_workout_id,done_exercises)
        
        return Response({'message': 'Workout posted!'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

# This view reccomends 3 workouts for the user based on user data
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

# This view saves a workout which was selected by the user for customization
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
        
        return Response({'workoutid': workout_id, 'do_weekly': do_weekly}, status=status.HTTP_201_CREATED)
    
    except (ValueError, AttributeError, Workout.DoesNotExist) as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

# This view returns the user s saved customized workouts
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_user_workout(request):
    user_id = request.user.id
    user_profile = UserProfile.objects.get(user=user_id)
    user_workouts = UserWorkout.objects.filter(user=user_profile)
    serializer = UserWorkoutSerializer(user_workouts, many=True)
    return Response(serializer.data)

#This view returns this week s workout data for the user starting with monday
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stats(request):
    user_id = request.user.id
    try:
        year = int(request.query_params.get('year'))
        month = int(request.query_params.get('month'))
        day = int(request.query_params.get('day'))
        
        # Create a date object
        date_obj = datetime.date(year, month, day)
        
        # Collect the workout data from this week
        stats = get_stats_of_the_week(user_id,date_obj)

        # Date as key, stat as value
        date_str = date_obj.strftime('%Y-%m-%d')
        return Response({
            date_str: stats
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)