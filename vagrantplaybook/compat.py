# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type 

# this module provides utilities for smoothing over the differences 
# between Python 2 (currently supported) and 3 (to be supported in future)
# see https://github.com/benjaminp/six

compat_string_types = basestring
compat_text_type = unicode
compat_integer_types = (int, long)

