from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys

from ansible.compat.six import integer_types, string_types, text_type

from pycompose.errors import ValueGeneratorError, ValueGeneratorTypeError

from pycompose.compose import ansible_unwrap
from pycompose.compose.node import Node

class NodeGroup:
    '''
    This class defines a group of nodes, representig a set of vagrant machines with similar characteristics.
    Nodes will be composed by NodeGroup.compose method, according with the configuration of values/value_generator
    of the group of node itself.
    '''

    def __init__(self, index, name, instances, box, boxname, hostname, aliases, ip, cpus, memory, ansible_groups, attributes):
        '''Creates a new NodeGroup.

        Keyword arguments:
        index           -- A number identifying the group of nodes withing the cluster.
        name            -- The name of the group of nodes.
        instances       -- The number of nodes/instances to be created in the group of nodes.
        box             -- The value/value generator to be used for assigning to each node in this group a base box to be used for creating vagrant machines implementing nodes in this group.
        boxname         -- The value/value generator to be used for assigning to each node in this group a box name a.k.a. the name for the machine in VirtualBox/VMware console.
        hostname        -- The value/value generator to be used for assigning to each node in this group a unique hostname.
        aliases         -- The value/value generator to be used for assigning to each node in this group a unique list of aliases a.k.a. (comma separated list of alias) alternative host names.
        ip              -- The value/value generator to be used for assigning to each node in this groupa unique ip.
        cpus            -- The value/value generator to be used for assigning to each node in this group cpus.
        memory          -- The value/value generator to be used for assigning to each node in this group memory.
        ansible_groups  -- The value/value generator to be used for assigning each node in this group to a list of ansible groups.
        attributes      -- The value/value generator to be used for assigning a dictionary with custom attributes - Hash(String, obj) - to each node in this group.
        '''

        self.index          = index
        self.name           = name
        self.instances      = instances
        self.box            = box
        self.boxname        = boxname
        self.hostname       = hostname
        self.aliases        = aliases
        self.ip             = ip
        self.cpus           = cpus
        self.memory         = memory
        self.ansible_groups = ansible_groups
        self.attributes     = attributes

    def _maybe_prefix(self, cluster_name, name):
        ''' utility function for concatenating cluster name (if present) to boxname/hostname.

        Keyword arguments:
        cluster_name    -- Name of the cluster
        name            -- Boxname or hostname of the node
        '''

        if cluster_name:
            return "{}-{}".format(cluster_name, name)
        else:
            return name

    def _generate(self, ansible_templar, var, generator, node_index, type = string_types):
        ''' utility function for resolving value/value generators

        Keyword arguments:
        ansible_templar --  The ansible templar engine
        var             --  The name of the var to be generated
        generator       --  The value generator expression (a ninja template managed by ansible; can be also a literal)
        node_index      --  The node index
        type            --  The expected type for the generated value
        '''

        # set the variables available within the ninja context for value generation
        ansible_templar.set_available_variables(dict(
            group_index = self.index,
            group_name = self.name,
            node_index = node_index
        ))

        # generates the values (or simple keeps the given value)
        try:
            value = ansible_templar.template(generator)
        except Exception, e:
            raise ValueGeneratorError(self.name, node_index, var, e.message), None, sys.exc_info()[2]

        # checks the generated value matches the expected type
        try:
            if type == integer_types:
                value = int(value)
        except Exception, e:
            raise ValueGeneratorTypeError(self.name, node_index, var, e.message)

        return ansible_unwrap(value)

    def compose(self, templar, cluster_name, cluster_domain, cluster_offset):
        ''' Composes the group of nodes, by creating the required number of nodes in accordance with values/value generators.

        Additionally:
        * some "embedded" trasformation will be applied to attributes:
          * boxname (prefied by cluster_name, if defined)
          * hostname (prefied by cluster_name, if defined)
        * some "autogenerated" node properties will be computed:
          * fqdn (hostname + cluster_domain, if defined)

        Keyword arguments:
        cluster_name    -- The name of the cluster
        cluster_domain  -- The domain to which the cluster belongs
        cluster_offset  -- The offset - the initial group_index - to be used for nodes in the nodegroup
        '''

        node_index = 0
        while node_index < self.instances:
          box            = self._generate(templar, 'box', self.box, node_index)
          boxname        = self._maybe_prefix(cluster_name, self._generate(templar, 'boxname', self.boxname, node_index))
          hostname       = self._maybe_prefix(cluster_name, self._generate(templar, 'hostname', self.hostname, node_index))
          aliases        = ','.join(self._generate(templar, 'aliases', self.aliases, node_index))
          fqdn           = hostname if not cluster_domain else "{}.{}".format(hostname, cluster_domain)
          ip             = self._generate(templar, 'ip', self.ip, node_index)
          cpus           = self._generate(templar, 'cpus', self.cpus, node_index, type = integer_types)
          memory         = self._generate(templar, 'memory', self.memory, node_index, type = integer_types)
          ansible_groups = self._generate(templar, 'ansible_groups', self.ansible_groups, node_index)
          attributes     = self._generate(templar, 'attributes', self.attributes, node_index)

          yield Node(box, boxname, hostname, fqdn, aliases, ip, cpus, memory, ansible_groups, attributes, cluster_offset + node_index, node_index)

          node_index += 1
