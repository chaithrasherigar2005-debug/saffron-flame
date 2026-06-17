from django.contrib import admin
from .models import Category, MenuItem
from .models import UserProfile
from .models import Order, OrderItem
from .models import Reservation


admin.site.register(Category)
admin.site.register(MenuItem)
admin.site.register(UserProfile)
admin.site.register(Order)
admin.site.register(OrderItem)
admin.site.register(Reservation)