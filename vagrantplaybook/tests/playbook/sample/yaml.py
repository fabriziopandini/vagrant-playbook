# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type 

sample_yaml = '''
---
mesos:
    nodegroup1:
        instances: 1
        ansible_groups:
          - ansible_groups1
          - ansible_groups2

    nodegroup2:
        ansible_groups:
          - ansible_groups1

    ansible_group_vars:
        ansible_groups1 :
            var1: "{{ nodes | count }}"
        ansible_groups2 :
            var2: "{{ nodes | count }}"
            var3: literal


    ansible_host_vars:
        ansible_groups1 :
            var1: "{{ node.hostname }}"
        ansible_groups2 :
            var2: "{{ node.ip }}"

'''
