from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import *

from users import models as user_models
from shopping import models as shopping_models

import time
class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        
        cart_items = shopping_models.CartItem.objects.filter(user=user)
        cart_subtotal = sum(item.game.price * item.quantity for item in cart_items)
        
        return Response({
            'success': True,
            'data': {
                **serializer.data,
                'cart_subtotal': cart_subtotal
            }
        })

class AllGameInfo(APIView):
    permission_classes = []

    def get(self, request):
        filters = request.query_params
        games = shopping_models.Game.objects.all()

        if not filters:
            serializer = BasicGameSerializer(games, many=True)
            return Response({
                'success': True,
                'data': serializer.data
            })
        
        try:
            if 'platform' in filters:
                platform = filters.get('platform')
                games = games.filter(platforms__name=platform)
            if 'genre' in filters:
                genre = filters.get('genre')
                games = games.filter(genres__name=genre)
            if 'is_sale' in filters:
                is_sale = filters.get('is_sale').lower() == 'true'
                if is_sale:
                    games = games.filter(is_sale=is_sale)
            if 'sort_by' in filters:
                sort_by = filters.get('sort_by')
                if sort_by == 'price_asc':
                    games = games.order_by('price')
                elif sort_by == 'price_desc':
                    games = games.order_by('-price')
                elif sort_by == 'release_date':
                    games = games.order_by('-release_date')
                elif sort_by == 'title':
                    games = games.order_by('title')
            if 'search' in filters:
                search_query = filters.get('search')
                games = games.filter(title__icontains=search_query)
            if 'pagination_limit' in filters:
                pagination_limit = int(filters.get('pagination_limit'))
                games = games[:pagination_limit]
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error processing filters: {str(e)}'
            }, status=400)
        
        if not games.exists():
            return Response({
                'success': False,
                'message': 'No games found with the provided filters.'
            }, status=404)
        
        serializer = BasicGameSerializer(games, many=True)
        return Response({
            'success': True,
            'data': serializer.data
        })

        # games = shopping_models.Game.objects.all()
        # serializer = BasicGameSerializer(games, many=True)
        
        # return Response({
        #     'success': True,
        #     'data': serializer.data
        # })
    
class SpecificGameInfo(APIView):
    permission_classes = []

    def post(self, request):
        game_id = request.data.get('game_id')
        
        if not game_id:
            return Response({
                'success': False,
                'message': 'Game ID is required.'
            }, status=400)

        try:
            game = shopping_models.Game.objects.get(id=game_id)
        except shopping_models.Game.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Game not found.'
            }, status=404)

        serializer = GameSerializer(game)
        
        return Response({
            'success': True,
            'data': serializer.data
        })

class EditGameCart(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        game_id = request.data.get('game_id')
        
        if not game_id:
            return Response({
                'success': False,
                'message': 'Game ID is required.'
            }, status=400)

        try:
            game = shopping_models.Game.objects.get(id=game_id)
        except shopping_models.Game.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Game not found.'
            }, status=404)
        
        owned_games = shopping_models.OwnedGame.objects.filter(user=user, game=game)
        if owned_games.exists():
            return Response({
                'success': False,
                'message': 'Game is already owned.'
            }, status=400)

        if shopping_models.CartItem.objects.filter(user=user, game=game).exists():
            return Response({
                'success': False,
                'message': 'Game is already in the cart.'
            }, status=400)

        shopping_models.CartItem.objects.create(user=user, game=game)

        cart_items = shopping_models.CartItem.objects.filter(user=user)
        cart_serializer = BasicUserCartItemSerializer(cart_items, many=True)
        
        return Response({
            'success': True,
            'data': cart_serializer.data,
            'message': 'Game added to cart successfully.'
        })
    
    def delete(self, request):
        user = request.user
        game_id = request.data.get('game_id')
        
        if not game_id:
            return Response({
                'success': False,
                'message': 'Game ID is required.'
            }, status=400)

        try:
            cart_item = shopping_models.CartItem.objects.get(user=user, game__id=game_id)
            cart_item.delete()
        except shopping_models.CartItem.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Game not found in cart.'
            }, status=404)

        cart_items = shopping_models.CartItem.objects.filter(user=user)
        cart_serializer = BasicUserCartItemSerializer(cart_items, many=True)
        
        return Response({
            'success': True,
            'data': cart_serializer.data,
            'message': 'Game removed from cart successfully.'
        })
    
class ViewCart(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        cart_items = shopping_models.CartItem.objects.filter(user=user)
        cart_subtotal = sum(item.game.price * item.quantity for item in cart_items)

        serializer = CartDetailItemSerializer(cart_items, many=True)
        
        return Response({
            'success': True,
            'data': {
                'cart_items': serializer.data,
                'cart_subtotal': cart_subtotal
            }
        })
    
class OwnedGamesView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        owned_games = shopping_models.OwnedGame.objects.filter(user=user)
        
        serializer = OwnedGameSerializer(owned_games, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })