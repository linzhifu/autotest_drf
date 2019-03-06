# 自定义中间件
from django.utils.deprecation import MiddlewareMixin


class MyMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # print('中间件测试：process_request')
        # 返回 None 或者 HttpResponse 对象
        # None继续处理其它中间件
        return None
        # HttpResponse就处理中止，返回到网页上
        # from django.http import HttpResponse
        # return HttpResponse('process_request报错啦')

    def process_view(self, request, callback, callback_args, callback_kwargs):
        # print("中间件测试：process_view")
        # 返回 None 或者 HttpResponse 对象
        # None继续处理其它中间件
        return None
        # HttpResponse就处理中止，返回到网页上
        # from django.http import HttpResponse
        # return HttpResponse('process_view报错啦')

    # 当一个视图抛出异常时，Django会调用process_exception()来处理
    # process_exception()应该返回一个 None 或者一个HttpResponse对象
    # 如果它返回一个HttpResponse对象，则将应用模板响应和响应中间件，并将生成的响应返回给浏览器
    # 否则，默认的异常处理开始工作。
    def process_exception(self, request, exception):
        # print("中间件测试：process_exception")
        return None

    # process_template_response(self,request,response)
    # 如果响应的实例有render()方法，process_template_response()在视图刚好执行完毕之后被调用
    # 这个方法必须返回一个实现了render方法的响应对象。

    def process_response(self, request, response):
        # print('中间件测试：process_response')
        return response
