from django.contrib import admin
from .models import Game, OwnedGame, CartItem, Platform, Genre, Order

# Register your models here.

class PlatformAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class GenreAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)

class GameAdmin(admin.ModelAdmin):
    list_display = ('title', 'price', 'release_date')
    search_fields = ('title', 'description')
    list_filter = ('release_date',)
    filter_horizontal = ('platforms', 'genres')

class OwnedGameAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'purchase_date')
    search_fields = ('user__username', 'game__title')
    list_filter = ('purchase_date',)

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'quantity', 'added_date')
    search_fields = ('user__username', 'game__title')
    list_filter = ('added_date',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'order_date')
    search_fields = ('user__username',)
    list_filter = ('order_date',)
    filter_horizontal = ('games',)

admin.site.register(Platform, PlatformAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(OwnedGame, OwnedGameAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)