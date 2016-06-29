from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from inspect import isfunction

class ContainerOf:

    def __init__(self, *types):
        self.types = types

    def isValid(self, value):
        print ("ContainerOf isValid %s %s" % (value, self.types))

        return self._isValueOf(value, self.types)

    def _isValueOf(self, value, types):
        print ("ContainerOf _isValueOf %s %s" % (value, types))
        for type in types:
            if isinstance(type, ContainerOf):
                if type.isValid(value):
                    return True
            else:
                if isinstance(value, type):
                    return True

        return False

class AnyOf(ContainerOf):
    pass

class ListOf(ContainerOf):

    def __init__(self, *item_types):
        self.item_types = item_types

    def isValid(self, value):
        print ("ListOf isValid %s" % (value))

        if not isinstance(value, list):
            return False

        return all([self._isValueOf(item, self.item_types) for item in value])

class DictOf(ContainerOf):

    def __init__(self, key_types, value_types):
        self.key_types = key_types
        self.value_types = value_types

    def isValid(self, value):

        if not isinstance(value, dict):
            return False

        return all([self._isValueOf(k, self.key_types) and self._isValueOf(v, self.value_types) for k, v in value.iteritems()])

class SafeClass:

    def __setattr__(self, name, value):
        if name.startswith("_"):
            self.__dict__[name] = value
            return

        if name in self.__class__._attributes_validation:
            expectedType = self.__class__._attributes_validation[name]
            print ("SafeClass validating %s %s" % (name, expectedType))

            if not isinstance(expectedType, ContainerOf):
                expectedType = ContainerOf(*expectedType)

            if expectedType.isValid(value):
                self.__dict__[name] = value
            else:
                raise TypeError ("Invalid value '%s' assigned to attribute '%s' in type '%s'. Use values of type %s" % (value, name, self.__class__.__name__, expectedType))
        else:
            raise AttributeError ("'%s' object has no attribute '%s'" % (self.__class__.__name__, name))
