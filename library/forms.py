# library/forms.py
from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import Book, Member, BorrowRecord

class BookSearchForm(forms.Form):
    q = forms.CharField(
        required=False,
        label='Search',
        widget=forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Search books...'
        })
    )
    category = forms.ChoiceField(
        required=False,
        label='Category',
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        from .models import Category
        self.fields['category'].choices = [('', '----')] + [
            (c.id, c.name) for c in Category.objects.all()
        ]

class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(required=True)
    last_name = forms.CharField(required=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name', 'password1', 'password2']

class MemberProfileForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['membership_number']
        widgets = {
            'membership_number': forms.TextInput(attrs={'class': 'form-control'})
        }

class BorrowBookForm(forms.ModelForm):
    class Meta:
        model = BorrowRecord
        fields = []  # No fields needed as they're set in view