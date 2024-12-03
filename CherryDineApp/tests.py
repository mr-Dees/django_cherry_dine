from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from decimal import Decimal
from unittest.mock import patch
import json

from .models import User, MenuItem, Order, OrderItem


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
