from django_filters import rest_framework as filters
from .models import Restaurant, MenuItem


class RestaurantFilter(filters.FilterSet):
    city = filters.CharFilter(field_name='city', lookup_expr='iexact')
    cuisine = filters.CharFilter(field_name='cuisine', lookup_expr='icontains')
    is_pure_veg = filters.BooleanFilter(field_name='is_pure_veg')
    is_open = filters.BooleanFilter(field_name='is_open')
    min_rating = filters.NumberFilter(field_name='rating', lookup_expr='gte')
    max_cost = filters.NumberFilter(field_name='avg_cost_for_two', lookup_expr='lte')
    fast_delivery = filters.BooleanFilter(method='filter_fast_delivery')

    class Meta:
        model = Restaurant
        fields = ['city', 'cuisine', 'is_pure_veg', 'is_open', 'min_rating', 'max_cost', 'fast_delivery']

    def filter_fast_delivery(self, queryset, name, value):
        if value:
            return queryset.filter(delivery_time__lte=30)
        return queryset


class MenuItemFilter(filters.FilterSet):
    category = filters.CharFilter(field_name='category', lookup_expr='iexact')
    is_veg = filters.BooleanFilter(field_name='is_veg')
    is_bestseller = filters.BooleanFilter(field_name='is_bestseller')
    is_available = filters.BooleanFilter(field_name='is_available')

    class Meta:
        model = MenuItem
        fields = ['category', 'is_veg', 'is_bestseller', 'is_available']
