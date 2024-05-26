from django.db.models import F
from datetime import date
from django.db.models import QuerySet
from django.db.models.functions import Cast
from django.contrib.postgres.fields import ArrayField
from django.db import models
from django.db.models import Q
# Models
from .models import UserDailyPerformance,UserProfile,Disease,Workout,Exercise,UserWorkout

# Enums
from .models import ExperienceLevel,Category,MuscleGroup

#Math imports
from scipy.interpolate import interp1d
import numpy as np

# date 
import datetime
from datetime import timedelta

# export data
import csv
import io
# pdf
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

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
            'time_working_out_sec': 0,
            'calories_burnt': 0
        }
    )
# user_daily_performance updaters
def add_cal_eaten(user_id, cal=0):
    obj, created = get_or_create_user_daily_performance(user_id)
    if created:
        obj.calorie_intake = cal
    else:
        obj.calorie_intake = F('calorie_intake') + cal
    obj.save()

def add_cal_burnt(user_id, cal=0):
    obj, created = get_or_create_user_daily_performance(user_id)
    if created:
        obj.calories_burnt = cal
    else:
        obj.calories_burnt = F('calories_burnt') + cal
    obj.save()

def add_workout_time(user_id, min=0):
    obj, created = get_or_create_user_daily_performance(user_id)
    if created:
        obj.time_working_out_sec = min
    else:
        obj.time_working_out_sec = F('time_working_out_sec') + min
    obj.save()
    
def handle_workout_done(user_id, user_workout_id, done_exercises):
    print(user_workout_id)
    user_workout = UserWorkout.objects.get(id=user_workout_id)
    
    cal_burnt = 0
    sec_working_out = 0
    weights = user_workout.weights
    
    if len(done_exercises) != len(weights):
        raise ValueError("Invalid Exercise count. Data was damaged!")
    
    # Evaluating data from the exercises
    for e_cntr, details in enumerate(done_exercises):
        rating = int(details["rating"])
        
        if rating == 1:
            weights[e_cntr] -= 0.1
        elif rating == 2:
            weights[e_cntr] -= 0.05
        elif rating == 3:
            pass
        elif rating == 4:
            weights[e_cntr] += 0.1
        elif rating == 5:
            weights[e_cntr] += 0.05  
        
        # Normalization
        if weights[e_cntr] > 2:
            weights[e_cntr] = 2
            
        if weights[e_cntr] < 0:
            weights[e_cntr] = 0
        
        cal = int(details["cal"])
        cal_burnt += cal
        
        duration = int(details["duration"])
        sec_working_out += duration
    
    # Updating weights
    user_workout.weights = weights
    user_workout.save()
    
    # Adding the time spent / calories burnt to the daily performance
    add_cal_burnt(user_id, cal_burnt)
    add_workout_time(user_id, sec_working_out)

# Returns the 3 most suitable workouts for the user
def get_best_3_workout(user_id, weightlifting, trx):
    # Step 0: Get user from db
    user_profile = UserProfile.objects.get(user=user_id)
    
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
        lower_body_value = MuscleGroup.LOWER_BODY.value
        workouts = workouts.exclude(Q(musclegroup__icontains=lower_body_value))

    # Exclude high intensity workouts if the user has cardiovascular disease
    if user_diseases.cardiovascular_d:
        professional_value = ExperienceLevel.PROFESSIONAL.value
        workouts = workouts.exclude(Q(category__icontains=professional_value))

    # Exclude long high intensity workouts if the user has asthma
    if user_diseases.asthma:
        professional_value = ExperienceLevel.PROFESSIONAL.value
        workouts = workouts.exclude(Q(category__icontains=professional_value))

        # Exclude workouts where exercise_order length is greater than 5
        workouts = workouts.annotate(
            exercise_order_len=Cast(F('exercise_order'), ArrayField(models.IntegerField()))
        ).exclude(exercise_order_len__len__gt=5)

    # Exclude weightlifting workouts if the user has osteoporosis
    if user_diseases.osteoporosis:
        weightlifting_value = Category.WEIGHTLIFTING.value
        workouts = workouts.exclude(Q(category__icontains=weightlifting_value))
    
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
    

# Calculating the weights for each exercise, to make more personal for the users
def calculate_weights(workout_id,user_id):
    try:
        workout = Workout.objects.get(workoutid=workout_id)
        user_profile = UserProfile.objects.get(user=user_id)
    except Workout.DoesNotExist:
        return False

    weights = []
    # User data for the calculation
    age = user_profile.age
    # Convert height from centimeters to meters
    height_in_meters = user_profile.height / 100

    # Calculate BMI
    bmi = float(user_profile.weight  / (height_in_meters ** 2))
    
    user_experience_level = user_profile.experiencelevel
    
    for exercise_id in workout.exercise_order:
        try:
            exercise = Exercise.objects.get(exerciseid=exercise_id)
            
            # Weight calculation logic
            exercise_experience_level = exercise.experiencelevel
            
            weight = calculate_weight(exercise_experience_level,age,bmi,user_experience_level)
            
            weights.append(weight)
        except Exercise.DoesNotExist:
            return False

    return weights
# Returns a float(max: 2, min: 0 (diseabled Exercise))
# by default no exercise is diseabled
def calculate_weight(exercise_experience_level,age,bmi,user_experience_level):
    # Converting the Enums to numbers
    exercise_level = ExperienceLevel.get_num(ExperienceLevel[exercise_experience_level])
    user_level = ExperienceLevel.get_num(ExperienceLevel[user_experience_level])
    
    # If the value is > 1 the exercise is easy for the user and needs boosting
    # If the value is < 1 the exercise is hard for the user and needs nerfing
    multiplier = 0.5

    # Experience
    level_difference = user_level - exercise_level
    
    if level_difference == 1:
        multiplier += 0.15
    elif level_difference >= 2:
        multiplier += 0.4
    elif level_difference == -1:
        multiplier -= 0.15
    elif level_difference <= -2:
        multiplier -= 0.4

    # Age
    # -For very young and old shorter Exercise
    multiplier += interpolate_age(age)
    #print(age)
    #print(interpolate_age(age))
    # Bmi
    # -For larger bmi shorter Exercise
    multiplier += interpolate_bmi(bmi)
    
    # Normalization    
    if(multiplier < 0):
        multiplier = 0.1
        
    if(multiplier > 2):
        multiplier = 2

    # I round the multiplier to 2 decimals
    return round(multiplier, 2)

# Math functions ----

# Age
x_points_age = np.array([12, 20, 120])
y_points_age = np.array([-0.5, 0.5, -0.5])
interpolation_function_age = interp1d(x_points_age, y_points_age)

def interpolate_age(x):
    if x < 12 or x > 120:
        raise ValueError("The input is out of the allowed range [12, 120].")

    # Calc the value
    y_value = interpolation_function_age(x)

    return y_value

#BMI
x_points_bmi = np.array([0, 10, 18, 24, 40, 50])
y_points_bmi = np.array([-0.5, -0.5, 0.5, 0.5, -0.5, -0.5])
interpolation_function_bmi = interp1d(x_points_bmi, y_points_bmi, kind='quadratic')

def interpolate_bmi(x):
    if x <= 0:
        raise ValueError("The input needs to be positive.")
    # Extremly large BMI
    elif x > 45 or x < 5:
        return -0.6

    # Calc the value
    y_value = interpolation_function_bmi(x)

    return y_value

# stats

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

def get_stats_of_the_week(user_id,monday_date):
    week_data = []
    
    for i in range(7):
        current_date = monday_date + timedelta(days=i)
        performances = UserDailyPerformance.objects.filter(user=user_id, date=current_date)
            
        # Format the result for each day
        if performances.exists():
            day_data = list(performances.values())
        else:
            day_data = [{}]  # Empty dictionary for days with no data
            
        week_data.append({
            'date': current_date.isoformat(),
            'dailyReportData': day_data
        })
        
    return week_data

def get_all_daily_stats_query(user_id):
    # One specific query for performance
    performances = UserDailyPerformance.objects.filter(user=user_id).values(
        'date', 'calorie_intake', 'time_working_out_sec', 'calories_burnt'
    ).order_by('date')
    
    return performances

def get_all_daily_stats_csv(user_id):
    performances = get_all_daily_stats_query(user_id)
    # Create a buffer to hold the CSV data
    buffer = io.StringIO()
    
    # Create a CSV writer
    writer = csv.writer(buffer)
    
    # Write the header
    writer.writerow(['date', 'calorie_intake', 'time_working_out_sec', 'calories_burnt'])
    
    # Write the data rows
    for performance in performances:
        writer.writerow([
            performance['date'].isoformat(),
            performance['calorie_intake'],
            performance['time_working_out_sec'],
            performance['calories_burnt']
        ])
    
    # Return the buffer's content as a string
    return buffer.getvalue()

def get_all_daily_stats_pdf(user_id):
    performances = get_all_daily_stats_query(user_id)
    
    # Create a buffer to hold the PDF data
    buffer = io.BytesIO()
    
    # Create a canvas
    c = canvas.Canvas(buffer, pagesize=letter)
    width, height = letter
    
    # Set the title and headers
    c.drawString(100, height - 40, "Daily Stats Report")
    c.drawString(100, height - 60, "Date")
    c.drawString(200, height - 60, "Calorie Intake")
    c.drawString(300, height - 60, "Time Working Out (sec)")
    c.drawString(450, height - 60, "Calories Burnt")
    
    # Write the data rows
    y = height - 80
    for performance in performances:
        c.drawString(100, y, performance['date'].isoformat())
        c.drawString(200, y, str(performance['calorie_intake']))
        c.drawString(300, y, str(performance['time_working_out_sec']))
        c.drawString(450, y, str(performance['calories_burnt']))
        y -= 20
    
    # Save the PDF
    c.showPage()
    c.save()
    
    # Move the buffer position to the beginning
    buffer.seek(0)
    
    # Return the buffer's content as a byte string
    return buffer.getvalue()