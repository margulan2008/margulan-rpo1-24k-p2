from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Ad, Review

class UserRegisterForm(UserCreationForm):
    email = forms.EmailField(required=True, label='Email')
    first_name = forms.CharField(max_length=30, required=True, label='Имя')
    last_name = forms.CharField(max_length=30, required=True, label='Фамилия')
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ('username', 'email', 'first_name', 'last_name')

class AdForm(forms.ModelForm):
    class Meta:
        model = Ad
        fields = ['category', 'city', 'image', 'title', 'description', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'rating': forms.RadioSelect(),
            'comment': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Напишите ваш отзыв...'}),
        }
