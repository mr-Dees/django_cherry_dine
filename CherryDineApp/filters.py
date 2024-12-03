import django_filters
from .models import MenuItem


class MenuItemFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = django_filters.NumberFilter(field_name='price', lookup_expr='lte')

    class Meta:
        model = MenuItem
        fields = ['category', 'min_price', 'max_price']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.filters['category'].label = 'Категория'
        self.filters['min_price'].label = 'Цена от'
        self.filters['max_price'].label = 'Цена до'
