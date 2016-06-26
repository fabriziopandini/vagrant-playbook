from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from ansible.utils.unicode import to_str
from ansible.compat.six import text_type, string_types
from ansible.parsing.yaml.objects import AnsibleMapping

def ansible_unwrap(value):
    ''' utility function for unwrapping values generated

    Keyword arguments:
    value           --  Generated value
    '''

    # if the value is a unicode string
    if isinstance(value, text_type):
        # converts to native string
        return to_str(value)
    # if the value is a list of values
    if isinstance(value, list):
        # unwraps all the elements in the list
        return [ansible_unwrap(i) for i in value]
    # if the value is a dictionary of values
    if isinstance(value, AnsibleMapping):
        return { ansible_unwrap(k): ansible_unwrap(v) for k, v in value.iteritems() }
    else:
        return value
