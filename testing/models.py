# This is an auto-generated Django model module.
# You'll have to do the following manually to clean this up:
#   * Rearrange models' order
#   * Make sure each model has one field with primary_key=True
#   * Make sure each ForeignKey and OneToOneField has `on_delete` set to the desired behavior
#   * Remove `managed = False` lines if you wish to allow Django to create, modify, and delete the table
# Feel free to rename the models, but don't rename db_table values or field names.
from django.db import models
import psycopg2


#ENUM DEF
class EnumField(models.Field):
    def __init__(self, enum_type, *args, **kwargs):
        self.enum_type = enum_type
        super().__init__(*args, **kwargs)

    def db_type(self, connection):
        if connection.vendor == 'postgresql':
            return self.enum_type
        return 'text'

    def from_db_value(self, value, expression, connection):
        if value is None:
            return value
        return value

    def to_python(self, value):
        if isinstance(value, psycopg2.extensions.AsIs):
            value = value.adapted
        return value
#DATA ORM-s

class Exercise(models.Model):
    exerciseid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=255, blank=False, null=True)
    category = EnumField(enum_type='category', blank=False, null=True)
    musclegroup = EnumField(enum_type='muscle_group', blank=False, null=True)
    experiencelevel = EnumField(enum_type='experience_level', blank=False, null=True)
    duration = models.IntegerField(blank=False, null=True)
    caloriesburnt = models.IntegerField(blank=False, null=True)
    drawablepicname = models.CharField(max_length=255, blank=False, null=True)

    class Meta:
        managed = False
        db_table = 'exercise'


class TestingExercise(models.Model):
    id = models.BigAutoField(primary_key=True)
    category = models.CharField(max_length=100)
    muscle_group = models.CharField(max_length=100)
    experience_level = models.CharField(max_length=100)
    duration = models.IntegerField()
    calories_burnt = models.IntegerField()
    drawablepicname = models.CharField(max_length=255)

    class Meta:
        managed = False
        db_table = 'testing_exercise'


class User(models.Model):
    id = models.BigAutoField(primary_key=True)
    sessiontoken = models.TextField()
    email = models.CharField(unique=True, max_length=255)
    name = models.CharField(max_length=50)
    password = models.TextField()
    gender = EnumField(enum_type='gender', blank=False, null=True)
    experiencelevel = EnumField(enum_type='experience_level', blank=False, null=True)
    age = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)

    class Meta:
        managed = False
        db_table = 'user'


class UserDailyPerformance(models.Model):
    id = models.BigAutoField(primary_key=True)
    user_id = models.ForeignKey(User, models.DO_NOTHING, blank=True, null=True)
    date = models.DateField()
    calorie_intake = models.IntegerField()
    hydration_ml = models.IntegerField()
    time_logged_in_minutes = models.IntegerField()
    time_working_out_minutes = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_daily_performance'


class UserWorkout(models.Model):
    userid = models.OneToOneField(User, models.DO_NOTHING, db_column='userid', primary_key=True)  # The composite primary key (userid, workoutid) found, that is not supported. The first column is selected.
    workoutid = models.ForeignKey('Workout', models.DO_NOTHING, db_column='workoutid')

    class Meta:
        managed = False
        db_table = 'user_workout'
        unique_together = (('userid', 'workoutid'),)


class UserWorkoutHistory(models.Model):
    workout_history_id = models.AutoField(primary_key=True)
    daily_performance = models.ForeignKey(UserDailyPerformance, models.DO_NOTHING, blank=True, null=True)
    workout = models.OneToOneField('Workout', models.DO_NOTHING, blank=True, null=True)
    duration_minutes = models.IntegerField()
    calories_burned = models.IntegerField()

    class Meta:
        managed = False
        db_table = 'user_workout_history'


class Workout(models.Model):
    workoutid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50, blank=True, null=True)
    experiencelevel = EnumField(enum_type='experience_level', blank=False, null=True)
    drawablepicname = models.CharField(max_length=255, blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'workout'


class WorkoutExercise(models.Model):
    workoutid = models.OneToOneField(Workout, models.DO_NOTHING, db_column='workoutid', primary_key=True)  # The composite primary key (workoutid, exerciseid) found, that is not supported. The first column is selected.
    exerciseid = models.ForeignKey(Exercise, models.DO_NOTHING, db_column='exerciseid')
    exercise_order = models.IntegerField(blank=True, null=True)

    class Meta:
        managed = False
        db_table = 'workout_exercise'
        unique_together = (('workoutid', 'exerciseid'),)