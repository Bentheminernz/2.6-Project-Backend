from django.db import models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from cryptography.fernet import Fernet
import hashlib

# Create your models here.
class User(AbstractUser):
    username = models.CharField(
        max_length=30,
        unique=True,
        help_text="Required. 30 characters or fewer. Letters, digits and @/./+/-/_ only.",
        validators=[AbstractUser.username_validator],
        error_messages={
            'unique': "A user with that username already exists.",
        },
    )
    email = models.EmailField(unique=True)

    def name(self):
        return f"{self.first_name} {self.last_name}" if self.first_name and self.last_name else self.username

    def __str__(self):
        return self.username
    
class CreditCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='credit_cards')
    name_on_card = models.CharField(max_length=100)
    last_four_digits = models.CharField(max_length=4)
    card_number_hash = models.CharField(max_length=64, unique=True)
    encrypted_card_number = models.BinaryField(null=True, blank=True)
    expiration_date = models.DateField()
    card_brand = models.CharField(max_length=20, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def set_card_number(self, card_number):
        # this model method is used to set the card number before saving (remove spaces and dashes)
        self._temp_card_number = card_number.replace(' ', '').replace('-', '')

    def save(self, *args, **kwargs):
        # runs on save
        if hasattr(self, '_temp_card_number'):
            # make sure we have a temp card number to process
            self.last_four_digits = self._temp_card_number[-4:] # gets last 4 digits
            self.card_number_hash = hashlib.sha256(self._temp_card_number.encode()).hexdigest() # hash's the card number
            if hasattr(settings, 'ENCRYPTION_KEY'):
                # if the encryption key is set then encrypt the card number!
                f = Fernet(settings.ENCRYPTION_KEY)
                self.encrypted_card_number = f.encrypt(self._temp_card_number.encode())

            # determine the card brand
            self.card_brand = self._determine_card_brand(self._temp_card_number)

            # deletes the temporary card number attribute (removes it from the model instance (security!!!))
            delattr(self, '_temp_card_number')
        super().save(*args, **kwargs)

    def _determine_card_brand(self, card_number):
        # determine the card brand based on the first numbers
        if card_number.startswith('4'):
            return 'Visa'
        elif card_number.startswith(('51', '52', '53', '54', '55')):
            return 'Mastercard'
        elif card_number.startswith(('34', '37')):
            return 'American Express'
        return 'Unknown'

    def get_decrypted_card_number(self):
        # decrypts the card number (this is used for autofill purposes)
        if self.encrypted_card_number and hasattr(settings, 'ENCRYPTION_KEY'):
            try:
                # if there is an encryption key set, decrypt the card number
                f = Fernet(settings.ENCRYPTION_KEY)
                decrypted_bytes = f.decrypt(self.encrypted_card_number)
                return decrypted_bytes.decode()
            except Exception as e:
                print(f"Decryption error: {e}")
                return None
        return None

    def get_masked_card_number(self):
        # return the decrypted card number with only last 4 digits visible
        full_number = self.get_decrypted_card_number()
        if full_number:
            return f"****{self.last_four_digits}"
        return f"****{self.last_four_digits}"

    def __str__(self):
        return f"{self.user.username} - {self.card_brand} ****{self.last_four_digits}"
    
    class Meta:
        verbose_name_plural = "Credit Cards"
        ordering = ['user', 'expiration_date']
    
class Address(models.Model):
    COUNTRY_CHOICES = [
        ('US', 'United States'),
        ('CA', 'Canada'),
        ('AU', 'Australia'),
        ('GB', 'United Kingdom'),
        ('DE', 'Germany'),
        ('FR', 'France'),
        ('JP', 'Japan'),
        ('NZ', 'New Zealand'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='addresses')
    street_address = models.CharField(max_length=255)
    suburb = models.CharField(max_length=100, blank=True)
    city = models.CharField(max_length=100)
    postcode = models.CharField(max_length=10)
    country = models.CharField(max_length=100, choices=COUNTRY_CHOICES, default='NZ')

    def __str__(self):
        return f"{self.user.username} - {self.street_address}, {self.city}, {self.country}"
    
    class Meta:
        verbose_name_plural = "Addresses"
        ordering = ['user', 'city', 'street_address']