from webs.coroweb import get, post
from webs.model import User, Blog, next_id
from webs.api_execption import ApiValueError, APIError
from aiohttp import web
from webs.config import configs
import hashlib
import time
import json


@get('/hello/{name}')
async def hello(*, name):
    u = User(name='Test1', email='test1@example.com', passwd='1234567890', image='about:blank')
    await u.save()
    u = User(name='Test2', email='test2@example.com', passwd='1234567890', image='about:blank')
    await u.save()
    u = User(name='Test3', email='test3@example.com', passwd='1234567890', image='about:blank')
    await u.save()
    return {
        'hello': name
    }


@get('/blogs')
async def index(request):
    summary = 'Lorem ipsum dolor sit amet, consectetur adipisicing elit, sed do eiusmod tempor incididunt ut labore et dolore magna aliqua.'
    blogs = [
        Blog(id='1', name='Test Blog', summary=summary, created_at=time.time() - 120),
        Blog(id='2', name='Something New', summary=summary, created_at=time.time() - 3600),
        Blog(id='3', name='Learn Swift', summary=summary, created_at=time.time() - 7200)
    ]
    return {
        '__template__': 'blogs.html',
        'blogs': blogs
    }


@get('/registry')
async def getr_egistry(request):
    return {
        '__template__': 'registry.html'
    }


@post('/registry')
async def create_user(*, name, email, password):
    if not name or not name.strip():
        raise ApiValueError("name")
    if not email or not email.strip():
        raise ApiValueError('email')
    if not password or not password.strip():
        raise ApiValueError('password')
    users = await User.findAll('email=?', [email])
    if len(users) > 0:
        raise APIError('register:failed', 'email', 'Email is already in use.')
    uid = next_id()
    sha1_passwd = '%s:%s' % (uid, password)

    user = User(id=uid, name=name, email=email, passwd=hashlib.sha1(sha1_passwd.encode('utf-8')).hexdigest(),
                image='http://www.gravatar.com/avatar/%s?d=mm&s=120' % (hashlib.md5(email.encode('utf-8')).hexdigest()))
    await user.save()
    r = web.Response()
    r.set_cookie(configs['cookie']['name'], user2cookie(user, 86400), max_age=86400, httponly=True)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/login')
async def get_login():
    return {
        '__template__': 'login.html'
    }


@post('/login')
async def authenticate(*, email, password):
    if not email:
        raise ApiValueError('email', 'Invalid email.')
    if not password:
        raise ApiValueError('password', 'Invalid password.')

    users = await User.findAll('email=?', [email])
    if len(users) == 0:
        raise ApiValueError('email', 'Email not exist.')
    user = users[0]
    # check passwd:
    sha1 = hashlib.sha1()
    sha1.update(user.id.encode('utf-8'))
    sha1.update(b':')
    sha1.update(password.encode('utf-8'))
    if user.passwd != sha1.hexdigest():
        raise ApiValueError('password', 'Invalid password.')
    # authenticate ok, set cookie:
    r = web.Response()
    r.set_cookie(configs['cookie']['name'], user2cookie(user, 86400), max_age=86400, httponly=False)
    user.passwd = '******'
    r.content_type = 'application/json'
    r.body = json.dumps(user, ensure_ascii=False).encode('utf-8')
    return r


@get('/edit')
async def createBlogs():
    return {
        '__template__': 'edit.html'
    }


# 计算加密cookie:
def user2cookie(user, max_age):
    # build cookie string by: id-expires-sha1
    expires = str(int(time.time() + max_age))
    s = '%s-%s-%s-%s' % (user.id, user.passwd, expires, configs['cookie']['key'])
    L = [user.id, expires, hashlib.sha1(s.encode('utf-8')).hexdigest()]
    return '-'.join(L)
