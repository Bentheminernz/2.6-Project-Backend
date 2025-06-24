from django.urls import path
from .api import *

app_name = 'api'

urlpatterns = [
    path('user/', UserView.as_view(), name='user'),
    path('games/all/', AllGameInfo.as_view(), name='all_games'), 
    path('games/specific/', SpecificGameInfo.as_view(), name='specific_game'),
    path('games/owned/', OwnedGamesView.as_view(), name='owned_games'),
    path('cart/edit/', EditGameCart.as_view(), name='add_game_to_cart'),
    path('cart/view/', ViewCart.as_view(), name='view_cart'),
    path('search/suggestion/', SearchSuggestions.as_view(), name='search_suggestions'),
]