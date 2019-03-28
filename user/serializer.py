from rest_framework import serializers
from user.models import Project, WebManager, WebCase, ApiManager, ApiCase
from django.contrib.auth.models import User
from django.contrib.auth.hashers import make_password


# django自带USER
# 用户信息
class UserSerializer(serializers.ModelSerializer):
    # write_only只写模式，序列化验证后不会通过API返回
    # read_only只读模式，序列化验证后不会写入数据库，只做返回用

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def validate_password(self, value):
        # 如果传入password,需要加密
        password = make_password(value)
        return password


# 项目
class ProjectSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)

    def get_username(self, row):
        user = User.objects.filter(id=row.user.id).first()
        return user.username

    class Meta:
        model = Project
        fields = ['id', 'proname', 'prodes', 'user', 'username']


# 前端测试管理
class WebManagerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    proname = serializers.SerializerMethodField(read_only=True)

    def get_username(self, row):
        user = User.objects.filter(id=row.user.id).first()
        return user.username

    def get_proname(self, row):
        project = Project.objects.filter(id=row.project.id).first()
        return project.proname

    class Meta:
        model = WebManager
        fields = [
            'id', 'webname', 'webdes', 'user', 'username', 'project',
            'proname', 'weburl'
        ]


# 前端测试案例
class WebCaseSerializer(serializers.ModelSerializer):
    weburl = serializers.SerializerMethodField(read_only=True)

    def get_weburl(self, row):
        webManager = WebManager.objects.filter(id=row.webManager.id).first()
        return webManager.weburl

    class Meta:
        model = WebCase
        fields = [
            'id', 'webname', 'webcss', 'weboprate', 'webparam', 'create_time',
            'update_time', 'index', 'webManager', 'weburl', 'oprateOBj'
        ]


# 后端测试管理
class ApiManagerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    proname = serializers.SerializerMethodField(read_only=True)

    def get_username(self, row):
        user = User.objects.filter(id=row.user.id).first()
        return user.username

    def get_proname(self, row):
        project = Project.objects.filter(id=row.project.id).first()
        return project.proname

    class Meta:
        model = ApiManager
        fields = [
            'id', 'apiname', 'apides', 'apiurl', 'user', 'username', 'project',
            'proname'
        ]


# 后端测试案例
class ApiCaseSerializer(serializers.ModelSerializer):
    apiManagerName = serializers.SerializerMethodField(read_only=True)
    apiManagerUrl = serializers.SerializerMethodField(read_only=True)

    def get_apiManagerName(self, row):
        apiManager = ApiManager.objects.filter(id=row.apiManager.id).first()
        return apiManager.apiname

    def get_apiManagerUrl(self, row):
        apiManager = ApiManager.objects.filter(id=row.apiManager.id).first()
        return apiManager.apiurl

    class Meta:
        model = ApiCase
        fields = [
            'id', 'apiname', 'apimethod', 'apiurl', 'apiparam', 'apijson',
            'apiresponse', 'update_time', 'create_time', 'index',
            'apiManagerName', 'apiManagerUrl', 'apiManager'
        ]
