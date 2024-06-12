from django.urls import path
from .views import RegistrationAPIView, RoutineView, LoginAPIView,  ExerciseView, ExerciseToRoutine

app_name = 'exercise'
urlpatterns = [
    path('register/',  RegistrationAPIView.as_view(), name='register'),
    path('login/', LoginAPIView.as_view(), name='login'),

    path('addexercise/', ExerciseView.as_view(), name='add_exercise'),
    path('exercises/', ExerciseView.as_view(), name='exercise_list'),
    path('exercise_delete/<int:pk>/', ExerciseView.as_view(), name='exercise_delete'),
    path('exercise_update/<int:pk>/', ExerciseView.as_view(), name='exercise_detail'),
    path('addroutine/', RoutineView.as_view(), name='create_routine'),
    path('getroutine/', RoutineView.as_view(), name='create_routine'),
    path('addexerciseroutine/', ExerciseToRoutine.as_view(), name='create_routine'),
    path('updateexerciseroutine/<int:exercise_id>/<int:routine_id>/', ExerciseToRoutine.as_view(), name='create_routine'),
    path('deleteroutine/<int:pk>/', ExerciseToRoutine.as_view(), name='create_routine'),
]
