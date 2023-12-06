from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class UserInfo(AbstractUser):
    avatar = models.FileField(verbose_name='用户头像', upload_to='avatar/', default='avatar/w.jpg')
    balance = models.DecimalField(verbose_name='余额', max_digits=8, decimal_places=2, default=30000.00)
    create_time = models.DateField(auto_now_add=True)
    mall = models.OneToOneField(to='Mall', null=True)

    def __str__(self):
        return self.username


class Mall(models.Model):
    site_name = models.CharField(verbose_name='个人站点名称', max_length=32)
    site_title = models.CharField(verbose_name='个人站点标题', max_length=32)

    def __str__(self):
        return self.site_name


class Category(models.Model):
    name = models.CharField(verbose_name='商品分类', max_length=32)
    mall = models.ForeignKey(to='Mall', null=True)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(verbose_name='商品标签', max_length=32)
    mall = models.ForeignKey(to='Mall', null=True)

    def __str__(self):
        return self.name


class Goods(models.Model):
    shop_name = models.CharField(verbose_name='商品名称', max_length=64)
    shop_price = models.DecimalField(verbose_name='商品单价', max_digits=7, decimal_places=2)
    desc = models.CharField(verbose_name='商品简介', max_length=255)
    content = models.TextField(verbose_name='商品说明')
    shop_picture = models.FileField(verbose_name='商品图片', upload_to='shop_picture/', default='shop_picture/w.jpeg')
    create_time = models.DateField(verbose_name='出售时间', auto_now_add=True)
    up_num = models.BigIntegerField(verbose_name='点赞数', default=0)
    down_num = models.BigIntegerField(verbose_name='点踩数', default=0)
    comment_num = models.BigIntegerField(verbose_name='评论数', default=0)
    mall = models.ForeignKey(to='Mall', null=True)
    category = models.ForeignKey(to='Category', null=True)
    tags = models.ManyToManyField(to='Tag', through='Goods2Tag', through_fields=('goods', 'tag'))

    def __str__(self):
        return self.shop_name


class Goods2Tag(models.Model):
    tag = models.ForeignKey(to='Tag')
    goods = models.ForeignKey(to='Goods')


class UpAndDown(models.Model):
    is_up = models.BooleanField()
    user = models.ForeignKey(to='UserInfo')
    goods = models.ForeignKey(to='Goods')


class Comment(models.Model):
    content = models.CharField(verbose_name='评论内容', max_length=255)
    content_time = models.DateTimeField(verbose_name='评论时间', auto_now_add=True)
    user = models.ForeignKey(to='UserInfo')
    goods = models.ForeignKey(to='Goods')
    parent = models.ForeignKey(to='self', null=True)


class ShopCar(models.Model):
    shop_time = models.DateTimeField(verbose_name='进购物车时间', auto_now_add=True)
    user = models.ForeignKey(to='UserInfo')
    goods = models.ForeignKey(to='Goods')


class Flow(models.Model):
    balance_flow = models.DecimalField(verbose_name='余额流水', max_digits=8, decimal_places=2)
    buy_num = models.BigIntegerField(verbose_name='买入数', default=0)
    sell_num = models.BigIntegerField(verbose_name='卖出数', default=0)
    pay_time = models.DateTimeField(verbose_name='支付时间', auto_now_add=True)
    user = models.ForeignKey(to='UserInfo')
    goods = models.ForeignKey(to='Goods')