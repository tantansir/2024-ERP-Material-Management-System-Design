from django.contrib import admin
from .models import *

# Register your models here.
admin.site.register(EUser)
admin.site.register(Vendor)
admin.site.register(Stock)
admin.site.register(Material)
admin.site.register(MaterialItem)
admin.site.register(StockHistory)
admin.site.register(PurchaseRequisition)
admin.site.register(RequisitionItem)
admin.site.register(Quotation)
admin.site.register(PurchaseOrder)
admin.site.register(OrderItem)
admin.site.register(GoodReceipt)
admin.site.register(Invoice)
admin.site.register(Account)
admin.site.register(AccountDetail)
admin.site.register(Record)
admin.site.register(Favorite)