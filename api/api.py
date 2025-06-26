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
        order_serializer = OrderCreateSerializer(data=request.data, context={'request': request})
        
        if not order_serializer.is_valid():
            return Response({
                'success': False,
                'message': order_serializer.errors
            }, status=400)

        try:
            validated_data = order_serializer.validated_data
            form_data = validated_data['form_data']
            game_ids = validated_data['game_ids']
            
            games = shopping_models.Game.objects.filter(id__in=game_ids)
            total_amount = order_serializer.calculate_total_amount(games)
            
            order = shopping_models.Order.objects.create(
                user=request.user,
                total_amount=total_amount,
                is_completed=True
            )
            
            # Create OrderItem instances with purchase prices
            order_items = []
            owned_game_objects = []
            
            for game in games:
                # Determine the purchase price (sale price if on sale, otherwise regular price)
                purchase_price = game.sale_price if game.is_sale and game.sale_price else game.price
                
                # Create OrderItem
                order_items.append(
                    shopping_models.OrderItem(
                        order=order,
                        game=game,
                        purchase_price=purchase_price,
                        quantity=1
                    )
                )
                
                # Create OwnedGame
                owned_game_objects.append(
                    shopping_models.OwnedGame(user=request.user, game=game)
                )
            
            shopping_models.OrderItem.objects.bulk_create(order_items)
            shopping_models.OwnedGame.objects.bulk_create(owned_game_objects)
            
            shopping_models.CartItem.objects.filter(
                user=request.user, 
                game__in=games
            ).delete()

            if form_data.get('saveCard', False):
                card_data = form_data.get('cardDetails', {})
                if card_data:
                    card_serializer = CreditCardCreateSerializer(
                        data=card_data, 
                        context={'request': request}
                    )
                    if card_serializer.is_valid():
                        card_serializer.save()

            if form_data.get('saveAddress', False):
                address_data = form_data.get('addressDetails') or form_data.get('address', {})
                if address_data:
                    address_serializer = AddressCreateSerializer(
                        data=address_data, 
                        context={'request': request}
                    )
                    if address_serializer.is_valid():
                        address_serializer.save()
            
            order_response_serializer = OrderSerializer(order)
            return Response({
                'success': True,
                'data': order_response_serializer.data,
                'message': 'Order created successfully!'
            })
            
        except Exception as e:
            return Response({
                'success': False,
                'message': f'Error creating order: {str(e)}'
            }, status=500)
        
class OrderInfoView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        orders = shopping_models.Order.objects.filter(user=user).order_by('-order_date')
        
        if not orders.exists():
            return Response({
                'success': False,
                'message': 'No orders found for this user.'
            }, status=404)
        
        serializer = OrderSerializer(orders, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
        })
    
    def post(self, request):
        order_id = request.data.get('order_id')
        
        if not order_id:
            return Response({
                'success': False,
                'message': 'Order ID is required.'
            }, status=400)

        try:
            order = shopping_models.Order.objects.get(id=order_id, user=request.user)
        except shopping_models.Order.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Order not found.'
            }, status=404)

        serializer = OrderSerializer(order)
        
        return Response({
            'success': True,
            'data': serializer.data
        })