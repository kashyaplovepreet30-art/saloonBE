from rest_framework.views import exception_handler


def custom_exception_handler(exc, context):
    response = exception_handler(exc, context)

    if response is not None:
        custom = {
            "status_code": response.status_code,
            "message": "Validation failed" if response.status_code == 400 else "Error",
            "errors": response.data,
        }
        response.data = custom

    return response
