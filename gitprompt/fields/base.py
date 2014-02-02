"""
Field Type
==========

"""
class FieldMeta(type):
    def __new__(mcs, name, bases, cls_dict):
        if callable(cls_dict['value']):
            cls_dict['value'] = classmethod(cls_dict['value'])
        cls_dict['_value'] = None
        return type.__new__(mcs, name, bases, cls_dict)

    def __str__(cls):
        return cls.as_str()

    def as_str(cls):
        if cls._value is None:
            if callable(cls.value):
                cls._value = cls.value()
            else:
                cls._value = cls.value
        return cls._value

    def __nonzero__(cls):
        return bool(cls.as_str())


class Field(object):
    __metaclass__ = FieldMeta
    def value(cls):
        return ''

