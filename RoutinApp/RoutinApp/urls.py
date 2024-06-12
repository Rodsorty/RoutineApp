
# En urls.py del proyecto
from django.urls import path, include

urlpatterns = [
    path('routinapp/', include('Exercises.url'))
]
