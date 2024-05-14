from django.db.models import F
from datetime import date

from .models import UserDailyPerformance

def get_or_create_user_daily_performance(id):
    """
    A function that checks if there is already a record for the given user today, 
    and if not, creates a new one with default values.
    """
    return UserDailyPerformance.objects.get_or_create(
        user_id=id,
        date=date.today(),
        defaults={
            'calorie_intake': 0,
            'time_working_out_minutes': 0,
            'calories_burnt': 0
        }
    )
# user_daily_performance updaters
def add_user_d_cal_eaten(user_id, cal=0):
    obj, created = get_or_create_user_daily_performance(user_id)
    if created:
        obj.calorie_intake = cal
    else:
        obj.calorie_intake = F('calorie_intake') + cal
    obj.save()

def add_user_d_cal_burnt(user_id, cal=0):
    obj, created = get_or_create_user_daily_performance(user_id)
    if created:
        obj.calories_burnt = cal
    else:
        obj.calories_burnt = F('calories_burnt') + cal
    obj.save()

def add_user_w_time(user_id, min=0):
    obj, created = get_or_create_user_daily_performance(user_id)
    if created:
        obj.time_working_out_minutes = min
    else:
        obj.time_working_out_minutes = F('time_working_out_minutes') + min
    obj.save()

# POST view handlers

def add_eaten_calorie_data(request):
    calorie_data = request.data.get('calorie_data', {})
    if not calorie_data.get('calories'):
        raise ValueError('Calories count is required')
    
    cal = calorie_data.get('calories')
    add_user_d_cal_eaten(request.user.id,cal)

# GET view handlers

#TODO
def process_wourout_done(request):
    calorie_data = request.data.get('calorie_data', {})
    if not calorie_data.get('calories'):
        raise ValueError('Calories count is required')
    
    cal = calorie_data.get('calories')
    add_user_d_cal_burnt(request.user.id,cal)
    
    return {'calories': cal}

def generate_workout_durations(user):
    """
    This function generates weights for exercises based on the user s data, like:
    - Age
    - BMI(weight/height^2)
    - Diseases
    - Experience level
    """
    user_ = UserProfile.objects.get(user=user)
    # workout_sessions = WorkoutSession.objects.filter(user=user)
    
    # Data processing here
    # Példa: visszaadunk egy listát az edzés gyakorlatainak hosszával [0..1] tartományban
    exercise_weights = [0.5, 0.7, 0.3, 0.9, 0.6]  # Példa float lista
    
    return exercise_weights

def generate_exercises(user_id):
    """
    This function select the best 3 base workout plans 
    stored in our database based on:
    - BMI(weight/height^2) - More or less Cardio focus
    - Diseases
        -- No LOWER_BODY training for bed knee
        -- No EXPERIENCED or PROFESSIONAL cardio for hearth problems
    - Experience level
    """
    user_ = UserProfile.objects.get(user=user)
    # workout_sessions = WorkoutSession.objects.filter(user=user)
    
    # Data processing here
    # Példa: visszaadunk egy listát az edzés gyakorlatainak hosszával [0..1] tartományban
    exercise_weights = [0.5, 0.7, 0.3, 0.9, 0.6]  # Példa float lista
    
    return exercise_weights

#TODO
def process_recom_workouts(request):
    # These check what kind of equipment does the user have
    weightlifting = request.GET.get('weightlifting')
    trx = request.GET.get('trx')
    # Generate exercises
    
    
    weights = generate_workout_durations(request.user.id)
    if level:
        #workouts = Workout.objects.filter(level=level)
        print("hello")
    else:
        #workouts = Workout.objects.all()
        print("hello")
    
    # Serializáljuk az adatokat a válaszhoz
    #serializer = WorkoutSerializer(workouts, many=True)
    return "haki"