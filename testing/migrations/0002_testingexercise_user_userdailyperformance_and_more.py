# Generated by Django 5.0.3 on 2024-04-13 21:38

import django.contrib.postgres.fields
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='TestingExercise',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('category', models.CharField(max_length=100)),
                ('muscle_group', models.CharField(max_length=100)),
                ('experience_level', models.CharField(max_length=100)),
                ('duration', models.IntegerField()),
                ('calories_burnt', models.IntegerField()),
                ('drawablepicname', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'testing_exercise',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('sessiontoken', models.TextField()),
                ('email', models.CharField(max_length=255, unique=True)),
                ('name', models.CharField(max_length=50)),
                ('password', models.TextField()),
                ('gender', models.CharField(choices=[('MALE', 'MALE'), ('FEMALE', 'FEMALE'), ('OTHER', 'OTHER')], max_length=50)),
                ('experiencelevel', models.CharField(choices=[('NEW', 'NEW'), ('INTERMEDIATE', 'INTERMEDIATE'), ('EXPERIENCED', 'EXPERIENCED'), ('PROFESSIONAL', 'PROFESSIONAL')], max_length=50)),
                ('age', models.IntegerField()),
                ('weight', models.DecimalField(decimal_places=2, max_digits=10)),
                ('height', models.DecimalField(decimal_places=2, max_digits=10)),
            ],
            options={
                'db_table': 'user',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UserDailyPerformance',
            fields=[
                ('id', models.BigAutoField(primary_key=True, serialize=False)),
                ('date', models.DateField()),
                ('calorie_intake', models.IntegerField()),
                ('hydration_ml', models.IntegerField()),
                ('time_logged_in_minutes', models.IntegerField()),
                ('time_working_out_minutes', models.IntegerField()),
            ],
            options={
                'db_table': 'user_daily_performance',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UserWorkout',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
            ],
            options={
                'db_table': 'user_workout',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='UserWorkoutHistory',
            fields=[
                ('workout_history_id', models.AutoField(primary_key=True, serialize=False)),
                ('duration_minutes', models.IntegerField()),
                ('calories_burned', models.IntegerField()),
            ],
            options={
                'db_table': 'user_workout_history',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='Workout',
            fields=[
                ('workoutid', models.AutoField(primary_key=True, serialize=False)),
                ('name', models.CharField(max_length=50, unique=True)),
                ('experiencelevel', models.CharField(choices=[('NEW', 'NEW'), ('INTERMEDIATE', 'INTERMEDIATE'), ('EXPERIENCED', 'EXPERIENCED'), ('PROFESSIONAL', 'PROFESSIONAL')], max_length=50)),
                ('drawablepicname', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'workout',
                'managed': False,
            },
        ),
        migrations.CreateModel(
            name='WorkoutExercise',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('exercise_order', django.contrib.postgres.fields.ArrayField(base_field=models.IntegerField(), default=list, size=None)),
            ],
            options={
                'db_table': 'workout_exercise',
                'managed': False,
            },
        ),
        migrations.AlterModelOptions(
            name='exercise',
            options={'managed': False},
        ),
    ]
