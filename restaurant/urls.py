from django.urls import path
from . import views
from customer import views as customer_views

urlpatterns = [
    
    # For restaurant registration and login
    path('register/', views.restaurant_register, name='restaurant_register'),
    path('login/', views.restaurant_login, name='restaurant_login'),
   

   # For restaurant dashboard
    path('dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),


    #For restaurant profile management
    path('restaurant_profile/', views.restaurant_profile, name='restaurant_profile'),
    path('profile/edit/', views.edit_profile, name='edit_profile'),


    #for restaurant menu management
    path('menu/', views.menu_management, name='menu_management'),
    path('menu/add/', views.add_menu_item, name='add_menu_item'),
    path('menu/edit/<int:pk>/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/delete/<int:pk>/', views.delete_menu_item, name='delete_menu_item'),
    

    #for order handling
    path('orders_handling/', views.order_handling, name='order_handling'),

   
    
    path('add-promo/', views.add_promo_code, name='add_promo_code'),


    path('reviews/', views.reviews_ratings, name='reviews_ratings'),
   
    path('sales/', views.sales_analytics, name='sales_analytics'),

    
    path('logout/', views.restaurant_logout, name='restaurant_logout'),
]

