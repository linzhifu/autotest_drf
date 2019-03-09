from django.contrib import admin
from user.models import LoginRecord, Project


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

    def save_models(self, request, obj):
        obj.user = request.user
        super().save_models()
