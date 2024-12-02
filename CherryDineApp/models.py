from django.contrib.auth.models import AbstractUser
from django.db import models


# Пользовательская модель с ролями
class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Администратор'),
        ('guest', 'Гость'),
    ]
    role = models.CharField(max_length=16, choices=ROLE_CHOICES, default='guest')
    phone_number = models.CharField(max_length=15, blank=True, null=True, help_text="")
    address = models.CharField(max_length=64, blank=True, null=True, help_text="")

    def __str__(self):
        return self.username


# Модель блюда в меню
class MenuItem(models.Model):
    CATEGORY_CHOICES = [
        ('starters', 'Закуски'),
        ('main', 'Основные блюда'),
        ('dessert', 'Десерты'),
    ]
    name = models.CharField(max_length=100)
    description = models.TextField()
    category = models.CharField(max_length=10, choices=CATEGORY_CHOICES)
    price = models.DecimalField(max_digits=6, decimal_places=2)

    def __str__(self):
        return self.name


# Модель заказа
class Order(models.Model):
    STATUS_CHOICES = [
        ('processing', 'В обработке'),
        ('ready', 'Готово'),
        ('delivered', 'Доставлено'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    items = models.ManyToManyField(MenuItem, through='OrderItem')
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='processing')
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def calculate_total(self):
        return sum(item.menu_item.price * item.quantity for item in self.orderitem_set.all())

    def __str__(self):
        return f"Заказ #{self.id} от {self.user.username}"


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)


# Модель отзыва
class Review(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    menu_item = models.ForeignKey(MenuItem, on_delete=models.CASCADE)
    order = models.ForeignKey(Order, on_delete=models.CASCADE)
    rating = models.PositiveSmallIntegerField()
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв от {self.user.username} на {self.menu_item.name}"
