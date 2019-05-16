from django.core.mail import EmailMessage
from django.contrib import auth
from django.contrib.auth.models import User, ContentType
from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
# from rest_framework.filters import OrderingFilter
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from user.models import LoginRecord, Project, WebManager, ApiManager, ApiCase, WebCase, TestType, CheckWebCase
from user.serializer import ProjectSerializer, UserSerializer, WebManagerSerializer, CheckWebCaseSerializer
from user.serializer import ApiManagerSerializer, ApiCaseSerializer, WebCaseSerializer, TestTypeSerializer
import string
import random
from user.tests import webCase, webTest, apiCase, apiTest, get_record, add_one_test_record
from user.tests import testMpcloudCase, mpcloudCases


# Create your views here.
# 首页
def home(request):
    # 对vue单页应用进行csrf_token设置，方便进行csrf防御
    # request.META["CSRF_COOKIE_USED"] = True
    return render(request, 'index.html')


# 用户登陆
class LoginView(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = {'errcode': 0, 'errmsg': 'ok'}
        body_data = request.data
        # 获取登陆方式
        login_type = body_data.get('type')
        # 用户名密码登陆
        if login_type == 'username':
            username = body_data.get('username')
            password = body_data.get('password')
            user = auth.authenticate(username=username, password=password)
            if not user:
                data['errcode'] = 101
                data['errmsg'] = '用户名或密码错误'
            elif user.is_active:
                # 验证通过,登陆用户，并返回用户信息
                # auth.login(request, user)
                ser = UserSerializer(instance=user)
                data['data'] = ser.data
            else:
                data['errcode'] = 102
                data['errmsg'] = '用户已被禁止登陆'
        # 邮箱登陆
        else:
            email = body_data.get('email')
            captcha = body_data.get('captcha')
            captcha_cache = cache.get(email)
            if captcha == captcha_cache:
                # 验证通过,登陆用户，并返回用户信息
                user = User.objects.filter(email=email).first()
                if not user:
                    # 用户不存在，创建新用户，用户名默认为邮箱，密码123
                    user = User.objects.create(
                        username=email,
                        email=email,
                        password=make_password('123'))
                ser = UserSerializer(instance=user)
                data['data'] = ser.data
            else:
                data['errcode'] = 104
                data['errmsg'] = '邮箱或验证码不正确'

        if data['errcode'] == 0:
            # 返回token
            # 存在就更新token，不存在就创建
            token = Token.objects.filter(user=user).first()
            if token:
                token.delete()
            token = Token.objects.create(user=user)
            data['token'] = token.key
            # 添加登陆记录，并加入数据库缓存作为登陆凭证（24小时内有效）
            cache.set(user.id, 1, 60 * 60 * 24)
            LoginRecord.objects.create(user=user)
        return Response(data)


# 获取验证码
class CaptchaView(APIView):
    authentication_classes = []
    permission_classes = []

    # 获取验证码：
    def get(self, request, *args, **kwargs):
        data = {'errcode': 0, 'errmsg': 'ok'}
        email = request.GET.get('email', '')

        # 判断验证码是否已经存在缓存中
        if cache.get(email, ''):
            data['errcode'] = 301
            data['errmsg'] = '验证码已发送，请稍后再获取'

        else:
            # 获取4位随机数（小写字母+数字）
            code = ''.join(
                random.sample(string.ascii_lowercase + string.digits, 4))
            try:
                # 发送邮件
                # send_mail(
                #     'LONGSYS自动化测试平台',
                #     '验证码：' + code,
                #     '18129832245@163.com',
                #     [email],
                #     fail_silently=False,
                # )

                # 邮件内容为HTML
                # 登陆地址
                url = 'http://mpstest.longsys.com/'
                html_content = "<p><strong>验证码：%s</strong></p>\
                    <p>This is an <font size=3 color='green'>\
                    <strong>important</strong></font> message.</p><br>\
                    <a href='%s'>点击登陆<a>" % (code, url)
                msg = EmailMessage(
                    '自动化测试平台-%s' % (code),
                    html_content,
                    '18129832245@163.com',
                    [email],
                )
                msg.content_subtype = 'html'
                msg.send()

            except Exception as e:
                print(e)
                data['errcode'] = 302
                data['errmsg'] = '发送失败'

        # 判断是否发送成功，加入缓存，有效期3min
        if not data.get('errcode'):
            cache.set(email, code, 60 * 1)
        return Response(data=data)


# 用户信息
class UserView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# 项目
class ProjectView(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


# 前端测试管理-自定义
class WebManagerView(ModelViewSet):
    queryset = WebManager.objects.all()
    serializer_class = WebManagerSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('project', )


# 前端测试案例-自定义
class WebCaseView(ModelViewSet):
    queryset = WebCase.objects.all()
    serializer_class = WebCaseSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('testType', )


# 前端测试数据验证-自定义
class CheckWebCaseView(ModelViewSet):
    queryset = CheckWebCase.objects.all()
    serializer_class = CheckWebCaseSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('testType', )


# 后端测试管理
class ApiManagerView(ModelViewSet):
    queryset = ApiManager.objects.all()
    serializer_class = ApiManagerSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('project', )


# 后端测试案例
class ApiCaseView(ModelViewSet):
    queryset = ApiCase.objects.all()
    serializer_class = ApiCaseSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('testType', )


# 测试类型
class TestTypeView(ModelViewSet):
    queryset = TestType.objects.all()
    serializer_class = TestTypeSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('content_type', 'object_id')


# 前端测试案例单元测试-自定义
class WebCaseTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        host = ip + ':4444/wd/hub'
        url = request.GET.get('url')
        testType_id = request.GET.get('testType')
        webType = TestType.objects.filter(id=testType_id).first()
        webManager = WebManager.objects.filter(id=webType.object_id).first()
        data = webCase(url, host, webType, webManager)
        return Response(data)


# 前端模块测试-自定义
class WebTypeTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        host = ip + ':4444/wd/hub'
        url = request.GET.get('url')
        content_type_id = request.GET.get('content_type')
        object_id = request.GET.get('object_id')
        webTypes = TestType.objects.filter(
            object_id=object_id, content_type_id=content_type_id)
        webManager = WebManager.objects.filter(id=object_id).first()
        data = webTest(
            url,
            host,
            webTypes,
            webManager,
            testName=webManager.webname,
            type='前端测试')
        return Response(data)


# 前端整体测试-自定义
class WebManagerTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        host = ip + ':4444/wd/hub'
        projectId = request.GET.get('projectId')
        project = Project.objects.get(id=projectId)
        webManagers = WebManager.objects.filter(project_id=projectId)
        for webManager in webManagers:
            content_type_id = ContentType.objects.get_for_model(WebManager)
            webTypes = TestType.objects.filter(
                object_id=webManager.id, content_type_id=content_type_id)
            data = webTest(
                webManager.weburl,
                host,
                webTypes,
                webManager,
                testName=webManager.webname,
                type='前端测试')
            if data['errcode']:
                data['errmsg'] = webManager.webname + '-' + data['errmsg']
                return Response(data)

        project.webresult = True
        project.save()
        return Response(data)


# 后端API单元测试
class ApiCaseTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        url = request.GET.get('url')
        testType_id = request.GET.get('testType')
        apiType = TestType.objects.filter(id=testType_id).first()
        apiManager = ApiManager.objects.filter(id=apiType.object_id).first()
        data = apiCase(url, apiType, apiManager)
        return Response(data)


# 后端模块测试
class ApiTypeTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        url = request.GET.get('url')
        content_type_id = request.GET.get('content_type')
        object_id = request.GET.get('object_id')
        apiTypes = TestType.objects.filter(
            object_id=object_id, content_type_id=content_type_id)
        apiManager = ApiManager.objects.filter(id=object_id).first()
        data = apiTest(
            url,
            apiTypes,
            apiManager,
            testName=apiManager.apiname,
            type='后端测试')
        return Response(data)


# 后端整体测试
class ApiManagerTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        projectId = request.GET.get('projectId')
        project = Project.objects.get(id=projectId)
        apiManagers = ApiManager.objects.filter(project_id=projectId)
        for apiManager in apiManagers:
            content_type_id = ContentType.objects.get_for_model(ApiManager)
            apiTypes = TestType.objects.filter(
                object_id=apiManager.id, content_type_id=content_type_id)
            data = apiTest(
                apiManager.apiurl,
                apiTypes,
                apiManager,
                testName=apiManager.apiname,
                type='后端测试')
            if data['errcode']:
                return Response(data)

        project.apiresult = True
        project.save()
        return Response(data)


# 项目测试
class projectTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        projectId = request.GET.get('projectId')
        project = Project.objects.get(id=projectId)
        # 后端测试
        print('后端测试开始')
        apiManagers = ApiManager.objects.filter(project_id=projectId)
        for apiManager in apiManagers:
            content_type_id = ContentType.objects.get_for_model(ApiManager)
            apiTypes = TestType.objects.filter(
                object_id=apiManager.id, content_type_id=content_type_id)
            data = apiTest(
                apiManager.apiurl,
                apiTypes,
                apiManager,
                testName=apiManager.apiname,
                type='后端测试')
            if data['errcode']:
                add_one_test_record(project, False)
                return Response(data)

        project.apiresult = True
        project.save()

        # 前端测试
        print('前端测试开始')
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        host = ip + ':4444/wd/hub'
        if project.proname == '量产云平台':
            for case in mpcloudCases:
                data = testMpcloudCase(host, case)
                if data['errcode']:
                    add_one_test_record(project, False)
                    project.webresult = False
                    project.result = False
                    project.save()
                    return Response(data)
        else:
            webManagers = WebManager.objects.filter(project_id=projectId)
            for webManager in webManagers:
                content_type_id = ContentType.objects.get_for_model(WebManager)
                webTypes = TestType.objects.filter(
                    object_id=webManager.id, content_type_id=content_type_id)
                data = webTest(
                    webManager.weburl,
                    host,
                    webTypes,
                    webManager,
                    testName=webManager.webname,
                    type='前端测试')
                if data['errcode']:
                    add_one_test_record(project, False)
                    return Response(data)

        project.webresult = True
        project.result = True
        project.save()
        add_one_test_record(project, True)

        return Response(data)


# 测试记录
class getRecord(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        data = {}
        projectId = request.GET.get('projectId')
        print(projectId)
        project = Project.objects.get(id=projectId)
        # 后端测试
        records = get_record(project)
        data['records'] = records
        return Response(data)


# 前端自动化测试项目
class webAutoTest(APIView):
    authentication_classes = []
    permission_classes = []

    def get(self, request, *args, **kwargs):
        # 量产云平台
        if request.GET.get('project') == '量产云平台':
            return Response(mpcloudCases)

        else:
            return Response([])

    def patch(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        host = ip + ':4444/wd/hub'
        case = request.data
        result = testMpcloudCase(host, case)
        return Response(result)

    def post(self, request, *args, **kwargs):
        if request.META.get('HTTP_X_FORWARDED_FOR'):
            ip = request.META['HTTP_X_FORWARDED_FOR']
        else:
            ip = request.META['REMOTE_ADDR']
        host = ip + ':4444/wd/hub'
        result = {}
        cases = request.data
        for case in cases:
            result = testMpcloudCase(host, case)
            if result['errcode']:
                return Response(result)
        return Response(result)
