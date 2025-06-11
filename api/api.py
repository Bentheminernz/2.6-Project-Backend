from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.authtoken.models import Token

from .serializers import *

from users import models as user_models
from shopping import models as shopping_models

class UserView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        serializer = UserSerializer(user)
        
        return Response({
            'success': True,
            'data': serializer.data
        })

class AllGameInfo(APIView):
    permission_classes = []

    def get(self, request):
        games = shopping_models.Game.objects.all()
        serializer = BasicGameSerializer(games, many=True)
        
        return Response({
            'success': True,
            'data': serializer.data
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

        if shopping_models.CartItem.objects.filter(user=user, game=game).exists():
            return Response({
                'success': False,
                'message': 'Game is already in the cart.'
            }, status=400)

        shopping_models.CartItem.objects.create(user=user, game=game)

        cart_items = shopping_models.CartItem.objects.filter(user=user)
        cart_serializer = CartItemSerializer(cart_items, many=True)
        
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
        cart_serializer = CartItemSerializer(cart_items, many=True)
        
        return Response({
            'success': True,
            'data': cart_serializer.data,
            'message': 'Game removed from cart successfully.'
        })