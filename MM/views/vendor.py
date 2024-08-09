from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect
from django.core.exceptions import ValidationError
from django.db.models import Sum, Count, Avg
import json

from ..models import EUser, Vendor
from .auxiliary import *

@login_required
def create(request: HttpRequest):
    if request.method == 'GET':
        return render(
            request=request,
            template_name='../templates/vendor/create.html',
        )
    elif request.method == 'POST':
        vname = request.POST.get('vname')
        city = request.POST.get('city')
        address = request.POST.get('address')
        postcode = request.POST.get('postcode')
        country = request.POST.get('country')
        language = request.POST.get('language')
        glAcount = request.POST.get('glAcount')
        phone = request.POST.get('phone')
        fax = request.POST.get('fax')
        tpType = request.POST.get('tpType')
        companyCode = request.POST.get('companyCode')
        pOrg = request.POST.get('pOrg')
        currency = request.POST.get('currency')

        # 检查供应商名称是否重复
        if Vendor.objects.filter(vname=vname).exists():
            return JsonResponse({"status": 0, "message": "供应商名称已存在，请更换名称"}, status=400)

        # 数据验证
        missing_fields = []
        if not vname: missing_fields.append('vname')
        if not city: missing_fields.append('city')
        if not postcode: missing_fields.append('postcode')
        if not country: missing_fields.append('country')
        if not language: missing_fields.append('language')
        if not glAcount: missing_fields.append('glAcount')
        if not companyCode: missing_fields.append('companyCode')
        if not pOrg: missing_fields.append('pOrg')

        if missing_fields:
            return JsonResponse({"status": 0, "message": f"缺少必要字段: {', '.join(missing_fields)}"}, status=400)

        try:
            user = request.user
            euser = EUser.objects.get(pk=user.pk)

            vendor = Vendor.objects.create(
                euser=euser,
                vname=vname,
                city=city,
                address=address,
                postcode=postcode,
                country=country,
                language=language,
                glAcount=glAcount,
                phone=phone,
                fax=fax,
                tpType=tpType,
                companyCode=companyCode,
                pOrg=pOrg,
                currency=currency
            )

            vendor.save()
            return JsonResponse({"status": 1, "message": "供应商创建成功！供应商编号为"+str(vendor.vid)+"。", "vendor_id": vendor.pk, "from_create": True})
        except EUser.DoesNotExist:
            return JsonResponse({"status": 0, "message": "当前用户没有关联的EUser实例"}, status=400)
        except Exception as e:
            return JsonResponse({"status": 0, "message": f"创建供应商时出错: {str(e)}"}, status=400)
    else:
        return JsonResponse({"status": 0, "message": "请求方法不允许"}, status=405)


@login_required
def search(request: HttpRequest):
    if request.method == 'GET':
        return render(request, 'vendor/search.html')
    elif request.method == 'POST':
        if 'pk' in request.POST:
            vendor_id = request.POST.get('pk')
            filters = {'pk': vendor_id}
            vendors = Vendor.objects.filter(**filters)
            if vendors.exists():
                vendor = vendors.first()
                vendor_data = {
                    'pk': vendor.pk,
                    'vname': vendor.vname,
                    'city': vendor.city,
                    'address': vendor.address,
                    'postcode': vendor.postcode,
                    'country': vendor.country,
                    'language': vendor.language,
                    'glAcount': vendor.glAcount,
                    'phone': vendor.phone,
                    'fax': vendor.fax,
                    'tpType': vendor.tpType,
                    'companyCode': vendor.companyCode,
                    'pOrg': vendor.pOrg,
                    'currency': vendor.currency,
                    'euser__uid': vendor.euser.uid,
                }
                return JsonResponse({'status': 1, 'vendor': vendor_data, 'redirect_url': f'/mm/vendor/display/{vendor.pk}/'})
            else:
                return JsonResponse({'status': 0, 'message': "No vendor found with the given ID."})
        else:
            vname = request.POST.get('vname')
            city = request.POST.get('city')
            country = request.POST.get('country')
            companyCode = request.POST.get('companyCode')
            uid = request.POST.get('uid')
            filters = {}
            if vname:
                filters['vname__icontains'] = vname
            if city:
                filters['city__icontains'] = city
            if country:
                filters['country__icontains'] = country
            if companyCode:
                filters['companyCode__icontains'] = companyCode
            if uid:
                filters['euser__uid__icontains'] = uid

            vendors = Vendor.objects.filter(**filters)
            vendors_list = list(vendors.values('pk', 'vname', 'city', 'country', 'companyCode', 'euser__uid'))
            return JsonResponse(vendors_list, safe=False)
    else:
        return HttpResponse(status=405)


@login_required
def display(request, pk):
    vendor = get_object_or_404(Vendor, pk=pk)
    from_create = request.GET.get('from_create', 'false').lower() == 'true'
    if request.method == 'GET':
        return render(request, '../templates/vendor/display.html', {'vendor': vendor, 'from_create': from_create})
    elif request.method == 'POST':
        try:
            vendor.vname = request.POST.get('vname')
            vendor.city = request.POST.get('city')
            vendor.address = request.POST.get('address') or None
            vendor.postcode = request.POST.get('postcode')
            vendor.country = request.POST.get('country')
            vendor.language = request.POST.get('language')
            vendor.glAcount = request.POST.get('glAcount')
            vendor.phone = request.POST.get('phone') or None
            vendor.fax = request.POST.get('fax') or None
            vendor.tpType = request.POST.get('tpType') or None
            vendor.companyCode = request.POST.get('companyCode')
            vendor.pOrg = request.POST.get('pOrg')
            vendor.currency = request.POST.get('currency') or None
            vendor.save()
            return JsonResponse({'status': 1, 'message': "Successfully updated!"})
        except Exception as e:
            return JsonResponse({'status': 0, 'message': f"Error: {str(e)}"})
    else:
        return HttpResponse(status=405)


@login_required
def history(request: HttpRequest):
    if request.method == 'GET':
        return render(
            request=request,
            template_name='../templates/vendor/history.html'
        )
    elif request.method == 'POST':
        mid = request.POST.get('mid')
        range_value = int(request.POST.get('range', 0))
        w1 = int(request.POST.get('w1', 25))
        w2 = int(request.POST.get('w2', 25))
        w3 = int(request.POST.get('w3', 25))
        w4 = int(request.POST.get('w4', 25))

        # 处理时间范围
        from datetime import datetime, timedelta
        end_date = datetime.now()
        if range_value == 1:
            start_date = end_date - timedelta(days=180)  # 近半年
        elif range_value == 2:
            start_date = end_date - timedelta(days=90)  # 近三月
        else:
            start_date = datetime.min  # 全部

        # 查询供应商的交易历史
        vendor_history = Vendor.objects.filter(
            purchaseorder__orderitem__goodreceipt__time__range=[start_date, end_date]
        ).annotate(
            total_amount=Sum('purchaseorder__orderitem__quantity'),
            total_transactions=Count('purchaseorder__orderitem'),
            average_score=Avg('purchaseorder__orderitem__qualityScore')
        ).values('vid', 'vname', 'total_amount', 'total_transactions', 'average_score')

        result = list(vendor_history)

        return JsonResponse(result, safe=False)

    return render(request, 'vendor/history.html')