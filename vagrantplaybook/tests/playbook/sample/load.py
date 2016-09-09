# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

sample_load = '''
---
mesos:
  box: fp/centos7
  master:
    instances: 3
    memory: 256
    ansible_groups:
      - zookeeper
      - mesos-master

  slave:
    instances: 2
    memory: 256
    ansible_groups:
      - mesos-slave

  registry:
    instances: 1
    memory: "{{ 1024 + 256 }}"
    aliases:
      -  myregistry.vagrant
    ansible_groups:
      - docker-registry
'''

sample_load_witherrors = '''
---
users:
  tj:
    name: tj
      age: 23
      email: 'tj@vision-media.ca'
    bob:
      name: 'bob'
      age: 27
    ted: { name: ted, age: 32, email: ted@tedtalks.com }
country:
  name: Österreich
  website: http://en.wikipedia.org/wiki/Austria
  space:
    description: space, the final frontier
brackets:
  square: Square [brackets] can go in the middle of strings
  squiggle: Squiggle {brackets} can also go in the middle of strings!
  extrasquare: [Scratch that] brackets can go at the beginning as long as they close and have text after.
  extrasquiggle: {Scratch that} squigs can go at the beginning also!
'''
