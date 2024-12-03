from threading import Thread
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.db.models import Count
from CherryDineApp.models import MenuItem, OrderItem
from CherryDineProject import settings


def async_send_mail(subject, html_message, recipient_list):
    def send():
        send_mail(
            subject=subject,
            message='',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=recipient_list,
            html_message=html_message,
            fail_silently=False
        )

    Thread(target=send).start()


def send_order_notification(order):
    def process():
        subject = f'Заказ #{order.id} подтвержден'
        html_message = render_to_string('restaurant/email/order_confirmation.html', {
            'order': order,
            'items': order.orderitem_set.all()
        })
        async_send_mail(subject, html_message, [order.user.email])

    Thread(target=process).start()


def send_recommendations_email(user, order):
    def process():
        # Получаем категории блюд из текущего заказа
        ordered_categories = [item.menu_item.category for item in order.orderitem_set.all()]

        # Получаем ID уже заказанных блюд
        ordered_items = OrderItem.objects.filter(order__user=user).values_list('menu_item_id', flat=True)

        # Находим популярные блюда из тех же категорий
        recommendations = MenuItem.objects.filter(category__in=ordered_categories) \
                              .exclude(id__in=ordered_items) \
                              .annotate(order_count=Count('orderitem')) \
                              .order_by('-order_count')[:5]

        if not recommendations.exists():
            recommendations = MenuItem.objects.exclude(
                id__in=order.items.values_list('id', flat=True)
            ).order_by('?')[:5]

        subject = f'Рекомендации на основе вашего заказа #{order.id}'
        html_message = render_to_string('restaurant/email/recommendations.html', {
            'user': user,
            'order': order,
            'recommendations': recommendations,
        })
        async_send_mail(subject, html_message, [user.email])

    Thread(target=process).start()
