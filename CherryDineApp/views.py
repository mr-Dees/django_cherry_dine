from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .forms import RegistrationForm, LoginForm, ProfileEditForm, MenuItemForm, OrderForm, ReviewForm
from .models import User, MenuItem, Order, Review


def is_admin(user):
    return user.role == 'admin'


def send_order_confirmation_email(order):
    subject = f'Подтверждение заказа #{order.id}'
    message = f'Ваш заказ #{order.id} успешно оформлен и находится в обработке.'
    from_email = 'noreply@cherrydine.com'
    recipient_list = [order.user.email]
    send_mail(subject, message, from_email, recipient_list)


def index(request):
    context = {
        'categories': MenuItem.objects.values('category').distinct(),
        'popular_dishes': MenuItem.objects.all()[:6]  # Лимит 6 блюд
    }
    return render(request, 'index.html', context)


def register(request):
    if request.method == 'POST':
        form = RegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            messages.success(request, 'Вы успешно зарегистрировались!')
            return redirect('login')
    else:
        form = RegistrationForm()
    return render(request, 'auth/register.html', {'form': form})


def login_view(request):
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user:
                login(request, user)
                return redirect('index')
            else:
                messages.error(request, 'Неверное имя пользователя или пароль')
    else:
        form = LoginForm()
    return render(request, 'auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


@login_required
def menu(request):
    items = MenuItem.objects.all()
    return render(request, 'shared/menu.html', {'dishes': items})


@login_required
def add_menu_item(request):
    # Проверяем, что пользователь является администратором
    if not request.user.role == 'admin':
        messages.error(request, 'У вас нет прав для добавления блюд')
        return redirect('menu')

    if request.method == 'POST':
        form = MenuItemForm(request.POST)
        if form.is_valid():
            menu_item = form.save()
            messages.success(request, f'Блюдо "{menu_item.name}" успешно добавлено в меню')
            return redirect('menu')
    else:
        form = MenuItemForm()

    return render(request, 'admin/add_menu_item.html', {'form': form})


@login_required
def edit_menu_item(request, pk):
    if not request.user.role == 'admin':
        messages.error(request, 'У вас нет прав для редактирования блюд')
        return redirect('menu')

    menu_item = get_object_or_404(MenuItem, pk=pk)
    # Получаем параметр next из GET или POST запроса
    next_page = request.GET.get('next') or request.POST.get('next', 'menu')

    if request.method == 'POST':
        form = MenuItemForm(request.POST, instance=menu_item)
        if form.is_valid():
            form.save()
            messages.success(request, f'Блюдо "{menu_item.name}" успешно обновлено')
            # Перенаправляем на указанную страницу
            if next_page == 'detail':
                return redirect('dish_detail', pk=pk)
            return redirect('menu')
    else:
        form = MenuItemForm(instance=menu_item)

    return render(request, 'admin/edit_menu_item.html', {
        'form': form,
        'menu_item': menu_item,
        'next_page': next_page
    })


@login_required
def delete_menu_item(request, pk):
    # Проверяем, что пользователь является администратором
    if not request.user.role == 'admin':
        messages.error(request, 'У вас нет прав для удаления блюд')
        return redirect('menu')

    menu_item = get_object_or_404(MenuItem, pk=pk)

    if request.method == 'POST':
        menu_item.delete()
        messages.success(request, f'Блюдо "{menu_item.name}" успешно удалено')
        return redirect('menu')

    return redirect('menu')


def dish_detail(request, pk):
    dish = get_object_or_404(MenuItem, pk=pk)
    return render(request, 'shared/dish_detail.html', {'dish': dish})


@login_required
def create_order(request):
    if request.method == 'POST':
        form = OrderForm(request.POST)
        if form.is_valid():
            order = form.save(commit=False)
            order.user = request.user
            order.save()
            form.save_m2m()
            send_order_confirmation_email(order)
            return redirect('order_detail', order_id=order.id)
    else:
        form = OrderForm()
    return render(request, 'guest/order/order_create.html', {'form': form})


@login_required
def cancel_order(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    if order.status == 'processing':
        order.delete()
        messages.success(request, 'Заказ успешно отменен')
    else:
        messages.error(request, 'Невозможно отменить заказ, так как он уже в обработке')
    return redirect('order_list')


# Корзина
@login_required
def cart(request):
    cart_items = request.session.get('cart', {})
    menu_items = MenuItem.objects.filter(id__in=cart_items.keys())

    items_with_details = []
    total_price = 0

    for item in menu_items:
        quantity = cart_items[str(item.id)]
        subtotal = item.price * quantity
        total_price += subtotal
        items_with_details.append({
            'item': item,
            'quantity': quantity,
            'subtotal': subtotal,
        })

    context = {
        'items_with_details': items_with_details,
        'total_price': total_price,
    }
    return render(request, 'guest/order/cart.html', context)


@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        item_id = str(item_id)

        try:
            menu_item = MenuItem.objects.get(id=item_id)
            cart[item_id] = cart.get(item_id, 0) + 1
            request.session['cart'] = cart

            return JsonResponse({
                'success': True,
                'message': f'{menu_item.name} добавлен в корзину',
                'cart_total': sum(cart.values())  # Общее количество товаров в корзине
            })

        except MenuItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            }, status=404)

    return JsonResponse({
        'success': False,
        'message': 'Неверный метод запроса'
    }, status=400)


@login_required
def remove_from_cart(request, item_id):
    cart = request.session.get('cart', {})
    if item_id in cart:
        del cart[item_id]
    request.session['cart'] = cart
    return redirect('cart')


# Список заказов
@login_required
def order_list(request):
    """Просмотр списка заказов текущего пользователя."""
    orders = Order.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'guest/order/order_list.html', {'orders': orders})


@login_required
def add_review(request, order_id):
    order = Order.objects.get(id=order_id, user=request.user)
    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.order = order
            review.save()
            return redirect('order_detail', order_id=order.id)
    else:
        form = ReviewForm()
    return render(request, 'guest/add_review.html', {'form': form, 'order': order})


@login_required
def profile(request):
    orders = Order.objects.filter(user=request.user)
    return render(request, 'guest/profile.html', {'orders': orders})


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # После успешного сохранения возвращаемся к профилю
    else:
        form = ProfileEditForm(instance=request.user)  # Загружаем данные текущего пользователя

    return render(request, 'guest/profile_edit.html', {'form': form})
