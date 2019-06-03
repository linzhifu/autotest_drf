from django.db import models
from django.contrib.auth.models import User, ContentType
from django.contrib.contenttypes.fields import GenericForeignKey, GenericRelation
from django.utils import timezone


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
    webresult = models.BooleanField(verbose_name='前端测试结果', default=False)
    apiresult = models.BooleanField(verbose_name='后端测试结果', default=False)
    result = models.BooleanField(verbose_name='测试结果', default=False)
    update_time = models.DateTimeField(verbose_name='最后修改', auto_now=True)

    adminUser = models.CharField(verbose_name='管理员账户', max_length=20, default='linzhifu221@163.com')
    adminPsw = models.CharField(verbose_name='管理员密码', max_length=20, default='Lin5535960')
    testUser = models.CharField(verbose_name='测试账户', max_length=20, default='17388730192@163.com')
    testPsw = models.CharField(verbose_name='测试密码', max_length=20, default='123')

    class Meta:
        verbose_name_plural = '项目信息'
        ordering = ['-update_time']

    def __str__(self):
        return self.proname


# 测试报告记录
class Report(models.Model):
    project = models.ForeignKey(
        Project, on_delete=models.CASCADE, verbose_name='所属项目')
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')
    version = models.CharField(verbose_name='软件版本信息', max_length=800)
    releaseNote = models.CharField('Release Note', max_length=800)
    update_time = models.DateTimeField(verbose_name='创建时间', auto_now=True)

    class Meta:
        verbose_name_plural = '测试报告记录'
        ordering = ['-update_time']

    def __str__(self):
        return self.update_time


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
    result = models.BooleanField(verbose_name='测试结果', default=False)
    update_time = models.DateTimeField(verbose_name='最后修改', auto_now=True)

    # 数据库不生成，只用于链表查询
    test_type = GenericRelation('TestType')
    test_record = GenericRelation('TestRecord')

    class Meta:
        verbose_name_plural = '前端测试管理'
        ordering = ['-update_time']

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
    result = models.BooleanField(verbose_name='测试结果', default=False)
    update_time = models.DateTimeField(verbose_name='最后修改', auto_now=True)

    # 数据库不生成，只用于链表查询
    test_type = GenericRelation('TestType')
    test_record = GenericRelation('TestRecord')

    class Meta:
        verbose_name_plural = '后端测试管理'
        ordering = ['-update_time']

    def __str__(self):
        return self.apiname


# 后端测试案例
class ApiCase(models.Model):
    testType = models.ForeignKey(
        'TestType', on_delete=models.CASCADE, verbose_name='测试分类')
    # 接口标题
    apiname = models.CharField('接口名称', max_length=100)
    # 请求方法
    REQUEST_METHOD = (('get', 'get'), ('post', 'post'), ('put', 'put'),
                      ('delete', 'delete'), ('patch', 'patch'))
    apimethod = models.CharField(
        verbose_name='请求方法',
        choices=REQUEST_METHOD,
        default='get',
        max_length=200,
        null=True,
        blank=True)
    # 地址
    apiurl = models.CharField('url地址', max_length=200, null=True)
    # 请求参数和值param
    apiparam = models.TextField(
        '请求参数param', max_length=800, null=True, blank=True)
    contentType = models.TextField(
        '请求body格式', max_length=800, default='application/json')
    # 请求数据Body
    apijson = models.TextField(
        '请求数据json', max_length=800, null=True, blank=True)
    # 响应数据
    apiresponse = models.TextField(
        '响应数据json', max_length=5000, null=True, blank=True)
    # 测试数据
    testdata = models.TextField(
        '测试数据', max_length=5000, null=True, blank=True)
    # 测试结果
    result = models.BooleanField('是否通过', default=False)
    # 创建时间-自动获取当前时间
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间-自动获取当前时间
    update_time = models.DateTimeField('更新时间', auto_now=True)
    # 测试顺序
    index = models.IntegerField('测试序号', default=1)
    # 创建人
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')

    # 测试是否需要管理员权限
    isAdmin = models.BooleanField(verbose_name='测试是否需要管理员权限', default=False)
    # 测试是否需要授权
    isAuth = models.BooleanField(verbose_name='测试是否需要授权', default=False)
    # 权限将要赋予的对象，需要填写type和id，type可以是role和user
    operatorType = models.TextField(
        '权限将要赋予的对象-Type', max_length=800, null=True, blank=True)
    operatorId = models.TextField(
        '权限将要赋予的对象-id', max_length=800, null=True, blank=True)
    # 权限针对的对象，需要填写type和id，type可以是模块名称，比如product、module、order、role、user
    objectType = models.TextField(
        '权限针对的对象-type', max_length=800, null=True, blank=True)
    objectId = models.TextField(
        '权限针对的对象-id', max_length=800, null=True, blank=True)
    # 权限定义的动作集合
    actions = models.TextField(
        '权限定义的动作集合', max_length=800, null=True, blank=True)

    class Meta:
        verbose_name_plural = '后端测试案例'
        ordering = ['index']


# 前端测试案例
class WebCase(models.Model):
    testType = models.ForeignKey(
        'TestType', on_delete=models.CASCADE, verbose_name='测试分类')
    # 步骤名称
    webname = models.CharField('步骤名称', max_length=100)
    # Css选择器
    webcss = models.TextField('Css选择器', max_length=800, null=True, blank=True)
    # 元素操作
    weboprate = models.TextField('元素操作', max_length=800, null=True, blank=True)
    # 操作参数
    webparam = models.TextField('操作参数', max_length=500, null=True, blank=True)
    # 创建时间-自动获取当前时间
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间-自动获取当前时间
    update_time = models.DateTimeField('最近修改', auto_now=True)
    # 测试顺序
    index = models.IntegerField('测试序号', default=1)
    # 创建人
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')

    class Meta:
        verbose_name_plural = '前端测试案例'
        ordering = ('index', )


# 前端数据验证
class CheckWebCase(models.Model):
    testType = models.ForeignKey(
        'TestType', on_delete=models.CASCADE, verbose_name='测试分类')
    # 步骤名称
    webname = models.CharField('步骤名称', max_length=100)
    # Css选择器
    webcss = models.TextField('Css选择器', max_length=800, null=True, blank=True)
    # 元素操作
    weboprate = models.TextField('元素操作', max_length=800, null=True, blank=True)
    # 操作参数
    webparam = models.TextField('操作参数', max_length=500, null=True, blank=True)
    # 验证数据
    checktext = models.TextField('验证数据', max_length=500, null=True, blank=True)
    # 创建时间-自动获取当前时间
    create_time = models.DateTimeField('创建时间', auto_now_add=True)
    # 更新时间-自动获取当前时间
    update_time = models.DateTimeField('最近修改', auto_now=True)
    # 测试顺序
    index = models.IntegerField('测试序号', default=1)
    # 创建人
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')

    class Meta:
        verbose_name_plural = '前端测试数据验证'
        ordering = ('index', )


# 测试类型分类
class TestType(models.Model):
    is_test = models.BooleanField(verbose_name='是否测试', default=True)
    result = models.BooleanField(verbose_name='测试结果', default=False)
    typename = models.CharField(verbose_name='名称', max_length=500)
    typedes = models.CharField(verbose_name='描述', max_length=500)
    update_time = models.DateTimeField(verbose_name='最后修改', auto_now=True)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    # 测试顺序
    index = models.IntegerField('测试序号', default=1)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, verbose_name='创建人')

    # 方便直接生成，不在数据表生成
    content_object = GenericForeignKey('content_type', 'object_id')
    # 方便查询记录
    test_record = GenericRelation('TestRecord')

    class Meta:
        verbose_name_plural = '测试类型分类'
        ordering = ('index', )

    def __str__(self):
        return self.typename


# 测试记录
class TestRecord(models.Model):
    test_all = models.IntegerField(default=0)
    test_pass = models.IntegerField(default=0)
    test_fail = models.IntegerField(default=0)
    test_time = models.DateField(default=timezone.now)
    content_type = models.ForeignKey(ContentType, on_delete=models.DO_NOTHING)
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey('content_type', 'object_id')

    class Meta:
        verbose_name = '测试计数'
        verbose_name_plural = '测试计数'
        ordering = [
            '-test_time',
        ]
