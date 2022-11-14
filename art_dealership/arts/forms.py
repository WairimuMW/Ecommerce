from .models import *
from django.forms import ModelForm
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django import forms

class ArtistRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    phonenumber = forms.IntegerField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phonenumber', 'password1', 'password2']
        
class CustomerRegistrationForm(UserCreationForm):
    email = forms.EmailField()
    phonenumber = forms.IntegerField()
    
    class Meta:
        model = User
        fields = ['username', 'email', 'phonenumber', 'password1', 'password2']


class CreateArtForm(ModelForm):
    class Meta:
        model = Art
        fields = '__all__'


class ArtistProfileForm(ModelForm):
    class Meta:
        model = ArtistProfile
        fields = '__all__'
        exclude = ['user']


class CustomerProfileForm(ModelForm):
    class Meta:
        model = CustomerProfile
        fields = '__all__'
        exclude = ['user']


class DeliveryForm(ModelForm):
    class Meta:
        model = Delivery
        fields = '__all__'
      