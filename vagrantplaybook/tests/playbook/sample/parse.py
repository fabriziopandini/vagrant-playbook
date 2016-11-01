# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type 

sample_execute_no_cluster = '''
---
'''

sample_execute_cluster_empty = '''
---
mesos:
'''

sample_execute_cluster_not_object = '''
---
mesos: 1
'''

sample_execute_nodegroup_empty = '''
---
mesos:
    zookeeper:
'''

sample_execute_nodegroup_with_attributes = '''
---
mesos:
    zookeeper:
        instances: 3
'''
