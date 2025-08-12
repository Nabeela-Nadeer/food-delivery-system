from django.contrib.auth.models import User
from django.db import models

class CustomerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    phone = models.CharField(max_length=20, blank=True)
    address = models.TextField(blank=True)

    def __str__(self):
        return self.user.username

from django.db import models
from django.contrib.auth.models import User

class Wallet(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return f"{self.user.username}'s Wallet - ₹{self.balance}"

class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ('credit', 'Credit'),
        ('debit', 'Debit'),
    ]
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    type = models.CharField(max_length=6, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)
    note = models.CharField(max_length=255, blank=True)

    def __str__(self):
        return f"{self.type.title()} ₹{self.amount} on {self.date.strftime('%Y-%m-%d')}"
