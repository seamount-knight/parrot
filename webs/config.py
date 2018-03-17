import os
import logging

configs = {
        'db': {
            'host': '127.0.0.1',
            'port': 3306,
            'user': 'www-data',
            'password': 'www-data',
            'database': 'awesome'
        },
        'session': {
            'secret': 'AwEsOmE'
        },
        'template_dir': None,
        'cookie': {
            'name': 'user',
            'key': 'AwEsOmE'
        }
    }


def setup():
    global configs
    settings = os.getenv('SETTINGS')
    n = settings.rfind('.')
    if n == -1:
        mod = __import__(settings, globals(), locals())
    else:
        name = settings[n+1:]
        mod = getattr(__import__(settings[:n], globals(), locals(), [name]), name)
    if 'configs' not in dir(mod):
        return configs
    configs = merge(configs, mod.configs)
    return configs


def merge(defaults, override):
    r = {}
    for k, v in defaults.items():
        if k in override:
            if isinstance(v, dict):
                r[k] = merge(v, override[k])
            else:
                r[k] = override[k]
        else:
            r[k] = v
    return r
