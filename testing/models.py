from django.db import models

class Exercise(models.Model):
    CATEGORY_CHOICES = [
        ('WARMUP', 'Warmup'),
        ('OWN_BODY_WEIGHT', 'Own Body Weight'),
    ]

    MUSCLE_GROUP_CHOICES = [
        ('UPPER_BODY', 'Upper Body'),
        ('LOWER_BODY', 'Lower Body'),
        ('ABS', 'Abs'),
        ('BACK', 'Back'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('NEW', 'New'),
        ('INTERMEDIATE', 'Intermediate'),
        ('EXPERIENCED', 'Experienced'),
        ('PROFESSIONAL', 'Professional'),
    ]

    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    muscle_group = models.CharField(max_length=100, choices=MUSCLE_GROUP_CHOICES)
    experience_level = models.CharField(max_length=100, choices=EXPERIENCE_LEVEL_CHOICES)
    duration = models.IntegerField()
    calories_burnt = models.IntegerField()
    drawablepicname = models.CharField(max_length=255)

    def __str__(self):
        return self.drawablepicname
