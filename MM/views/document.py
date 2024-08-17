import json
from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.db.models import QuerySet, Sum, F
from django.contrib.auth.decorators import login_required
from django.forms.models import model_to_dict
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import JsonResponse

from ..models import *
from .auxiliary import *


@login_required
def search_document_flow(request: HttpRequest):
    if request.method == 'POST':
        vendor_code = request.POST.get('vendor_code')
        time_range = request.POST.get('time_range')

        orders = PurchaseOrder.objects.all()
        invoices = Invoice.objects.all()
        receipts = GoodReceipt.objects.all()

        if vendor_code:
            orders = orders.filter(vendor__vid__exact=vendor_code)
            invoices = invoices.filter(orderItem__po__vendor__vid__exact=vendor_code)
            receipts = receipts.filter(orderItem__po__vendor__vid__exact=vendor_code)

        if time_range == '1':  # 近半年
            start_date = datetime.now() - timedelta(days=182)
        elif time_range == '2':  # 近三月
            start_date = datetime.now() - timedelta(days=91)
        else:
            start_date = None

        if start_date:
            orders = orders.filter(time__gte=start_date)
            invoices = invoices.filter(invoiceDate__gte=start_date)
            receipts = receipts.filter(time__gte=start_date)

        data = {
            'orders': list(orders.values('id', 'vendor__vname', 'time')),
            'invoices': list(invoices.values('id', 'orderItem__po__vendor__vname', 'invoiceDate')),
            'receipts': list(receipts.values('id', 'orderItem__po__vendor__vname', 'time')),
        }

        return JsonResponse(data)

    return render(
        request=request,
        template_name='../templates/document/search.html'
    )
