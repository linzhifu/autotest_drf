from rest_framework import serializers
from user.models import Project, WebManager, WebCase, ApiManager, ApiCase, \
    TestType, CheckWebCase, Report
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User, ContentType


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
    # username = serializers.SerializerMethodField(read_only=True)

    # def get_username(self, row):
    #     user = User.objects.filter(id=row.user.id).first()
    #     return user.username

    class Meta:
        model = Project
        fields = '__all__'
        # fields = ['id', 'proname', 'prodes', 'user', 'username']


# 测试报告记录
class ReportSerializer(serializers.ModelSerializer):

    proname = serializers.SerializerMethodField(read_only=True)
    username = serializers.SerializerMethodField(read_only=True)

    def get_proname(self, row):
        prject = Project.objects.filter(id=row.project.id).first()
        return prject.proname

    def get_username(self, row):
        user = User.objects.filter(id=row.user.id).first()
        return user.username

    class Meta:
        model = Report
        fields = ['id', 'project', 'proname', 'user', 'username', 'update_time', 'version', 'releaseNote', 'allInfo']
        # depth = 1


# 前端测试管理
class WebManagerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    proname = serializers.SerializerMethodField(read_only=True)
    contenttype = serializers.SerializerMethodField(read_only=True)

    def get_username(self, row):
        user = User.objects.filter(id=row.user.id).first()
        return user.username

    def get_proname(self, row):
        project = Project.objects.filter(id=row.project.id).first()
        return project.proname

    def get_contenttype(self, row):
        contenttype = ContentType.objects.get_for_model(WebManager)
        return contenttype.id

    class Meta:
        model = WebManager
        fields = [
            'id', 'webname', 'webdes', 'user', 'username', 'project',
            'proname', 'weburl', 'result', 'update_time', 'contenttype'
        ]


# 前端测试数据验证
class CheckWebCaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = CheckWebCase
        fields = '__all__'


# 前端测试案例
class WebCaseSerializer(serializers.ModelSerializer):
    # weburl = serializers.SerializerMethodField(read_only=True)
    # webparam = serializers.CharField(allow_null=True, allow_blank=True)

    # def get_weburl(self, row):
    #     webManager = WebManager.objects.filter(id=row.webManager.id).first()
    #     return webManager.weburl

    class Meta:
        model = WebCase
        fields = '__all__'
        # fields = [
        #     'id', 'webname', 'webcss', 'weboprate', 'webparam', 'create_time',
        #     'update_time', 'index', 'user'
        # ]
        # extra_kwargs = {'webparam': {'allow_null': True}}


# 后端测试管理
class ApiManagerSerializer(serializers.ModelSerializer):
    username = serializers.SerializerMethodField(read_only=True)
    proname = serializers.SerializerMethodField(read_only=True)
    contenttype = serializers.SerializerMethodField(read_only=True)

    def get_username(self, row):
        user = User.objects.filter(id=row.user.id).first()
        return user.username

    def get_proname(self, row):
        project = Project.objects.filter(id=row.project.id).first()
        return project.proname

    def get_contenttype(self, row):
        contenttype = ContentType.objects.get_for_model(ApiManager)
        return contenttype.id

    class Meta:
        model = ApiManager
        fields = [
            'id', 'apiname', 'apides', 'apiurl', 'user', 'username', 'project',
            'proname', 'contenttype', 'result', 'update_time'
        ]


# 后端测试案例
class ApiCaseSerializer(serializers.ModelSerializer):
    # apiManagerName = serializers.SerializerMethodField(read_only=True)
    # apiManagerUrl = serializers.SerializerMethodField(read_only=True)

    # def get_apiManagerName(self, row):
    #     apiManager = ApiManager.objects.filter(id=row.apiManager.id).first()
    #     return apiManager.apiname

    # def get_apiManagerUrl(self, row):
    #     apiManager = ApiManager.objects.filter(id=row.apiManager.id).first()
    #     return apiManager.apiurl

    class Meta:
        model = ApiCase
        fields = '__all__'
        # fields = [
        #     'id', 'apiname', 'apimethod', 'apiurl', 'apiparam', 'apijson',
        #     'apiresponse', 'update_time', 'create_time', 'index',
        #     'apiManagerName', 'apiManagerUrl', 'apiManager', 'user'
        # ]


# 测试分类
class TestTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TestType
        fields = '__all__'
