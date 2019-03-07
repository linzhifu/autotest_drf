from rest_framework.views import exception_handler


# 自定义异常处理
def my_exception_handler(exc, context):
    # Call REST framework's default exception handler first,
    # to get the standard error response.
    response = exception_handler(exc, context)

    # Now add the HTTP status code to the response.
    if response is not None:
        # 添加异常识别码
        response.data['errcode'] = 901

    return response
