from django.shortcuts import render
from django.db import connection

# Create your views here.
from testing.models import Exercise

#def exercise_list(request):
#    exercises = Exercise.objects.all()
#    return render(request, 'exercise_list.html', {'exercises': exercises})

def exercise_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM exercise")
        exercises = cursor.fetchall()
        return render(request, 'exercise_list.html', {'exercises': exercises})
