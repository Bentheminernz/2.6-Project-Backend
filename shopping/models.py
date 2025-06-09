from django.db import models
from users.models import User

# Create your models here.
class Game(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    release_date = models.DateField()
    image = models.ImageField(upload_to='games/')
    download_link = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return self.title
    
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

    def __str__(self):
        return f"{self.user.username} has {self.quantity} of {self.game.title} in cart"