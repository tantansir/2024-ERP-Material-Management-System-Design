from django.shortcuts import get_object_or_404, render
from django.http import JsonResponse, HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect

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
        companyCode = request.POST.get('companyCode')
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
            messages.success(request, "Successfully created!")
            return redirect('MM:display_vendor', pk=vendor.pk)
        except EUser.DoesNotExist:
            messages.error(request, "当前用户没有关联的EUser实例")
            return render(request, 'vendor/create.html', {
                'form': request.POST,
            })
        except Exception as e:
            messages.error(request, f"创建供应商时出错: {str(e)}")
            return render(request, 'vendor/create.html', {
                'form': request.POST,
            })
    else:
        return HttpResponse(status=405)

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
    if request.method == 'GET':
        return render(request, '../templates/vendor/display.html', {'vendor': vendor})
    elif request.method == 'POST':
        try:
            vendor.vname = request.POST.get('vname')
            vendor.city = request.POST.get('city')
            vendor.address = request.POST.get('address')
            vendor.postcode = request.POST.get('postcode')
            vendor.country = request.POST.get('country')
            vendor.language = request.POST.get('language')
            vendor.glAcount = request.POST.get('glAcount')
            vendor.phone = request.POST.get('phone')
            vendor.fax = request.POST.get('fax')
            vendor.tpType = request.POST.get('tpType')
            vendor.companyCode = request.POST.get('companyCode')
            vendor.pOrg = request.POST.get('pOrg')
            vendor.currency = request.POST.get('currency')
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
    else:
        return HttpResponse(status=405)