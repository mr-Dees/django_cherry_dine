from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User, Order, MenuItem, Review


class LoginForm(forms.Form):
    username = forms.CharField(
        label='Имя пользователя',
        widget=forms.TextInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Введите имя пользователя'
        })
    )
    password = forms.CharField(
        label='Пароль',
        widget=forms.PasswordInput(attrs={
            'class': 'form-control mb-3',
            'placeholder': 'Введите пароль'
        })
    )


class RegistrationForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2', 'address', 'first_name', 'last_name', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Настраиваем поля формы
        self.fields['username'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Введите имя пользователя'
        })
        self.fields['email'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Введите email'
        })
        self.fields['password1'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Введите пароль'
        })
        self.fields['password2'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Подтвердите пароль'
        })
        self.fields['first_name'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Имя'
        })
        self.fields['last_name'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Фамилия'
        })
        self.fields['phone_number'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Номер телефона'
        })
        self.fields['address'].widget.attrs.update({
            'class': 'form-control mb-3',
            'placeholder': 'Адрес доставки'
        })

        # Обновляем help_texts
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


# forms.py
class ReviewForm(forms.ModelForm):
    rating = forms.IntegerField(
        label='Оценка',
        widget=forms.NumberInput(
            attrs={
                'class': 'form-control',
                'min': '1',
                'max': '5',
                'placeholder': 'Оценка от 1 до 5'
            }
        )
    )
    comment = forms.CharField(
        label='Комментарий',
        widget=forms.Textarea(
            attrs={
                'class': 'form-control',
                'rows': 4,
                'placeholder': 'Напишите ваш отзыв'
            }
        )
    )

    class Meta:
        model = Review
        fields = ['rating', 'comment']
