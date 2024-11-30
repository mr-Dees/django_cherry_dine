from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Order, MenuItem, Review


class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'address', 'first_name', 'last_name', 'phone_number']

    def save(self, commit=True):
        user = super().save(commit=False)
        # Сохраняем дополнительные поля в модель пользователя
        user.first_name = self.cleaned_data.get('first_name')
        user.last_name = self.cleaned_data.get('last_name')
        user.phone_number = self.cleaned_data.get('phone_number')
        user.address = self.cleaned_data.get('address')
        if commit:
            user.save()
        return user

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Оставляем подсказки только для формы регистрации
        self.fields['first_name'].help_text = "Необязательное поле"
        self.fields['last_name'].help_text = "Необязательное поле"
        self.fields['phone_number'].help_text = "Необязательное поле"
        self.fields['address'].help_text = "Необязательное поле"


class ProfileEditForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'email', 'address']  # Указываем, какие поля можно редактировать

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Выключаем подсказки
        self.fields['first_name'].help_text = ""
        self.fields['last_name'].help_text = ""
        self.fields['email'].help_text = ""
        self.fields['address'].help_text = ""


class OrderForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['items']


# forms.py

class MenuItemForm(forms.ModelForm):
    class Meta:
        model = MenuItem
        fields = ['name', 'description', 'category', 'price']
        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'price': forms.NumberInput(attrs={'step': '0.01', 'min': '0'}),
        }
        labels = {
            'name': 'Название блюда',
            'description': 'Описание',
            'category': 'Категория',
            'price': 'Цена',
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
