from django.http import JsonResponse

from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework import status
from django.contrib.auth import get_user_model

from .models import UserDailyPerformance,UserWorkout
from .serializers import WorkoutSerializer,UserWorkoutSerializer
from .data_processors import *
from.api_response_generators import *

from rest_framework.permissions import IsAuthenticated

from decouple import config
from django.http import HttpResponse
from django.core.mail import EmailMessage

@permission_classes([IsAuthenticated])
@api_view(['GET'])
def get_user_data(request):
    try:
    # Decode the access token
        user_id = request.user.id
        User = get_user_model()
        user = User.objects.get(pk=user_id)
        # Generate the response (Tokens)
        response = generate_only_user_data(user, user.profile)
        return Response(response, status=status.HTTP_200_OK)
    
    except Exception as e:
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
        
        # Find the nearest prev monday
        mon_date = find_previous_monday(date_obj)
        
        # Collect the workout data from this week
        stats = get_stats_of_the_week(user_id,mon_date)
        # Date as key, stat as value
        date_str = date_obj.strftime('%Y-%m-%d')
        return Response({
            date_str: stats
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_401_UNAUTHORIZED)
    
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_stats_via_email(request):
    user_id = request.user.id
    
    try:
        user_profile = UserProfile.objects.get(user=user_id)
        user_email = user_profile.user.email
        
        if not user_email.endswith('@gmail.com'):
            return Response({'error': 'Email domain not allowed. Only Gmail is accepted.'}, status=status.HTTP_400_BAD_REQUEST)
        
        csv_selected = request.GET.get('csv', 'false').lower() == 'true'
        pdf_selected = request.GET.get('pdf', 'false').lower() == 'true'
        
        if csv_selected:
            attachment_data = get_all_daily_stats_csv(user_id)
            attachment_filename = 'daily_stats.csv'
            attachment_mimetype = 'text/csv'
        elif pdf_selected:
            attachment_data = get_all_daily_stats_pdf(user_id)
            attachment_filename = 'daily_stats.pdf'
            attachment_mimetype = 'application/pdf'
        else:
            return Response({'error': "No selected pdf or csv option!"}, status=status.HTTP_400_BAD_REQUEST)
        
        body_text = 'Dear ' + user_profile.user.username + ', Your workout stats by day is attached to this e-mail.'
        # Create email
        email = EmailMessage(
            subject='Muscle Mind stats - ' + user_profile.user.username,
            body=body_text,
            from_email=config('EMAIL_HOST_USER'),
            to=[user_email],
        )
        # Attach file
        email.attach(attachment_filename, attachment_data, attachment_mimetype)
        
        # Send email
        email.send()
        
        return Response({'success': 'Email sent successfully!'}, status=status.HTTP_200_OK)
    
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)