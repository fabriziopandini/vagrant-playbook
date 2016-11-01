# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type
 
class Node:
    '''
    This class defines a node throught a set of setting to be used when creating vagrant machines in the cluster.
    Settings will be assigned value by cluster.compose method, according with the configuration
    of the group of nodes to which the node belongs.
    '''

    def __init__(self, box, boxname, hostname, fqdn, aliases, ip, cpus, memory, ansible_groups, attributes, index, group_index):
        '''Creates a new Node.

        Keyword arguments:
        box             -- The vagrant base box to be used for creating the vagrant machine that implements the node.
        boxname         -- The box name to be used for this node, a.k.a. the name to be used for the machine in VirtualBox/VMware console.
        hostname        -- The hostname to be used for the node.
        fqdn            -- The fully qualified name to be used for the node.
        aliases         -- The list of aliases (comma separated list of alias), a.k.a. alternative host names to be used for the node.
        ip              -- The ip for to be used the node.
        cpus            -- The cpu for to be used the node.
        memory          -- The memory to be used for the node.
        ansible_groups  -- The list of ansible_groups to be used for the node.
        attributes      -- A set of custom attributes to be used for the node.
        index           -- A number identifying the node within the group of nodes to which the node belongs.
        group_index     -- A number identifying the group of nodes to which the node belongs.
        '''

        self.box            = box
        self.boxname        = boxname
        self.hostname       = hostname
        self.fqdn           = fqdn
        self.aliases        = aliases
        self.ip             = ip
        self.cpus           = cpus
        self.memory         = memory
        self.ansible_groups = ansible_groups
        self.attributes     = attributes
        self.index          = index
        self.group_index    = group_index
