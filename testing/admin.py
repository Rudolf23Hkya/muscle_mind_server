from django.contrib import admin
from .models import *
from .custom_forms import *

admin.site.register(UserProfile)
admin.site.register(Exercise)
admin.site.register(UserDailyPerformance)
admin.site.register(UserWorkout)
admin.site.register(UserWorkoutHistory)
admin.site.register(WorkoutExercise)
admin.site.register(Disease)
admin.site.register(Workout)
'''
class WorkoutAdmin(admin.ModelAdmin):
    form = WorkoutForm
    
# Registering the Workout model with the WorkoutAdmin class
admin.site.register(Workout, WorkoutAdmin)
'''