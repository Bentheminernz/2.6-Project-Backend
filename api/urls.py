from django.urls import path
from .api import *

app_name = 'api'

urlpatterns = [
    path('user/', UserView.as_view(), name='user'),
]