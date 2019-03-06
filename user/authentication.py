from rest_framework.authentication import BaseAuthentication
from user.models import UserInfo

# 自定义验证


class TokenAuthentication(BaseAuthentication):
    # 通过token认证
    # 通过request.user=email  request.auth=token
    # 不通过request.user=None  request.auth=None
    # 提供给后续权限认证
    def authenticate(self, request):
        email = request.GET.get('email')
        token = request.GET.get('token')
        if token and email:
            key = email.split('@')[0] + email.split('@')[1]
            if token == request.COOKIES.get(key+'token'):
                # 赋值request.user=user对象  request.auth=token
                user = UserInfo.objects.filter(email=email).first()
                if user:
                    # 用户存在
                    return (user, user.role)
                else:
                    return (None, None)
            else:
                print(request.COOKIES)
                return (None, None)
        else:
            # from rest_framework import exceptions
            # raise exceptions.AuthenticationFailed({
            #     'errocde': 901,
            #     'errmsg': 'Token fail'
            # })
            return (None, None)