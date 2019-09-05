from django.contrib import admin
from user.models import LoginRecord, Project, ApiManager, ApiCase, WebManager, \
    WebCase, TestType, CheckWebCase, TestRecord, Report, ApiVar, AppManager, AppCase, \
    CheckAppCase, AppSrcCase


# Register your models here.
@admin.register(LoginRecord)
class LoginRecordAdmin(admin.ModelAdmin):
    model = LoginRecord

    list_display = [
        'user',
        'login_time',
    ]


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    model = Project

    list_display = [
        'id', 'proname', 'prodes', 'user', 'webresult', 'apiresult',
        'apiresult', 'update_time'
    ]


@admin.register(ApiManager)
class ApiManagerAdmin(admin.ModelAdmin):
    model = ApiManager

    list_display = [
        'id', 'apiname', 'apides', 'apiurl', 'user', 'project', 'result',
        'update_time'
    ]


@admin.register(ApiCase)
class ApiCaseAdmin(admin.ModelAdmin):
    model = ApiCase

    list_display = [
        'id', 'apiname', 'apimethod', 'apiurl', 'testType', 'result',
        'create_time', 'update_time', 'index', 'user'
    ]


@admin.register(ApiVar)
class ApiVarAdmin(admin.ModelAdmin):
    model = ApiVar

    list_display = ['id', 'apiManager', 'varname', 'varvalue']


@admin.register(WebManager)
class WebManagerAdmin(admin.ModelAdmin):
    model = WebManager

    list_display = [
        'id', 'webname', 'webdes', 'weburl', 'user', 'project', 'result',
        'update_time'
    ]


@admin.register(CheckWebCase)
class CheckWebCaseAdmin(admin.ModelAdmin):
    model = CheckWebCase

    list_display = [
        'id', 'webname', 'testType', 'create_time', 'update_time', 'index',
        'user'
    ]


@admin.register(WebCase)
class WebCaseAdmin(admin.ModelAdmin):
    model = WebCase

    list_display = [
        'id', 'webname', 'testType', 'create_time', 'update_time', 'index',
        'user'
    ]


@admin.register(AppManager)
class AppManagerAdmin(admin.ModelAdmin):
    model = AppManager

    list_display = [
        'id', 'appname', 'appdes', 'desired_caps', 'user', 'project', 'result',
        'update_time'
    ]


@admin.register(AppCase)
class AppCaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'appname', 'testType', 'create_time', 'update_time', 'index',
        'user'
    ]


@admin.register(CheckAppCase)
class CheckAppCaseAdmin(admin.ModelAdmin):

    list_display = [
        'id', 'appname', 'testType', 'create_time', 'update_time', 'index',
        'user'
    ]


@admin.register(AppSrcCase)
class AppSrcCaseAdmin(admin.ModelAdmin):
    list_display = [
        'id', 'appname', 'appdes', 'srcname', 'project', 'update_time', 'index',
        'user', 'result'
    ]


@admin.register(TestType)
class TestTypeAdmin(admin.ModelAdmin):
    model = TestType

    list_display = ('id', 'typename', 'typedes', 'content_object', 'index',
                    'user', 'result', 'update_time')


@admin.register(TestRecord)
class TestRecordAdmin(admin.ModelAdmin):
    model = TestRecord

    list_display = [
        'content_object', 'test_all', 'test_pass', 'test_fail', 'test_time'
    ]


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    model = Report
    list_display = ['project', 'user', 'update_time', 'version', 'releaseNote']
