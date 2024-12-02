from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),

    # Авторизация
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),

    # Меню
    path('menu/', views.menu, name='menu'),
    path('menu/edit/<int:pk>/', views.edit_menu_item, name='edit_menu_item'),
    path('menu/delete/<int:pk>/', views.delete_menu_item, name='delete_menu_item'),
    path('add-menu-item/', views.add_menu_item, name='add_menu_item'),
    path('dish/<int:pk>/', views.dish_detail, name='dish_detail'),

    # Корзина
    path('cart/', views.cart, name='cart'),
    path('cart/add/<int:item_id>/', views.add_to_cart, name='add_to_cart'),
    path('cart/update/<int:item_id>/', views.update_cart_quantity, name='update_cart_quantity'),
    path('cart/remove/<int:item_id>/', views.remove_from_cart, name='remove_from_cart'),

    # Заказы
    path('orders/', views.order_list, name='order_list'),
    path('orders/<int:pk>/', views.order_detail, name='order_detail'),
    path('create-order/', views.create_order, name='create_order'),
    path('cancel-order/<int:order_id>/', views.cancel_order, name='cancel_order'),

    # Профиль
    path('profile/', views.profile, name='profile'),
    path('profile/edit/', views.profile_edit, name='profile_edit'),

    # Отзывы
    path('add-review/<int:order_id>/', views.add_review, name='add_review'),
]