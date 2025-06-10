from django.urls import path
from .api import *

app_name = 'api'

urlpatterns = [
    path('user/', UserView.as_view(), name='user'),
    path('all-games/', AllGameInfo.as_view(), name='all_games'), 
    path('cart/edit/', EditGameCart.as_view(), name='add_game_to_cart'),
]