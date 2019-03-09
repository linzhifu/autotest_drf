from django.db import models
from django.contrib.auth.models import User


# Create your models here.
# 登陆记录
class LoginRecord(models.Model):
    login_time = models.DateTimeField(verbose_name='登陆时间', auto_now=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='用户')

    class Meta:
        verbose_name_plural = '用户登陆记录'


# 项目信息
class Project(models.Model):
    proname = models.CharField(verbose_name='项目', max_length=20, null=True)
    prodes = models.CharField(verbose_name='项目描述', max_length=50, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name='创建人')

    class Meta:
        verbose_name_plural = '项目信息'
