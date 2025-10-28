from django.db import models
from users.models import User 
from django.utils import timezone

class Product(models.Model):
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    stock = models.IntegerField()
    image_url = models.URLField(blank=True, null=True)
    low_stock_threshold = models.PositiveIntegerField(default=10) 
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='products')
 
    def is_low_stock(self):
        return self.stock <= self.low_stock_threshold
    def __str__(self):
        return self.name

class Sale(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='sales')
    quantity = models.PositiveIntegerField(default=1)
    date = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"{self.product.name} - {self.quantity} sold on {self.date.date()}"

class PromoCode(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()  
    active = models.BooleanField(default=True)
    expiry_date = models.DateTimeField()

    def is_valid(self):
        return self.active and self.expiry_date > timezone.now()

    def __str__(self):
        return self.code

