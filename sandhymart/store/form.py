from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Product, Customer


class productForm(ModelForm):
    class Meta:
        model = Product
        fields = '__all__'


class createUserForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class customerSettingsForm(ModelForm):
    class Meta:
        model = Customer
        fields = '__all__'
        exclude = ['user']
