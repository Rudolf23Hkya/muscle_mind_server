from enum import Enum
from django.db import models
import psycopg2
from django.contrib.postgres.fields import ArrayField

#ENUM DEF
class Category(Enum):
    WEIGHTLIFTING = 'WEIGHTLIFTING'
    TRX = 'TRX'
    CARDIO = 'CARDIO'
    WARMUP = 'WARMUP'
    OWN_BODY_WEIGHT = 'OWN_BODY_WEIGHT'
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class ExperienceLevel(Enum):
    NEW = 'NEW'
    INTERMEDIATE = 'INTERMEDIATE'
    EXPERIENCED = 'EXPERIENCED'
    PROFESSIONAL = 'PROFESSIONAL'
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class Gender(Enum):
    MALE = 'MALE'
    FEMALE = 'FEMALE'
    OTHER = 'OTHER'
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]

class MuscleGroup(Enum):
    LOWER_BODY = 'LOWER_BODY'
    UPPER_BODY = 'UPPER_BODY'
    ABS = 'ABS'
    BACK = 'BACK'
    
    @classmethod
    def choices(cls):
        return [(item.value, item.name) for item in cls]
    
#DATA ORM-s
class Exercise(models.Model):
    exerciseid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255)
    category = models.CharField(max_length=50, choices=Category.choices())
    musclegroup = models.CharField(max_length=50, choices=MuscleGroup.choices())
    experiencelevel = models.CharField(max_length=50, choices=ExperienceLevel.choices())
    duration = models.IntegerField()
    caloriesburnt = models.IntegerField()
    drawablepicname = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'exercise'


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    sessiontoken = models.TextField()
    email = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=50)
    password = models.TextField()
    gender = models.CharField(max_length=50, choices=Gender.choices())
    experiencelevel = models.CharField(max_length=50, choices=ExperienceLevel.choices())
    age = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.email

    class Meta:
        managed = False
        db_table = 'user'

class Workout(models.Model):
    workoutid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    experiencelevel = models.CharField(max_length=50, choices=ExperienceLevel.choices())
    drawablepicname = models.CharField(max_length=255)
    
    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'workout'


class UserDailyPerformance(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(User, models.DO_NOTHING)
    date = models.DateField()
    calorie_intake = models.IntegerField()
    hydration_ml = models.IntegerField()
    time_logged_in_minutes = models.IntegerField()
    time_working_out_minutes = models.IntegerField()
    
    def __str__(self):
        return self.date + " " + self.user

    class Meta:
        managed = False
        db_table = 'user_daily_performance'


class UserWorkout(models.Model):
    user = models.OneToOneField(User, models.DO_NOTHING,primary_key=True)
    workout = models.ForeignKey(Workout, models.DO_NOTHING)
    
    def __str__(self):
        return self.user + " - " + self.workout

    class Meta:
        managed = False
        db_table = 'user_workout'
        # Composite primary key constraint (user_id, workout_id)
        unique_together = (('user_id', 'workout_id'),)

#Just the workouts
class UserWorkoutHistory(models.Model):
    workout_history_id = models.AutoField(primary_key=True)
    daily_performance = models.ForeignKey(UserDailyPerformance, models.DO_NOTHING)
    workout = models.OneToOneField(Workout, models.DO_NOTHING)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()
    
    def __str__(self):
        return self.workout + "dur: " + self.duration_minutes

    class Meta:
        managed = False
        db_table = 'user_workout_history'


class WorkoutExercise(models.Model):
    workout = models.OneToOneField(Workout, on_delete=models.DO_NOTHING, primary_key=True)
    exercise = models.ForeignKey(Exercise, models.DO_NOTHING)
    exercise_order = ArrayField(models.IntegerField(),default=list)
    
    def __str__(self):
        return self.workout + " - " + self.exercise + "ord: " + self.exercise_order

    class Meta:
        managed = False
        db_table = 'workout_exercise'
        # Composite primary key constraint (userid, workoutid)
        unique_together = (('workout_id', 'exercise_id'),)