from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import RestaurantProfile
from .models import MenuItem,Category

class RestaurantSignUpForm(UserCreationForm):
    email = forms.EmailField(required=True)
    restaurant_name = forms.CharField(max_length=100, label="Restaurant Name")
    owner_name = forms.CharField(max_length=100, label="Owner Name")
    address = forms.CharField(widget=forms.Textarea)
    phone = forms.CharField(max_length=20)

    class Meta:
        model = User
        fields = ('username', 'email', 'password1', 'password2')

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add 'form-control' class to all widgets
        for field_name, field in self.fields.items():
            existing_classes = field.widget.attrs.get('class', '')
            field.widget.attrs['class'] = (existing_classes + ' form-control').strip()

            
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
            # Create RestaurantProfile linked to User
            RestaurantProfile.objects.create(
                user=user,
                name=self.cleaned_data['restaurant_name'],
                address=self.cleaned_data['address'],
                phone=self.cleaned_data['phone'],
                owner_name=self.cleaned_data['owner_name'],  # see model update below
            )
        return user

#profile editing form
class RestaurantProfileForm(forms.ModelForm):
    class Meta:
        model = RestaurantProfile
        fields = [ 'owner_name', 'address', 'phone', 'opening_hours']


#menu management form
class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'price', 'image','category']
        category = forms.ModelChoiceField(queryset=Category.objects.all(), required=True)

# restaurant/forms.py

from django import forms
from .models import OrderItem, MenuItem,Order

class OrderItemForm(forms.ModelForm):
    menu_item = forms.ModelChoiceField(queryset=MenuItem.objects.none())
    quantity = forms.IntegerField(min_value=1, initial=1)

    class Meta:
        model = OrderItem
        fields = ['menu_item', 'quantity']

    def __init__(self, *args, **kwargs):
        restaurant = kwargs.pop('restaurant', None)
        super().__init__(*args, **kwargs)
        if restaurant:
            self.fields['menu_item'].queryset = MenuItem.objects.filter(restaurant=restaurant)

from django import forms


class ReviewForm(forms.ModelForm):
    rating = forms.ChoiceField(choices=[(i, str(i)) for i in range(1,6)], widget=forms.Select(attrs={'class': 'form-select'}))
    review = forms.CharField(widget=forms.Textarea(attrs={'rows': 3, 'class': 'form-control'}), required=False)

    class Meta:
        model = Order
        fields = ['rating', 'review']

from django import forms
from .models import Promotion

class PromotionForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    class Meta:
        model = Promotion
        fields = ['code', 'discount_percent', 'start_date', 'end_date', 'active']
