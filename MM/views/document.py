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
import datetime
from django.http import JsonResponse

from ..models import *
from .auxiliary import *


@login_required
def search_document_flow(request: HttpRequest):
    if request.method == 'POST':
        materialitem_id = request.POST.get('materialitemid')
        time_range = request.POST.get('time_range')

        orderitems = OrderItem.objects.all()

        if materialitem_id:
            orderitems = orderitems.filter(meterialItem__id__exact=materialitem_id)

        if time_range == '1':  # 近半年
            start_date = datetime.datetime.now() - datetime.timedelta(days=182)
        elif time_range == '2':  # 近三月
            start_date = datetime.datetime.now() - datetime.timedelta(days=91)
        else:
            start_date = None

        if start_date:
            orderitems = orderitems.filter(po__time__gte=start_date)

        data = {
            'orderitems': list(orderitems.values('po', 'po__euser__id', 'po__vendor__vname', 'id', 'itemId',
                                                 'meterialItem__material__mname', 'po__time')),
        }

        return JsonResponse(data)

    return render(
        request=request,
        template_name='../templates/document/search.html'
    )

@login_required
def display_document_flow(request: HttpRequest, pk):
    if request.method != 'POST':
        orderitem = get_object_or_404(OrderItem, pk=pk)
        po=orderitem.po
        materialitem = orderitem.meterialItem
        material=materialitem.material
        stock=materialitem.stock
        invoice=Invoice.objects.filter(orderItem=orderitem).first()
        goodreceipt=GoodReceipt.objects.filter(orderItem=orderitem).first()
        invoice_dict={}
        goodreceipt_dict={}
        if(invoice):
            invoice_dict = model_to_dict(invoice)
        if(goodreceipt):
            goodreceipt_dict = model_to_dict(goodreceipt)
        po_dict = model_to_dict(po)
        po_dict['time'] = po.time.strftime('%Y-%m-%d %H:%M:%S')  # Format datetime to string
        data = {
            'material': model_to_dict(material),
            'stock': model_to_dict(stock),
            'materialitem': model_to_dict(materialitem),
            'po': po_dict,
            'orderitem': model_to_dict(orderitem),
            'goodreceipt': goodreceipt_dict,
            'invoice': invoice_dict
        }

        return render(
            request=request,
            template_name='../templates/document/display.html',
            context=data
        )

