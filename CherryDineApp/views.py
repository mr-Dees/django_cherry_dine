from django.contrib import messages
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required, user_passes_test
import json
from django.http import HttpResponseForbidden, JsonResponse
from django.shortcuts import render, redirect, get_object_or_404
from django.core.mail import send_mail
from .forms import RegistrationForm, LoginForm, ProfileEditForm, MenuItemForm, OrderForm, ReviewForm
from .models import User, MenuItem, Order, Review, OrderItem
from .filters import MenuItemFilter


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
    return render(request, 'restaurant/auth/register.html', {'form': form})


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
    return render(request, 'restaurant/auth/login.html', {'form': form})


def logout_view(request):
    logout(request)
    return redirect('index')


def menu(request):
    # Если пользователь не авторизован, показываем сообщение
    if not request.user.is_authenticated:
        messages.info(request, 'Для оформления заказа необходимо войти или зарегистрироваться')

    # Получаем все блюда
    queryset = MenuItem.objects.all()

    # Применяем фильтры
    menu_filter = MenuItemFilter(request.GET, queryset=queryset)
    filtered_dishes = menu_filter.qs

    # Применяем сортировку
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'name':
            filtered_dishes = filtered_dishes.order_by('name')
        elif sort_by == 'name_desc':
            filtered_dishes = filtered_dishes.order_by('-name')
        elif sort_by == 'price':
            filtered_dishes = filtered_dishes.order_by('price')
        elif sort_by == 'price_desc':
            filtered_dishes = filtered_dishes.order_by('-price')
        elif sort_by == 'category':
            filtered_dishes = filtered_dishes.order_by('category', 'name')
        elif sort_by == 'category_desc':
            filtered_dishes = filtered_dishes.order_by('-category', 'name')

    # Добавляем информацию о корзине
    cart = request.session.get('cart', {})
    for dish in filtered_dishes:
        dish.in_cart = str(dish.id) in cart

    context = {
        'dishes': filtered_dishes,
        'filter': menu_filter,
        'current_sort': sort_by,
    }
    return render(request, 'shared/menu.html', context)


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
    # Если пользователь не авторизован, показываем сообщение
    if not request.user.is_authenticated:
        messages.info(request, 'Для оформления заказа необходимо войти или зарегистрироваться')

    dish = get_object_or_404(MenuItem, pk=pk)
    cart = request.session.get('cart', {})
    dish.in_cart = str(pk) in cart

    context = {
        'dish': dish,
    }
    return render(request, 'shared/dish_detail.html', context)


@login_required
def create_order(request):
    if request.method == 'POST':
        cart = request.session.get('cart', {})

        if not cart:
            messages.error(request, 'Корзина пуста')
            return redirect('cart')

        try:
            # Создаем заказ
            order = Order.objects.create(
                user=request.user,
                status='processing',
                total_price=sum(
                    MenuItem.objects.get(id=item_id).price * quantity
                    for item_id, quantity in cart.items()
                )
            )

            # Добавляем товары в заказ
            for item_id, quantity in cart.items():
                menu_item = MenuItem.objects.get(id=item_id)
                OrderItem.objects.create(
                    order=order,
                    menu_item=menu_item,
                    quantity=quantity
                )

            # Очищаем корзину
            request.session['cart'] = {}
            messages.success(request, 'Заказ успешно создан')
            return redirect('order_list')

        except Exception as e:
            print("Error:", str(e))
            messages.error(request, f'Ошибка при создании заказа: {str(e)}')
            return redirect('cart')

    return redirect('cart')


def order_detail(request, pk):
    order = get_object_or_404(Order, pk=pk)
    return render(request, 'guest/order/order_detail.html', {'order': order})


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

    # Сортировка
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'name':
            menu_items = menu_items.order_by('name')
        elif sort_by == 'name_desc':
            menu_items = menu_items.order_by('-name')
        elif sort_by == 'price':
            menu_items = menu_items.order_by('price')
        elif sort_by == 'price_desc':
            menu_items = menu_items.order_by('-price')

    items_with_details = []
    for item in menu_items:
        quantity = cart_items[str(item.id)]
        items_with_details.append({
            'item': item,
            'quantity': quantity,
            'subtotal': item.price * quantity,
        })

    # Сортировка по сумме позиции
    if sort_by == 'subtotal':
        items_with_details = sorted(items_with_details, key=lambda x: x['subtotal'])
    elif sort_by == 'subtotal_desc':
        items_with_details = sorted(items_with_details, key=lambda x: x['subtotal'], reverse=True)

    context = {
        'items_with_details': items_with_details,
        'total_price': sum(item['subtotal'] for item in items_with_details),
        'current_sort': sort_by,
    }
    return render(request, 'guest/order/cart.html', context)


@login_required
def add_to_cart(request, item_id):
    if request.method == 'POST':
        # Проверяем, есть ли JSON данные в запросе
        if not request.body or not request.headers.get('Content-Type') == 'application/json':
            return JsonResponse({'success': True}, status=200)  # Возвращаем без сообщения

        try:
            # Получаем данные из JSON
            data = json.loads(request.body.decode('utf-8'))
            quantity = int(data.get('quantity', 1))

            # Получаем товар
            menu_item = MenuItem.objects.get(id=item_id)

            # Обновляем корзину
            cart = request.session.get('cart', {})
            item_id = str(item_id)

            # Если товар уже есть в корзине, прибавляем количество
            if item_id in cart:
                cart[item_id] += quantity
            else:
                cart[item_id] = quantity

            request.session['cart'] = cart

            return JsonResponse({
                'success': True,
                'message': f'{menu_item.name} добавлен в корзину ({quantity} шт.)',
                'cart_total': sum(cart.values())
            })

        except MenuItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            }, status=404)

    return JsonResponse({
        'success': False,
        'message': 'Неверный метод запроса'
    }, status=405)


@login_required
def remove_from_cart(request, item_id):
    if request.method == 'POST':
        cart = request.session.get('cart', {})
        item_id = str(item_id)

        try:
            menu_item = MenuItem.objects.get(id=item_id)
            if item_id in cart:
                del cart[item_id]
                request.session['cart'] = cart
                return JsonResponse({
                    'success': True,
                    'message': f'{menu_item.name} удален из корзины',
                    'cart_total': sum(cart.values())
                })
        except MenuItem.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'Товар не найден'
            })

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


@login_required
def update_cart_quantity(request, item_id):
    if request.method == 'POST':
        try:
            data = json.loads(request.body.decode('utf-8'))
            quantity = int(data.get('quantity', 1))
            cart = request.session.get('cart', {})
            item_id = str(item_id)

            menu_item = MenuItem.objects.get(id=item_id)
            cart[item_id] = quantity
            request.session['cart'] = cart
            subtotal = menu_item.price * quantity

            return JsonResponse({
                'success': True,
                'message': 'Количество обновлено',
                'subtotal': float(subtotal),
                'cart_total': sum(cart.values())
            })
        except (json.JSONDecodeError, ValueError, MenuItem.DoesNotExist) as e:
            return JsonResponse({
                'success': False,
                'message': str(e)
            }, status=400)

    return JsonResponse({
        'success': False,
        'message': 'Метод не поддерживается'
    }, status=405)


@login_required
def update_order_status(request, order_id):
    if request.user.role != 'admin':
        return JsonResponse({'success': False, 'message': 'Доступ запрещен'}, status=403)

    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order = Order.objects.get(id=order_id)
            order.status = data['status']
            order.save()
            return JsonResponse({'success': True})
        except Exception as e:
            return JsonResponse({'success': False, 'message': str(e)})

    return JsonResponse({'success': False, 'message': 'Неверный метод запроса'})


# Список заказов
@login_required
def order_list(request):
    if request.user.role == 'admin':
        orders = Order.objects.all()
    else:
        orders = Order.objects.filter(user=request.user)

    # Сортировка
    sort_by = request.GET.get('sort')
    if sort_by:
        if sort_by == 'date':
            orders = orders.order_by('created_at')
        elif sort_by == 'date_desc':
            orders = orders.order_by('-created_at')
        elif sort_by == 'status':
            orders = orders.order_by('status')
        elif sort_by == 'status_desc':
            orders = orders.order_by('-status')
        elif sort_by == 'price':
            orders = orders.order_by('total_price')
        elif sort_by == 'price_desc':
            orders = orders.order_by('-total_price')
    else:
        orders = orders.order_by('-created_at')  # По умолчанию новые сверху

    return render(request, 'guest/order/order_list.html', {
        'orders': orders,
        'current_sort': sort_by,
    })


@login_required
def add_review(request, order_id):
    order = get_object_or_404(Order, id=order_id, user=request.user)

    # Проверяем, существует ли уже отзыв для этого заказа
    existing_review = Review.objects.filter(order=order).first()
    if existing_review:
        messages.error(request, 'Вы уже оставили отзыв к этому заказу')
        return redirect('profile')

    if request.method == 'POST':
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.user = request.user
            review.order = order
            review.save()
            messages.success(request, 'Спасибо за ваш отзыв!')
            return redirect('profile')
    else:
        form = ReviewForm()

    return render(request, 'guest/add_review.html', {
        'form': form,
        'order': order
    })


@login_required
def profile(request):
    # Получаем только доставленные заказы
    delivered_orders = Order.objects.filter(
        user=request.user,
        status='delivered'
    ).order_by('-created_at')

    context = {
        'orders': delivered_orders,
    }
    return render(request, 'shared/profile.html', context)


@login_required
def profile_edit(request):
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('profile')  # После успешного сохранения возвращаемся к профилю
    else:
        form = ProfileEditForm(instance=request.user)  # Загружаем данные текущего пользователя

    return render(request, 'shared/profile_edit.html', {'form': form})
