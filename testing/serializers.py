from rest_framework import serializers
from django.contrib.auth.models import User
import re

from .models import UserProfile,Workout,Exercise,UserWorkout

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['user','gender', 'experiencelevel', 'age', 'weight', 'height']
        
    def validate_gender(self, value):
        if value not in ["MALE", "FEMALE", "OTHER"]:
            raise serializers.ValidationError("Invalid user Gender value.")
        return value

    def validate_experiencelevel(self, value):
        if value not in ["NEW", "INTERMEDIATE", "EXPERIENCED", "PROFESSIONAL"]:
            raise serializers.ValidationError("Invalid user Experience value.")
        return value

    def validate_age(self, value):
        if value < 12 or value > 120:
            raise serializers.ValidationError("Invalid user age.")
        return value

    def validate_weight(self, value):
        if value < 20.0 or value > 500.0:
            raise serializers.ValidationError("Invalid user weight.")
        return value

    def validate_height(self, value):
        if value < 50.0 or value > 251.0:
            raise serializers.ValidationError("Invalid user height.")
        return value

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}  # Making password write-only
        
    def validate_email(self, value):
        pattern = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(pattern, value):
            raise serializers.ValidationError("Invalid email format")
        
        # Check if the email already exists
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("The given e-mail is already in use.")
        
        return value

    def validate_username(self, value):
        if len(value) < 2:
            raise serializers.ValidationError("Username must be at least 2 characters long!")
        return value
    
    def validate_password(self, value):
        if len(value) < 6:
            raise serializers.ValidationError("Password must be at least 6 characters long")
        return value
    
class WorkoutSerializer(serializers.ModelSerializer):
    exercises = serializers.SerializerMethodField()

    class Meta:
        model = Workout
        fields = '__all__'

    def get_exercises(self, obj):
        # Az exercise_order mező alapján iterálunk
        exercise_ids = obj.exercise_order
        exercises = [Exercise.objects.get(pk=exercise_id) for exercise_id in exercise_ids]
        return ExerciseSerializer(exercises, many=True).data

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = '__all__'
        
class UserWorkoutSerializer(serializers.ModelSerializer):
    workout = WorkoutSerializer()
    #workout_id = serializers.CharField(source='workout.workoutid')

    class Meta:
        model = UserWorkout
        fields = ['id','workout', 'weights', 'do_weekly']
