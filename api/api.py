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
            page = int(request.query_params.get('page', 1))
            page_size = int(request.query_params.get('page_size', 50))
          
            offset = (page - 1) * page_size
            
            total_games = games.count()
            
            games_paginated = games[offset:offset + page_size]
            
            total_pages = (total_games + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            serializer = GameSerializer(games_paginated, many=True)
            return Response({
                'success': True,
                'data': {
                    "games": serializer.data,
                    "pagination": {
                        'current_page': page,
                        'page_size': page_size,
                        'total_games': total_games,
                        'total_pages': total_pages,
                        'has_next': has_next,
                        'has_previous': has_previous,
                    }
                }
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
            if 'hide_owned' in filters:
                hide_owned = filters.get('hide_owned').lower() == 'true'
                if hide_owned:
                    if request.user.is_authenticated:
                        user = request.user
                        owned_games = shopping_models.OwnedGame.objects.filter(user=user).values_list('game_id', flat=True)
                        games = games.exclude(id__in=owned_games)
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

            page = int(filters.get('page', 1))
            page_size = int(filters.get('page_size', 50))
            
            offset = (page - 1) * page_size
            
            total_games = games.count()
            
            games = games[offset:offset + page_size]
            
            total_pages = (total_games + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
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
        
        serializer = GameSerializer(games, many=True)
        return Response({
            'success': True,
            'data': {
                'games': serializer.data,
                'pagination': {
                    'current_page': page if 'page' in filters else 1,
                    'page_size': page_size if 'page_size' in filters else len(serializer.data),
                    'total_games': total_games if 'page' in filters else len(serializer.data),
                    'total_pages': total_pages if 'page' in filters else 1,
                    'has_next': has_next if 'page' in filters else False,
                    'has_previous': has_previous if 'page' in filters else False,
                }
            }
        })
    
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
    
class SearchSuggestions(APIView):
    permission_classes = []

    def get(self, request):
        query = request.query_params.get('query', '')
        if not query:
            return Response({
                'success': False,
                'message': 'Query parameter is required.'
            }, status=400)

        games = shopping_models.Game.objects.filter(title__icontains=query)[:10]
        suggestions = []
        for game in games:
            suggestions.append({
                'id': game.id,
                'title': game.title
            })

        return Response({
            'success': True,
            'data': suggestions
        })

class CreateOrder(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user
        game_ids = request.data.get('game_ids', [])
        
        if not game_ids:
            return Response({
                'success': False,
                'message': 'Game IDs are required.'
            }, status=400)
        
        if not isinstance(game_ids, list):
            return Response({
                'success': False,
                'message': 'Game IDs must be provided as a list.'
            }, status=400)
        
        try:
            games = shopping_models.Game.objects.filter(id__in=game_ids)
            
            if len(games) != len(game_ids):
                return Response({
                    'success': False,
                    'message': 'One or more games not found.'
                }, status=404)
            
            owned_games = shopping_models.OwnedGame.objects.filter(
                user=user, 
                game__in=games
            ).values_list('game_id', flat=True)
            
            if owned_games:
                owned_game_titles = games.filter(id__in=owned_games).values_list('title', flat=True)
                return Response({
                    'success': False,
                    'message': f'You already own the following games: {", ".join(owned_game_titles)}'
                }, status=400)
            
            total_amount = 0
            for game in games:
                if game.is_sale and game.sale_price:
                    total_amount += game.sale_price
                else:
                    total_amount += game.price
            
            order = shopping_models.Order.objects.create(
                user=user,
                total_amount=total_amount,
                is_completed=True
            )
            
            order.games.set(games)
            
            owned_game_objects = [
                shopping_models.OwnedGame(user=user, game=game)
                for game in games
            ]
            shopping_models.OwnedGame.objects.bulk_create(owned_game_objects)
            
            shopping_models.CartItem.objects.filter(
                user=user, 
                game__in=games
            ).delete()
            
            return Response({
                'success': True,
                'data': {
                    'order_id': order.id,
                    'total_amount': float(order.total_amount),
                    'order_date': order.order_date,
                    'games_purchased': [game.title for game in games]
                },
                'message': 'Order created successfully!'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating order: {str(e)}'
            }, status=500)