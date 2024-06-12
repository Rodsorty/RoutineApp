# En exercises/models.py
from django.contrib.auth.models import User
from django.db import models

class Exercise(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='exercises')
    name = models.CharField(max_length=100, unique=True)
    description = models.TextField()
    muscle_group = models.CharField(max_length=50)
    difficulty_level = models.CharField(max_length=20)
    equipment_needed = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to='exercise_images/', blank=True, null=True)

    def __str__(self):
        return self.name


class Routine(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='routines')
    date = models.DateField(unique=True)
    exercises = models.ManyToManyField(Exercise, through='RoutineExercise', blank= True)

    def __str__(self):
        return str(self.date)

class RoutineExercise(models.Model):
    routine = models.ForeignKey(Routine, on_delete=models.CASCADE)
    exercise = models.ForeignKey(Exercise, on_delete=models.CASCADE)
    done = models.BooleanField(default=False)
    actions = models.CharField(max_length=100, blank=True, null=True)
    notes = models.CharField(max_length=100, blank=True, null=True)

    def __str__(self):
        return f"{self.routine} - {self.exercise}"