import logging

logging.basicConfig(level=logging.INFO)


class Field(object):
    def __init__(self, name, column_type, default, primary_key=False):
        self.name = name
        self.column_type = column_type
        self.default = default
        self.primary_key = primary_key

    def __str__(self):
        return '<%s, %s:%s>' % (self.__class__.__name__, self.column_type, self.column_name)


class CharField(Field):
    def __init__(self, max_length=None, name=None,
                 default=None, primary_key=False):
        if max_length is None:
            raise RuntimeError('char_field must set max_length')
        column_type = 'varchar({})'.format(max_length)
        super(CharField, self).__init__(name=name, column_type=column_type,
                                        default=default,
                                        primary_key=primary_key)


class FloatField(Field):
    def __init__(self, name=None, default=None, primary_key=False):
        column_type = 'real'
        super(FloatField, self).__init__(name=name, default=default,
                                         column_type=column_type,
                                         primary_key=primary_key)


class BooleanField(Field):
    def __init__(self, name=None, default=False, primary_key=False):
        column_type = 'bool'
        super(BooleanField, self).__init__(name=name, column_type=column_type,
                                           default=default, primary_key=primary_key)


class TextField(Field):
    def __init__(self, name=None, default=None, primary_key=None):
        column_type = 'mediumtext'
        super(TextField, self).__init__(name=name, default=default,
                                        column_type=column_type, primary_key=primary_key)
