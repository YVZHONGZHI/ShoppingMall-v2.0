import json

from w import models
from bs4 import BeautifulSoup
from django.db.models import F
from django.contrib import auth
from django.db import transaction
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from w.myforms import RegisterForm, SetPasswordForm, ExhibitForm

# Create your views here.


def login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user_obj = auth.authenticate(request, username=username, password=password)
        if user_obj:
            auth.login(request, user_obj)
            return redirect('/home/')
        return redirect('/register/')
    return render(request, 'login.html')


def register(request):
    form_obj = RegisterForm()
    if request.method == 'POST':
        back_dic = {"code": 1000, 'msg': ''}
        categories = ['手机', '平板', '笔记本电脑']
        tags = ['华为', '苹果', '三星', 'OPPO', '真我', 'IQOO', '戴尔', '￥0-3000', '￥3000-6000', '￥6000-10000', '￥10000-15000', '￥15000+']
        form_obj = RegisterForm(request.POST)
        if form_obj.is_valid():
            clean_data = form_obj.cleaned_data
            clean_data.pop('confirm_password')
            file_obj = request.FILES.get('avatar')
            if file_obj:
                clean_data['avatar'] = file_obj
            mall = models.Mall.objects.create(site_name=clean_data['username'], site_title=clean_data['username'] + '的网店')
            for name in categories:
                models.Category.objects.create(name=name, mall_id=mall.pk)
            for name in tags:
                models.Tag.objects.create(name=name, mall_id=mall.pk)
            clean_data['mall_id'] = mall.pk
            models.UserInfo.objects.create_user(**clean_data)
            back_dic['msg'] = '注  册  成  功!'
        else:
            back_dic['code'] = 1001
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'register.html', locals())


def home(request):
    goods_queryset = models.Goods.objects.all()
    return render(request, 'home.html', locals())


@login_required
def vip(request):
    goods_list = models.Goods.objects.all()
    return render(request, 'vip.html', locals())


@login_required
def exhibit(request):
    form_obj = ExhibitForm()
    goods_list = models.Goods.objects.all()
    if request.method == 'POST':
        back_dic = {"code": 1000, 'msg': ''}
        form_obj = ExhibitForm(request.POST)
        if form_obj.is_valid():
            password = request.POST.get('password')
            if auth.authenticate(request, username=request.user, password=password):
                back_dic['password'] = password
                back_dic['msg'] = "暂  时  缺  货  ,  为  您  推  荐  其  它  产  品"
                back_dic['url'] = '/home/'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = "账号密码错误!"
        else:
            back_dic['code'] = 1002
            back_dic['msg'] = form_obj.errors
        return JsonResponse(back_dic)
    return render(request, 'exhibit.html', locals())


def site(request, site_name, **kwargs):
    user_obj = models.UserInfo.objects.filter(mall__site_name=site_name).first()
    if user_obj:
        mall = user_obj.mall
        goods_list = models.Goods.objects.filter(mall__site_name=site_name)
        if kwargs:
            condition = kwargs.get('condition')
            param = kwargs.get('param')
            if condition == 'category':
                goods_list = goods_list.filter(category_id=param)
            elif condition == 'tag':
                goods_list = goods_list.filter(tags__id=param)
            else:
                year, month = param.split('-')
                goods_list = goods_list.filter(create_time__year=year, create_time__month=month)
        return render(request, 'site.html', locals())
    return render(request, 'errors.html')


def goods_detail(request, site_name, goods_id):
    user_obj = models.UserInfo.objects.filter(mall__site_name=site_name).first()
    if user_obj:
        mall = user_obj.mall
        goods_obj = models.Goods.objects.filter(mall__site_name=site_name, pk=goods_id).first()
        if goods_obj:
            comment_list = models.Comment.objects.filter(goods=goods_obj)
            return render(request, 'goods_detail.html', locals())
    return render(request, 'errors.html')


def set_password(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        if request.method == 'POST':
            old_password = request.POST.get('old_password')
            new_password = request.POST.get('password')
            confirm_password = request.POST.get('confirm_password')
            is_right = request.user.check_password(old_password)
            if is_right:
                form_obj = SetPasswordForm(request.POST)
                if form_obj.is_valid():
                    if new_password == confirm_password:
                        if new_password == old_password:
                            back_dic['code'] = 1002
                            back_dic['msg'] = '新密码不能与原密码重复'
                        else:
                            request.user.set_password(new_password)
                            request.user.save()
                            back_dic['msg'] = '修改成功'
                    else:
                        back_dic['code'] = 1003
                        back_dic['msg'] = '两次密码不一致'
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = form_obj.errors
            else:
                back_dic['code'] = 1004
                back_dic['msg'] = '原密码错误'
        return JsonResponse(back_dic)


def set_avatar(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        if request.method == 'POST':
            file_obj = request.FILES.get('avatar')
            user_obj = request.user
            if file_obj:
                user_obj.avatar = file_obj
            else:
                user_obj.avatar = 'avatar/w.jpg'
            user_obj.save()
            back_dic['msg'] = '修改成功'
        return JsonResponse(back_dic)


@login_required
def backend(request):
    car_list = models.ShopCar.objects.filter(user=request.user)
    flow_list = models.Flow.objects.filter(user=request.user)
    goods_list = models.Goods.objects.filter(mall=request.user.mall)
    return render(request, 'backend/backend.html', locals())


@login_required
def logout(request):
    auth.logout(request)
    return redirect('/home/')


def shop_car(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        if request.user.is_authenticated:
            goods_id = request.POST.get('goods_id')
            goods_obj = models.Goods.objects.filter(pk=goods_id).first()
            if not goods_obj.mall.userinfo == request.user:
                is_click = models.ShopCar.objects.filter(user=request.user, goods=goods_obj)
                if not is_click:
                    back_dic['msg'] = '加入购物车成功'
                    models.ShopCar.objects.create(user=request.user, goods=goods_obj)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '不能重复点击'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '自己不能点击'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '<a href="/login/" style="text-decoration:none">请先登录</a>'
        return JsonResponse(back_dic)


def up_or_down(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        if request.user.is_authenticated:
            goods_id = request.POST.get('goods_id')
            is_up = request.POST.get('is_up')
            is_up = json.loads(is_up)
            goods_obj = models.Goods.objects.filter(pk=goods_id).first()
            if not goods_obj.mall.userinfo == request.user:
                is_click = models.UpAndDown.objects.filter(user=request.user, goods=goods_obj)
                if not is_click:
                    if is_up:
                        models.Goods.objects.filter(pk=goods_id).update(up_num=F('up_num') + 1)
                        back_dic['msg'] = '点赞成功'
                    else:
                        models.Goods.objects.filter(pk=goods_id).update(down_num=F('down_num') + 1)
                        back_dic['msg'] = '点踩成功'
                    models.UpAndDown.objects.create(user=request.user, goods=goods_obj, is_up=is_up)
                else:
                    back_dic['code'] = 1001
                    back_dic['msg'] = '不能重复点击'
            else:
                back_dic['code'] = 1002
                back_dic['msg'] = '自己不能点击'
        else:
            back_dic['code'] = 1003
            back_dic['msg'] = '<a href="/login/" style="text-decoration:none">请先登录</a>'
        return JsonResponse(back_dic)


def comment(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        if request.method == 'POST':
            if request.user.is_authenticated:
                goods_id = request.POST.get('goods_id')
                content = request.POST.get('content')
                parent_id = request.POST.get('parent_id')
                if content:
                    with transaction.atomic():
                        models.Goods.objects.filter(pk=goods_id).update(comment_num=F('comment_num') + 1)
                        user_obj = models.Comment.objects.create(user=request.user, goods_id=goods_id, content=content, parent_id=parent_id)
                    content_time = user_obj.content_time
                    back_dic['msg'] = content_time.strftime('%Y-%m-%d %H:%M:%S')
                else:
                    back_dic['code'] = 1002
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '<a href="/login/" style="text-decoration:none">请先登录</a>'
            return JsonResponse(back_dic)


def pay(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        if request.method == 'POST':
            goods_id = request.POST.get('goods_id')
            goods_obj = models.Goods.objects.filter(pk=goods_id).first()
            buy_user = models.UserInfo.objects.filter(username=request.user).first()
            if buy_user.balance >= goods_obj.shop_price:
                models.UserInfo.objects.filter(username=request.user).update(balance=F('balance') - goods_obj.shop_price)
                models.UserInfo.objects.filter(mall=goods_obj.mall_id).update(balance=F('balance') + goods_obj.shop_price)
                new_buy_user = models.UserInfo.objects.filter(username=request.user).first()
                sell_user = models.UserInfo.objects.filter(mall=goods_obj.mall_id).first()
                models.Flow.objects.create(user=request.user, goods_id=goods_id, buy_num=1, balance_flow=new_buy_user.balance)
                models.Flow.objects.create(user=sell_user, goods_id=goods_id, sell_num=1, balance_flow=sell_user.balance)
                models.ShopCar.objects.filter(user=request.user, goods_id=goods_id).delete()
                back_dic['msg'] = '支付成功'
            else:
                back_dic['code'] = 1001
                back_dic['msg'] = '您的余额不足'
            return JsonResponse(back_dic)


def cancel(request):
    if request.is_ajax():
        back_dic = {"code": 1000, 'msg': ''}
        if request.method == 'POST':
            goods_id = request.POST.get('goods_id')
            models.ShopCar.objects.filter(user=request.user, goods_id=goods_id).delete()
            back_dic['msg'] = '取消订单成功'
            return JsonResponse(back_dic)


@login_required
def add_goods(request):
    if request.method == 'POST':
        shop_name = request.POST.get('shop_name')
        shop_price = request.POST.get('shop_price')
        content = request.POST.get('content')
        file_obj = request.FILES.get('shop_picture')
        category_id = request.POST.get('category')
        tag_id_list = request.POST.getlist('tag')
        soup = BeautifulSoup(content, 'html.parser')
        tags = soup.find_all()
        for tag in tags:
            if tag.name == 'script':
                tag.decompose()
        desc = soup.text[0:130]
        if not file_obj:
            file_obj = 'shop_picture/w.jpeg'
        goods_obj = models.Goods.objects.create(shop_name=shop_name, shop_price=shop_price, content=str(soup), shop_picture=file_obj, desc=desc, category_id=category_id, mall=request.user.mall)
        goods_obj_list = []
        for tag_id in tag_id_list:
            tag_goods_obj = models.Goods2Tag(goods=goods_obj, tag_id=tag_id)
            goods_obj_list.append(tag_goods_obj)
        models.Goods2Tag.objects.bulk_create(goods_obj_list)
        return redirect('/backend/')
    tag_list = models.Tag.objects.filter(mall=request.user.mall)
    category_list = models.Category.objects.filter(mall=request.user.mall)
    return render(request, 'backend/add_goods.html', locals())