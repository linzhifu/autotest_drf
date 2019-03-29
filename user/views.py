from django.core.mail import EmailMessage
from django.contrib import auth
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from django.contrib.auth.hashers import make_password
from django_filters.rest_framework import DjangoFilterBackend
from user.models import LoginRecord, Project, WebManager, ApiManager, ApiCase, WebCase
from user.serializer import ProjectSerializer, UserSerializer, WebManagerSerializer, ApiManagerSerializer, ApiCaseSerializer, WebCaseSerializer
import string
import random
from user.tests import webCase


# Create your views here.
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


# 前端测试管理
class WebManagerView(ModelViewSet):
    queryset = WebManager.objects.all()
    serializer_class = WebManagerSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('project', )


# 前端测试案例
class WebCaseView(ModelViewSet):
    queryset = WebCase.objects.all()
    serializer_class = WebCaseSerializer
    filter_backends = (DjangoFilterBackend, )
    filter_fields = ('webManager', )


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
    filter_fields = ('apiManager', )


# 前端测试案例测试
class WebTest(APIView):
    def post(self, request, *args, **kwargs):
        data = {'errcode': 0, 'errmsg': 'ok'}
        body_data = request.data
        url = request.GET.get('url')
        print(body_data)
        webCase(url, body_data)
        return Response(data)
