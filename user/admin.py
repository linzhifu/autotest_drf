from django.contrib import admin
from user.models import LoginRecord, Project, ApiManager, ApiCase, WebManager


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


@admin.register(ApiCase)
class ApiCaseAdmin(admin.ModelAdmin):
    model = ApiCase


@admin.register(WebManager)
class WebManagerAdmin(admin.ModelAdmin):
    model = WebManager
