# -*- coding: utf-8 -*-
# import asyncio
# import logging, os
# from aiohttp import web
# from orm.model import create_pool
# from webs.coroweb import add_routes
# from webs.app import init_jinjia2, logger_factory, response_factory, datetime_filter
# from webs import config
#
# os.environ.setdefault('SETTINGS', 'conf.config_override')
#
#
# async def init(loop):
#     config.setup()
#     db_config = config.configs['db']
#
#     await create_pool(loop=loop, host=db_config['host'], port=db_config['port'],
#                       user=db_config['user'], password=db_config['password'],
#                       db=db_config['database'])
#     app = web.Application(loop=loop, middlewares=[logger_factory, response_factory])
#     init_jinjia2(app=app, filters=dict(datetime=datetime_filter), path=config.configs['template_dir'])
#
#     add_routes(app, 'handlers.handlers')
#
#     srv = await loop.create_server(app.make_handler(), '0.0.0.0', 9000)
#     logging.info('server started at http://127.0.0.1:9000...')
#     return srv
#
#
# loop = asyncio.get_event_loop()
# loop.run_until_complete(init(loop))
# loop.run_forever()

from webs import app

app.run()
