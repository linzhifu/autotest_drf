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
from django.urls import path, re_path
from user import views

# django 2.0 开始 路由包括正则表达式的话，需要用re_path，否则会报错：
# ?: (2_0.W001) Your URL pattern 'api/(?P<version>[v1|v2]+)/user/'
# has a route that contains '(?P<', begins with a '^', or ends with
# a '$'. This was likely an oversight when migrating to django.urls.path().


urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'(?P<version>[v1|v2]+)/user', views.UserView.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/captcha/', views.CaptchaView.as_view()),
    re_path(r'(?P<version>[v1|v2]+)/login/', views.LoginView.as_view()),
]
