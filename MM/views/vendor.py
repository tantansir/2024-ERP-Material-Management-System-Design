from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required

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
        # 打印接收到的POST数据
        print(request.POST)

        # 获取POST数据
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
        companyCode = request.POST.get('company')
        pOrg = request.POST.get('pOrg')
        currency = request.POST.get('currency')

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
            # 获取当前登录用户的EUser实例
            euser = EUser.objects.get(pk=request.user.pk)

            # 创建供应商对象
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
            return JsonResponse({"status": 1, "message": "供应商创建成功"})
        except EUser.DoesNotExist:
            return JsonResponse({"status": 0, "message": "当前用户没有关联的EUser实例"}, status=500)
        except Exception as e:
            return JsonResponse({"status": 0, "message": f"创建供应商时出错: {str(e)}"}, status=500)
    else:
        return HttpResponse(status=405)


@login_required
def search(request: HttpRequest):
    user = request.user
    if request.method == 'GET':
        return render(
            request=request,
            template_name='../templates/vendor/search.html'
        )
    else:
        return HttpResponse(status=405)

@login_required
def history(request: HttpRequest):
    if request.method == 'GET':
        return render(
            request=request,
            template_name='../templates/vendor/history.html'
        )
    else:
        return HttpResponse(status=405)