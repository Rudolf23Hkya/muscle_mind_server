from django.contrib import admin
from .models import *
# Register your models here.

admin.site.register(UserProfile)
admin.site.register(Exercise)
admin.site.register(Workout)
admin.site.register(UserDailyPerformance)
admin.site.register(UserWorkout)
admin.site.register(UserWorkoutHistory)
admin.site.register(WorkoutExercise)