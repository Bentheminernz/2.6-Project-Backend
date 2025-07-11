from django.db import models
from users.models import User
from django.conf import settings
import string
import random

# Create your models here.
PLATFORM_CHOICES = [
    ('PC', 'PC'),
    ('MAC', 'Mac'),
    ('PS4', 'PlayStation 4'),
    ('PS5', 'PlayStation 5'),
    ('XBOX_ONE', 'Xbox One'),
    ('XBOX_SERIES', 'Xbox Series X/S'),
    ('SWITCH', 'Nintendo Switch'),
    ('SWITCH2', 'Nintendo Switch 2'),
]

GAME_GENRE_CHOICES = [
    ('ACTION', 'Action'),
    ('ADVENTURE', 'Adventure'),
    ('RPG', 'Role-Playing Game'),
    ('SHOOTER', 'Shooter'),
    ('SPORTS', 'Sports'),
    ('RACING', 'Racing'),
    ('PUZZLE', 'Puzzle'),
    ('STRATEGY', 'Strategy'),
    ('SIMULATION', 'Simulation'),
    ('FIGHTING', 'Fighting'),
    ('PLATFORMER', 'Platformer'),
    ('HORROR', 'Horror'),
    ('MMO', 'Massively Multiplayer Online'),
    ('SANDBOX', 'Sandbox'),
    ('STEALTH', 'Stealth'),
    ('MUSIC', 'Music/Rhythm'),
    ('PARTY', 'Party'),
    ('SURVIVAL', 'Survival'),
    ('VISUAL_NOVEL', 'Visual Novel'),
    ('INDIE', 'Indie'),
]

class Platform(models.Model):
    name = models.CharField(max_length=50, choices=PLATFORM_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_name_display()

class Genre(models.Model):
    name = models.CharField(max_length=50, choices=GAME_GENRE_CHOICES, unique=True)
    
    def __str__(self):
        return self.get_name_display()

class Game(models.Model):
    title = models.CharField(max_length=255)
    developer = models.CharField(max_length=255)
    publisher = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    release_date = models.DateField()
    image = models.ImageField(upload_to='games/')
    platforms = models.ManyToManyField(
        Platform,
        blank=True,
        related_name='games'
    )
    genres = models.ManyToManyField(
        Genre,
        blank=True,
        related_name='games'
    )
    is_sale = models.BooleanField(default=False)
    sale_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    sale_start_date = models.DateField(blank=True, null=True)
    sale_end_date = models.DateField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-release_date']
        verbose_name_plural = 'Games'

    def __str__(self):
        return self.title
    
    def return_image_url(self):
        if settings.DEBUG:
            return f"http://localhost:8070{self.image.url}"
        else:
            return f"https://lawrencestudios.com{self.image.url}"
    
class OwnedGame(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='owned_games')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='owners')
    purchase_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')

    def __str__(self):
        return f"{self.user.username} owns {self.game.title}"
    
class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='cart_items')
    quantity = models.PositiveIntegerField(default=1)
    added_date = models.DateField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'game')

    def get_game_id(self):
        return self.game.id if self.game else None

    def __str__(self):
        return f"{self.user.username} has {self.quantity} of {self.game.title} in cart"
    
def generate_order_id():
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))

class OrderItem(models.Model):
    """Represents an individual game purchase within an order"""
    order = models.ForeignKey('Order', on_delete=models.CASCADE, related_name='order_items')
    game = models.ForeignKey(Game, on_delete=models.CASCADE, related_name='order_items')
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField(default=1)
    
    class Meta:
        unique_together = ('order', 'game')
    
    def __str__(self):
        return f"{self.game.title} in Order {self.order.id} - ${self.purchase_price}"

class Order(models.Model):
    id = models.CharField(
        primary_key=True,
        max_length=8,
        unique=True,
        editable=False,
        default=generate_order_id
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    games = models.ManyToManyField(Game, related_name='orders', blank=True)
    order_date = models.DateField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_completed = models.BooleanField(default=False)

    def __str__(self):
        return f"Order {self.id} by {self.user.username} on {self.order_date} - Total: ${self.total_amount:.2f}"