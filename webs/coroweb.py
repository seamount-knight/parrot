import functools
import inspect
import logging
import asyncio
import os
from aiohttp import web
from urllib import parse


def get(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__method__ = 'GET'
        wrapper.__route__ = path
        return wrapper
    return decorator


def post(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__method__ = 'POST'
        wrapper.__route__ = path
        return wrapper
    return decorator


def put(path):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)
        wrapper.__method__ = 'PUT'
        wrapper.__route__ = path
        return wrapper
    return decorator


class RequestHandler(object):
    def __init__(self, app, func):
        self.app = app
        self.func = func

    async def __call__(self, request):
        kw = None
        if self._has_var_kw_arg or self._has_named_kw_args:
            if request.method == 'POST':
                if not request.content_type:
                    web.HTTPBadRequest(body='Missing Content-Type.')
                ct = request.content_type.lower()
                if ct.startswith('application/json'):
                    params = await request.json()
                    if not isinstance(params, dict):
                        raise web.HTTPBadRequest(body='JSON body must be object.')
                    kw = params
                elif ct.startswith('application/x-www-form-urlencoded') or ct.startswith('multipart/form-data'):
                    params = await request.post()
                    kw = dict(**params)
                else:
                    return web.HTTPBadRequest(body='Unsupported Content-Type: %s' % request.content_type)
            elif request.method == 'GET':
                qs = request.query_string
                if qs:
                    kw = dict()
                    params = parse.parse_qs(qs=qs, keep_blank_values=True)
                    for k, v in params.items():
                        kw[k] = v[0]
        if kw is None:
            kw = dict(**request.match_info)
        else:
            if not self._has_var_kw_arg and self._has_named_kw_args:
                copy = dict()
                for name in self._get_named_kw_args:
                    if name in kw:
                        copy[name] = kw[name]
                kw = copy
            for k, v in request.match_info.items():
                if k in kw:
                    logging.warning("Duplicate arg name in named arg and kw args: %s' % k")
                kw[k] = v
        if self._has_request_args:
            kw['request'] = request

        # check required args
        for arg in self._get_required_kw_args:
            if arg not in kw:
                return web.HTTPBadRequest(body='Missing argument: %s' % name)

        logging.info('call with args: {}'.format(kw))

        try:
            r = await self.func(**kw)
            return r
        except Exception as e:
            return dict(error=e.error, data=e.data, message=e.message)

    @property
    def _get_required_kw_args(self):
        args = []
        params = inspect.signature(self.func).parameters
        for name, param in params.items():
            if param.kind == inspect.Parameter.KEYWORD_ONLY and param.default == inspect.Parameter.empty:
                args.append(name)
        return tuple(args)

    @property
    def _get_named_kw_args(self):
        args = []
        params = inspect.signature(self.func).parameters
        for name, param in params.items():
            if param.kind == inspect.Parameter.KEYWORD_ONLY:
                args.append(name)
        return tuple(args)

    @property
    def _has_named_kw_args(self):
        params = inspect.signature(self.func).parameters
        for name, param in params.items():
            if param.kind == inspect.Parameter.KEYWORD_ONLY:
                return True

    @property
    def _has_var_kw_arg(self):
        params = inspect.signature(self.func).parameters
        for name, param in params.items():
            if param.kind == inspect.Parameter.VAR_KEYWORD:
                return True

    @property
    def _has_request_args(self):
        sig = inspect.signature(self.func)
        params = sig.parameters
        found =False
        for name, param in params.items():
            if name == 'request':
                found = True
                continue
            if found:
                if param.kind != inspect.Parameter.VAR_POSITIONAL and \
                                 param.kind != inspect.Parameter.KEYWORD_ONLY and \
                                 param.kind != inspect.Parameter.VAR_KEYWORD:
                    raise ValueError('request parameter must be the last named parameter in function: %s%s' % (
                        self.func.__name__, str(sig)))
        return found


def add_static(app):
    path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'static')
    app.router.add_static('/static/', path)
    logging.info('add static %s => %s' % ('/static/', path))


def add_route(app, fn):
    method = getattr(fn, '__method__', None)
    path = getattr(fn, '__route__', None)
    if path is None or method is None:
        raise ValueError('@get or @post not defined in %s.' % str(fn))
    if not asyncio.iscoroutinefunction(fn) and not inspect.isgeneratorfunction(fn):
        fn = asyncio.coroutine(fn)
    logging.info(
        'add route %s %s => %s(%s)' % (method, path, fn.__name__, ', '.join(inspect.signature(fn).parameters.keys())))
    app.router.add_route(method, path, RequestHandler(app, fn))


def add_routes(app, module_name):
    n = module_name.rfind('.')
    if n == -1:
        mod = __import__(module_name, globals(), locals())
    else:
        name = module_name[n + 1:]
        mod = getattr(__import__(module_name[:n], globals(), locals(), [name]), name)
    for attr in dir(mod):
        if attr.startswith('_'):
            continue
        fn = getattr(mod, attr)
        if callable(fn):
            path = getattr(fn, '__route__', None)
            method = getattr(fn, '__method__', None)
            if path and method:
                add_route(app, fn)
