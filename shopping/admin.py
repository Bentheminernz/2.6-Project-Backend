from django.contrib import admin
from .models import Game, OwnedGame, CartItem, Platform, Genre, Order, OrderItem

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

    def has_change_permission(self, request, obj=None):
        return False

class CartItemAdmin(admin.ModelAdmin):
    list_display = ('user', 'game', 'quantity', 'added_date')
    search_fields = ('user__username', 'game__title')
    list_filter = ('added_date',)

class OrderAdmin(admin.ModelAdmin):
    list_display = ('user', 'total_amount', 'order_date')
    search_fields = ('user__username',)
    list_filter = ('order_date',)
    filter_horizontal = ('games',)

    def has_change_permission(self, request, obj=None):
        return False
    
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ('order', 'game', 'purchase_price', 'quantity')
    search_fields = ('order__user__username', 'game__title')

admin.site.register(Platform, PlatformAdmin)
admin.site.register(Genre, GenreAdmin)
admin.site.register(Game, GameAdmin)
admin.site.register(OwnedGame, OwnedGameAdmin)
admin.site.register(CartItem, CartItemAdmin)
admin.site.register(Order, OrderAdmin)
admin.site.register(OrderItem, OrderItemAdmin)