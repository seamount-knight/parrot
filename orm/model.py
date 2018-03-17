import logging
import aiomysql
from orm.field import *

logging.basicConfig(level=logging.INFO)


def create_args_string(length):
    args = []
    i = 0
    while i < length:
        i += 1
        args.append('?')
    return ', '.join(args)

async def create_pool(loop, **kwargs):
    logging.info('create database connection pool...')
    global __pool
    __pool = await aiomysql.create_pool(
        host=kwargs.get('host', 'localhost'),
        port=kwargs.get('port', 3306),
        user=kwargs.get('user'),
        password=kwargs.get('password'),
        db=kwargs.get('db'),
        charset=kwargs.get('charset', 'utf8'),
        autocommit=kwargs.get('autocommit', True),
        maxsize=kwargs.get('maxsize', 10),
        minsize=kwargs.get('minsize', 1),
        loop=loop
    )


async def select(sql, args, size=None):
    global __pool
    with (await __pool) as conn:
        cursor = await conn.cursor(aiomysql.DictCursor)
        await cursor.execute(sql.replace('?', '%s'), args or ())
        if size:
            result = await cursor.fetchmany(size)
        else:
            result = await cursor.fetchall()
        await cursor.close()
        return result


async def execute(sql, args):
    global __pool
    with (await __pool) as conn:
        try:
            cursor = await conn.cursor()
            await cursor.execute(sql.replace('?', '%s'), args)
            affected = cursor.rowcount
            await cursor.close()
        except Exception as e:
            raise
        return affected


class ModelMetaClass(type):

    def __new__(cls, name, bases, attrs):
        if name == 'Model':
            return type.__new__(cls, name, bases, attrs)

        tableName = attrs.get('__table__', None) or name
        logging.info('tableName : {}'.format(tableName))

        mappings = dict()
        fields = []
        primary_key = None

        for k, v in attrs.items():
            if isinstance(v, Field):
                mappings[k] = v
                if v.primary_key:
                    if primary_key is not None:
                        raise Exception('duplicate primary_key')
                    primary_key = k
                    logging.info('primary_key: {}'.format(primary_key))

                else:
                    fields.append(k)

        if primary_key is None:
            raise RuntimeError('primary key not found')

        for k in mappings.keys():
            attrs.pop(k)

        escaped_fields = list(map(lambda f: '`%s`' % f, fields))

        attrs['__mappings__'] = mappings
        attrs['__table_name__'] = tableName
        attrs['__fields__'] = fields
        attrs['__primary_key__'] = primary_key

        attrs['__select__'] = 'select `%s`, %s from `%s`' % (primary_key, ', '.join(escaped_fields), tableName)
        attrs['__insert__'] = 'insert into `%s` (%s, `%s`) values (%s)' % (tableName, ', '.join(escaped_fields),
                                                                           primary_key,
                                                                           create_args_string(len(escaped_fields) + 1))
        attrs['__update__'] = 'update `%s` set %s where `%s`=?' % (tableName,
                                                                   ', '.join(map(lambda f: '`%s`=?', escaped_fields)),
                                                                   primary_key)
        attrs['__delete__'] = 'delete `%s` where `%s`=?' % (tableName, primary_key)

        return type.__new__(cls, name, bases, attrs)


class Model(dict, metaclass=ModelMetaClass):

    def __init__(self, **kwargs):
        super(Model, self).__init__(**kwargs)

    def __getattr__(self, key):
        try:
            return self[key]
        except KeyError:
            raise AttributeError(r"'Model' object has no attribute '%s'" % key)

    def __setattr__(self, key, value):
        self[key] = value

    def getValue(self, key):
        return self[key]

    def getValueOrDefault(self, key):
        value =  getattr(self, key, None)
        if value is None:
            field = self.__mappings__[key]
            if field.default is not None:
                value = field.default() if callable(field.default) else field.default
                logging.info('using default value for %s: %s' % (key, str(value)))
                setattr(self, key, value)
        return value

    @classmethod
    async def findone(cls, pk):
        '''
        find object by primary key
        :param pk: 
        :return: 
        '''
        rs = await select('%s where `%s`=?' % (cls.__select__, cls.__primary_key__), [pk], 1)
        if len(rs) == 0:
            return None
        return cls(**rs[0])

    @classmethod
    async def findAll(cls, where=None, args=None):
        objs = []
        sql = cls.__select__
        if where is not None:
            sql = cls.__select__ + ' where ' + where
        logging.info(sql)
        rs = await select('{}'.format(sql), args)
        for obj in rs:
            objs.append(cls(**obj))
        return objs

    async def save(self):
        args = list(map(self.getValueOrDefault, self.__fields__))
        args.append(self.getValueOrDefault(self.__primary_key__))
        logging.info('{} : {}'.format(self.__insert__, args))
        rows = await execute(self.__insert__, args)
        if rows != 1:
            logging.warn('failed to insert record: affected rows: %s' % rows)
