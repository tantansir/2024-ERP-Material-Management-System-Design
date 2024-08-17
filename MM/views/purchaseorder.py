import json
from django.core import serializers
from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required
from django import forms
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from datetime import timedelta, date
from .auxiliary import getRegex


from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required

from ..models import EUser, Material, MaterialItem, Stock
from .auxiliary import *


from ..models import EUser, Material, MaterialItem, Stock,PurchaseRequisition,RequisitionItem,Quotation,Vendor,PurchaseOrder,OrderItem
from django.shortcuts import redirect


class PurchaseorderForm(forms.Form):
    euserid = forms.CharField(label="创建者ID", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    telephone = forms.CharField(label="收货方电话", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    fax = forms.CharField(label="收货方传真", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    shippingAddress = forms.CharField(label="送货地址", max_length=256, widget=forms.TextInput(attrs={'class': 'form-control'}))
    vendor_id = forms.CharField(label="参考供应商编码", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    rfq__id = forms.CharField(label="参考询价单编码", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))


class OrderForem(forms.Form):
    pid = forms.CharField(label="采购订单编码", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    itemId = forms.CharField(label="条目编码", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    price = forms.CharField(label="单价", max_length=256,widget=forms.TextInput(attrs={'class': 'form-control'}))
    currency = forms.CharField(label="货币", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    quantity = forms.CharField(label="数量", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    deliveryDate = forms.CharField(label="送货时间", max_length=128,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    plant = forms.CharField(label="工厂", max_length=128,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    material_id = forms.CharField(label="物料编码", max_length=128,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))


class ComplexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime('%Y-%m-%d %H:%M:%S')
        elif isinstance(obj, date):
            return obj.strftime('%Y-%m-%d')
        else:
            return json.JSONEncoder.default(self, obj)


"""
2. FUNCTION(查找采购订单)
"""
def getquotebyid(request: HttpRequest, pk):
    if request.method == "GET":
        pk = str(int(pk))
        print("pk:", pk)
        quotation = Quotation.objects.filter(id = pk).values()


@csrf_exempt
def vqcreate(request: HttpRequest, pk):
    if request.method == "GET":
        pk = str(int(pk))
        print("pk:", pk)
        quotation = Quotation.objects.filter(id = pk).values()
        vendorid = quotation[0]['vendor_id']
        riid = quotation[0]['ri_id']
        vendor = Vendor.objects.filter(vid = vendorid).values()
        requisitionItem = RequisitionItem.objects.filter(id = riid).values()
        miid = requisitionItem[0]['meterial_id']
        mate = RequisitionItem.objects.filter(id = riid).values("meterial__id",  "meterial__stock__id",
                                                                                             "quantity","deliveryDate",
                                                                "meterial__stock__pOrg","meterial__stock__pGrp","meterial__sloc",
                                                                "meterial__stock__name")

        materialitem = list(mate)
        vendor = list(vendor)
        quotation = list(quotation)
        return render(request, '../templates/quotation/vq-create.html', locals())
    if request.method == "POST":
        pk = str(int(pk))
        price = request.POST.get("price")
        currency = request.POST.get("currency")
        validTime = request.POST.get("validTime")
        validTime = getDate2(validTime)
        quotation1 = Quotation.objects.filter(id=pk).update(price=price,  validTime=validTime,currency=currency)
        quotation = Quotation.objects.filter(id=pk).values()
        vendorid = quotation[0]['vendor_id']
        riid = quotation[0]['ri_id']
        vendor = Vendor.objects.filter(vid=vendorid).values()
        requisitionItem = RequisitionItem.objects.filter(id=riid).values()
        miid = requisitionItem[0]['meterial_id']
        mate = RequisitionItem.objects.filter(id=riid).values("meterial__id", "meterial__stock__id",
                                                              "quantity",
                                                              "deliveryDate", "meterial__stock__pOrg",
                                                              "meterial__stock__pGrp",
                                                              "meterial__sloc", "meterial__stock__name")

        materialitem = list(mate)
        vendor = list(vendor)
        quotation = list(quotation)
        if quotation1:
            insertmessage = "修改成功"
            return render(request, '../templates/quotation/vq-create.html', locals())
        else:
            insertmessage = "修改失败"
            return render(request, '../templates/quotation/vq-create.html', locals())


@csrf_exempt
def vqcreatejiekou(request):
    if request.method == "POST":
        pk = request.POST.get("quoid")
        print("id:",pk)
        price = request.POST.get("price")
        currency = request.POST.get("currency")
        validTime = request.POST.get("validTime")
        validTime = getDate2(validTime)
        quotation1 = Quotation.objects.filter(id=pk).update(price=price, validTime=validTime, currency=currency)
        if quotation1:
            print("修改成功")
        return HttpResponse(json.dumps(pk))


@csrf_exempt
def poinfo(request: HttpRequest, pk):
    if request.method == "GET":
        pk = str(int(pk))
        print("pk:", pk)
        caigou = PurchaseOrder.objects.filter(id = pk).values("telephone","fax","shippingAddress")
        vendorid =  PurchaseOrder.objects.filter(id = pk).values("vendor_id")
        vendorid = vendorid[0]['vendor_id']
        vendor = Vendor.objects.filter(vid = vendorid).values("vid","vname","city","address")
        vendor = list(vendor)
        orderitems  = OrderItem.objects.filter(po_id= pk).values("itemId","meterialItem__id","meterialItem__material__mname",
                                                                 "quantity","price","meterialItem__stock__id","meterialItem__stock__name","meterialItem__sloc",
                                                                 "deliveryDate","po__rfq__rej","currency","status")
        orderitems = list(orderitems)
        caigou= list(caigou)
        print(orderitems)
        for i in orderitems:
            if i['status']=='0':
                i['status']="货物未发出"
            if i['status']=='1':
                i['status']="货物已送达"
            if i['status']=='2':
                i['status']="已收到发票"
            if i['status']=='4':
                i['status']="已完成支付"

        xiangqing = PurchaseOrder.objects.filter(id = pk).values("id","euser_id","time","orderitem__currency")
        xiangqing = list(xiangqing)
        print(xiangqing)
        sum = 0
        sumquantity =0
        sumquantity = len(orderitems)
        for i in orderitems:
            print(i['quantity'])
            print(i['price'])
            i['sum'] = i['quantity']*i['price']
            sum+=i['sum']
            #sumquantity+=i['quantity']
        xiangqing[0]['sum'] = sum
        xiangqing[0]['sumquantity'] = sumquantity
        print(len(xiangqing))
        while len(xiangqing)!=1:
            xiangqing.pop()
        print(orderitems)
        print(xiangqing)
        print(orderitems)
        return render(request, '../templates/purchaseorder/po-info.html', locals())



@csrf_exempt
def pomodifyinfo(request: HttpRequest, pk):
    if request.method == "GET":
        pk = str(int(pk))
        caigou = PurchaseOrder.objects.filter(id = pk).values("telephone","fax","shippingAddress")
        vendorid =  PurchaseOrder.objects.filter(id = pk).values("vendor_id")
        vendorid = vendorid[0]['vendor_id']
        vendor = Vendor.objects.filter(vid = vendorid).values("vid","vname","city","address")
        vendor = list(vendor)
        orderitems  = OrderItem.objects.filter(po_id= pk).values("itemId","meterialItem__id","meterialItem__material__mname",
                                                                 "quantity","price","meterialItem__stock__id","meterialItem__sloc",
                                                                 "deliveryDate","status","currency")
        orderitems = list(orderitems)

        for i in orderitems:
            if i['status']=='0':
                i['status']="货物未发出"
            if i['status']=='1':
                i['status']="货物已送达"
            if i['status']=='2':
                i['status']="已收到发票"
            if i['status']=='4':
                i['status']="已完成支付"

        caigou= list(caigou)
        xiangqing = PurchaseOrder.objects.filter(id = pk).values("id","euser_id","time","orderitem__currency")
        xiangqing = list(xiangqing)

        sum = 0
        sumquantity =0
        for i in orderitems:

            i['sum'] = i['quantity']*i['price']
            sum+=i['sum']
            sumquantity+=i['quantity']
        xiangqing[0]['sum'] = sum
        xiangqing[0]['sumquantity'] = sumquantity
        while len(xiangqing)!=1:
            xiangqing.pop()

        message = request.session.pop('message', None)
        return render(request, '../templates/purchaseorder/po-modify.html', locals())
    if request.method == "POST":
        pk = str(int(pk))
        caigou = PurchaseOrder.objects.filter(id = pk).values("telephone","fax","shippingAddress")
        vendorid =  PurchaseOrder.objects.filter(id = pk).values("vendor_id")
        vendorid = vendorid[0]['vendor_id']
        vendor = Vendor.objects.filter(vid = vendorid).values("vid","vname","city","address")
        vendor = list(vendor)
        orderitems  = OrderItem.objects.filter(po_id= pk).values("itemId","meterialItem__id","meterialItem__material__mname",
                                                                 "quantity","price","meterialItem__stock__id","meterialItem__sloc",
                                                                 "deliveryDate","status","currency")
        orderitems = list(orderitems)

        for i in orderitems:
            if i['status']=='0':
                i['status']="货物未发出"
            if i['status']=='1':
                i['status']="货物已送达"
            if i['status']=='2':
                i['status']="已收到发票"
            if i['status']=='4':
                i['status']="已完成支付"

        caigou= list(caigou)
        xiangqing = PurchaseOrder.objects.filter(id = pk).values("id","euser_id","time","orderitem__currency")
        xiangqing = list(xiangqing)

        sum = 0
        sumquantity =0
        for i in orderitems:

            i['sum'] = i['quantity']*i['price']
            sum+=i['sum']
            sumquantity+=i['quantity']
        xiangqing[0]['sum'] = sum
        xiangqing[0]['sumquantity'] = sumquantity
        while len(xiangqing) != 1:
            xiangqing.pop()

        telephone = request.POST.get("telephone")
        shippingAddress = request.POST.get("shippingAddress")
        fax = request.POST.get("fax")
        quotation1 = PurchaseOrder.objects.filter(id=pk).update(telephone=telephone,
                                                                shippingAddress=shippingAddress, fax=fax,
                                                                )
        if quotation1:
            request.session['message'] = "修改成功"
        else:
            request.session['message'] = "修改失败"

        return HttpResponseRedirect(request.path)  # 重定向到当前页面以防止刷新显示消息




@csrf_exempt
def pomodifyinfo2(request):
    if request.method == "POST":
        data = request.POST.get("json")
        data = eval(data)
        id = data[0]['id']
        print('JID', id)
        itemId = data[0]['itemId']
        quantity = data[0]['quantity']
        currency = data[0]['currency']
        deliveryDate = getDate2(data[0]['deliveryDate'])
        orderitem = OrderItem.objects.filter(po_id = id).update(itemId = itemId,
                                                           quantity=quantity,
                                                           currency = currency,
                                                           deliveryDate =deliveryDate)
        if orderitem:
            print("xiugai")
            print(data)
            datalist = {
                "message": "创建成功",
                "content": orderitem
            }
            return HttpResponse(json.dumps(datalist))



@csrf_exempt
def pomodifyinfo3(request):
    if request.method == "POST":
        data = request.POST.get("json")
        data = eval(data)
        print(data)
        id = data[0]['id']
        itemId = data[0]['itemId']
        quantity = data[0]['quantity']
        currency = data[0]['currency']
        deliveryDate = getDate2(data[0]['deliveryDate'])
        orderitem = OrderItem.objects.filter(po_id = id).update(quantity=quantity,
                                                           currency = currency,
                                                           deliveryDate =deliveryDate)
        if orderitem:
            print("xiugai")
            print(data)
            datalist = {
                "message": "创建成功",
                "content": orderitem
            }
            return HttpResponse(json.dumps(datalist))















@csrf_exempt
def vreview(request: HttpRequest):
    if request.method == "GET":
        quotation= Quotation.objects.all().values("id","vendor_id","collNo",
                                                  "ri__quantity","vendor__vname","price","ri__meterial__material_id")
        quotation = list(quotation)
        print("quotation长度：",len(quotation))
        print(quotation)
        for i in quotation:
            vendorid = i['vendor_id']
            orderitem = OrderItem.objects.filter(po__vendor=vendorid).values()
            orderitem = list(orderitem)
            sum = 0
            ontimeScore = 0
            quantityScore =0
            serviceScore =0
            qualityScore =0
            for j in orderitem:
                sum+=j['price']*j['quantity']
            for p in orderitem:
                if p['ontimeScore']==None:
                    p['ontimeScore'] =0
                if p['quantityScore']==None:
                    p['quantityScore'] =0
                if p['serviceScore']==None:
                    p['serviceScore'] =0
                if p['qualityScore']==None:
                    p['qualityScore'] =0
                quanzhong = p['price']*p['quantity']/sum
                ontimeScore+=p['ontimeScore']*quanzhong
                quantityScore+=p['quantityScore']*quanzhong
                serviceScore+=p['serviceScore']*quanzhong
                qualityScore+=p['qualityScore']*quanzhong
            i['qualityScore'] = round(qualityScore, 1)
            i['serviceScore'] = round(serviceScore, 1)
            i['quantityScore'] = round(quantityScore, 1)
            i['ontimeScore'] = round(ontimeScore, 1)
            i['sum'] = sum
            i['avgscore'] = round((quantityScore + serviceScore + quantityScore + ontimeScore) / 4, 1)
        quotation.sort(key=lambda x: x["avgscore"], reverse=True)
        for i in range(len(quotation)):
            quotation[i]['paiming'] = i+1
        print(quotation)
        return render(request, '../templates/quotation/vq-value.html',locals())
    if request.method == "POST":
        a = request.POST.get("indus")
        b = request.POST.get("collNo")
        print(a)
        print(b)
        quotation = Quotation.objects.filter(ri__meterial__sOrg=a,collNo=b).values("id","vendor_id","collNo",
                                                  "ri__quantity","vendor__vname","price","ri__meterial__material_id")
        quotation = list(quotation)
        for i in quotation:
            vendorid = i['vendor_id']
            orderitem = OrderItem.objects.filter(po__vendor=vendorid).values()
            orderitem = list(orderitem)
            print(orderitem)
            sum = 0
            ontimeScore = 0
            quantityScore = 0
            serviceScore = 0
            qualityScore = 0
            for j in orderitem:
                sum += j['price'] * j['quantity']
            for p in orderitem:
                print(p['ontimeScore'])
                if p['ontimeScore'] == None:
                    p['ontimeScore'] = 0
                if p['quantityScore'] == None:
                    p['quantityScore'] = 0
                if p['serviceScore'] == None:
                    p['serviceScore'] = 0
                if p['qualityScore'] == None:
                    p['qualityScore'] = 0
                quanzhong = p['price'] * p['quantity'] / sum
                ontimeScore += p['ontimeScore'] * quanzhong
                quantityScore += p['quantityScore'] * quanzhong
                serviceScore += p['serviceScore'] * quanzhong
                qualityScore += p['qualityScore'] * quanzhong
            i['qualityScore'] = round(qualityScore,1)
            i['serviceScore'] = round(serviceScore,1)
            i['quantityScore'] = round(quantityScore,1)
            i['ontimeScore'] = round(ontimeScore,1)
            i['sum'] = sum
            i['avgscore'] = round((quantityScore + serviceScore + quantityScore + ontimeScore) / 4,1)
        quotation.sort(key=lambda x: x["avgscore"], reverse=True)
        for i in range(len(quotation)):
            quotation[i]['paiming'] = i+1
        return render(request, '../templates/quotation/vq-value.html', locals())









@csrf_exempt
def searchqo(request):
    if request.method == "GET":
        vendorid =  Quotation.objects.all().values("id","euser_id","ri__meterial__material_id","vendor_id","time")
        vendorid = list(vendorid)
        return render(request, '../templates/quotation/vendor_quotation.html', locals())
    if request.method == "POST":
        '''for i in request:
            print(i)
        id = request.POST.get("id")
        print(id)
        ven = request.POST.get("ven")
        print(ven)
        mate = request.POST.get("mate")
        print(mate)
        eu = request.POST.get("euser")
        print(eu)
        collNo = request.POST.get("collNo")
        print(collNo)'''
        queryDict={}
        for i in request.POST.items():
            if i[1] is not None and len(i[1])>0 and i[0]!='material_id' and i[0]!='time':
                queryDict[i[0]]=i[1]
        if len(request.POST.get('material_id'))>0:
            queryDict['ri__meterial_id']=request.POST.get('material_id')
        if request.POST.get('time')=='近三月':
            queryDict['time__gte'] = timezone.now()-timedelta(days=90)
        elif request.POST.get('time')=='近半年':
            queryDict['time__gte'] = timezone.now() - timedelta(days=180)

        print(queryDict)
        quotations = Quotation.objects.filter(**queryDict).values("id", "euser_id", "ri__meterial_id", "vendor_id", "time")
        quotations=list(quotations)
        print(quotations)
        return render(request, '../templates/quotation/vendor_quotation.html', locals())




@csrf_exempt
def searchpo(request):
    if request.method == "GET":
        vendorid = OrderItem.objects.all().values("po_id",
                                                  "itemId",
                                                  "meterialItem__id",
                                                  "quantity",
                                                  "price",
                                                  "currency",
                                                  "po__vendor",
                                                  "po__euser",
                                                  "po__time",
                                                  "status")
        for i in vendorid:
            if i['quantity']==None:
                i['quantity']=0
            if i['price']==None:
                i['price'] =0
            i['sum'] = i['quantity']*i['price']
        for i in vendorid:
            if i['status']=='0':
                i['status']="货物未发出"
            if i['status']=='1':
                i['status']="货物已送达"
            if i['status']=='2':
                i['status']="已收到发票"
            if i['status']=='4':
                i['status']="已完成支付"
        vendorid = list(vendorid)
        print(vendorid)
        return render(request, '../templates/purchaseorder/purchase_order.html', locals())
    if request.method == "POST":
        id = request.POST.get("id")
        ven = request.POST.get("ven")
        mate = request.POST.get("mate")
        eu = request.POST.get("euser")
        print(id)

        vendorid = OrderItem.objects.filter(po_id=id, po__vendor=ven,
                                                meterialItem__id=mate,
                                                po__euser=eu,
                                                ).values("po_id","itemId","currency",
                                                         "po__time","meterialItem__id","quantity","price","po__vendor","po__euser","status")
        print("test", vendorid)
        for i in vendorid:
            if i['quantity'] == None:
                i['quantity'] = 0
            if i['price'] == None:
                i['price'] = 0
            i['sum'] = i['quantity'] * i['price']
        for i in vendorid:
            if i['status'] == '0':
                i['status'] = "货物未发出"
            if i['status'] == '1':
                i['status'] = "货物已送达"
            if i['status'] == '2':
                i['status'] = "已收到发票"
            if i['status'] == '4':
                i['status'] = "已完成支付"
        vendorid = list(vendorid)
        return render(request, '../templates/purchaseorder/purchase_order.html', locals())







@csrf_exempt
def searchpo2(request):
    if request.method == "GET":
        vendorid =  PurchaseOrder.objects.all().values('rfq__quantity','rfq__price','id','rfq__ri__meterial_id',
                                                       'euser_id','time','rfq__rej','vendor_id','rfq__collNo','rfq__ri__itemId',
                                                       'rfq__ri__currency','rfq__ri__status')
        for i in vendorid:
            i['sum'] = i['rfq__quantity']*i['rfq__price']
        for i in vendorid:
            if i['rfq__ri__status']=='0':
                i['rfq__ri__status'] = "已创建采购申请"
            if i['rfq__ri__status']=='1':
                i['rfq__ri__status'] = "已创建采购订单"
        vendorid = list(vendorid)
        print(vendorid)
        return render(request, '../templates/receipt/purchase_order.html', locals())
    if request.method == "POST":
        id = request.POST.get("id")
        ven = request.POST.get("ven")
        mate = request.POST.get("mate")
        eu = request.POST.get("euser")
        vendorid = PurchaseOrder.objects.filter(id=id,vendor_id=ven,
                                                rfq__ri__meterial=mate,
                                                euser_id=eu,
                                                ).values('rfq__quantity', 'rfq__price', 'id', 'rfq__ri__meterial_id',
                                                      'euser_id', 'time', 'rfq__rej', 'vendor_id', 'rfq__collNo','rfq__ri__itemId',
                                                         'rfq__ri__currency','rfq__ri__status')
        print(vendorid)
        for i in vendorid:
            i['sum'] = i['rfq__quantity']*i['rfq__price']
        for i in vendorid:
            if i['rfq__ri__status']=='0':
                i['rfq__ri__status'] = "已创建采购申请"
            if i['rfq__ri__status']=='1':
                i['rfq__ri__status'] = "已创建采购订单"
        vendorid = list(vendorid)
        return render(request, '../templates/receipt/purchase_order.html', locals())







@csrf_exempt
def searchpo3(request):
    if request.method == "GET":
        vendorid =  PurchaseOrder.objects.all().values('rfq__quantity','rfq__price','id','rfq__ri__meterial_id',
                                                       'euser_id','time','rfq__rej','vendor_id','rfq__collNo','rfq__ri__itemId',
                                                       'rfq__ri__currency','rfq__ri__status')
        for i in vendorid:
            i['sum'] = i['rfq__quantity']*i['rfq__price']
        for i in vendorid:
            if i['rfq__ri__status']=='0':
                i['rfq__ri__status'] = "已创建采购申请"
            if i['rfq__ri__status']=='1':
                i['rfq__ri__status'] = "已创建采购订单"
        vendorid = list(vendorid)
        print(vendorid)
        return render(request, '../templates/invoice/purchase_order.html', locals())
    if request.method == "POST":
        id = request.POST.get("id")
        ven = request.POST.get("ven")
        mate = request.POST.get("mate")
        eu = request.POST.get("euser")
        vendorid = PurchaseOrder.objects.filter(id=id,vendor_id=ven,
                                                rfq__ri__meterial=mate,
                                                euser_id=eu,
                                                ).values('rfq__quantity', 'rfq__price', 'id', 'rfq__ri__meterial_id',
                                                      'euser_id', 'time', 'rfq__rej', 'vendor_id', 'rfq__collNo','rfq__ri__itemId',
                                                         'rfq__ri__currency','rfq__ri__status')
        print(vendorid)
        for i in vendorid:
            i['sum'] = i['rfq__quantity']*i['rfq__price']
        for i in vendorid:
            if i['rfq__ri__status']=='0':
                i['rfq__ri__status'] = "已创建采购申请"
            if i['rfq__ri__status']=='1':
                i['rfq__ri__status'] = "已创建采购订单"
        vendorid = list(vendorid)
        return render(request, '../templates/invoice/purchase_order.html', locals())






@csrf_exempt
def searchjiekou(request):
    if request.method == "POST":
        print("111")
        cname = request.POST.get("cname")
        ctime = request.POST.get("ctime")
        gcode = request.POST.get("gcode")
        reque = RequisitionItem.objects.filter(deliveryDate=ctime,pr__euser_id=cname,
                                               meterial_id=gcode).values("pr_id","pr__euser_id","deliveryDate",
                                                                         "meterial__id","itemId","pr__time")
        reque = list(reque)
        return HttpResponse(json.dumps(reque, cls=ComplexEncoder))


def getDate2(string):
    dateInfo = string.split('. ')
    string = datetime.date(
        year=int(dateInfo[2]), month=int(dateInfo[1]), day=int(dateInfo[0])
    )
    return string


@csrf_exempt
def searchjiekouzhuanhua(request):
    if request.method == 'POST':
        post = request.POST
        cname = request.POST.get("cname")
        ctime = request.POST.get("ctime")
        gcode = request.POST.get("gcode")

        # 如果 ctime 不是空的，转换日期
        if ctime:
            try:
                ctime = getDate2(ctime)
            except ValueError:
                return JsonResponse({'error': '日期格式不正确'})

        # 基本查询集，包含所有记录
        reque = Quotation.objects.all()

        # 根据 cname 过滤
        if cname:
            reque = reque.filter(euser_id=cname)

        # 根据 ctime 过滤
        if ctime:
            reque = reque.filter(time=ctime)

        # 根据 gcode 过滤
        if gcode:
            reque = reque.filter(ri_meterial_id=gcode)

        # 获取查询结果
        reque = reque.values("id", "euser__id", "time", "ri__meterial__material__id", "ri__meterial__id")
        reque = list(reque)
        print(reque)
        return JsonResponse(reque, safe=False)  # 使用 safe=False 以返回列表

    return JsonResponse({'error': '只接受 POST 请求'})


@csrf_exempt
def choose(request):
    if request.method == "GET":

        return render(request, '../templates/purchaseorder/po-create_choose.html', locals())