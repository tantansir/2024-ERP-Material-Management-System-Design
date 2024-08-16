from django.shortcuts import get_object_or_404, render
from django.http import HttpRequest, HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib import auth, messages
from django.contrib.auth.decorators import login_required
import re
from django.shortcuts import redirect

from ..models import EUser

def login(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        return render(
            request=request,
            template_name='../templates/user/login.html',
        )
    elif request.method == 'POST':
        email = request.POST.get('email')
        password = request.POST.get('password')
        message = None
        if (password=='' or email==''):
            message = "部分字段为空"
        else:
            queryset = EUser.objects.filter(email__exact=email)
            if len(queryset) == 0:
                message = "用户名错误"
            else:
                euser = auth.authenticate(username=queryset.get().username, password=password)
                if euser is None:
                    message = "密码错误"
        if message is None:
            auth.login(request=request, user=euser)
            return HttpResponseRedirect(reverse('MM:home'))
        else:
            return render(
                request=request,
                template_name='../templates/user/login.html',
                context={'message': message}
            )


def register(request: HttpRequest) -> HttpResponse:
    if request.method == 'GET':
        return render(
            request=request,
            template_name='../templates/user/register.html',
        )
    elif request.method == 'POST':
        post = request.POST
        username = post.get('username')
        first_name = post.get('first_name')
        last_name = post.get('last_name')
        password = post.get('password')
        password1 = post.get('password2')
        email = post.get('email')
        sector = post.get('sector')
        phone = post.get('phone')
        question1 = post.get('question1')
        answer1 = post.get('answer1')
        question2 = post.get('question2')
        answer2 = post.get('answer2')

        message = None

        # 检查是否有空字段
        if (username == '' or password == '' or password1 == '' or email == '' or sector == '' or phone == '' or
                question1 == '' or question2 == '' or answer1 == '' or answer2 == ''):
            message = "部分字段为空"

        # 检查密码是否包含字母和数字
        elif not (re.search(r'[A-Za-z]', password) and re.search(r'[0-9]', password)):
            message = "密码必须同时包含字母和数字"

        # 检查电话是否为11位数字
        elif not re.match(r'^\d{11}$', phone):
            message = "电话必须为11位数字"

        # 检查邮箱格式是否正确
        elif not re.match(r'^[\w\.-]+@[\w\.-]+\.\w+$', email):
            message = "邮箱格式不正确"

        # 检查两次密码是否一致
        elif password != password1:
            message = "两次输入的密码不一致"

        # 检查邮箱是否已经注册
        else:
            queryset = EUser.objects.filter(email__exact=email)
            if len(queryset) > 0:
                message = "您的邮箱已被注册过"
            queryset = EUser.objects.filter(username__exact=username)
            if len(queryset) > 0:
                message = "您的用户名已被注册过"

        if message is None:
            euser = EUser(
                username=username,
                first_name=first_name,
                last_name=last_name,
                sector=sector,
                phone=phone,
                email=email,
                question1=question1, question2=question2,
                answer1=answer1, answer2=answer2,
            )
            euser.set_password(password)
            euser.save()
            messages.success(request=request, message="用户创建成功！")
            return HttpResponseRedirect(reverse('MM:login'))
        else:
            messages.error(request, message)
            return redirect('MM:register')


@login_required
def home(request):
    return render(
        request=request,
        template_name='../templates/user/index.html',
    )
    # return HttpResponse(request.user.username)

def logout(request):
    auth.logout(request=request)
    return HttpResponseRedirect(reverse('MM:login'))