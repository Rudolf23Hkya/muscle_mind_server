from django.db.models import F
from datetime import date
from django.db.models import QuerySet
from django.contrib.auth.models import User
# Models
from .models import UserDailyPerformance,UserProfile,Disease,Workout

# Enums
from .models import ExperienceLevel,Category,MuscleGroup

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

# Returns the 3 most suitable workouts for the user
def get_best_3_workout(user_id, weightlifting, trx):
    # Step 0: Get user from db
    user = User.objects.get(id=user_id)
    user_profile = UserProfile.objects.get(user=user)
    
    # Step 1: Start with all workouts
    workouts = Workout.objects.all()

    # Step 2: Exclude workouts based on equipment availability
    if not weightlifting:
        workouts = workouts.exclude(category__contains=[Category.WEIGHTLIFTING.value])
    if not trx:
        workouts = workouts.exclude(category__contains=[Category.TRX.value])
    
    # Step 3: Exclude workouts based on Diseases
    user_diseases = Disease.objects.get(user=user_profile)
    # Exclude workouts that target the lower body if the user has a bad knee
    if user_diseases.bad_knee:
        workouts = workouts.exclude(musclegroup__contains=[MuscleGroup.LOWER_BODY.value])

    # Exclude high intensity workouts if the user has cardiovascular disease
    if user_diseases.cardiovascular_d:
        workouts = workouts.exclude(category__contains=[ExperienceLevel.PROFESSIONAL.value])

    # Exclude long high intensity workouts if the user has asthma
    if user_diseases.asthma:
        workouts = workouts.exclude(category__contains=[ExperienceLevel.PROFESSIONAL.value])
        # exercise_order lenght is greater than 5
        workouts = workouts.exclude(exercise_order__length__gt=5)

    # Exclude weightlifting workouts if the user has osteoporosis
    if user_diseases.osteoporosis:
        workouts = workouts.exclude(category__contains=[Category.WEIGHTLIFTING.value])
    
    # Step 4: Exclude workouts based on Experience(+1 level max)
    user_experience_level = user_profile.experiencelevel
    allowed_levels = ExperienceLevel.get_allowed_levels(user_experience_level)

    workouts = workouts.filter(experiencelevel__in=allowed_levels)
    
    # Step 5: Adjust the number of workouts to be 3 always
    workout_count = workouts.count()
    
    if workout_count > 3:
        workouts = workouts.order_by('?')[:3]  # Randomly select 3 workouts if more than 3
    elif workout_count < 3:
        remaining_count = 3 - workout_count
        additional_workouts = Workout.objects.exclude(id__in=workouts.values_list('id', flat=True)).order_by('?')[:remaining_count]
        workouts = list(workouts) + list(additional_workouts)
    
    if isinstance(workouts, QuerySet):
        workouts = list(workouts)    
    return workouts