from users.models import User
from shopping.models import Game, CartItem, Platform, Genre, OwnedGame
from rest_framework import serializers

class UserSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'cart_items')
        read_only_fields = ('id',)

    def get_cart_items(self, obj):
        cart_items = obj.cart_items.all()
        return BasicUserCartItemSerializer(cart_items, many=True).data
    
class BasicUserCartItemSerializer(serializers.ModelSerializer):
    game_id = serializers.SerializerMethodField()
    
    class Meta:
        model = CartItem
        fields = ('id', 'game_id')
        read_only_fields = ('id',)
    
    def get_game_id(self, obj):
        return obj.get_game_id()

class PlatformSerializer(serializers.ModelSerializer):
    class Meta:
        model = Platform
        fields = ('id', 'name')
        read_only_fields = ('id',)

class GenreSerializer(serializers.ModelSerializer):
    class Meta:
        model = Genre
        fields = ('id', 'name')
        read_only_fields = ('id',)

class GameSerializer(serializers.ModelSerializer):
    platforms = PlatformSerializer(many=True, read_only=True)
    genres = GenreSerializer(many=True, read_only=True)
    image = serializers.SerializerMethodField()

    class Meta:
        model = Game
        fields = (
            'id', 'title', 'developer', 'publisher', 'description', 
            'price', 'release_date', 'image', 'trailer_url', 'platforms',
            'genres', 'is_sale', 'sale_price', 'sale_start_date', 'sale_end_date'
        )
        read_only_fields = ('id',)

    def get_image(self, obj):
        return obj.return_image_url()
    
class CartDetailItemSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = CartItem
        fields = ('id', 'game', 'quantity', 'added_date')
        read_only_fields = ('id', 'added_date')

class OwnedGameSerializer(serializers.ModelSerializer):
    game = GameSerializer()

    class Meta:
        model = OwnedGame
        fields = ('id', 'game', 'purchase_date')
        read_only_fields = ('id', 'purchase_date')