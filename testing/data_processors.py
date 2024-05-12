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

def process_add_eaten_calorie_data(request):
    calorie_data = request.data.get('calorie_data', {})
    if not calorie_data.get('calories'):
        raise ValueError('Calories count is required')
    
    cal = calorie_data.get('calories')
    add_user_d_cal_eaten(request.user.id,cal)
    
    return {'calories': cal}

def process_wourout_done(request):
    calorie_data = request.data.get('calorie_data', {})
    if not calorie_data.get('calories'):
        raise ValueError('Calories count is required')
    
    cal = calorie_data.get('calories')
    add_user_d_cal_burnt(request.user.id,cal)
    
    return {'calories': cal}