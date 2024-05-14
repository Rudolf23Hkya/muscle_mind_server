from django import forms
from django.contrib.postgres.forms import SimpleArrayField
from .models import Workout, MuscleGroup
'''
class WorkoutForm(forms.ModelForm):
    musclegroup = SimpleArrayField(forms.ChoiceField(choices=MuscleGroup.choices))
    exercise_order = SimpleArrayField(forms.IntegerField())

    class Meta:
        model = Workout
        fields = '__all__'
        
'''