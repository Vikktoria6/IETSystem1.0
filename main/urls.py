from django.urls import path
from . import views

urlpatterns = [
    path ('', views.index, name = 'main') ,
    path('electives', views.electives, name = 'electives'),
    path('trajectory', views.trajectory, name = 'trajectory')
] 
