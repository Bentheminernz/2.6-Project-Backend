from users.models import User
from shopping.models import Game, CartItem
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'cart_items')
        read_only_fields = ('id',)

    def get_cart_items(self, obj):
        cart_items = obj.cart_items.all()
        return CartItemSerializer(cart_items, many=True).data

class GameSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = ('id', 'title', 'description', 'price', 'image')
        read_only_fields = ('id',)

    def get_image(self, obj):
        return obj.return_image_url()
    
class CartItemSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = CartItem
        fields = ('id', 'game', 'quantity', 'added_date')
        read_only_fields = ('id', 'added_date')
