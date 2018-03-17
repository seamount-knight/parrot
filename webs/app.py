#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import json
import logging
import os
import time
import asyncio
import hashlib
from datetime import datetime
from aiohttp import web
from jinja2 import Environment, FileSystemLoader
from webs import config
from orm.model import create_pool
from webs.coroweb import add_routes, add_static
from webs.model import User


__author__ = 'knight'

'''
async webs application.
'''

logging.basicConfig(level=logging.INFO)


def init_jinjia2(app, **kw):
    logging.info('init jinjia')
    options = dict(
        autoescape=kw.get('autoescape', True),
        block_start_string=kw.get('block_start_string', '{%'),
        block_end_string=kw.get('block_end_string', '%}'),
        variable_start_string=kw.get('variable_start_string', '{{'),
        variable_end_string=kw.get('variable_end_string', '}}'),
        auto_reload=kw.get('auto_reload', True)
    )

    path = kw.get('path', None)

    if path is None:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    logging.info('set jinja2 template path: %s' % path)
    env = Environment(loader=FileSystemLoader(path), **options)

    filters = kw.get('filters', None)
    if filters is not None:
        for name, f in filters.items():
            env.filters[name] = f
    app['__templating__'] = env


async def logger_factory(app, handler):
    async def logger(request):
        logging.info('Request: %s %s' % (request.method, request.path))
        return (await handler(request))
    return logger


async def response_factory(app, handler):
    async def response(request):
        logging.info('Response handler...')
        r = await handler(request)
        if isinstance(r, web.StreamResponse):
            return r
        elif isinstance(r, bytes):
            resp = web.Response(body=r)
            resp.content_type = 'application/octet-stream'
            return resp
        elif isinstance(r, str):
            if r.startswith('redirect:'):
                return web.HTTPFound(r[9:])
            resp = web.Response(body=r.encode('utf-8'))
            resp.content_type = 'text/html;charset=utf-8'
            return resp
        elif isinstance(r, dict):
            template = r.get('__template__')
            if template is None:
                resp = web.Response(body=json.dumps(r, ensure_ascii=False,
                                                    default=lambda o: o.__dict__).encode('utf-8'))
                resp.content_type = 'application/json; charset=utf-8'
            else:
                r['user'] = request.__user__
                resp = web.Response(body=app['__templating__'].get_template(template).render(**r).encode('utf-8'))
                resp.content_type = 'text/html; charset=utf-8'
                return resp
        if isinstance(r, int) and r >= 100 and r < 600:
            return web.Response(status=r)
        if isinstance(r, tuple) and len(r) == 2:
            t, m = r
            if isinstance(t, int) and t >= 100 and t < 600:
                return web.Response(status=t, body=str(m))
        resp = web.Response(body=str(r).encode('utf-8'))
        resp.content_type = 'text/plain; charset=utf-8'
        return resp
    return response

async def auth_factory(app, handler):
    async def auth(request):
        configs = config.configs
        logging.info('check user: %s %s' % (request.method, request.path))
        request.__user__ = None
        cookie_str = request.cookies.get(configs['cookie']['name'])
        if cookie_str:
            user = await cookie2user(cookie_str)
            if user:
                logging.info('set current user: %s' % user.email)
                request.__user__ = user
        return (await handler(request))
    return auth


async def cookie2user(cookie_str):
    configs = config.configs
    if not cookie_str:
        return None
    try:
        L = cookie_str.split('-')
        if len(L) != 3:
            return None
        uid, expires, sha1 = L
        if int(expires) < time.time():
            return None
        user = await User.findone(pk=uid)
        if user is None:
            return None
        s = '%s-%s-%s-%s' % (uid, user.passwd, expires, configs['cookie']['key'])
        if sha1 != hashlib.sha1(s.encode('utf-8')).hexdigest():
            logging.info('invalid sha1')
            return None
        user.passwd = '******'
        return user
    except Exception as e:
        logging.exception(e)
        return None


def datetime_filter(t):
    delta = int(time.time() - t)
    if delta < 60:
        return u'1分钟前'
    if delta < 3600:
        return u'%s分钟前' % (delta // 60)
    if delta < 86400:
        return u'%s小时前' % (delta // 3600)
    if delta < 604800:
        return u'%s天前' % (delta // 86400)
    dt = datetime.fromtimestamp(t)
    return u'%s年%s月%s日' % (dt.year, dt.month, dt.day)


os.environ.setdefault('SETTINGS', 'conf.config_override')


async def init(loop):
    config.setup()
    logging.info(config.configs)
    db_config = config.configs['db']

    await create_pool(loop=loop, host=db_config['host'], port=db_config['port'],
                      user=db_config['user'], password=db_config['password'],
                      db=db_config['database'])
    app = web.Application(loop=loop, middlewares=[logger_factory, auth_factory, response_factory])
    init_jinjia2(app=app, filters=dict(datetime=datetime_filter), path=config.configs['template_dir'])
    add_static(app)
    add_routes(app, 'handlers.handlers')

    srv = await loop.create_server(app.make_handler(), '0.0.0.0', 9000)
    logging.info('server started at http://0.0.0.0:9000...')
    return srv


def run():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(init(loop))
    loop.run_forever()
