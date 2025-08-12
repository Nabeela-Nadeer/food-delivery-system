from django.contrib.auth.models import User
from django.db import models
from customer.models import CustomerProfile

class RestaurantProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)  # Restaurant name
    owner_name = models.CharField(max_length=100, default="Unknown Owner")
    address = models.TextField()
    phone = models.CharField(max_length=20)
    opening_hours = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name

class MenuItem(models.Model):
    restaurant = models.ForeignKey(RestaurantProfile, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=6, decimal_places=2)
    image = models.ImageField(upload_to='menu_images/', blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.name} - {self.restaurant.name}"


from django.db import models
from django.contrib.auth.models import User
from customer.models import CustomerProfile
from restaurant.models import RestaurantProfile, MenuItem

class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('preparing', 'Preparing'),
        ('dispatched', 'Dispatched'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]

    restaurant = models.ForeignKey(RestaurantProfile, on_delete=models.CASCADE, related_name='orders')
    customer = models.ForeignKey(CustomerProfile, on_delete=models.CASCADE, related_name='orders')
    order_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total_price = models.DecimalField(max_digits=10, decimal_places=2, default=0)  # calculated


    rating = models.PositiveSmallIntegerField(null=True, blank=True)  # 1 to 5 stars
    review = models.TextField(blank=True, null=True)
    

    def __str__(self):
        return f"Order #{self.id} by {self.customer.user.username} - {self.status}"

    def calculate_total_price(self):
        total = sum(item.subtotal() for item in self.items.all())
        self.total_price = total
        self.save()

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.menu_item.name}"

    def subtotal(self):
        return self.menu_item.price * self.quantity


from django.db import models
from django.utils import timezone
from datetime import timedelta

class Promotion(models.Model):
    restaurant = models.ForeignKey(
        'RestaurantProfile', 
        on_delete=models.CASCADE
    )
    code = models.CharField(max_length=50, unique=True)
    discount_percent = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        help_text="Discount %",
        default=0.00
    )
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(default=timezone.now() + timedelta(days=30))
    active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.code} - {self.discount_percent}%"






