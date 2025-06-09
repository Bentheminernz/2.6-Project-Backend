from django.contrib import admin
from .models import Game, OwnedGame, CartItem

# Register your models here.
class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'release_date')
    search_fields = ('title', 'description')
    list_filter = ('release_date',)

class OwnedGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'purchase_date')
    search_fields = ('user__username', 'game__title')
    list_filter = ('purchase_date',)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'quantity', 'added_date')
    search_fields = ('user__username', 'game__title')
    list_filter = ('added_date',)

admin.site.register(Game, GameAdmin)
admin.site.register(OwnedGame, OwnedGameAdmin)
admin.site.register(CartItem, CartItemAdmin)