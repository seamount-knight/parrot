import time, uuid
import logging
from orm import model
import asyncio


def next_id():
    return '%015d%s000' % (int(time.time() * 1000), uuid.uuid4().hex)


class User(model.Model):
    __table__ = 'users'

    id = model.CharField(max_length=50, primary_key=True, default=next_id)
    name = model.CharField(max_length=50)
    email = model.CharField(max_length=50)
    passwd = model.CharField(max_length=50)
    admin = model.BooleanField()
    image = model.CharField(max_length=50)
    created_at = model.FloatField(default=time.time)


class Blog(model.Model):
    __table__ = 'blogs'

    id = model.CharField(max_length=50, primary_key=True, default=next_id)
    user_id = model.CharField(max_length=50)
    user_name = model.CharField(max_length=50)
    user_image = model.CharField(max_length=50)
    name = model.CharField(max_length=50)
    summary = model.CharField(max_length=200)
    content = model.TextField()
    created_at = model.FloatField(default=time.time)


class Comment(model.Model):
    __table__ = 'comment'

    id = model.CharField(max_length=50, primary_key=True, default=next_id)
    blog_id = model.CharField(max_length=50)
    user_id = model.CharField(max_length=50)
    user_name = model.CharField(max_length=50)
    user_image = model.CharField(max_length=500)
    content = model.TextField()
    reated_at = model.FloatField(default=time.time)


async def test(loop):
    await model.create_pool(user='root', password='123456', db='awesome',
                            host='db', loop=loop)

    u = User(name='Test', email='test@example.com', passwd='1234567890', image='about:blank')
    logging.info(u)
    await u.save()

if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(test(loop))
    loop.close()
