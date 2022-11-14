from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register (ArtistProfile)
admin.site.register (CustomerProfile)
admin.site.register (Art)
admin.site.register (Order)
admin.site.register (OrderItem)
admin.site.register (Delivery)
