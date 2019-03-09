from rest_framework import serializers
from user.models import Project
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# django自带USER
# 用户信息
class UserSerializer(serializers.ModelSerializer):
    # write_only只写模式，序列化验证后不会通过API返回
    # read_only只读模式，序列化验证后不会写入数据库，只做返回用

    class Meta:
        model = User
        fields = ['username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # 如果传入password,需要加密
        password = make_password(value)
        return password


# 项目
class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
