from django.db import models
from django.contrib.contenttypes.models import ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation


# Create your models here.
# 用户信息
class UserInfo(models.Model):
    username = models.CharField(max_length=20, null=True, blank=True)
    password = models.CharField(max_length=100, null=True, blank=True)
    email = models.EmailField(null=True, blank=True)
    created_time = models.DateTimeField(auto_now_add=True)
    # 用户角色
    role_list = (
        (0, 'user'),
        (1, 'admin'),
    )
    role = models.IntegerField(
        choices=role_list, default=0, null=True, blank=True)

    # 数据库不生成，只用于链表查询
    login_record = GenericRelation('LoginRecord')


# 登陆记录
class LoginRecord(models.Model):
    login_time = models.DateTimeField(auto_now=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()

    # 方便直接获取，不在数据表生成
    content_object = GenericForeignKey('content_type', 'object_id')
