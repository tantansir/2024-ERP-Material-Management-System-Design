import json
from django.core import serializers
from django.core.exceptions import ObjectDoesNotExist
from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required
from django import forms
from django.utils import timezone
from datetime import timedelta

from django.views.decorators.csrf import csrf_exempt

from ..models import EUser, Material, MaterialItem, Stock,PurchaseRequisition,RequisitionItem,Quotation,Vendor,OrderItem
from .auxiliary import *


class QuotationForm(forms.Form):
    euserid = forms.CharField(label="创建者ID", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    vendorvid = forms.CharField(label="供应商ID", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    riid = forms.CharField(label="参考请购条目ID", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mid = forms.CharField(label="物料条目", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    deadline = forms.CharField(label="截止日期", max_length=256, widget=forms.TextInput(attrs={'class': 'form-control'}))
    quantity = forms.CharField(label="数量", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    deliveryDate = forms.CharField(label="送货时间", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    collNo = forms.CharField(label="集合码", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    price = forms.CharField(label="报价", max_length=256,widget=forms.TextInput(attrs={'class': 'form-control'}))
    currency = forms.CharField(label="货币", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    validTime = forms.CharField(label="报价有效期", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))




class ModifyquotationForm(forms.Form):
    price = forms.CharField(label="报价", max_length=256,widget=forms.TextInput(attrs={'class': 'form-control'}))
    currency = forms.CharField(label="货币", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    validTime = forms.CharField(label="报价有效期", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))




class VendormodifyquotationForm(forms.Form):
    deadline = forms.CharField(label="截止日期", max_length=256, widget=forms.TextInput(attrs={'class': 'form-control'}))
    quantity = forms.CharField(label="数量", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    deliveryDate = forms.CharField(label="送货时间", max_length=128,
                                   widget=forms.TextInput(attrs={'class': 'form-control'}))
    collNo = forms.CharField(label="集合码", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    rej = forms.CharField(label="拒绝情况", max_length=1, widget=forms.TextInput(attrs={'class': 'form-control'}))



class searchquotationForm(forms.Form):
    collNo = forms.CharField(label="集合码", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    riid = forms.CharField(label="参考请购条目ID", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))
    mid = forms.CharField(label="物料条目", max_length=128, widget=forms.TextInput(attrs={'class': 'form-control'}))



@csrf_exempt
@login_required
def makebyrq(request: HttpRequest, pk,itemId):
    if request.method == "GET":
        reque = PurchaseRequisition.objects.filter(id=pk,requisitionitem__itemId=itemId).values("requisitionitem__id",
                                                               "requisitionitem__itemId",
                                                               "requisitionitem__meterial__id",
                                                               "requisitionitem__meterial__stock",
                                                               "requisitionitem__meterial__sloc",
                                                               "requisitionitem__estimatedPrice",
                                                               "requisitionitem__currency",
                                                               "requisitionitem__quantity",
                                                               "requisitionitem__deliveryDate",
                                                               )

        reque = list(reque)
        stoid = reque[0]['requisitionitem__meterial__stock']
        stoname = Stock.objects.filter(id = stoid).values()
        print(stoname)
        stoname = list(stoname)
        print(stoname)
        name = stoname[0]['name']
        reque[0]['stockname'] = name
        print(reque)
        return render(request, '../templates/quotation/RFQ-create.html', locals())
    if request.method =="POST":
        collNo = request.POST.get("collNo")
        deadline = request.POST.get("deadline")
        quantity = request.POST.get("quantity")
        deliveryDate = request.POST.get("deliveryDate")
        vendorvid = request.POST.get("vendorvid")
        print(quantity)
        euser = request.user
        euserid = euser.pk
        now_time = datetime.datetime.now()
        quotation = Quotation.objects.create(deadline=deadline,
                                             quantity=quantity,
                                             ri_id=pk,
                                             vendor_id=vendorvid,
                                             euser_id=euserid,
                                             time=now_time,
                                             collNo=collNo,
                                             deliveryDate=deliveryDate,
                                             rej=0
                                             )
        if quotation:
            print("111111c")
        return render(request, '../templates/quotation/RFQ-create.html', locals())








@csrf_exempt
@login_required
def rfqinfojiekou(request):
    if request.method =="POST":
        user = request.user
        euser = EUser.objects.get(username=user.username)
        quantity = request.POST.get("quantity")
        price = request.POST.get("price")

        #currency = request.POST.get("currency")
        pk = request.POST.get("id")
        requisition_item = RequisitionItem.objects.get(id=pk)
        currency = requisition_item.currency

        pk = request.POST.get("id")
        deliveryDate = request.POST.get("deliveryDate")
        deliveryDate = getDate2(deliveryDate)
        collNo = request.POST.get("collNo")
        deadline = request.POST.get("deadline")
        deadline = getDate2(deadline)
        data = request.POST.get("json")
        data1 = eval(data)
        now_time = datetime.datetime.now()
        quolist = []
        for i in data1:
            vid = i['vid']
            quotation = Quotation.objects.create(deadline=deadline,
                                                 quantity=quantity,
                                                 price=price,
                                                 currency=currency,
                                                 ri_id=pk,
                                                 vendor_id=vid,
                                                 euser=euser,
                                                 time=now_time,
                                                 collNo=collNo,
                                                 deliveryDate=deliveryDate,
                                                 rej=None,
                                                 )
            quoid = quotation.id
            quolist.append(quoid)
            if quotation:
                print("cjcg")
        return HttpResponse(json.dumps(quolist))





@csrf_exempt
def getall(request):
    if request.method == "GET":
        quoatations = Quotation.objects.all().values()
        quoatations = list(quoatations)
        print(quoatations)
        return render(request, '../templates/quotation/RFQ.html',locals())
    if request.method == "POST":
        queryDict={}
        for i in request.POST.items():
            if i[1] is not None and len(i[1])>0:
                queryDict[i[0]]=i[1]
        quoatations = Quotation.objects.filter(**queryDict).values()
        if quoatations:
            quoatations = list(quoatations)
            return render(request, '../templates/quotation/RFQ.html', locals())
        else:
            insertmessage = "创建失败"
            return render(request, '../templates/quotation/RFQ.html', locals())



@csrf_exempt
def searchqinggou(request):
    if request.method == "GET":
        quoatations = PurchaseRequisition.objects.all().values()
        quoatations = list(quoatations)
        return render(request, '../templates/quotation/RFQ-create_search.html', locals())
    if request.method == "POST":
        id = request.POST.get("id")
        euserid = request.POST.get("euserid")
        mid = request.POST.get("materialid")
        quoatations = PurchaseRequisition.objects.filter(id=id,
                                           euser_id=euserid,requisitionitem__meterial__material__id=mid
                                             ).values()
        quoatations = list(quoatations)
        if quoatations:
            quoatations = list(quoatations)
            return render(request, '../templates/quotation/RFQ-create_search.html', locals())
        else:
            insertmessage = "创建失败"
            return render(request, '../templates/quotation/RFQ-create_search.html', locals())





@csrf_exempt
def rfqinfo(request: HttpRequest, pk):
    if request.method == "GET":
        quoatations = PurchaseRequisition.objects.filter(id = pk).values()

        quoatations = list(quoatations)
        print(quoatations)

        rq = RequisitionItem.objects.filter(pr_id=pk).values("meterial__stock__id","meterial__id",
                                                             "itemId","meterial__sloc","meterial__stock__name","quantity","deliveryDate")

        rq = list(rq)
        print(rq)
        return render(request, '../templates/quotation/RFQ-create_info.html', locals())




@csrf_exempt
def rfqinfo2(request: HttpRequest, pk):
    if request.method == "GET":
        quoatations = Quotation.objects.filter(id=pk).values("id","euser_id","ri_id",
                                                             "deadline","time","rej","vendor_id","collNo")

        quoatations = list(quoatations)
        #print('***********\n',quoatations)
        riid = quoatations[0]['ri_id']
        viid = quoatations[0]['vendor_id']
        colno = quoatations[0]['collNo']
        caigou = RequisitionItem.objects.filter(id=riid).values("quotation__vendor__pOrg", "meterial__stock__pGrp",
                                                             "meterial__id", "meterial__sloc","quantity",
                                                                "deliveryDate","meterial__stock__name")


        vendor =Vendor.objects.filter(vid=viid).values("score","vid","vname","city",
                                                       "address","postcode")


        vendor = list(vendor)



        caigou = list(caigou)
        for i in caigou:
            i['collNo'] = colno
        while len(caigou)!=1:
            caigou.pop()
        print(caigou)
        baojia = Quotation.objects.filter(id=pk).values("price","deadline","currency","quantity")
        for i in baojia:
            i['sum']=i['quantity']*i['price']
        baojia = list(baojia)
        return render(request, '../templates/quotation/RFQ-info.html', locals())




@csrf_exempt
def searchquo(request):
    if request.method == "GET":
        quoatations = Quotation.objects.all().values()
        quotattions1 = Quotation.objects.all().values("ri__status")
        quoatations = list(quoatations)
        quotattions1 = list(quotattions1)
        for i in range(len(quoatations)):
            quoatations[i]['ri__status'] = quotattions1[i]['ri__status']
        print(quoatations)
        return render(request, '../templates/quotation/vq-modify_search.html', locals())
    if request.method == "POST":
        '''id = request.POST.get("id")
        euserid = request.POST.get("euserid")
        vendorid = request.POST.get("vendorid")
        collno = request.POST.get("collNo")'''
        queryDict={}
        for i in request.POST.items():
            if i[1] is not None and len(i[1])>0 and i[0]!='time':
                queryDict[i[0]]=i[1]
        quotation = Quotation.objects.filter(**queryDict).values()
        print(quotation)
        quoatations = list(quotation)
        if quotation:
            quoatations = list(quotation)
            return render(request, '../templates/quotation/vq-modify_search.html', locals())
        else:
            insertmessage = "创建失败"
            return render(request, '../templates/quotation/vq-modify_search.html', locals())



@csrf_exempt
def pcs(request):
    if request.method == "GET":
        quoatations = Quotation.objects.all().values("ri__meterial__material_id","id",
                                                     "ri_id","quantity","collNo","price",
                                                     "currency","rej")
        quoatations = list(quoatations)
        return render(request, '../templates/purchaseorder/po-create_search.html', locals())
    if request.method == "POST":
        id = request.POST.get("id")
        mete= request.POST.get("mete")
        collNo = request.POST.get("collNo")
        quoatations = Quotation.objects.filter(ri__meterial__material_id=mete,id = id,
                                               collNo=collNo).values("ri__meterial__material_id","id",
                                                     "ri_id","quantity","collNo","price",
                                                     "currency","rej")
        if quoatations:
            quoatations = list(quoatations)
            return render(request, '../templates/purchaseorder/po-create_search.html', locals())
        else:
            insertmessage = "创建失败"
            return render(request, '../templates/purchaseorder/po-create_search.html', locals())



