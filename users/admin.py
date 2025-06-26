from django.contrib import admin
from .models import User, CreditCard, Address

# Register your models here.
class UserAdmin(admin.ModelAdmin):
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'is_active')
    search_fields = ('username', 'email', 'first_name', 'last_name')
    list_filter = ('is_staff', 'is_active')

class CreditCardAdmin(admin.ModelAdmin):
    list_display = ('user', 'name_on_card', 'card_number', 'expiration_date')
    search_fields = ('user__username', 'name_on_card', 'card_number')
    list_filter = ('expiration_date',)

    def has_change_permission(self, request, obj=None):
        return False

class AddressAdmin(admin.ModelAdmin):
    list_display = ('user', 'street_address', 'city', 'country')
    search_fields = ('user__username', 'street_address', 'city', 'country')
    list_filter = ('country',)

admin.site.register(User, UserAdmin)
admin.site.register(CreditCard, CreditCardAdmin)
admin.site.register(Address, AddressAdmin)