"""autotest_drf URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, re_path, include
from rest_framework import routers
from user import views

# django 2.0 开始 路由包括正则表达式的话，需要用re_path，否则会报错：
# ?: (2_0.W001) Your URL pattern 'api/(?P<version>[v1|v2]+)/user/'
# has a route that contains '(?P<', begins with a '^', or ends with
# a '$'. This was likely an oversight when migrating to django.urls.path().
router = routers.DefaultRouter()
router.register('user', views.UserView)
router.register('project', views.ProjectView)
router.register('webManager', views.WebManagerView)
router.register('apiManager', views.ApiManagerView)
router.register('apiCase', views.ApiCaseView)
router.register('apiVar', views.ApiVarView)
router.register('webCase', views.WebCaseView)
router.register('testType', views.TestTypeView)
router.register('checkWebCase', views.CheckWebCaseView)
router.register('report', views.ReportView)
router.register('appManager', views.AppManagerView)
router.register('appCase', views.AppCaseView)
router.register('checkAppCase', views.CheckAppCaseView)

urlpatterns = [
    path('', views.home),
    path('admin/', admin.site.urls),
    re_path(r'(?P<version>[v1|v2]+)/captcha/', views.CaptchaView.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/login/', views.LoginView.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/webCaseTest/', views.WebCaseTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/webTypeTest/', views.WebTypeTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/webManagerTest/', views.WebManagerTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/apiCaseTest/', views.ApiCaseTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/apiTypeTest/', views.ApiTypeTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/apiManagerTest/', views.ApiManagerTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/projectTest/', views.projectTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/getRecord/', views.getRecord.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/webAutoTest/', views.webAutoTest.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/mpcloudExcel/', views.MpcloudExcel.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/', include(router.urls)),
]
