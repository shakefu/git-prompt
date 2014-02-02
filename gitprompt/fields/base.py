"""
Field Type
==========

"""
class FieldMeta(type):
    def __new__(mcs, name, bases, cls_dict):
        if callable(cls_dict['value']):
            cls_dict['value'] = classmethod(cls_dict['value'])
        return type.__new__(mcs, name, bases, cls_dict)

    def __str__(cls):
        return cls.as_str()

    def as_str(cls):
        if callable(cls.value):
            cls.value = cls.value()
        return cls.value

    def __cmp__(cls, other):
        return cmp(str(cls), other)

    def __nonzero__(cls):
        return bool(cls.as_str())


class Field(object):
    __metaclass__ = FieldMeta
    def value(cls):
        return ''

