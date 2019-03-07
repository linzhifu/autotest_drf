from django.core.mail import EmailMessage
from django.contrib.auth.hashers import check_password
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from user.permission import UserPeimission, EditPeimission
from rest_framework.response import Response
from user.models import UserInfo, LoginRecord, Project, Pemission
from user.serializer import UserInfoSerializer, ProjectSerializer, PermissionSerializer
import string
import random
import hashlib
import time


# Create your views here.
# 添加权限
class PermissionView(ModelViewSet):
    queryset = Pemission.objects.all()
    serializer_class = PermissionSerializer


# 用户信息
class UserView(ModelViewSet):
    permission_classes = [
        UserPeimission,
    ]
    queryset = UserInfo.objects.all()
    serializer_class = UserInfoSerializer

    # # 获取用户信息
    # def get(self, request, *args, **kwargs):
    #     # 返回信息格式
    #     data = {'errcode': 0, 'errmsg': 'ok'}
    #     users = UserInfo.objects.all()
    #     pg = CursorPagination()
    #     pg_users = pg.paginate_queryset(users, request, view=self)
    #     ser = UserInfoSerializer(
    #         instance=pg_users, many=True, context={'request': request})
    #     data['data'] = ser.data
    #     response = pg.get_paginated_response(data)
    #     # safe=False 参数不仅仅可以为字典，也可以为列表
    #     # response = JsonResponse(ser.data, safe=False)

    #     return response

    # # 创建新用户
    # def post(self, request, *args, **kwargs):
    #     # 定制(email=admin,token=admin)
    #     # 返回信息格式
    #     data = {'errcode': 0, 'errmsg': 'ok'}

    #     # 获取post数据，已通过解析器转换为json格式
    #     body_data = request.data

    #     # 通过邮箱判断用户是否已存在
    #     email = body_data.get('email')
    #     if UserInfo.objects.filter(email=email).first():
    #         # 邮箱已存在，返回报错
    #         data['errcode'] = 101
    #         data['errmsg'] = '用户邮箱已存在'

    #     else:
    #         # 序列化数据，并做验证
    #         # 默认情况下，序列化程序必须传递所有必填字段的值，
    #         # 否则会引发验证错误。您可以使用该partial参数以允许部分更新
    #         ser_user = UserInfoSerializer(
    #             data=body_data, many=False, partial=True)
    #         if ser_user.is_valid():
    #             ser_user.save()
    #         else:
    #             # 验证不通过，返回错误提示
    #             data['errcode'] = 102
    #             data['errmsg'] = ser_user.errors

    #     return Response(data)

    # # 更新用户信息
    # def patch(self, request, *args, **kwargs):
    #     # 返回信息格式
    #     data = {'errcode': 0, 'errmsg': 'ok'}

    #     # 获取post数据，已通过解析器转换为json格式
    #     body_data = request.data

    #     # 通过邮箱判断用户是否存在
    #     email = body_data.get('email')
    #     key = email.split('@')[0] + email.split('@')[1]
    #     captcha = body_data.get('captcha')
    #     user_obj = UserInfo.objects.filter(email=email).first()
    #     # 验证对象权限
    #     self.check_object_permissions(request, user_obj)
    #     if not user_obj:
    #         # 用户不存在，返回报错
    #         data['errcode'] = 103
    #         data['errmsg'] = '用户不存在，无法更新'

    #     elif not captcha:
    #         # 验证码为空
    #         data['errcode'] = 104
    #         data['errmsg'] = '验证码不能为空'

    #     elif captcha and captcha.lower() != request.COOKIES.get(key):
    #         data['errcode'] = 105
    #         data['errmsg'] = '验证码错误'

    #     else:
    #         # 序列化数据，并做验证
    #         # 默认情况下，序列化程序必须传递所有必填字段的值，
    #         # 否则会引发验证错误。您可以使用该partial参数以允许部分更新
    #         ser_user = UserInfoSerializer(
    #             instance=user_obj, data=body_data, many=False, partial=True)
    #         if ser_user.is_valid():
    #             ser_user.save()
    #         else:
    #             # 验证不通过，返回错误提示
    #             data['errcode'] = 106
    #             data['errmsg'] = ser_user.errors

    #     return Response(data)

    # # 删除用户
    # def delete(self, request, *args, **kwargs):
    #     # 返回信息格式
    #     data = {'errcode': 0, 'errmsg': 'ok'}

    #     # 获取post数据，已通过解析器转换为json格式
    #     body_data = request.data

    #     # 通过邮箱判断用户是否存在
    #     email = body_data.get('email')
    #     user_obj = UserInfo.objects.filter(email=email).first()
    #     # 验证对象权限
    #     self.check_object_permissions(request, user_obj)
    #     if not user_obj:
    #         # 用户不存在，返回报错
    #         data['errcode'] = 105
    #         data['errmsg'] = '用户不存在，无法删除'

    #     else:
    #         user_obj.delete()

    #     return Response(data)


# 用户登陆
class LoginView(APIView):
    authentication_classes = []

    def post(self, request, *args, **kwargs):
        data = {'errcode': '0', 'errmsg': 'ok'}
        # 邮箱登陆
        body_data = request.data
        email = body_data.get('email')
        key = email.split('@')[0] + email.split('@')[1]
        password = body_data.get('password')
        captcha = body_data.get('captcha')
        user_obj = UserInfo.objects.filter(email=email).first()
        # 判断用户是否存在
        if not user_obj:
            data['errcode'] = 201
            data['errmsg'] = '用户不存在'
        # 判断密码、验证码至少存在一个
        elif not password and not captcha:
            data['errcode'] = 202
            data['errmsg'] = '请输入正确的密码或验证码'
        # 如果是密码登陆，判断密码
        elif password and not check_password(password, user_obj.password):
            data['errcode'] = 203
            data['errmsg'] = '密码错误'
        elif captcha and captcha.lower() != request.COOKIES.get(key):
            data['errcode'] = 204
            data['errmsg'] = '验证码错误'
        else:
            # 生成MD5加密token(时间戳+email)，失效5min
            time_str = time.time()
            m = hashlib.md5()
            md5_str = (str(time_str) + email).encode(encoding='utf-8')
            m.update(md5_str)
            token = m.hexdigest()
            data['token'] = token
            # 序列化数据，并做验证
            # 默认情况下，序列化程序必须传递所有必填字段的值，
            # 否则会引发验证错误。您可以使用该partial参数以允许部分更新
            ser_user = UserInfoSerializer(instance=user_obj)
            # 登陆成功，返回用户信息
            data['data'] = ser_user.data
            # 添加一条登陆记录
            login_record = LoginRecord(content_object=user_obj)
            login_record.save()

        response = Response(data)
        response.set_cookie(key + 'token', data['token'], max_age=60 * 60)
        return response


# 获取验证码
class CaptchaView(APIView):
    authentication_classes = []

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
    permission_classes = [EditPeimission, ]
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
