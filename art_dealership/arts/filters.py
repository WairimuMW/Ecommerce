import django_filters
from .models import *

class ArtFilter(django_filters.FilterSet):
    class Meta:
        model = Art
        fields = ['art_type']

class DeliveryFilter(django_filters.FilterSet):
    class Meta:
        model = Delivery
        fields = ['status']

class PaymentFilter(django_filters.FilterSet):
    class Meta:
        model = Delivery
        fields = ['payment']
        