from django.contrib import admin

# Register your models here.
from django.contrib import admin
from .models import Product, Bill, BillItem, DenominationMaster, BillDenomination, ReturnDenomination


admin.site.register(Product)
admin.site.register(Bill)
admin.site.register(BillItem)
admin.site.register(DenominationMaster)
admin.site.register(BillDenomination)
admin.site.register(ReturnDenomination)