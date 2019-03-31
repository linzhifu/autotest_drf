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
    proname = models.CharField(verbose_name='项目', max_length=20)
    prodes = models.CharField(verbose_name='项目描述', max_length=50)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')

    class Meta:
        verbose_name_plural = '项目信息'

    def __str__(self):
        return self.proname


# 前端测试管理
class WebManager(models.Model):
    webname = models.CharField(verbose_name='前端测试名称', max_length=20, null=True)
    webdes = models.CharField(verbose_name='前端测试描述', max_length=50, null=True)
    # 地址
    weburl = models.CharField('url地址', max_length=200, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name='所属项目')

    class Meta:
        verbose_name_plural = '前端测试管理'

    def __str__(self):
        return self.webname


# 后端测试管理
class ApiManager(models.Model):
    apiname = models.CharField(verbose_name='后端测试名称', max_length=20, null=True)
    apides = models.CharField(verbose_name='后端测试描述', max_length=50, null=True)
    # 地址
    apiurl = models.CharField('url地址', max_length=200, null=True)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name='所属项目')

    class Meta:
        verbose_name_plural = '后端测试管理'

    def __str__(self):
        return self.apiname


# 后端测试案例
class ApiCase(models.Model):
    apiManager = models.ForeignKey(
        'ApiManager', on_delete=models.CASCADE, verbose_name='前端模块')
    # 接口标题
    apiname = models.CharField('接口名称', max_length=100, null=True)
    # 请求方法
    REQUEST_METHOD = (('get', 'get'), ('post', 'post'), ('put', 'put'),
                      ('delete', 'delete'), ('patch', 'patch'))
    apimethod = models.CharField(
        verbose_name='请求方法',
        choices=REQUEST_METHOD,
        default='get',
        max_length=200,
        null=True)
    # 地址
    apiurl = models.CharField('url地址', max_length=200, null=True)
    # 请求参数和值param
    apiparam = models.TextField(
        '请求参数param', max_length=800, null=True, blank='None')
    # 请求数据Body
    apijson = models.TextField(
        '请求数据json', max_length=800, null=True, blank='None')
    # 响应数据
    apiresponse = models.TextField(
        '响应数据json',
        max_length=5000,
        null=True,
    )
    # 测试结果
    apistatus = models.BooleanField('是否通过', default=True)
    # 创建时间-自动获取当前时间
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间-自动获取当前时间
    update_time = models.DateTimeField('创建时间', auto_now=True)
    # 测试顺序
    index = models.IntegerField('测试序号', default=1)
    # 创建人
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')

    class Meta:
        verbose_name_plural = '后端测试案例'


# 前端测试案例
class WebCase(models.Model):
    webManager = models.ForeignKey(
        'WebManager', on_delete=models.CASCADE, verbose_name='前端模块')
    # 步骤名称
    webname = models.CharField('步骤名称', max_length=100, null=True)
    # Css选择器
    webcss = models.TextField('Css选择器', max_length=800, null=True)
    # 元素操作
    weboprate = models.TextField(
        '元素操作', max_length=800, null=True, blank='None')
    # 操作参数
    webparam = models.TextField(
        '操作参数',
        max_length=500,
        null=True,
    )
    # 操作类型
    oprateOBj = models.CharField('操作类型', max_length=200, null=True)
    # 创建时间-自动获取当前时间
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间-自动获取当前时间
    update_time = models.DateTimeField('创建时间', auto_now=True)
    # 测试顺序
    index = models.IntegerField('测试序号', default=1)
    # 创建人
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')

    class Meta:
        verbose_name_plural = '前端测试案例'
        ordering = ('index', )
