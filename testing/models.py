from enum import Enum
from django.db import models
from django.contrib.postgres.fields import ArrayField
from django.contrib.auth.models import User

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

    # Used for workout recommendation(+1 level max)
    @classmethod
    def get_allowed_levels(cls, current_level):
        levels = list(cls)
        allowed_levels = []
        current_index = levels.index(cls[current_level])

        # Add all lower and current levels
        for level in levels[:current_index + 1]:
            allowed_levels.append(level.value)
        
        # Add the next level if it exists
        if current_index + 1 < len(levels):
            allowed_levels.append(levels[current_index + 1].value)

        return allowed_levels
        # New method to get the numeric value
    @classmethod
    def get_num(cls, level):
        level_map = {
            cls.NEW: 0,
            cls.INTERMEDIATE: 1,
            cls.EXPERIENCED: 2,
            cls.PROFESSIONAL: 3
        }
        return level_map.get(level, None)

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
    caloriesburnt = models.IntegerField()
    drawablepicname = models.CharField(max_length=255)
    reps = models.IntegerField(null=True, blank=True)
    duration = models.IntegerField(null=True, blank=True)
    
    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'exercise'

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE,primary_key=True, related_name='profile',db_column='id')
    gender = models.CharField(max_length=50, choices=Gender.choices())
    experiencelevel = models.CharField(max_length=50, choices=ExperienceLevel.choices())
    age = models.IntegerField()
    weight = models.DecimalField(max_digits=10, decimal_places=2)
    height = models.DecimalField(max_digits=10, decimal_places=2)
    
    def __str__(self):
        return self.user.email

    class Meta:
        managed = False
        db_table = 'user'

class Workout(models.Model):
    workoutid = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=50)
    experiencelevel = models.CharField(max_length=50, choices=ExperienceLevel.choices())
    drawablepicname = models.CharField(max_length=255)
    musclegroup = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    category = ArrayField(
        models.CharField(max_length=100),
        blank=True,
        default=list
    )
    exercise_order = ArrayField(
        models.IntegerField(),
        blank=True,
        default=list
    )
    def save(self, *args, **kwargs):
        # Convert to uppercase
        self.name = self.name
        self.experiencelevel = self.experiencelevel
        self.drawablepicname = self.drawablepicname
        self.musclegroup = [mg.upper() for mg in self.musclegroup]
        self.category = [cat.upper() for cat in self.category]

        # Validate musclegroup and category
        valid_musclegroups = {item.value for item in MuscleGroup}
        valid_categories = {item.value for item in Category}

        for mg in self.musclegroup:
            if mg not in valid_musclegroups:
                raise ValueError(f"Invalid musclegroup value: {mg}")

        for cat in self.category:
            if cat not in valid_categories:
                raise ValueError(f"Invalid category value: {cat}")

        # Call the original save method
        super(Workout, self).save(*args, **kwargs)
    
    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'workout'

class UserDailyPerformance(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, models.DO_NOTHING)
    date = models.DateField()
    calorie_intake = models.IntegerField()
    time_working_out_sec = models.IntegerField()
    calories_burnt = models.IntegerField()
    
    def __str__(self):
        return f"{self.date} {self.user}"

    class Meta:
        managed = False
        db_table = 'user_daily_performance'


class UserWorkout(models.Model):
    id = models.BigAutoField(primary_key=True)
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE,db_column='user_id')
    workout = models.ForeignKey(Workout, on_delete=models.CASCADE,db_column='workout_id')
    weights = ArrayField(models.FloatField(), default=list)
    do_weekly = models.IntegerField()
    
    def __str__(self):
        return self.user.user.username + " - " + self.workout.name

    class Meta:
        managed = False
        db_table = 'user_workout'


class WorkoutExercise(models.Model):
    id = models.BigAutoField(primary_key=True)
    workout = models.ForeignKey(Workout, on_delete=models.DO_NOTHING)
    exercise = models.ForeignKey(Exercise, models.DO_NOTHING)
    
    def __str__(self):
        return self.workout.name + " - " + self.exercise.name

    class Meta:
        managed = False
        db_table = 'workout_exercise'
        unique_together = ('workout', 'exercise')

class Disease(models.Model):
    user = models.OneToOneField(UserProfile, on_delete=models.CASCADE, primary_key=True)
    cardiovascular_d = models.BooleanField(default=False)
    bad_knee = models.BooleanField(default=False)
    asthma = models.BooleanField(default=False)
    osteoporosis = models.BooleanField(default=False)
    
    def __str__(self):
        return self.user.user.username + "'s diseases"

    class Meta:
        managed = False
        db_table = 'disease'