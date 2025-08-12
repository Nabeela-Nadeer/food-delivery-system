from django.contrib import admin
from .models import  RestaurantProfile, MenuItem,Order

admin.site.register(RestaurantProfile)
admin.site.register(MenuItem)
admin.site.register(Order)
