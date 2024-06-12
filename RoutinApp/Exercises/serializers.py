from rest_framework import serializers
from .models import Exercise, Routine, RoutineExercise

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        exclude = ['user']  # Excluir el campo 'user' del serializer

class updateExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = "__all__"

class ExerciseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Exercise
        fields = ['id', 'name', 'description', 'muscle_group', 'difficulty_level', 'equipment_needed', 'image']

class RoutineSerializer(serializers.ModelSerializer):
    class Meta:
        model = Routine
        exclude = ['user']  # Excluir el campo 'user' del serializer

    def create(self, validated_data):
        # Antes de crear la rutina, asigna el usuario autenticado al campo 'user'
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class RoutineWithExercisesSerializer(serializers.ModelSerializer):
    exercises = serializers.SerializerMethodField()  # Custom field to include 'done'

    class Meta:
        model = Routine
        fields = ['id', 'date', 'exercises']

    def get_exercises(self, obj):
        routine_exercises = obj.routineexercise_set.all().order_by('id')  # Fetch all related RoutineExercise objects
        return RoutineExerciseSerializer(routine_exercises, many=True).data



class RoutineExerciseSerializer(serializers.ModelSerializer):
    exercise_details = serializers.SerializerMethodField()

    class Meta:
        model = RoutineExercise
        fields = ['id','done', 'actions', 'notes', 'exercise_details']

    def get_exercise_details(self, obj):
        exercise = obj.exercise
        return {
            "id": exercise.id,
            "name": exercise.name,
            "description": exercise.description,
            "muscle_group": exercise.muscle_group,
            "difficulty_level": exercise.difficulty_level,
            "equipment_needed": exercise.equipment_needed,
        }
