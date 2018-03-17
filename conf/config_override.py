import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

configs = {
    'db': {
        'user': 'root',
        'password': '123456',
    },
    # 'template_dir': base_dir + '/wwww/templates',
    'static_dir': base_dir + '/wwww/static'
}