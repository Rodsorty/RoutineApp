# En myapp/views.py
from rest_framework.decorators import api_view, permission_classes
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from .serializers import ExerciseSerializer, updateExerciseSerializer, ExerciseSerializer, Routine, RoutineExerciseSerializer, RoutineWithExercisesSerializer
from rest_framework import generics
from rest_framework import filters
from django.http import JsonResponse
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from .models import Exercise, RoutineExercise
from .models import Routine
from datetime import datetime
from rest_framework.authentication import TokenAuthentication




class RegistrationAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        if username and password:
            if not User.objects.filter(username=username).exists():
                user = User.objects.create_user(username=username, password=password)
                refresh = RefreshToken.for_user(user)
                return Response({
                    'refresh': str(refresh),
                    'access': str(refresh.access_token),
                }, status=status.HTTP_201_CREATED)
            else:
                return Response({'error': 'Username already exists'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Username and password are required'}, status=status.HTTP_400_BAD_REQUEST)



class LoginAPIView(APIView):
    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')
        user = authenticate(username=username, password=password)
        if user:
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token),
            })
        else:
            return Response({'error': 'Invalid credentials'}, status=status.HTTP_401_UNAUTHORIZED)






class ExerciseView(APIView):

    @permission_classes([IsAuthenticated])
    def post(self, request):
        serializer = ExerciseSerializer(data=request.data)
        if serializer.is_valid():
            # Asignar el usuario autenticado al ejercicio
            serializer.validated_data['user'] = request.user
            exercise = serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


    def get(self, request):
        queryset = Exercise.objects.all()

        # Aplicar filtros
        name = request.GET.get('name') or ''
        muscle = request.GET.get('muscle') or ''

        if name:
            queryset = queryset.filter(name__icontains=name)
        if muscle:
            queryset = queryset.filter(muscle_group__icontains=muscle)

        queryset = queryset.order_by('name') 
        paginator = Paginator(queryset, 10)
        page_number = request.GET.get('page', 1)

        try:
            exercises = paginator.page(page_number)
        except EmptyPage:
            exercises = paginator.page(paginator.num_pages)
        except PageNotAnInteger:
            exercises = paginator.page(1)

        # Número total de registros
        total_records = paginator.count
        serialized_exercises = ExerciseSerializer(exercises, many=True)

        # Agregar el número total de registros a los datos de respuesta
        response_data = {
            'total_records': total_records,
            'exercises': serialized_exercises.data
        }

        return Response(response_data)



    def put(self, request, pk):
        try:
            exercise = Exercise.objects.get(pk=pk)
            serializer = updateExerciseSerializer(
                exercise, data=request.data, partial=True
            )
            if serializer.is_valid():
                serializer.save()
                return Response(data=serializer.data, status = status.HTTP_200_OK)
            return Response(data=serializer.errors, status = status.HTTP_400_BAD_REQUEST)
        except Exercise.DoesNotExist:
            return Response({'error': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)


    def delete(self, request, pk):
        try:
            exercise = Exercise.objects.get(pk=pk)
            exercise.delete()
            return Response({'message': 'Exercise deleted successfully'})
        except Exercise.DoesNotExist:
            return Response({'error': 'Exercise not found'}, status=status.HTTP_404_NOT_FOUND)


class RoutineView(APIView):
    @permission_classes([IsAuthenticated])
    def post(self, request):
        fecha = request.data.get('date', None)
        exercises_data = request.data.get('exercises', [])

        if fecha:
            try:
                fecha_datetime = datetime.strptime(fecha, '%Y-%m-%d').date()
            except ValueError:
                return Response({'error': 'Formato de fecha incorrecto'}, status=status.HTTP_400_BAD_REQUEST)
        else:
            return Response({'error': 'Se requiere la fecha'}, status=status.HTTP_400_BAD_REQUEST)

        # Verificar si ya existe una rutina con la misma fecha
        if Routine.objects.filter(date=fecha_datetime).exists():
            return Response({'error': 'Ya existe una rutina para esta fecha'}, status=status.HTTP_400_BAD_REQUEST)

        # Obtiene el usuario autenticado
        user = request.user

        # Crea la rutina asignándole el usuario
        rutina = Routine.objects.create(user=user, date=fecha_datetime)

        if exercises_data:
            exercise_serializer = ExerciseSerializer(data=exercises_data, many=True)
            if exercise_serializer.is_valid():
                for exercise in exercise_serializer.validated_data:
                    exercise['user'] = user  # Asigna el usuario a cada ejercicio
                created_exercises = exercise_serializer.save()
            else:
                rutina.delete()  # Elimina la rutina creada si hay errores en los ejercicios
                return Response(exercise_serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        return Response({'message': 'Rutina creada exitosamente'}, status=status.HTTP_201_CREATED)


    def get(self, request):
        routines = Routine.objects.all()
        date = request.GET.get('date') or ''

        if date:
            routines = routines.filter(date=date)

        # Fetching related RoutineExercise instances and passing them to serializer
        for routine in routines:
            routine.exercises_with_done = routine.routineexercise_set.all()

        serializer = RoutineWithExercisesSerializer(routines, many=True)
        return Response(serializer.data)

class ExerciseToRoutine(APIView):
    def post(self, request):
        # Obtener los datos del request
        exercise_id = request.data.get('exercise_id')
        done = request.data.get('done')
        notes = request.data.get('notes')
        actions = request.data.get('actions')
        routine_id = request.data.get('routine_id')

 

        # Verificar si el ejercicio y la rutina existen
        try:
            exercise = Exercise.objects.get(pk=exercise_id)
            routine = Routine.objects.get(pk=routine_id)
        except Exercise.DoesNotExist:
            return Response({'error': 'El ejercicio no existe'}, status=status.HTTP_404_NOT_FOUND)
        except Routine.DoesNotExist:
            return Response({'error': 'La rutina no existe'}, status=status.HTTP_404_NOT_FOUND)

        # Crear la relación entre el ejercicio y la rutina
        routine_exercise = RoutineExercise.objects.create(
            routine=routine,
            exercise=exercise,
            done=done,
            notes=notes,
            actions=actions
        )

        # Serializar y devolver la relación creada
        serializer = RoutineExerciseSerializer(routine_exercise)
        return Response(serializer.data, status=status.HTTP_201_CREATED)


    def put(self, request, exercise_id, routine_id):
        # Obtener los datos del request
        done = request.data.get('done')
        notes = request.data.get('notes')
        actions = request.data.get('actions')

        # Verificar si la relación entre ejercicio y rutina existe
        try:
            routine_exercise = RoutineExercise.objects.get(pk=exercise_id)
        except RoutineExercise.DoesNotExist:
            return Response({'error': 'La relación entre ejercicio y rutina no existe'}, status=status.HTTP_404_NOT_FOUND)

        # Actualizar los campos especificados si no son None
        if done is not None:
            routine_exercise.done = done
        if notes is not None:
            routine_exercise.notes = notes
        if actions is not None:
            routine_exercise.actions = actions

        # Guardar los cambios
        try:
            routine_exercise.save()
        except Exception as e:
            # Manejar errores de guardado aquí
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

        # Devolver solo el código de estado 200 OK si todo está bien
        return Response(status=status.HTTP_200_OK)


    def delete(self, request, pk):
        try:
            exercise = Routine.objects.get(pk=pk)
            exercise.delete()
            return Response({'message': 'Routine deleted successfully'})
        except Exercise.DoesNotExist:
            return Response({'error': 'Routine not found'}, status=status.HTTP_404_NOT_FOUND)

