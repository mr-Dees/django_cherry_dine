from django.contrib import admin
from .models import User, MenuItem, Order, Review

# Регистрируем модели в админке
admin.site.register(User)
admin.site.register(MenuItem)
admin.site.register(Order)
admin.site.register(Review)
