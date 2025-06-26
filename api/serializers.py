from users.models import User, CreditCard, Address
from shopping.models import Game, CartItem, Platform, Genre, OwnedGame, Order, OrderItem
from rest_framework import serializers
from decimal import Decimal
from datetime import datetime

class UserSerializer(serializers.ModelSerializer):
    cart_items = serializers.SerializerMethodField()
    credit_cards = serializers.SerializerMethodField()
    addresses = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('id', 'username', 'email', 'first_name', 'last_name', 'cart_items', 'credit_cards', 'addresses')
        read_only_fields = ('id',)

    def get_cart_items(self, obj):
        cart_items = obj.cart_items.all()
        return BasicUserCartItemSerializer(cart_items, many=True).data
    
    def get_credit_cards(self, obj):
        credit_cards = obj.credit_cards.all()
        return CreditCardSerializer(credit_cards, many=True).data
    
    def get_addresses(self, obj):
        addresses = obj.addresses.all()
        return AddressSerializer(addresses, many=True).data
    
class CreditCardSerializer(serializers.ModelSerializer):
    cardNumber = serializers.CharField(source='card_number')
    expiryDate = serializers.CharField(source='expiration_date')
    nameOnCard = serializers.CharField(source='name_on_card')

    class Meta:
        model = CreditCard
        fields = ('id', 'nameOnCard', 'cardNumber', 'expiryDate', 'cvv')
        read_only_fields = ('id',)

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('id', 'street_address', 'suburb', 'city', 'postcode', 'country')
        read_only_fields = ('id',)
    
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

class OrderCreateSerializer(serializers.Serializer):
    game_ids = serializers.ListField(
        child=serializers.IntegerField(),
        min_length=1,
        error_messages={'min_length': 'At least one game ID is required.'}
    )
    form_data = serializers.DictField()

    def validate_game_ids(self, value):
        user = self.context['request'].user
        
        games = Game.objects.filter(id__in=value)
        if len(games) != len(value):
            raise serializers.ValidationError("One or more games not found.")
        
        owned_games = OwnedGame.objects.filter(
            user=user, 
            game__in=games
        ).values_list('game_id', flat=True)
        
        if owned_games:
            owned_game_titles = games.filter(id__in=owned_games).values_list('title', flat=True)
            raise serializers.ValidationError(
                f'You already own the following games: {", ".join(owned_game_titles)}'
            )
        
        return value

    def calculate_total_amount(self, games):
        total_amount = Decimal('0.00')
        for game in games:
            if game.is_sale and game.sale_price:
                total_amount += game.sale_price
            else:
                total_amount += game.price
        return total_amount

class CreditCardCreateSerializer(serializers.ModelSerializer):
    expiryDate = serializers.CharField(write_only=True)
    nameOnCard = serializers.CharField(source='name_on_card')
    cardNumber = serializers.CharField(source='card_number')

    class Meta:
        model = CreditCard
        fields = ('nameOnCard', 'cardNumber', 'expiryDate', 'cvv')

    def validate_expiryDate(self, value):
        """Convert MM/YY format to proper date"""
        try:
            month, year = value.split('/')
            year = int(year)
            if year < 100:
                year += 2000
            return f"{year}-{int(month):02d}-01"
        except Exception:
            raise serializers.ValidationError('Invalid expiry date format. Use MM/YY.')

    def create(self, validated_data):
        """Create credit card with proper expiration date"""
        expiry_date = validated_data.pop('expiryDate', None)
        validated_data['expiration_date'] = expiry_date
        validated_data['user'] = self.context['request'].user
        
        existing_card = CreditCard.objects.filter(
            user=validated_data['user'],
            card_number=validated_data['card_number']
        ).first()
        
        if existing_card:
            return existing_card
        
        return super().create(validated_data)

class AddressCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ('street_address', 'suburb', 'city', 'postcode', 'country')

    def create(self, validated_data):
        user = self.context['request'].user
        validated_data['user'] = user
        
        existing_address = Address.objects.filter(
            user=user,
            street_address=validated_data['street_address'],
            suburb=validated_data['suburb'],
            city=validated_data['city'],
            postcode=validated_data['postcode'],
            country=validated_data['country']
        ).first()
        
        if existing_address:
            return existing_address
        
        return super().create(validated_data)

class OrderItemSerializer(serializers.ModelSerializer):
    game = GameSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ('id', 'game', 'purchase_price', 'quantity')
        read_only_fields = ('id',)

class OrderSerializer(serializers.ModelSerializer):
    order_items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ('id', 'total_amount', 'order_date', 'order_items')