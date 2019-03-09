from rest_framework.permissions import BasePermission


# 自定义权限

# 访问用户信息权限
class UserPeimission(BasePermission):
    # 权限认证失败，返回的信息
    message = {'errcode': 902, 'errmsg': '用户没有权限,请重新登录'}

    def has_permission(self, request, view):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # token认证通过后，request.user是email，可以访问view
        # token认证不通过，request.user是None，不能访问View
        # 创建新用户，不需要token认证，request.method=post
        if request.user or request.method == 'POST':
            return True

    # GenericAPIView中get_object时调用
    # 如果视图继承ApiView,只能自己在视图
    # 中调用check_object_permissions(self, request, obj)
    # 才能触发这个验证
    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # 只能自己操作自己 或者是 管理员
        return request.user == obj or obj.role


# 编辑信息权限
class EditPeimission(BasePermission):
    # 权限认证失败，返回的信息
    # message = {'errcode': 902, 'errmsg': '用户没有权限,请重新登录'}

    # def has_permission(self, request, view):
    #     """
    #     Return `True` if permission is granted, `False` otherwise.
    #     """
    #     # token认证通过后，request.user是user对象，可以访问view
    #     # token认证不通过，request.user是None，不能访问View
    #     if request.user:
    #         return True

    # GenericAPIView中get_object时调用
    # 如果视图继承ApiView,只能自己在视图
    # 中调用check_object_permissions(self, request, obj)
    # 才能触发这个验证
    def has_object_permission(self, request, view, obj):
        """
        Return `True` if permission is granted, `False` otherwise.
        """
        # 只能自己操作自己 或者超级管理员
        return request.user == obj.user or request.user.is_staff
