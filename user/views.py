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
from user.models import LoginRecord, Project, WebManager, ApiManager, ApiCase, WebCase, \
    TestType, CheckWebCase, Report
from user.serializer import ProjectSerializer, UserSerializer, WebManagerSerializer, \
    CheckWebCaseSerializer, ApiManagerSerializer, ApiCaseSerializer, WebCaseSerializer, \
    TestTypeSerializer, ReportSerializer
import string
import random
from user.tests import webCase, webTest, apiCase, apiTest, get_record, add_one_test_record
from user.tests import testMpcloudCase, mpcloudCases
import openpyxl
from openpyxl.styles import colors, Font
import os


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
                        password=make_password('123'),
                        is_superuser=True)
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
                url = 'http://autotest.longsys.com/'
                html_content = "<p>Hello %s：</p>\
                    <p>This is longsys autotest system, your captcha is: %s</p>\
                    <a href='%s'>Please Login<a>" % (email, code, url)
                msg = EmailMessage(
                    'Captcha:%s' % (code),
                    html_content,
                    'leo.lin@longsys.com',
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


# 测试报告记录
class ReportView(ModelViewSet):
    queryset = Report.objects.all()
    serializer_class = ReportSerializer


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

    def post(self, request, *args, **kwargs):
        url = request.GET.get('url')
        testType_id = request.GET.get('testType')
        testUserInfo = request.data.get('testUserInfo')
        apiType = TestType.objects.filter(id=testType_id).first()
        apiManager = ApiManager.objects.filter(id=apiType.object_id).first()
        data = apiCase(url, apiType, apiManager, testUserInfo)
        return Response(data)


# 后端模块测试
class ApiTypeTest(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        url = request.GET.get('url')
        testUserInfo = request.data.get('testUserInfo')
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
            type='后端测试',
            testUserInfo=testUserInfo)
        return Response(data)


# 后端整体测试
class ApiManagerTest(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        projectId = request.GET.get('projectId')
        project = Project.objects.get(id=projectId)
        testUserInfo = request.data.get('testUserInfo')
        # print(testUserInfo)
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
                type='后端测试',
                testUserInfo=testUserInfo)
            if data['errcode']:
                data['errmsg'] = apiManager.apiname + ': ' + data['errmsg']
                project.apiresult = False
                project.save()
                return Response(data)

        project.apiresult = True
        project.save()
        return Response(data)


# 项目测试
class projectTest(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        projectId = request.GET.get('projectId')
        project = Project.objects.get(id=projectId)
        testUserInfo = request.data.get('testUserInfo')
        print(testUserInfo)
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
                type='后端测试',
                testUserInfo=testUserInfo)
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


# 前端自动化测试项目
class MpcloudExcel(APIView):
    authentication_classes = []
    permission_classes = []

    def post(self, request, *args, **kwargs):
        res = {'errcode': 0, 'errmsg': 'ok'}
        # 量产云平台
        data = request.data
        report = data['mpcloudReport']
        fileName = data['fileName']
        try:
            wb = openpyxl.load_workbook('量产云平台研发验证报告.xlsx')
            # 红色
            redFont = Font(color=colors.RED)
            # 绿色
            greenFont = Font(color=colors.GREEN)

            # 权限测试
            sheet = wb.get_sheet_by_name('权限测试')
            # 产品-产品工程师
            product_pm = 'PASS'
            for test in report['product_pm']:
                if test['testInfo'] == '个人资料':
                    sheet['D4'] = test['result']
                    sheet['E4'] = test['note']
                    if sheet['D4'].value == 'PASS':
                        sheet['D4'].font = greenFont
                    else:
                        product_pm = 'FAIL'
                        sheet['D4'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D9'] = test['result']
                    sheet['E9'] = test['note']
                    if sheet['D9'].value == 'PASS':
                        sheet['D9'].font = greenFont
                    else:
                        product_pm = 'FAIL'
                        sheet['D9'].font = redFont

                if test['testInfo'] == '添加项目':
                    sheet['D16'] = test['result']
                    sheet['E16'] = test['note']
                    if sheet['D16'].value == 'PASS':
                        sheet['D16'].font = greenFont
                    else:
                        product_pm = 'FAIL'
                        sheet['D16'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D20'] = test['result']
                    sheet['E20'] = test['note']
                    if sheet['D20'].value == 'PASS':
                        sheet['D20'].font = greenFont
                    else:
                        product_pm = 'FAIL'
                        sheet['D20'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D28'] = test['result']
                    sheet['E28'] = test['note']
                    if sheet['D28'].value == 'PASS':
                        sheet['D28'].font = greenFont
                    else:
                        product_pm = 'FAIL'
                        sheet['D28'].font = redFont

            # 项目-产品工程师
            model_pm = 'PASS'
            for test in report['model_pm']:
                if test['testInfo'] == '个人资料':
                    sheet['D33'] = test['result']
                    sheet['E33'] = test['note']
                    if sheet['D33'].value == 'PASS':
                        sheet['D33'].font = greenFont
                    else:
                        model_pm = 'FAIL'
                        sheet['D33'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D38'] = test['result']
                    sheet['E38'] = test['note']
                    if sheet['D38'].value == 'PASS':
                        sheet['D38'].font = greenFont
                    else:
                        model_pm = 'FAIL'
                        sheet['D38'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D45'] = test['result']
                    sheet['E45'] = test['note']
                    if sheet['D45'].value == 'PASS':
                        sheet['D45'].font = greenFont
                    else:
                        model_pm = 'FAIL'
                        sheet['D45'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D51'] = test['result']
                    sheet['E51'] = test['note']
                    if sheet['D51'].value == 'PASS':
                        sheet['D51'].font = greenFont
                    else:
                        model_pm = 'FAIL'
                        sheet['D51'].font = redFont

            # 产品-研发工程师
            product_rd = 'PASS'
            for test in report['product_rd']:
                if test['testInfo'] == '个人资料':
                    sheet['D56'] = test['result']
                    sheet['E56'] = test['note']
                    if sheet['D56'].value == 'PASS':
                        sheet['D56'].font = greenFont
                    else:
                        product_rd = 'FAIL'
                        sheet['D56'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D61'] = test['result']
                    sheet['E61'] = test['note']
                    if sheet['D61'].value == 'PASS':
                        sheet['D61'].font = greenFont
                    else:
                        product_rd = 'FAIL'
                        sheet['D61'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D68'] = test['result']
                    sheet['E68'] = test['note']
                    if sheet['D68'].value == 'PASS':
                        sheet['D68'].font = greenFont
                    else:
                        product_rd = 'FAIL'
                        sheet['D68'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D73'] = test['result']
                    sheet['E73'] = test['note']
                    if sheet['D73'].value == 'PASS':
                        sheet['D73'].font = greenFont
                    else:
                        product_rd = 'FAIL'
                        sheet['D73'].font = redFont

                if test['testInfo'] == '添加样品':
                    sheet['D78'] = test['result']
                    sheet['E78'] = test['note']
                    if sheet['D78'].value == 'PASS':
                        sheet['D78'].font = greenFont
                    else:
                        product_rd = 'FAIL'
                        sheet['D78'].font = redFont

            # 项目-研发工程师
            model_rd = 'PASS'
            for test in report['model_rd']:
                if test['testInfo'] == '个人资料':
                    sheet['D81'] = test['result']
                    sheet['E81'] = test['note']
                    if sheet['D81'].value == 'PASS':
                        sheet['D81'].font = greenFont
                    else:
                        model_rd = 'FAIL'
                        sheet['D81'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D86'] = test['result']
                    sheet['E86'] = test['note']
                    if sheet['D86'].value == 'PASS':
                        sheet['D86'].font = greenFont
                    else:
                        model_rd = 'FAIL'
                        sheet['D86'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D93'] = test['result']
                    sheet['E93'] = test['note']
                    if sheet['D93'].value == 'PASS':
                        sheet['D93'].font = greenFont
                    else:
                        model_rd = 'FAIL'
                        sheet['D93'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D98'] = test['result']
                    sheet['E98'] = test['note']
                    if sheet['D98'].value == 'PASS':
                        sheet['D98'].font = greenFont
                    else:
                        model_rd = 'FAIL'
                        sheet['D98'].font = redFont

                if test['testInfo'] == '添加样品':
                    sheet['D103'] = test['result']
                    sheet['E103'] = test['note']
                    if sheet['D103'].value == 'PASS':
                        sheet['D103'].font = greenFont
                    else:
                        model_rd = 'FAIL'
                        sheet['D103'].font = redFont

            # 产品-测试工程师
            product_te = 'PASS'
            for test in report['product_te']:
                if test['testInfo'] == '个人资料':
                    sheet['D106'] = test['result']
                    sheet['E106'] = test['note']
                    if sheet['D106'].value == 'PASS':
                        sheet['D106'].font = greenFont
                    else:
                        product_te = 'FAIL'
                        sheet['D106'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D111'] = test['result']
                    sheet['E111'] = test['note']
                    if sheet['D111'].value == 'PASS':
                        sheet['D111'].font = greenFont
                    else:
                        product_te = 'FAIL'
                        sheet['D111'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D118'] = test['result']
                    sheet['E118'] = test['note']
                    if sheet['D118'].value == 'PASS':
                        sheet['D118'].font = greenFont
                    else:
                        product_te = 'FAIL'
                        sheet['D118'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D123'] = test['result']
                    sheet['E123'] = test['note']
                    if sheet['D123'].value == 'PASS':
                        sheet['D123'].font = greenFont
                    else:
                        product_te = 'FAIL'
                        sheet['D123'].font = redFont

                if test['testInfo'] == '添加样品':
                    sheet['D128'] = test['result']
                    sheet['E128'] = test['note']
                    if sheet['D128'].value == 'PASS':
                        sheet['D128'].font = greenFont
                    else:
                        product_te = 'FAIL'
                        sheet['D128'].font = redFont

            # 项目-测试工程师
            model_te = 'PASS'
            for test in report['model_te']:
                if test['testInfo'] == '个人资料':
                    sheet['D131'] = test['result']
                    sheet['E131'] = test['note']
                    if sheet['D131'].value == 'PASS':
                        sheet['D131'].font = greenFont
                    else:
                        model_te = 'FAIL'
                        sheet['D131'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D136'] = test['result']
                    sheet['E136'] = test['note']
                    if sheet['D136'].value == 'PASS':
                        sheet['D136'].font = greenFont
                    else:
                        model_te = 'FAIL'
                        sheet['D136'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D143'] = test['result']
                    sheet['E143'] = test['note']
                    if sheet['D143'].value == 'PASS':
                        sheet['D143'].font = greenFont
                    else:
                        model_te = 'FAIL'
                        sheet['D143'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D148'] = test['result']
                    sheet['E148'] = test['note']
                    if sheet['D148'].value == 'PASS':
                        sheet['D148'].font = greenFont
                    else:
                        model_te = 'FAIL'
                        sheet['D148'].font = redFont

                if test['testInfo'] == '添加样品':
                    sheet['D153'] = test['result']
                    sheet['E153'] = test['note']
                    if sheet['D153'].value == 'PASS':
                        sheet['D153'].font = greenFont
                    else:
                        model_te = 'FAIL'
                        sheet['D153'].font = redFont

            # 产品-PMC
            product_pmc = 'PASS'
            for test in report['product_pmc']:
                if test['testInfo'] == '个人资料':
                    sheet['D156'] = test['result']
                    sheet['E156'] = test['note']
                    if sheet['D156'].value == 'PASS':
                        sheet['D156'].font = greenFont
                    else:
                        product_pmc = 'FAIL'
                        sheet['D156'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D161'] = test['result']
                    sheet['E161'] = test['note']
                    if sheet['D161'].value == 'PASS':
                        sheet['D161'].font = greenFont
                    else:
                        product_pmc = 'FAIL'
                        sheet['D161'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D168'] = test['result']
                    sheet['E168'] = test['note']
                    if sheet['D168'].value == 'PASS':
                        sheet['D168'].font = greenFont
                    else:
                        product_pmc = 'FAIL'
                        sheet['D168'].font = redFont

                if test['testInfo'] == '创建订单':
                    sheet['D173'] = test['result']
                    sheet['E173'] = test['note']
                    if sheet['D173'].value == 'PASS':
                        sheet['D173'].font = greenFont
                    else:
                        product_pmc = 'FAIL'
                        sheet['D173'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D177'] = test['result']
                    sheet['E177'] = test['note']
                    if sheet['D177'].value == 'PASS':
                        sheet['D177'].font = greenFont
                    else:
                        product_pmc = 'FAIL'
                        sheet['D177'].font = redFont

            # 项目-PMC
            model_pmc = 'PASS'
            for test in report['model_pmc']:
                if test['testInfo'] == '个人资料':
                    sheet['D182'] = test['result']
                    sheet['E182'] = test['note']
                    if sheet['D182'].value == 'PASS':
                        sheet['D182'].font = greenFont
                    else:
                        model_pmc = 'FAIL'
                        sheet['D182'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D187'] = test['result']
                    sheet['E187'] = test['note']
                    if sheet['D187'].value == 'PASS':
                        sheet['D187'].font = greenFont
                    else:
                        model_pmc = 'FAIL'
                        sheet['D187'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D194'] = test['result']
                    sheet['E194'] = test['note']
                    if sheet['D194'].value == 'PASS':
                        sheet['D194'].font = greenFont
                    else:
                        model_pmc = 'FAIL'
                        sheet['D194'].font = redFont

                if test['testInfo'] == '创建订单':
                    sheet['D199'] = test['result']
                    sheet['E199'] = test['note']
                    if sheet['D199'].value == 'PASS':
                        sheet['D199'].font = greenFont
                    else:
                        model_pmc = 'FAIL'
                        sheet['D199'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D203'] = test['result']
                    sheet['E203'] = test['note']
                    if sheet['D203'].value == 'PASS':
                        sheet['D203'].font = greenFont
                    else:
                        model_pmc = 'FAIL'
                        sheet['D203'].font = redFont

            # 产品-产线工程师
            product_pe = 'PASS'
            for test in report['product_pe']:
                if test['testInfo'] == '个人资料':
                    sheet['D208'] = test['result']
                    sheet['E208'] = test['note']
                    if sheet['D208'].value == 'PASS':
                        sheet['D208'].font = greenFont
                    else:
                        product_pe = 'FAIL'
                        sheet['D208'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D213'] = test['result']
                    sheet['E213'] = test['note']
                    if sheet['D213'].value == 'PASS':
                        sheet['D213'].font = greenFont
                    else:
                        product_pe = 'FAIL'
                        sheet['D213'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D220'] = test['result']
                    sheet['E220'] = test['note']
                    if sheet['D220'].value == 'PASS':
                        sheet['D220'].font = greenFont
                    else:
                        product_pe = 'FAIL'
                        sheet['D220'].font = redFont

            # 项目-产线工程师
            model_pe = 'PASS'
            for test in report['model_pe']:
                if test['testInfo'] == '个人资料':
                    sheet['D225'] = test['result']
                    sheet['E225'] = test['note']
                    if sheet['D225'].value == 'PASS':
                        sheet['D225'].font = greenFont
                    else:
                        model_pe = 'FAIL'
                        sheet['D225'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D230'] = test['result']
                    sheet['E230'] = test['note']
                    if sheet['D230'].value == 'PASS':
                        sheet['D230'].font = greenFont
                    else:
                        model_pe = 'FAIL'
                        sheet['D230'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D237'] = test['result']
                    sheet['E237'] = test['note']
                    if sheet['D237'].value == 'PASS':
                        sheet['D237'].font = greenFont
                    else:
                        model_pe = 'FAIL'
                        sheet['D237'].font = redFont

            # 产品-项目工程师
            product_pj = 'PASS'
            for test in report['product_pj']:
                if test['testInfo'] == '个人资料':
                    sheet['D242'] = test['result']
                    sheet['E242'] = test['note']
                    if sheet['D242'].value == 'PASS':
                        sheet['D242'].font = greenFont
                    else:
                        product_pj = 'FAIL'
                        sheet['D242'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D247'] = test['result']
                    sheet['E247'] = test['note']
                    if sheet['D247'].value == 'PASS':
                        sheet['D247'].font = greenFont
                    else:
                        product_pj = 'FAIL'
                        sheet['D247'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D254'] = test['result']
                    sheet['E254'] = test['note']
                    if sheet['D254'].value == 'PASS':
                        sheet['D254'].font = greenFont
                    else:
                        product_pj = 'FAIL'
                        sheet['D254'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D259'] = test['result']
                    sheet['E259'] = test['note']
                    if sheet['D259'].value == 'PASS':
                        sheet['D259'].font = greenFont
                    else:
                        product_pj = 'FAIL'
                        sheet['D259'].font = redFont

            # 项目-项目工程师
            model_pj = 'PASS'
            for test in report['model_pj']:
                if test['testInfo'] == '个人资料':
                    sheet['D263'] = test['result']
                    sheet['E263'] = test['note']
                    if sheet['D263'].value == 'PASS':
                        sheet['D263'].font = greenFont
                    else:
                        model_pj = 'FAIL'
                        sheet['D263'].font = redFont

                if test['testInfo'] == '我的群组':
                    sheet['D268'] = test['result']
                    sheet['E268'] = test['note']
                    if sheet['D268'].value == 'PASS':
                        sheet['D268'].font = greenFont
                    else:
                        model_pj = 'FAIL'
                        sheet['D268'].font = redFont

                if test['testInfo'] == '产品列表':
                    sheet['D275'] = test['result']
                    sheet['E275'] = test['note']
                    if sheet['D275'].value == 'PASS':
                        sheet['D275'].font = greenFont
                    else:
                        model_pj = 'FAIL'
                        sheet['D275'].font = redFont

                if test['testInfo'] == '订单列表':
                    sheet['D280'] = test['result']
                    sheet['E280'] = test['note']
                    if sheet['D280'].value == 'PASS':
                        sheet['D280'].font = greenFont
                    else:
                        model_pj = 'FAIL'
                        sheet['D280'].font = redFont

            # 功能测试
            sheet = wb.get_sheet_by_name('功能测试')
            # 收集生产日志文件
            collectLogFile = 'PASS'
            for test in report['collectLogFile']:
                if test['testInfo'] == '单台测试PC':
                    sheet['H5'] = test['result']
                    sheet['I5'] = test['note']
                    if sheet['H5'].value == 'PASS':
                        sheet['H5'].font = greenFont
                    else:
                        collectLogFile = 'FAIL'
                        sheet['H5'].font = redFont

                if test['testInfo'] == '多台测试PC':
                    sheet['H9'] = test['result']
                    sheet['I9'] = test['note']
                    print
                    if sheet['H9'].value == 'PASS':
                        sheet['H9'].font = greenFont
                    else:
                        collectLogFile = 'FAIL'
                        sheet['H9'].font = redFont

                if test['testInfo'] == '测试完立即关闭MPTool':
                    sheet['H10'] = test['result']
                    sheet['I10'] = test['note']
                    if sheet['H10'].value == 'PASS':
                        sheet['H10'].font = greenFont
                    else:
                        collectLogFile = 'FAIL'
                        sheet['H10'].font = redFont

                if test['testInfo'] == '断网测试':
                    sheet['H11'] = test['result']
                    sheet['I11'] = test['note']
                    if sheet['H11'].value == 'PASS':
                        sheet['H11'].font = greenFont
                    else:
                        collectLogFile = 'FAIL'
                        sheet['H11'].font = redFont

            # 收集生产记录功能
            collectLogRecord = 'PASS'
            for test in report['collectLogRecord']:
                if test['testInfo'] == '单台测试PC':
                    sheet['H12'] = test['result']
                    sheet['I12'] = test['note']
                    if sheet['H12'].value == 'PASS':
                        sheet['H12'].font = greenFont
                    else:
                        collectLogRecord = 'FAIL'
                        sheet['H12'].font = redFont

                if test['testInfo'] == '多台测试PC':
                    sheet['H16'] = test['result']
                    sheet['I16'] = test['note']
                    print
                    if sheet['H16'].value == 'PASS':
                        sheet['H16'].font = greenFont
                    else:
                        collectLogRecord = 'FAIL'
                        sheet['H16'].font = redFont

                if test['testInfo'] == '测试完立即关闭MPTool':
                    sheet['H17'] = test['result']
                    sheet['I17'] = test['note']
                    if sheet['H17'].value == 'PASS':
                        sheet['H17'].font = greenFont
                    else:
                        collectLogRecord = 'FAIL'
                        sheet['H17'].font = redFont

                if test['testInfo'] == '断网测试':
                    sheet['H18'] = test['result']
                    sheet['I18'] = test['note']
                    if sheet['H18'].value == 'PASS':
                        sheet['H18'].font = greenFont
                    else:
                        collectLogRecord = 'FAIL'
                        sheet['H18'].font = redFont

            # 离线Key工具测试
            offlineTest = 'PASS'
            for test in report['offlineTest']:
                if test['testInfo'] == '登陆、查看订单(离线Key授权工具使用)':
                    sheet['H19'] = test['result']
                    sheet['I19'] = test['note']
                    if sheet['H19'].value == 'PASS':
                        sheet['H19'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H19'].font = redFont

                if test['testInfo'] == '查找设备(离线Key授权工具使用)':
                    sheet['H20'] = test['result']
                    sheet['I20'] = test['note']
                    print
                    if sheet['H20'].value == 'PASS':
                        sheet['H20'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H20'].font = redFont

                if test['testInfo'] == '查看订单权限(离线Key授权工具使用)':
                    sheet['H21'] = test['result']
                    sheet['I21'] = test['note']
                    if sheet['H21'].value == 'PASS':
                        sheet['H21'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H21'].font = redFont

                if test['testInfo'] == '授权(离线Key授权工具使用)':
                    sheet['H22'] = test['result']
                    sheet['I22'] = test['note']
                    if sheet['H22'].value == 'PASS':
                        sheet['H22'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H22'].font = redFont

                if test['testInfo'] == '正常使用':
                    sheet['H23'] = test['result']
                    sheet['I23'] = test['note']
                    if sheet['H23'].value == 'PASS':
                        sheet['H23'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H23'].font = redFont

                if test['testInfo'] == 'Ukey没授权数量':
                    sheet['H24'] = test['result']
                    sheet['I24'] = test['note']
                    print
                    if sheet['H24'].value == 'PASS':
                        sheet['H24'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H24'].font = redFont

                if test['testInfo'] == 'Ukey授权订单和MPTool配置订单不一致':
                    sheet['H25'] = test['result']
                    sheet['I25'] = test['note']
                    if sheet['H25'].value == 'PASS':
                        sheet['H25'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H25'].font = redFont

                if test['testInfo'] == '离线在线授权切换':
                    sheet['H26'] = test['result']
                    sheet['I26'] = test['note']
                    if sheet['H26'].value == 'PASS':
                        sheet['H26'].font = greenFont
                    else:
                        offlineTest = 'FAIL'
                        sheet['H26'].font = redFont

            # 在线授权测试
            onlineTest = 'PASS'
            for test in report['onlineTest']:
                if test['testInfo'] == '单台测试PC':
                    sheet['H27'] = test['result']
                    sheet['I27'] = test['note']
                    if sheet['H27'].value == 'PASS':
                        sheet['H27'].font = greenFont
                    else:
                        onlineTest = 'FAIL'
                        sheet['H27'].font = redFont

                if test['testInfo'] == '多台测试PC':
                    sheet['H28'] = test['result']
                    sheet['I28'] = test['note']
                    print
                    if sheet['H28'].value == 'PASS':
                        sheet['H28'].font = greenFont
                    else:
                        onlineTest = 'FAIL'
                        sheet['H28'].font = redFont

            # 中转测试
            midwareTest = ''
            if collectLogFile == 'PASS' and collectLogRecord == 'PASS'\
                    and offlineTest == 'PASS' and onlineTest == 'PASS':
                midwareTest = 'PASS'
            else:
                midwareTest = 'FAIL'

            # 压力测试
            pressureTest = 'PASS'
            sheet = wb.get_sheet_by_name('压力测试')
            for test in report['pressureTest']:
                if test['testInfo'] == '获取授权API压力测试':
                    sheet['H5'] = test['result']
                    sheet['I5'] = test['note']
                    if sheet['H5'].value == 'PASS':
                        sheet['H5'].font = greenFont
                    else:
                        pressureTest = 'FAIL'
                        sheet['H5'].font = redFont

            # list页面表格
            sheet = wb.get_sheet_by_name('list')
            sheet['C3'] = report['version']['量产云平台']
            sheet['C4'] = report['version']['电流板']
            sheet['M3'] = report['version']['MPTool']
            sheet['J4'] = report['version']['离线Key授权工具']
            sheet['J3'] = report['version']['syncAgent']
            sheet['C5'] = report['version']['transferStation']
            sheet['C9'] = report['releaseNote']
            sheet['C10'] = report['result']

            # 测试结果
            # 产品-产品经理
            sheet['E12'] = product_pm
            if product_pm == 'PASS':
                sheet['E12'].font = greenFont
            else:
                sheet['E12'].font = redFont
            # 项目-产品经理
            sheet['E13'] = model_pm
            if model_pm == 'PASS':
                sheet['E13'].font = greenFont
            else:
                sheet['E13'].font = redFont
            # 产品-研发工程师
            sheet['E14'] = product_rd
            if product_rd == 'PASS':
                sheet['E14'].font = greenFont
            else:
                sheet['E14'].font = redFont
            # 项目-研发工程师
            sheet['E15'] = model_rd
            if model_rd == 'PASS':
                sheet['E15'].font = greenFont
            else:
                sheet['E15'].font = redFont
            # 产品-测试工程师
            sheet['E16'] = product_te
            if product_te == 'PASS':
                sheet['E16'].font = greenFont
            else:
                sheet['E16'].font = redFont
            # 项目-测试工程师
            sheet['E17'] = model_te
            if model_te == 'PASS':
                sheet['E17'].font = greenFont
            else:
                sheet['E17'].font = redFont
            # 产品-PMC
            sheet['E18'] = product_pmc
            if product_pmc == 'PASS':
                sheet['E18'].font = greenFont
            else:
                sheet['E18'].font = redFont
            # 项目-PMC
            sheet['E19'] = model_pmc
            if model_pmc == 'PASS':
                sheet['E19'].font = greenFont
            else:
                sheet['E19'].font = redFont
            # 产品-产线工程师
            sheet['E20'] = product_pe
            if product_pe == 'PASS':
                sheet['E20'].font = greenFont
            else:
                sheet['E20'].font = redFont
            # 项目-产线工程师
            sheet['E21'] = model_pe
            if model_pe == 'PASS':
                sheet['E21'].font = greenFont
            else:
                sheet['E21'].font = redFont
            # 产品-项目工程师
            sheet['E22'] = product_pj
            if product_pj == 'PASS':
                sheet['E22'].font = greenFont
            else:
                sheet['E22'].font = redFont
            # 产品-项目工程师
            sheet['E23'] = model_pj
            if model_pj == 'PASS':
                sheet['E23'].font = greenFont
            else:
                sheet['E23'].font = redFont
            # 收集生产日志文件
            sheet['E23'] = collectLogFile
            if collectLogFile == 'PASS':
                sheet['E23'].font = greenFont
            else:
                sheet['E23'].font = redFont
            # 收集生产记录功能
            sheet['E24'] = collectLogRecord
            if collectLogRecord == 'PASS':
                sheet['E24'].font = greenFont
            else:
                sheet['E24'].font = redFont
            # 离线授权
            sheet['E25'] = offlineTest
            if offlineTest == 'PASS':
                sheet['E25'].font = greenFont
            else:
                sheet['E25'].font = redFont
            # 在线授权
            sheet['E26'] = onlineTest
            if onlineTest == 'PASS':
                sheet['E26'].font = greenFont
            else:
                sheet['E26'].font = redFont
            # 中转软件
            sheet['E27'] = midwareTest
            if midwareTest == 'PASS':
                sheet['E27'].font = greenFont
            else:
                sheet['E27'].font = redFont
            # 压力测试
            sheet['E28'] = pressureTest
            if pressureTest == 'PASS':
                sheet['E28'].font = greenFont
            else:
                sheet['E28'].font = redFont

            wb.save('../log/reports/' + fileName)
            wb.close()
        except Exception as e:
            res['errcode'] = 1
            res['errmsg'] = str(e)

        return Response(res)

    def delete(self, request, *args, **kwargs):
        res = {'errcode': 0, 'errmsg': 'ok'}
        fileName = request.GET.get('fileName')
        try:
            os.remove('../log/reports/' + fileName)
        except Exception as e:
            res['errcode'] = 1
            res['errmsg'] = str(e)

        return Response(res)
