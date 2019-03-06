from django.contrib.auth.hashers import make_password
from rest_framework import serializers
from user.models import UserInfo


# 关联模型
class UserInfoSerializer(serializers.ModelSerializer):
    # write_only只写模式，序列化验证后不会通过API返回
    # read_only只读模式，序列化验证后不会写入数据库，只做返回用
    captcha = serializers.CharField(write_only=True)
    serializers.SerializerMethodField

    class Meta:
        model = UserInfo
        fields = [
            'id', 'username', 'password', 'email', 'created_time', 'captcha'
        ]
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # 如果传入password,需要加密
        password = make_password(value)
        return password

    def validate(self, data):
        # 数据验证完后，删除验证码
        if data.get('captcha'):
            data.pop('captcha')
        return data
