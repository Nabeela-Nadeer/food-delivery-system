from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.decorators import login_required
from django.db.models import Q
from django.core.paginator import Paginator
from .forms import CustomerSignUpForm, CustomerProfileForm, UserForm
from .models import CustomerProfile
from restaurant.models import RestaurantProfile, MenuItem, Category
from restaurant.models import Order,MenuItem,OrderItem
from decimal import Decimal, InvalidOperation
from django.contrib import messages
from restaurant.forms import ReviewForm
from django.contrib import messages
from decimal import Decimal
from customer.models import Wallet
from .models import Wallet, Transaction

def customer_register(request):
    if request.method == 'POST':
        form = CustomerSignUpForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('customer_login')
    else:
        form = CustomerSignUpForm()
    return render(request, 'customer/register.html', {'form': form})


def customer_login(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('customer_dashboard')
    else:
        form = AuthenticationForm()
    return render(request, 'customer/login.html', {'form': form})


def customer_logout(request):
    logout(request)
    return redirect('home')



@login_required
def customer_dashboard(request):
    user = request.user
    profile = getattr(user, 'customerprofile', None)

    recent_items = MenuItem.objects.select_related('restaurant__user').order_by('-id')[:10]

    context = {
        'user': user,
        'profile': profile,
        'recent_items': recent_items,
    }
    return render(request, 'customer/dashboard.html', context)




@login_required
def customer_profile(request):
    user = request.user
    profile, created = CustomerProfile.objects.get_or_create(user=user)

    if request.method == "POST":
        user_form = UserForm(request.POST, instance=user)
        profile_form = CustomerProfileForm(request.POST, instance=profile)
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            return redirect('customer_dashboard')
    else:
        user_form = UserForm(instance=user)
        profile_form = CustomerProfileForm(instance=profile)

    return render(request, 'customer/profile.html', {
        'user_form': user_form,
        'profile_form': profile_form
    })

@login_required
def restaurant_list(request):
    name = request.GET.get('name', '').strip()
    address = request.GET.get('address', '').strip()

    restaurants = RestaurantProfile.objects.all()

    if name:
        restaurants = restaurants.filter(name__icontains=name)
    if address:
        restaurants = restaurants.filter(address__icontains=address)

    paginator = Paginator(restaurants, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'restaurants': page_obj,
        'name': name,
        'address': address,
    }

    return render(request, 'customer/restaurant_list.html', context)



def restaurant_menu(request, restaurant_id):
    restaurant = get_object_or_404(RestaurantProfile, pk=restaurant_id)
    
    search = request.GET.get('search', '').strip()
    selected_category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')

    menu_items = MenuItem.objects.filter(restaurant=restaurant)

    if search:
        menu_items = menu_items.filter(name__icontains=search)

    if selected_category:
        menu_items = menu_items.filter(category_id=selected_category)

    try:
        if min_price:
            menu_items = menu_items.filter(price__gte=float(min_price))
    except ValueError:
        pass
    try:
        if max_price:
            menu_items = menu_items.filter(price__lte=float(max_price))
    except ValueError:
        pass

    categories = Category.objects.all()

    context = {
        'restaurant': restaurant,
        'menu_items': menu_items,
        'categories': categories,
        'search': search,
        'selected_category': selected_category,
        'min_price': min_price,
        'max_price': max_price,
    }
    return render(request, 'restaurant/menu_list.html', context)



@login_required
def order_detail(request, order_id):
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    order = get_object_or_404(Order, id=order_id, customer=customer_profile)

    return render(request, 'customer/order_detail.html', {'order': order})



from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils import timezone

from restaurant.models import MenuItem, Promotion, RestaurantProfile, Order, OrderItem
from customer.models import CustomerProfile, Wallet


@login_required
def order_now(request, item_id):
    menu_item = get_object_or_404(MenuItem, id=item_id)
    customer_profile = get_object_or_404(CustomerProfile, user=request.user)
    wallet, _ = Wallet.objects.get_or_create(user=request.user)

    discount_amount = 0
    total_price = menu_item.price
    quantity = 1
    promo_code = ''

    if request.method == 'POST':
        quantity = int(request.POST.get('quantity', 1))
        if quantity < 1:
            quantity = 1

        total_price = menu_item.price * quantity

        promo_code = request.POST.get('promo_code', '').strip()

        if promo_code:
            promo = Promotion.objects.filter(
                code__iexact=promo_code,
                restaurant=menu_item.restaurant,
                active=True,
                start_date__lte=timezone.now(),
                end_date__gte=timezone.now()
            ).first()

            if promo:
                discount_amount = (total_price * promo.discount_percent) / 100
                total_price -= discount_amount
                messages.success(request, f"Promo applied! You saved ₹{discount_amount:.2f}")
            else:
                messages.error(request, "Invalid or expired promo code.")

        if wallet.balance < total_price:
            messages.error(request, "Insufficient wallet balance. Please add funds.")
            return redirect('wallet')  # Adjust to your actual wallet topup URL name

        # Deduct wallet balance
        wallet.balance -= total_price
        wallet.save()

        # Create order
        order = Order.objects.create(
            restaurant=menu_item.restaurant,
            customer=customer_profile,
            status='pending',
            total_price=total_price
        )

        # Create order item
        OrderItem.objects.create(
            order=order,
            menu_item=menu_item,
            quantity=quantity
        )

        messages.success(request, "Order placed successfully!")
        return redirect('order_history')  # Adjust to your order history URL

    context = {
        'menu_item': menu_item,
        'discount_amount': discount_amount,
        'total_price': total_price,
        'quantity': quantity,
        'promo_code': promo_code,
    }
    return render(request, 'customer/order_now.html', context)




@login_required
def order_history(request):
    orders = Order.objects.filter(customer__user=request.user).order_by('-order_date')

    # Handle review submission
    if request.method == 'POST':
        order_id = request.POST.get('order_id')
        order = get_object_or_404(Order, id=order_id, customer__user=request.user)

        # Only allow review if order is delivered
        if order.status != 'delivered':
            messages.error(request, "You can only review delivered orders.")
            return redirect('order_history')

        form = ReviewForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, "Thank you for your review!")
            return redirect('order_history')
        else:
            messages.error(request, "Please correct the errors in your review.")

    else:
        form = ReviewForm()

    context = {
        'orders': orders,
        'review_form': form,
    }
    return render(request, 'customer/order_history.html', context)


@login_required
def wallet(request):
    wallet, created = Wallet.objects.get_or_create(user=request.user)
    transactions = wallet.transactions.order_by('-date')

    if request.method == 'POST':
        amount = request.POST.get('amount')
        try:
            amount = Decimal(amount)
            if amount <= 0:
                messages.error(request, "Amount must be positive.")
            else:
                wallet.balance += amount
                wallet.save()

                Transaction.objects.create(
                    wallet=wallet,
                    type='credit',
                    amount=amount,
                    note='Funds added to wallet'
                )
                messages.success(request, f"₹{amount} added to your wallet successfully!")
                return redirect('wallet')
        except (ValueError, TypeError):
            messages.error(request, "Invalid amount entered.")

    return render(request, 'customer/wallet.html', {
        'wallet': wallet,
        'transactions': transactions,
    })



