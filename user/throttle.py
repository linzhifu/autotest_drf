from rest_framework.throttling import SimpleRateThrottle


# 设置节流（访问频率限制）
class UserThrottle(SimpleRateThrottle):
    # 全局设置关键字
    scope = 'limit'

    # 重写get_cache_key函数，返回用户IP，用于记录缓存的KEY
    def get_cache_key(self, request, view):
        return self.get_ident(request)
