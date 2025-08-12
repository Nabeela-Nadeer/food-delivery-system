from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from .forms import RestaurantSignUpForm
from .models import RestaurantProfile
from django.contrib import messages
from .forms import RestaurantProfileForm
from .models import MenuItem
from .forms import MenuItemForm
from django.contrib.auth.models import User
from restaurant.models import Order  


#restaurant registration
def restaurant_register(request):
    if request.method == 'POST':
        form = RestaurantSignUpForm(request.POST)
        if form.is_valid():
            user = form.save()  # profile created inside save()
            messages.success(request, 'Registration successful! Please log in.')
            return redirect('restaurant_login')  # Redirect to restaurant login page
    else:
        form = RestaurantSignUpForm()
    return render(request, 'restaurant/register.html', {'form': form})



# Restaurant Login
def restaurant_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('restaurant_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'restaurant/login.html', {'form': form})


# Restaurant Logout
def restaurant_logout(request):
    logout(request)
    return redirect('home')


# Restaurant Dashboard

from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404
from restaurant.models import RestaurantProfile, MenuItem
from customer.models import CustomerProfile

@login_required
def restaurant_dashboard(request):
    restaurant_profile = get_object_or_404(RestaurantProfile, user=request.user)

    recent_items = MenuItem.objects.filter(
        restaurant=restaurant_profile
    ).order_by('-id')[:5]

    # Customers who ordered from this restaurant (distinct customers)
    customers = CustomerProfile.objects.filter(
        orders__restaurant=restaurant_profile
    ).distinct()

    return render(request, 'restaurant/dashboard.html', {
        'recent_items': recent_items,
        'customers': customers,
    })




#For restaurant profile management
@login_required
def restaurant_profile(request):
    profile = get_object_or_404(RestaurantProfile, user=request.user)
    return render(request, 'restaurant/restaurant_profile.html', {'profile': profile})

@login_required
def edit_profile(request):
    profile = get_object_or_404(RestaurantProfile, user=request.user)
    if request.method == 'POST':
        form = RestaurantProfileForm(request.POST, instance=profile)
        if form.is_valid():
            form.save()
            return redirect('restaurant_profile')
    else:
        form = RestaurantProfileForm(instance=profile)
    return render(request, 'restaurant/edit_profile.html', {'form': form})


# For restaurants menu management
@login_required
def menu_management(request):
    # Get the restaurant profile for the logged-in user
    restaurant_profile = get_object_or_404(RestaurantProfile, user=request.user)

    # Now filter menu items using the object, not a string
    menu_items = MenuItem.objects.filter(restaurant=restaurant_profile)

    return render(request, 'restaurant/menu_management.html', {'menu_items': menu_items})

@login_required
def add_menu_item(request):
    restaurant_profile = get_object_or_404(RestaurantProfile, user=request.user)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES)
        if form.is_valid():
            menu_item = form.save(commit=False)
            menu_item.restaurant = restaurant_profile  # Assign RestaurantProfile, not User
            menu_item.save()
            return redirect('menu_management')  # Refresh page after adding
    else:
        form = MenuItemForm()

    return render(request, 'restaurant/add_menu_item.html', {'form': form})


@login_required
def edit_menu_item(request, pk):
    # Get the restaurant profile of the logged-in user
    restaurant_profile = get_object_or_404(RestaurantProfile, user=request.user)
    
    # Fetch the menu item belonging to this restaurant
    item = get_object_or_404(MenuItem, pk=pk, restaurant=restaurant_profile)
    
    if request.method == 'POST':
        form = MenuItemForm(request.POST, request.FILES, instance=item)
        if form.is_valid():
            form.save()
            return redirect('menu_management')
    else:
        form = MenuItemForm(instance=item)
    
    return render(request, 'restaurant/edit_menu_item.html', {'form': form})

@login_required
def delete_menu_item(request, pk):
    # Get the restaurant profile linked to the logged-in user
    restaurant_profile = get_object_or_404(RestaurantProfile, user=request.user)

    # Now get the menu item belonging to this restaurant
    item = get_object_or_404(MenuItem, pk=pk, restaurant=restaurant_profile)

    if request.method == 'POST':
        item.delete()
        return redirect('menu_management')

    return render(request, 'restaurant/delete_menu_item.html', {'item': item})



from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Order, RestaurantProfile

@login_required
def order_handling(request):
    restaurant_profile = get_object_or_404(RestaurantProfile, user=request.user)
    orders = Order.objects.filter(restaurant=restaurant_profile).order_by('-order_date')

    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        new_status = request.POST.get('status')
        order = get_object_or_404(Order, id=order_id, restaurant=restaurant_profile)
        if new_status in dict(Order.STATUS_CHOICES).keys():
            order.status = new_status
            order.save()
        return redirect('order_handling')

    return render(request, 'restaurant/order_handling.html', {'orders': orders})


from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from customer.models import CustomerProfile
from .forms import OrderItemForm,PromotionForm


@login_required
def create_order(request, restaurant_id):
    restaurant = get_object_or_404(RestaurantProfile, pk=restaurant_id)
    customer = get_object_or_404(CustomerProfile, user=request.user)

    if request.method == 'POST':
        form = OrderItemForm(request.POST, restaurant=restaurant)
        if form.is_valid():
            # Create order if not exists (for simplicity creating new every time)
            order = Order.objects.create(restaurant=restaurant, customer=customer)
            
            # Create order item
            order_item = form.save(commit=False)
            order_item.order = order
            order_item.save()

            # Update total price
            order.calculate_total_price()

            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderItemForm(restaurant=restaurant)

    return render(request, 'restaurant/create_order.html', {'form': form, 'restaurant': restaurant})

@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer__user=request.user)
    return render(request, 'restaurant/order_detail.html', {'order': order})



@login_required
def reviews_ratings(request):
    try:
        restaurant = request.user.restaurantprofile
        print(f"Logged in as restaurant: {restaurant.name}")
    except RestaurantProfile.DoesNotExist:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('home')

    orders_with_reviews = Order.objects.filter(
        restaurant=restaurant,
    ).exclude(rating__isnull=True).order_by('-order_date')

    print(f"Found {orders_with_reviews.count()} orders with reviews.")

    for o in orders_with_reviews:
        print(f"Order #{o.id}: Rating {o.rating}, Review: {o.review}")

    context = {
        'orders': orders_with_reviews,
    }
    return render(request, 'restaurant/reviews_ratings.html', context)




from django.db.models import Sum
from django.utils.timezone import now
from datetime import timedelta

def get_weekly_sales(restaurant):
    one_week_ago = now() - timedelta(days=7)
    weekly_orders = Order.objects.filter(
        restaurant=restaurant,
        status='delivered',
        order_date__gte=one_week_ago
    )
    total_weekly_sales = weekly_orders.aggregate(Sum('total_price'))['total_price__sum'] or 0
    return total_weekly_sales

from django.db.models import Count
from .models import OrderItem

def get_popular_items(restaurant):
    one_month_ago = now() - timedelta(days=30)
    popular_items = (
        OrderItem.objects.filter(
            order__restaurant=restaurant,
            order__status='delivered',
            order__order_date__gte=one_month_ago
        )
        .values('menu_item__name')
        .annotate(total_ordered=Sum('quantity'))
        .order_by('-total_ordered')
    )
    return popular_items

from django.contrib.auth.decorators import login_required
from django.shortcuts import render
from datetime import timedelta
from django.utils.timezone import now
from django.db.models import Sum

@login_required
def sales_analytics(request):
    restaurant = request.user.restaurantprofile

    one_week_ago = now() - timedelta(days=7)
    one_month_ago = now() - timedelta(days=30)

    weekly_sales = Order.objects.filter(
        restaurant=restaurant,
        status='delivered',
        order_date__gte=one_week_ago
    ).aggregate(total=Sum('total_price'))['total'] or 0

    monthly_sales = Order.objects.filter(
        restaurant=restaurant,
        status='delivered',
        order_date__gte=one_month_ago
    ).aggregate(total=Sum('total_price'))['total'] or 0

    popular_items = (
        OrderItem.objects.filter(
            order__restaurant=restaurant,
            order__status='delivered',
            order__order_date__gte=one_month_ago
        )
        .values('menu_item__name')
        .annotate(total_ordered=Sum('quantity'))
        .order_by('-total_ordered')
    )

    context = {
        'weekly_sales': weekly_sales,
        'monthly_sales': monthly_sales,
        'popular_items': popular_items,
    }
    return render(request, 'restaurant/sales_analytics.html', context)


@login_required
def add_promo_code(request):
    restaurant = get_object_or_404(RestaurantProfile, user=request.user)

    if request.method == 'POST':
        form = PromotionForm(request.POST)
        if form.is_valid():
            promo = form.save(commit=False)
            promo.restaurant = restaurant
            promo.save()
            messages.success(request, "Promo code added successfully!")
            return redirect('restaurant_dashboard')
    else:
        form = PromotionForm()

    return render(request, 'restaurant/add_promo.html', {'form': form})
