from __future__ import (absolute_import, division, print_function)
__metaclass__ = type 

#TODO: remove dependencies from ansible (use default json library + ninja2)
from ansible.utils.unicode import to_str
from ansible.template import Templar
from ansible.parsing.dataloader import DataLoader

from vagrantplaybook.compat import compat_text_type

ansible_tempar = Templar
ansible_loader = DataLoader

def ansible_unwrap(value):
    ''' utility function for unwrapping values generated

    Keyword arguments:
    value           --  Generated value
    '''

    # if the value is a unicode string
    if isinstance(value, compat_text_type):
        # converts to native string
        return to_str(value)
    # if the value is a list of values
    if isinstance(value, list):
        # unwraps all the elements in the list
        return [ansible_unwrap(i) for i in value]
    # if the value is a dictionary of values
    if isinstance(value, dict):
        return { ansible_unwrap(k): ansible_unwrap(v) for k, v in value.iteritems() }
    else:
        return value
