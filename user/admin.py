from django.contrib import admin
from user.models import LoginRecord, Project, ApiManager, ApiCase, WebManager, \
    WebCase, TestType, CheckWebCase, TestRecord


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
        'proname',
        'prodes',
        'user',
    ]


@admin.register(ApiManager)
class ApiManagerAdmin(admin.ModelAdmin):
    model = Project

    list_display = ['apiname', 'apides', 'apiurl', 'user', 'project']


@admin.register(ApiCase)
class ApiCaseAdmin(admin.ModelAdmin):
    model = ApiCase

    list_display = [
        'apiname', 'apimethod', 'apiurl', 'apiManager', 'apistatus',
        'create_time', 'update_time', 'index', 'user'
    ]


@admin.register(WebManager)
class WebManagerAdmin(admin.ModelAdmin):
    model = WebManager

    list_display = [
        'webname', 'webdes', 'weburl', 'user', 'project', 'result',
        'update_time'
    ]


@admin.register(CheckWebCase)
class CheckWebCaseAdmin(admin.ModelAdmin):
    model = CheckWebCase

    list_display = [
        'webname', 'testType', 'create_time', 'update_time', 'index', 'user'
    ]


@admin.register(WebCase)
class WebCaseAdmin(admin.ModelAdmin):
    model = WebCase

    list_display = [
        'webname', 'testType', 'create_time', 'update_time', 'index', 'user'
    ]


@admin.register(TestType)
class TestTypeAdmin(admin.ModelAdmin):
    model = TestType

    list_display = ('typename', 'typedes', 'content_object', 'index', 'user',
                    'result', 'update_time')


@admin.register(TestRecord)
class TestRecordAdmin(admin.ModelAdmin):
    model = TestRecord

    list_display = [
        'content_object', 'test_all', 'test_pass', 'test_fail', 'test_time'
    ]
