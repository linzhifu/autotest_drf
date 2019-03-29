from rest_framework.authentication import BaseAuthentication
from rest_framework.authtoken.models import Token
from django.core.cache import cache
from django.contrib.auth.models import User


# 自定义验证
class TokenAuthentication(BaseAuthentication):
    # 通过token认证
    # 通过request.user=user对象  request.auth=user.token
    # 不通过request.user=None  request.auth=None
    # 提供给后续权限认证
    def authenticate(self, request):
        userId = request.GET.get('userId')
        token = request.GET.get('token')
        authen_user = (None, None)
        if userId and token:
            # 验证token
            user = User.objects.filter(id=userId).first()
            token_user = Token.objects.filter(user=user).first()
            if token == token_user.key:
                # token一致，验证token是否在有效时间内
                if cache.get(userId):
                    authen_user = (user, token)
        return authen_user
