from .models import User,Address
from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth import get_user_model

User=get_user_model()

class userRegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username','email','phone','password1','password2']

class userUpdationForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['username','email','phone','profile_image']

class addAddressForm(forms.ModelForm):
    class Meta:
        model=Address
        exclude=['user',]

class editAddressForm(forms.ModelForm):
    class Meta:
        model=Address
        exclude=['user',]

