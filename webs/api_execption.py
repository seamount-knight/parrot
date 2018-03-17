# -*- utf-8 -*-

class APIError(Exception):
    def __init__(self, error, data='', message=''):
        super(ApiError, self).__init__(message)
        self.error = error
        self.data = data
        self.message = message


class ApiValueError(APIError):
    def __init__(self, field, message=''):
        super(ApiValueError, self).__init__('value:invalid', field, message)


class APIResourceNotFoundError(APIError):
    '''
    Indicate the resource was not found. The data specifies the resource name.
    '''
    def __init__(self, field, message=''):
        super(APIResourceNotFoundError, self).__init__('value:notfound', field, message)


class APIPermissionError(APIError):
    '''
    Indicate the api has no permission.
    '''
    def __init__(self, message=''):
        super(APIPermissionError, self).__init__('permission:forbidden', 'permission', message)
