# Generated by Django 5.0.3 on 2024-04-15 18:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('testing', '0002_testingexercise_user_userdailyperformance_and_more'),
    ]

    operations = [
        migrations.DeleteModel(
            name='TestingExercise',
        ),
        migrations.AlterModelTable(
            name='exercise',
            table='exercise',
        ),
    ]
