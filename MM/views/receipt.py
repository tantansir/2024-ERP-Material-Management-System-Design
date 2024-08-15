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

from ..models import *
from .auxiliary import *

@login_required
def create_receipt(request: HttpRequest):
    """
    根据请求创建收据。

    该函数用于处理创建收据的HTTP请求。如果请求方法为GET，则会渲染并返回创建收据的页面；
    如果请求方法不是GET，则返回一个405错误，表示方法不允许。

    参数:
    - request: HttpRequest对象，包含请求的元数据和方法。

    返回值:
    - 如果请求方法为GET，返回渲染后的创建收据页面。
    - 如果请求方法不是GET，返回一个状态码为405的HttpResponse对象。
    """
    # 对于GET请求，调用render函数渲染并返回指定的模板页面
    if request.method == 'GET':
        return render(
            request=request,
            template_name='../templates/receipt/create.html'
        )
    # 对于非GET请求，返回一个表示方法不允许的HTTP响应
    else:
        return HttpResponse(status=405)

@login_required
def search_receipt(request: HttpRequest):
    """
    根据HTTP请求方法处理收据搜索逻辑。

    如果请求方法为GET，则提供搜索收据的表单界面。
    对于任何非GET方法的请求，返回405状态码，表示方法不允许。

    参数:
    - request: HttpRequest对象，包含来自客户端的请求信息。

    返回值:
    - 对于GET请求，返回一个渲染后的搜索收据的HTML页面。
    - 对于非GET请求，返回一个HttpResponse对象，状态码为405。
    """
    if request.method == 'GET':
        # GET请求，返回搜索收据的表单界面
        return render(
            request=request,
            template_name='../templates/receipt/search.html'
        )
    else:
        # 非GET请求，返回405状态码，表示方法不允许
        return HttpResponse(status=405)

@login_required
def display_receipt(request: HttpRequest):
    """
    根据请求显示收据信息。

    该函数从HTTP请求中获取订单ID和物品ID，然后查询和组装相关数据，
    最后将数据传递给模板进行渲染，生成收据页面。

    :param request: HttpRequest对象，包含前端发送的请求信息
    :return: 渲染后的收据页面
    """
    # 从请求中获取查询参数
    get = request.GET
    grID = get.get('grID')
    orderID = get.get('orderID')
    itemID = get.get('itemID')

    # 根据订单ID和物品ID查询OrderItem对象，如果不存在则返回404错误
    item: OrderItem = get_object_or_404(OrderItem, po__id__exact=orderID, itemId__exact=itemID)

    # 查询对应的GoodReceipt对象
    gr = GoodReceipt.objects.get(pk__exact=grID)

    # 将OrderItem对象转换为字典
    item_dict = model_to_dict(item)

    # 查询MaterialItem对象，并将其添加到字典中
    materialItem: MaterialItem = get_object_or_404(MaterialItem, id__exact=item.meterialItem.id)
    item_dict['materialItem'] = model_to_dict(materialItem)

    # 查询Material对象，并将其添加到字典中
    material: Material = get_object_or_404(Material, id__exact=materialItem.material.id)
    item_dict['material'] = model_to_dict(material)

    # 查询Stock对象，并将其添加到字典中
    stock: Stock = get_object_or_404(Stock, id__exact=materialItem.stock.id)
    item_dict['stock'] = model_to_dict(stock)

    # 查询PurchaseOrder对象，并将其添加到字典中
    po: PurchaseOrder = get_object_or_404(PurchaseOrder, id__exact=item.po.id)
    item_dict['po'] = model_to_dict(po)

    # 将GoodReceipt对象转换为字典，并添加到item_dict中
    item_dict['gr'] = model_to_dict(gr)

    # 渲染模板并返回收据页面
    return render(
        request=request,
        template_name='../templates/receipt/display.html',
        context={'context': item_dict}
    )

@login_required
def load_order_item(request: HttpRequest):
    """
    根据请求加载订单项信息及其相关联的数据。

    该函数从HttpRequest对象中获取订单ID和物品ID，然后根据这些ID获取订单项、物料项、物料和库存信息，
    以及采购订单信息。这些信息被转换为字典形式，并传递给模板以供渲染。

    参数:
    - request: HttpRequest对象，包含订单ID和物品ID。

    返回:
    - 渲染后的模板，包含订单项及其相关数据。

    解释:
    1. 获取请求中的参数，包括订单ID和物品ID。
    2. 使用这些ID获取订单项(OrderItem)、物料项(MaterialItem)、物料(Material)和库存(Stock)对象，
       以及采购订单(PurchaseOrder)对象。
    3. 将这些对象转换为字典形式，以便在模板中使用。
    4. 渲染并返回包含这些数据的模板。
    """
    # 从GET请求中获取参数
    get = request.GET
    orderID = get.get('orderID')
    itemID = get.get('itemID')
    # 获取订单项信息
    item: OrderItem = get_object_or_404(OrderItem, po__id__exact=orderID, itemId__exact=itemID)
    item_dict = model_to_dict(item)
    
    # 获取物料项信息
    materialItem: MaterialItem = get_object_or_404(MaterialItem, id__exact=item.meterialItem.id)
    material: Material = get_object_or_404(Material, id__exact=materialItem.material.id)
    stock: Stock = get_object_or_404(Stock, id__exact=materialItem.stock.id)
    
    # 获取采购订单信息
    po: PurchaseOrder = get_object_or_404(PurchaseOrder, id__exact=item.po.id)
    item_dict['po_'] = model_to_dict(po)
    
    # 将相关联的对象添加到字典中
    item_dict['materialItem_'] = model_to_dict(materialItem)
    item_dict['material_'] = model_to_dict(material)
    item_dict['stock_'] = model_to_dict(stock)
    
    # 渲染并返回模板
    return render(
        request=request,
        template_name='../templates/receipt/create2.html',
        context={'context': item_dict}
    )

@login_required
def display_purchase_order(request: HttpRequest, pk):
    """
    显示采购订单详情页面。

    根据提供的请求和采购订单ID（pk），检索相应的采购订单、供应商和订单项信息，
    并计算订单总额。最终渲染并返回采购订单详情页面。

    参数:
    - request: HttpRequest对象，包含当前请求信息。
    - pk: 采购订单的主键ID，用于查询具体订单。

    返回:
    - 渲染后的采购订单详情页面，包含订单、供应商和订单项等信息。
    """
    if request.method == "GET":
        # 获取指定ID的采购订单，"O"表示仅获取确认的订单
        pk = getPkExact(pk, "O")
        # 根据ID获取采购订单详细信息
        purchaseOrder: PurchaseOrder = PurchaseOrder.objects.get(id=pk)
        # 根据采购订单获取对应的供应商信息
        vendor: Vendor = Vendor.objects.get(vid=purchaseOrder.vendor.vid)
        # 获取该采购订单的所有订单项，并选择需要的字段
        orderItems = OrderItem.objects.filter(po_id=pk).values(
            "itemId","meterialItem__id","meterialItem__material__mname",
            "quantity","price","meterialItem__stock__id", "meterialItem__stock__name",
            "meterialItem__sloc","deliveryDate","po__rfq__rej","currency","status"
        )
        # 将查询结果转换为列表，以便于后续处理
        orderItems = list(orderItems)
        # 根据状态码将订单项的状态转换为易读的文本描述
        for i in orderItems:
            if i['status']=='0':
                i['status']="货物未发出"
            elif i['status']=='1':
                i['status']="货物已送达"
            elif i['status']=='2':
                i['status']="已收到发票"
            elif i['status']=='3':
                i['status']="已完成支付"
        # 计算每个订单项的小计，并累加到总金额
        sum = 0
        for i in orderItems:
            i['sum'] = i['quantity'] * i['price']
            sum += i['sum']
        # 渲染并返回采购订单详情页面
        return render(
            request, '../templates/receipt/order.html',
            context={
                "purchaseOrder": purchaseOrder, "vendor": vendor, "orderItems": orderItems,
                "sum": sum, "itemNum": len(orderItems), "currency": orderItems[0]['currency'],
                "user_id": purchaseOrder.euser.uid
            }    
        )

@login_required
def search_orders(request):
    """
    根据请求方法处理订单搜索逻辑。

    - 如果是GET请求，返回一个空的采购订单列表。
    - 如果是POST请求，根据提交的参数过滤并返回相关的订单项。

    参数:
    - request: HttpRequest对象，包含请求方法（GET或POST）和请求数据。

    返回:
    - 对于GET请求，返回一个空的采购订单列表。
    - 对于POST请求，返回根据过滤条件得到的订单项列表。
    """
    if request.method == "GET":
        # 初始化一个空的采购订单列表
        purchaseOrders = []
        # 渲染并返回订单页面，此处不包含任何订单数据
        return render(request, '../templates/receipt/orders.html', context={"purchaseOrders":purchaseOrders})
    if request.method == "POST":
        # 从POST请求中获取参数，并将它们转换为对应的主键
        id = request.POST.get("id"); id = getPk(id)
        ven = request.POST.get("ven"); ven = getPk(ven)
        mate = request.POST.get("mate"); mate = getPk(mate)
        eu = request.POST.get("eu"); eu = getPk(eu)
        # 获取查询范围，并将其转换为对应的月数
        range = int(request.POST.get("range"))
        range_list = [12, 6, 3]
        now = timezone.now()
        # 根据选择的时间范围计算查询的开始时间
        start = now + datetime.timedelta(days=-30 * range_list[range])
        # 根据过滤条件查询订单项
        orderItems: QuerySet = OrderItem.objects.filter(
            po__id__regex=id, po__vendor__vid__regex=ven, meterialItem__material__id__regex=mate,
            po__euser__uid__regex=eu, po__time__range=[start, now]
        )
        # 对查询结果进行聚合计算和排序
        orderItems: QuerySet = orderItems.values(
            "po__id", "itemId", "meterialItem__material__id", "quantity", "price", "currency",
            "po__euser__uid", "po__vendor__vid", "po__time", "status", sum=F("quantity")*F("price")
        ).order_by("po__id")
        # 将查询结果转换为列表
        orderItems = list(orderItems)
        # 根据订单状态代码，将状态数字转换为对应的描述
        for i in orderItems:
            if i['status']=='0':
                i['status']="货物未发出"
            if i['status']=='1':
                i['status']="货物已送达"
            if i['status']=='2':
                i['status']="已收到发票"
            if i['status']=='3':
                i['status']="已完成支付"
        # 渲染并返回包含过滤后订单数据的页面
        return render(request, '../templates/receipt/orders.html', {"orderItems":orderItems})