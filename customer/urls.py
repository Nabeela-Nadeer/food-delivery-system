from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.customer_register, name='customer_register'),
    path('login/', views.customer_login, name='customer_login'),
    path('logout/', views.customer_logout, name='customer_logout'),
    path('dashboard/', views.customer_dashboard, name='customer_dashboard'),
    path('profile/', views.customer_profile, name='customer_profile'),
    path('restaurants/', views.restaurant_list, name='restaurant_list'),
    path('orders/', views.order_history, name='order_history'),
    path('wallet/', views.wallet, name='wallet'),
    path('order-now/<int:item_id>/', views.order_now, name='order_now'),
    path('order/<int:order_id>/', views.order_detail, name='order_detail'),
    path('restaurant/<int:restaurant_id>/menu/', views.restaurant_menu, name='restaurant_menu'),
]
