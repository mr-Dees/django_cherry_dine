from django.test import TestCase, Client
from django.urls import reverse
from decimal import Decimal
from unittest.mock import patch
from .models import User, MenuItem, Order, OrderItem
import json


class OrderTestCase(TestCase):
    def setUp(self):
        # Создаем тестового пользователя
        self.client = Client()
        self.user = User.objects.create_user(
            username='user',
            password='pass',
            email='user@mail.ru'
        )

        # Создаем админа
        self.admin = User.objects.create_user(
            username='admin',
            password='pass',
            email='admin@mail.ru',
            role='admin'
        )

        # Создаем тестовое блюдо
        self.menu_item = MenuItem.objects.create(
            name='Тестовое блюдо',
            description='Описание',
            category='main',
            price=Decimal('100.00')
        )

    @patch('CherryDineApp.views.send_order_notification')
    def test_create_order(self, mock_send_notification):
        """Тест создания заказа"""
        self.client.login(username='user', password='pass')

        # Добавляем товар в корзину
        session = self.client.session
        session['cart'] = {str(self.menu_item.id): 2}
        session.save()

        response = self.client.post(reverse('create_order'))

        self.assertEqual(response.status_code, 302)
        order = Order.objects.first()
        self.assertIsNotNone(order)
        self.assertEqual(order.user, self.user)
        self.assertEqual(order.status, 'processing')
        self.assertEqual(order.total_price, Decimal('200.00'))
        mock_send_notification.assert_called_once()

    @patch('CherryDineApp.views.send_recommendations_email')
    def test_update_order_status(self, mock_send_recommendations):
        """Тест обновления статуса заказа"""
        self.client.login(username='admin', password='pass')

        order = Order.objects.create(
            user=self.user,
            status='processing',
            total_price=Decimal('200.00')
        )
        OrderItem.objects.create(
            order=order,
            menu_item=self.menu_item,
            quantity=2
        )

        response = self.client.post(
            reverse('update_order_status', args=[order.id]),
            data=json.dumps({'status': 'delivered'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])
        order.refresh_from_db()
        self.assertEqual(order.status, 'delivered')
        mock_send_recommendations.assert_called_once()

    def test_cancel_order(self):
        """Тест отмены заказа"""
        self.client.login(username='user', password='pass')

        order = Order.objects.create(
            user=self.user,
            status='processing',
            total_price=Decimal('200.00')
        )

        response = self.client.post(reverse('cancel_order', args=[order.id]))

        self.assertEqual(response.status_code, 302)
        order.refresh_from_db()
        self.assertEqual(order.status, 'cancelled')

    def test_non_admin_cannot_update_status(self):
        """Тест запрета обновления статуса не-админом"""
        self.client.login(username='user', password='pass')

        order = Order.objects.create(
            user=self.user,
            status='processing',
            total_price=Decimal('200.00')
        )

        response = self.client.post(
            reverse('update_order_status', args=[order.id]),
            data=json.dumps({'status': 'delivered'}),
            content_type='application/json'
        )

        self.assertEqual(response.status_code, 403)

    def test_cart_operations(self):
        """Тест операций с корзиной"""
        self.client.login(username='user', password='pass')

        # Добавление в корзину
        response = self.client.post(
            reverse('add_to_cart', args=[self.menu_item.id]),
            data=json.dumps({'quantity': 2}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)
        self.assertTrue(response.json()['success'])

        cart = self.client.session.get('cart', {})
        self.assertEqual(cart.get(str(self.menu_item.id)), 2)

        # Обновление количества
        response = self.client.post(
            reverse('update_cart_quantity', args=[self.menu_item.id]),
            data=json.dumps({'quantity': 3}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 200)

        # Удаление из корзины
        response = self.client.post(reverse('remove_from_cart', args=[self.menu_item.id]))
        self.assertEqual(response.status_code, 200)
        cart = self.client.session.get('cart', {})
        self.assertNotIn(str(self.menu_item.id), cart)

    def test_cart_total_calculation(self):
        """Тест расчета общей стоимости корзины"""
        self.client.login(username='user', password='pass')

        second_item = MenuItem.objects.create(
            name='Второе тестовое блюдо',
            description='Описание',
            category='main',
            price=Decimal('150.00')
        )

        session = self.client.session
        session['cart'] = {
            str(self.menu_item.id): 2,  # 100 * 2 = 200
            str(second_item.id): 3  # 150 * 3 = 450
        }
        session.save()

        response = self.client.get(reverse('cart'))

        self.assertEqual(response.context['total_price'], Decimal('650.00'))

    def test_invalid_cart_operations(self):
        """Тест обработки некорректных операций с корзиной"""
        self.client.login(username='user', password='pass')

        # Попытка добавить несуществующий товар
        response = self.client.post(
            reverse('add_to_cart', args=[999]),
            data=json.dumps({'quantity': 1}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 404)

        # Попытка обновить количество несуществующего товара
        response = self.client.post(
            reverse('update_cart_quantity', args=[999]),
            data=json.dumps({'quantity': 1}),
            content_type='application/json'
        )
        self.assertEqual(response.status_code, 400)

    def test_add_review(self):
        """Тест добавления отзыва"""
        self.client.login(username='user', password='pass')

        order = Order.objects.create(
            user=self.user,
            status='delivered',
            total_price=Decimal('200.00')
        )

        response = self.client.post(
            reverse('add_review', args=[order.id]),
            data={'rating': 5, 'comment': 'Отличный заказ'}
        )

        self.assertEqual(response.status_code, 302)
        review = order.review_set.first()
        self.assertIsNotNone(review)
        self.assertEqual(review.rating, 5)

    def test_duplicate_review(self):
        """Тест запрета повторных отзывов"""
        self.client.login(username='user', password='pass')

        order = Order.objects.create(
            user=self.user,
            status='delivered',
            total_price=Decimal('200.00')
        )

        # Первый отзыв
        self.client.post(
            reverse('add_review', args=[order.id]),
            data={'rating': 5, 'comment': 'Отличный заказ'}
        )

        # Повторный отзыв
        response = self.client.post(
            reverse('add_review', args=[order.id]),
            data={'rating': 4, 'comment': 'Другой отзыв'}
        )

        self.assertEqual(order.review_set.count(), 1)

    def test_profile_edit(self):
        """Тест редактирования профиля"""
        self.client.login(username='user', password='pass')

        response = self.client.post(
            reverse('profile_edit'),
            data={
                'first_name': 'John',
                'last_name': 'Doe',
                'email': 'new@mail.ru',
                'address': 'New Address'
            }
        )

        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'John')
        self.assertEqual(self.user.email, 'new@mail.ru')

    def test_menu_filtering(self):
        """Тест фильтрации меню"""
        MenuItem.objects.create(
            name='Десерт',
            description='Описание',
            category='dessert',
            price=Decimal('50.00')
        )

        response = self.client.get(
            reverse('menu'),
            {'category': 'main', 'min_price': '90', 'max_price': '110'}
        )

        self.assertEqual(len(response.context['dishes']), 1)
        self.assertEqual(response.context['dishes'][0], self.menu_item)

    def test_menu_sorting(self):
        """Тест сортировки меню"""
        MenuItem.objects.create(
            name='Абрикос',
            description='Описание',
            category='dessert',
            price=Decimal('50.00')
        )

        response = self.client.get(reverse('menu'), {'sort': 'name'})
        dishes = list(response.context['dishes'])
        self.assertEqual(dishes[0].name, 'Абрикос')

    def test_menu_item_image(self):
        """Тест загрузки изображения блюда"""
        self.client.login(username='admin', password='pass')

        # Создаем временный файл для теста
        from PIL import Image
        import tempfile

        # Создаем временное изображение
        image = Image.new('RGB', (100, 100), color='red')
        temp_file = tempfile.NamedTemporaryFile(suffix='.jpg')
        image.save(temp_file)
        temp_file.seek(0)

        response = self.client.post(
            reverse('add_menu_item'),
            {
                'name': 'Блюдо с картинкой',
                'description': 'Описание',
                'category': 'main',
                'price': '100.00',
                'image': temp_file
            }
        )

        menu_item = MenuItem.objects.get(name='Блюдо с картинкой')
        self.assertTrue(menu_item.image)
