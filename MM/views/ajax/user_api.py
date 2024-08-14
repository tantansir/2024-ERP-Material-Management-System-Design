from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect, JsonResponse
from django.urls import reverse
from django.contrib import auth, messages
from django import forms
from django.contrib.auth.decorators import login_required
from django.core import serializers
from django.forms.models import model_to_dict
from django.db.models import QuerySet, Sum
import json
import pandas as pd
from ...models import EUser

DATA_URL = './MM/data/'

@login_required
def load_user(request: HttpRequest):
    user: QuerySet = EUser.objects.all()
    return HttpResponse(json.dumps(list(user), default=str))

@login_required
def get_user_info(request):
    user = request.user
    try:
        euser = EUser.objects.get(id=user.id)
        data = {
            'id': euser.id,  # 返回用户ID
            'username': euser.username,  # 返回用户名
            'email': euser.email,
            'sector': euser.sector,
            'phone': euser.phone,
            'date_joined': euser.date_joined.strftime('%Y-%m-%d %H:%M:%S'),
        }
        return JsonResponse({'status': 'success', 'data': data})
    except EUser.DoesNotExist:
        return JsonResponse({'status': 'error', 'message': 'User does not exist'}, status=404)