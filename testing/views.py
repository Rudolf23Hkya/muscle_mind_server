from django.shortcuts import render
from django.db import connection


def exercise_list(request):
    with connection.cursor() as cursor:
        cursor.execute("SELECT * FROM exercise")
        exercises = cursor.fetchall()
        return render(request, 'exercise_list.html', {'exercises': exercises})
