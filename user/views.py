from django.core.mail import EmailMessage
from django.contrib import auth
from django.contrib.auth.models import User
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from user.models import LoginRecord, Project
from user.serializer import ProjectSerializer, UserSerializer
import string
import random


# Create your views here.
# 用户信息
class UserView(ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# 用户登陆
class LoginView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        data = {'errcode': 0, 'errmsg': 'ok'}
        # 邮箱登陆
        body_data = request.data
        username = body_data.get('username')
        password = body_data.get('password')
        user = auth.authenticate(username=username, password=password)
        if not user:
            data['errcode'] = 101
            data['errmsg'] = '用户名或密码错误'
        elif user.is_active:
            # 验证通过
            auth.login(request, user)
        else:
            data['errcode'] = 102
            data['errmsg'] = '用户已被禁止登陆'
        response = Response(data)
        # 添加登陆记录，并加入cookie记录
        if data['errcode'] == 0:
            if not request.COOKIES.get(username):
                response.set_cookie(username, True, max_age=60 * 5)
                LoginRecord.objects.create(user=user)
        return response


# 用户注销
class LogoutView(APIView):
    permission_classes = []

    def get(self, request, *args, **kwargs):
        data = {'errcode': 0, 'errmsg': 'ok'}
        auth.logout(request)
        return Response(data)


# 获取验证码
class CaptchaView(APIView):
    authentication_classes = []
    permission_classes = []

    # 获取验证码：
    def get(self, request, *args, **kwargs):
        data = {'errcode': 0, 'errmsg': 'ok'}
        email = request.GET.get('email', '')

        # 获取email，因为cookie中的key不能包含@，所以这里去除@
        email = request.GET.get('email', '')
        key = email.split('@')[0] + email.split('@')[1]

        # 判断验证码是否已经存在cookie中
        if request.COOKIES.get(key, ''):
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
                html_content = "<p><strong>验证码：%s</strong></p>\
                    <p>This is an <font size=3 color='green'>\
                    <strong>important</strong></font> message.</p>" % (code)
                msg = EmailMessage(
                    'LONGSYS自动化测试平台-%s' % (code),
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

        response = Response(data=data)
        # 判断是否发送成功，加入缓存，有效期3min
        if not data.get('errcode'):
            response.set_cookie(key, code, max_age=60 * 5)
        return response


# 项目
class ProjectView(ModelViewSet):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
