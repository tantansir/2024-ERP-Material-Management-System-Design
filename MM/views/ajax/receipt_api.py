from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.core.exceptions import ValidationError
from django.forms.models import model_to_dict
from django.db.models import QuerySet, Sum, Count, F, Avg
from django.utils import timezone
import pytz
import json
import datetime

from ...models import *
from ..auxiliary import *

@login_required
def search_receipt(request: HttpRequest):
    """
    根据用户ID或商品收据ID搜索商品收据信息。

    - 如果请求方法不是POST，返回405状态码的HTTP响应。
    - 如果请求方法是POST：
      - 从请求的POST数据中获取'pk'，如果'pk'为空或None，则从'uid'获取用户ID，并根据是否有日期信息进行查询。
      - 如果提供了日期信息，将根据用户ID和日期进行查询。
      - 如果没有提供日期信息，只根据用户ID进行查询。
      - 查询到的商品收据信息将被序列化为JSON格式，并返回包含状态、消息和商品收据数据的HTTP响应。
      - 如果提供了商品收据的ID（pk），将根据此ID进行精确查询。
        - 如果查询结果不是恰好一个，返回状态为0和错误消息的HTTP响应。
        - 如果查询结果恰好一个，返回状态为1，消息为成功，以及商品收据数据的HTTP响应。

    参数:
    - request: HttpRequest对象，包含请求方法和请求数据。

    返回:
    - 如果请求方法不是POST，返回405状态码的HTTP响应。
    - 如果请求方法是POST，根据查询结果返回JSON格式的HTTP响应。
    """
    # 如果请求方法不是POST，返回405状态码的HTTP响应
    if request.method != 'POST':
        return HttpResponse(status=405)
    # 从请求的POST数据中获取数据
    post = request.POST
    pk = post.get('pk')
    # 如果pk为空或None，从uid获取用户ID，并进行查询
    if pk == '' or pk is None:
        uid = getPk(post.get('uid'), 'U')
        date = post.get('date')
        # 根据是否有日期信息，设置查询条件
        if date == '':
            results: QuerySet = GoodReceipt.objects.filter(
                euser__uid__regex=uid
            )
        else:
            dateInfo = date.split('. ')
            results: QuerySet = GoodReceipt.objects.filter(
                euser__uid__regex=uid, time__year=int(dateInfo[2]),
                time__month=int(dateInfo[0]), time__day=int(dateInfo[1])
            )
        # 序列化查询结果
        results_list = json.loads(serializers.serialize('json', list(results)))
        for i, r in enumerate(results):
            user: EUser = EUser.objects.get(pk__exact=r.euser.pk)
            orderItem: OrderItem = OrderItem.objects.get(pk__exact=r.orderItem.id)
            po: PurchaseOrder = PurchaseOrder.objects.get(pk__exact=orderItem.po.id)
            materialItem: MaterialItem = get_object_or_404(MaterialItem, id__exact=orderItem.meterialItem.id)
            stock: Stock = get_object_or_404(Stock, id__exact=materialItem.stock.id)
            material: Material = get_object_or_404(Material, id__exact=materialItem.material.id)
            results_list[i]['user'] = model_to_dict(user)
            results_list[i]['orderItem'] = model_to_dict(orderItem)
            results_list[i]['po'] = model_to_dict(po)
            results_list[i]['stock'] = model_to_dict(stock)
            results_list[i]['material'] = model_to_dict(material)
        return HttpResponse(json.dumps({'status':1, 'message':"商品收据检索成功！", 'gr':results_list}, default=str))
    else:
        # 如果提供了商品收据的ID，进行精确查询
        pk = getPkExact(pk, 'GR')
        results: QuerySet = GoodReceipt.objects.filter(pk__exact=pk)
        if len(results) != 1:
            return HttpResponse(json.dumps({'status':0, 'message':"商品收据相关信息错误！"}))
        else:
            results_list = json.loads(serializers.serialize('json', list(results)))
            for i, r in enumerate(results):
                r: GoodReceipt
                user: EUser = EUser.objects.get(pk__exact=r.euser.pk)
                orderItem: OrderItem = OrderItem.objects.get(pk__exact=r.orderItem.id)
                po: PurchaseOrder = PurchaseOrder.objects.get(pk__exact=orderItem.po.id)
                materialItem: MaterialItem = get_object_or_404(MaterialItem, id__exact=orderItem.meterialItem.id)
                stock: Stock = get_object_or_404(Stock, id__exact=materialItem.stock.id)
                material: Material = get_object_or_404(Material, id__exact=materialItem.material.id)
                results_list[i]['user'] = model_to_dict(user)
                results_list[i]['orderItem'] = model_to_dict(orderItem)
                results_list[i]['po'] = model_to_dict(po)
                results_list[i]['stock'] = model_to_dict(stock)
                results_list[i]['material'] = model_to_dict(material)
            return HttpResponse(json.dumps({'status':1, 'message':"商品收据检索成功！", 'gr':results_list}, default=str))


@login_required
def create_receipt(request: HttpRequest):
    """
    创建收据

    根据用户提交的表单数据，创建一个新的收据记录。这包括验证表单数据的准确性，
    保存收据信息，更新订单状态和相关分数，以及更新库存和会计记录。

    参数:
    - request: HttpRequest对象，包含用户提交的表单数据。

    返回:
    - HttpResponse对象，包含操作状态和相关消息的JSON数据。
    """
    # 获取表单数据
    post = request.POST
    po_id = getPkExact(post.get('po_id'), 'PO')
    oi_itemId = getPkExact(post.get('oi_id'), 'OI')
    actualQnty = int(post.get('actualQnty'))
    sType = post.get('sType')
    qualityScore = post.get('qualityScore')
    serviceScore = post.get('serviceScore')
    postTime = getDate(post.get('postTime'))
    time = getDate(post.get('time'))

    # 获取订单项和用户信息
    orderItem: OrderItem = OrderItem.objects.get(po__id__exact=po_id, itemId=oi_itemId)
    euser = EUser.objects.get(pk__exact=request.user.id)

    # 创建新的收据对象
    new_gr = GoodReceipt(
        actualQnty=actualQnty, sType=sType, time=time, postTime=postTime, orderItem=orderItem, euser=euser
    )

    # 验证收据数据
    try:
        new_gr.full_clean()
    except ValidationError as e:
        error_fields = list(e.error_dict.keys())
        return HttpResponse(json.dumps({'status':0, 'message':"表单填写错误！", 'fields':error_fields}))

    # 保存收据并更新订单状态
    new_gr.save()
    orderItem.status = '1'
    orderItem.qualityScore = int(qualityScore) * 20
    orderItem.serviceScore = int(serviceScore) * 20
    orderItem.quantityScore = actualQnty / orderItem.quantity * 100

    # 计算及时性分数
    dif = (time - orderItem.deliveryDate).days
    score = 0
    if dif <= 0: score=100
    elif 0 < dif < 7: score=80
    elif 7 <= dif < 15: score=60
    elif 15 <= dif < 30: score=40
    else: score= 20
    orderItem.ontimeScore = score

    # 保存订单更新
    orderItem.save()

    # 获取物料项信息
    materialItem: MaterialItem = MaterialItem.objects.get(pk__exact=orderItem.meterialItem.id)

    # 创建新的库存历史记录
    new_stockHistory = StockHistory(
        item=materialItem, type='1', unrestrictUse=materialItem.unrestrictUse,
        blocked=materialItem.blocked, qltyInspection=materialItem.qltyInspection,
        time=time,
    )

    # 验证库存历史数据
    try:
        new_stockHistory.full_clean()
        new_stockHistory.save()
    except ValidationError as e:
        error_fields = list(e.error_dict.keys())
        return HttpResponse(json.dumps({'status':0, 'message':"表单填写错误！", 'fields':error_fields}))

    # 根据收据类型更新库存数量
    if sType=='1': materialItem.blocked += actualQnty
    elif sType=='2': materialItem.qltyInspection += actualQnty
    elif sType=='3': materialItem.unrestrictUse += actualQnty

    # 保存库存更新
    materialItem.save()

    # 创建新的会计记录
    new_account = Account(
        sumAmount=orderItem.price * actualQnty, JEType='WE', postDate=postTime
    )

    # 验证会计记录数据
    try:
        new_account.full_clean()
    except ValidationError as e:
        error_fields = list(e.error_dict.keys())
        return HttpResponse(json.dumps({'status':0, 'message':"表单填写错误！", 'fields':error_fields}))

    # 保存会计记录
    new_account.save()

    # 创建会计明细记录
    accountDetail1 = AccountDetail(
        glAccount='200200', type='0', amount=orderItem.price * actualQnty, je=new_account
    )
    accountDetail2 = AccountDetail(
        glAccount='310000', type='1', amount=orderItem.price * actualQnty,
        gr=new_gr, je=new_account
    )

    # 验证会计明细数据
    try:
        accountDetail1.full_clean()
        accountDetail2.full_clean()
    except ValidationError as e:
        error_fields = list(e.error_dict.keys())
        return HttpResponse(json.dumps({'status':0, 'message':"表单填写错误！", 'fields':error_fields}))

    # 保存会计明细记录
    accountDetail1.save()
    accountDetail2.save()

    # 返回成功消息
    return HttpResponse(json.dumps({'status':1, 'message':"商品收据创建成功！收据编号为"+str(new_gr.id)+"。"}))

