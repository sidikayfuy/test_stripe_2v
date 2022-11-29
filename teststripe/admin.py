from django.contrib import admin
from .models import Item, TypeCurrency, Currency, Order, ItemOrder, Discount, Promocode, Tax

admin.site.register(Item)
admin.site.register(TypeCurrency)
admin.site.register(Currency)
admin.site.register(Order)
admin.site.register(ItemOrder)
admin.site.register(Discount)
admin.site.register(Promocode)
admin.site.register(Tax)
