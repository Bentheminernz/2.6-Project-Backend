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
        return CreditCardSerializer(credit_cards, many=True, context=self.context).data
    
    def get_addresses(self, obj):
        addresses = obj.addresses.all()
        return AddressSerializer(addresses, many=True).data
    
class CreditCardSerializer(serializers.ModelSerializer):
    nameOnCard = serializers.CharField(source='name_on_card')
    lastFourDigits = serializers.CharField(source='last_four_digits')
    cardBrand = serializers.CharField(source='card_brand')
    expiryDate = serializers.CharField(source='expiration_date')
    cardNumber = serializers.SerializerMethodField()  # For autofill only

    class Meta:
        model = CreditCard
        fields = ('id', 'nameOnCard', 'lastFourDigits', 'cardBrand', 'expiryDate', 'cardNumber')
        read_only_fields = ('id', 'lastFourDigits', 'cardBrand', 'cardNumber')

    def get_cardNumber(self, obj):
        """Return decrypted card number for autofill (use carefully)"""
        # Only return full card number for the card owner
        request = self.context.get('request')
        if request and request.user == obj.user:
            return obj.get_decrypted_card_number()
        return f"****{obj.last_four_digits}"

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

    def validate_form_data(self, value):
        # validate that cvv is provided for payment processing
        card_details = value.get('cardDetails', {})
        cvv = card_details.get('cvv', '').strip()
        
        if not cvv:
            raise serializers.ValidationError("CVV is required for payment processing.")
        
        if not cvv.isdigit() or len(cvv) < 3 or len(cvv) > 4:
            raise serializers.ValidationError("Invalid CVV format.")
        
        # if detected then just validate it, as i have no means of actually processing the payment. cvv is also never stored for security purposes
        return value

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
    cardNumber = serializers.CharField(write_only=True)

    # accepts the CVV for demoed payment processing but its never stored
    cvv = serializers.CharField(write_only=True)

    class Meta:
        model = CreditCard
        fields = ('nameOnCard', 'cardNumber', 'expiryDate', 'cvv')

    def validate_cardNumber(self, value):
        # very basic card number validation (as i have no means of actually processing the card)
        cleaned_number = value.replace(' ', '').replace('-', '')
        if not cleaned_number.isdigit():
            raise serializers.ValidationError('Card number must contain only digits.')
        if len(cleaned_number) < 13 or len(cleaned_number) > 19:
            raise serializers.ValidationError('Invalid card number length.')
        return cleaned_number

    def validate_cvv(self, value):
        # very basic CVV validation (as i have no means of actually processing the CVV)
        if not value.isdigit():
            raise serializers.ValidationError('CVV must contain only digits.')
        if len(value) < 3 or len(value) > 4:
            raise serializers.ValidationError('CVV must be 3 or 4 digits.')
        return value

    def validate_expiryDate(self, value):
        # convert it to valid date format for django model
        try:
            month, year = value.split('/')
            year = int(year)
            if year < 100:
                year += 2000
            
            from datetime import datetime
            current_year = datetime.now().year
            current_month = datetime.now().month
            
            if year < current_year or (year == current_year and int(month) < current_month):
                raise serializers.ValidationError('Card has expired.')
                
            return f"{year}-{int(month):02d}-01"
        except Exception:
            raise serializers.ValidationError('Invalid expiry date format. Use MM/YY.')

    def create(self, validated_data):
        # creates the card with proper security measures
        card_number = validated_data.pop('cardNumber')
        cvv = validated_data.pop('cvv')
        expiry_date = validated_data.pop('expiryDate')
        
        # since this isn't an actual payment processing system, we won't process the payment here
        # instead we'll just assume that this is a valid card and that the CVV was provided
        
        validated_data['expiration_date'] = expiry_date
        validated_data['user'] = self.context['request'].user
        
        # check if the card hash already exists, this is to prevent duplicate cards
        import hashlib
        card_hash = hashlib.sha256(card_number.encode()).hexdigest()
        existing_card = CreditCard.objects.filter(
            user=validated_data['user'],
            card_number_hash=card_hash
        ).first()
        
        # if it does already exist then just return the existing card
        if existing_card:
            return existing_card
        
        # create a new card instance
        card = CreditCard(**validated_data)
        card.set_card_number(card_number)
        card.save()
        
        return card

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