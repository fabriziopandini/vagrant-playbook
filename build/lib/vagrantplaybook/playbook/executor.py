# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import yaml
import types

from vagrantplaybook.ansible import ansible_unwrap, ansible_loader

from vagrantplaybook.errors import PlaybookLoadError, PlaybookParseError, PlaybookCompileError
from vagrantplaybook.compose.cluster import Cluster

class Executor:
    '''
    This class defines a Playbook parser and executor.
    It takes in input a yaml file with the definition of the cluster, and then
    execute it generating another yaml file containing the definition of all
    the nodes/VM in the cluster
    '''

    def __init__(self):
        self._loader = ansible_loader()

    def execute(self, yamlfile, yamlplaybook):
        #load yaml playbook into a generic data structure
        playbook = self._load_from_file(yamlfile) if yamlfile else executor.load(yamlplaybook)

        #parse the playbook into a cluster definition
        cluster = self._parse(playbook)

        #compose the cluster
        clustername, nodesmap, inventory, ansible_group_vars, ansible_host_vars = self._compose(cluster)

        #return the composed cluster in yaml format
        return self._yaml(clustername, nodesmap, inventory, ansible_group_vars, ansible_host_vars)

    def _load_from_file(self, file_name):
        '''Loads a playbook from a yaml file.

        Keyword arguments:
        file_name       -- The yaml file name (and path),
        '''
        try:
            return self._loader.load_from_file(file_name)
        except Exception, e:
            raise PlaybookLoadError(file_name, e.message), None, sys.exc_info()[2]

    def _load(self, yaml_string):
        '''Loads a playbook from a yaml string.

        Keyword arguments:
        yaml_strin       -- The yaml string,
        '''
        try:
            return self._loader.load(yaml_string, '<string>', show_content=True)
        except Exception, e:
            raise PlaybookLoadError('<string>', e.message), None, sys.exc_info()[2]

    def _parse(self, loaded_data):
        '''Parse a playbook - represented as a AnsibleMapping - into a cluster with its nodegroups.

        Keyword arguments:
        loaded_data     -- The AnsibleMapping representing the playbook,
        '''
        if not isinstance(loaded_data, dict):
            raise PlaybookParseError("Invalid cluster definition: see documentation.")
        elif len(loaded_data) != 1:
            raise PlaybookParseError("Invalid cluster definition: please provide one cluster object.")

        # Parse the first level of the yaml document (loaded into a dictionary).
        # The first level is the cluster to be composed
        k1 = ansible_unwrap(loaded_data.keys()[0])
        v1 = ansible_unwrap(loaded_data[k1])
        cluster = Cluster(k1, loader = self._loader)

        if not isinstance(v1, dict):
            raise PlaybookParseError("Invalid cluster definition: please provide attributes for cluster %s." % (v1))

        # Parse the second level of the yaml document (loaded into a dictionary).
        # The second level is either cluster attributes and also
        #  nodegroups definition
        for k2, v2 in v1.iteritems():
            k2 = ansible_unwrap(k2)
            v2 = ansible_unwrap(v2)

            # If the element is one of cluster attributes sets the attribute value.
            # NB. cluster class checks the type of value assigned to the attribute
            if k2 in self._get_object_attributes(cluster):
                try:
                    cluster.__setattr__(k2, v2)
                except Exception, e:
                    raise PlaybookParseError("Error parsing cluster attributes '%s': %s" % (k1, e.message))

            # Ohterwise the element is a nodegroup
            # Nb. the DataLoader provides guarantee that keys are unique within an element
            #  and therefore nodegroup name are uniques within a cluster
            else:
                nodegroup = cluster.add_node_group(k2, 1)

                # if there are attributes for the nodegroup
                if isinstance(v2, dict):
                    # Parse the third level of the yaml document (loaded into a dictionary).
                    # the third level is nodegroups attributes
                    for k3, v3 in v2.iteritems():
                        k3 = ansible_unwrap(k3)
                        v3 = ansible_unwrap(v3)

                        # Sets the nodegroup attribute value.
                        # NB. nodegroup class checks the type of value assigned to the attribute
                        # and checks if the attribute exists
                        nodegroup.__setattr__(k3, v3)

        return cluster

    def _compose(self, cluster):
        '''Compose a cluster - an object containing a parsed playbook - by generating a set of objects
            representing the composed cluster.

        Keyword arguments:
        cluster     -- The object containing a parsed playbook,
        '''

        try:
            nodesmap, inventory, ansible_group_vars, ansible_host_vars = cluster.compose()
        except Exception, e:
            raise PlaybookCompileError(cluster.name, e.message), None, sys.exc_info()[2]

        return cluster.name, nodesmap, inventory, ansible_group_vars, ansible_host_vars

    def _yaml(self, clustername, nodesmap, inventory, ansible_group_vars, ansible_host_vars):
        '''Transform a set of objects representing the composed cluster into a yaml cluster specification.

        Keyword arguments:
        clustername            -- Name of the cluster
        nodesmap               -- List of nodes in the cluster (in map format)
        inventory              -- Ansible inventory  - linking ansible groups and hosts
        ansible_group_vars     -- Ansible group vars - grouped by ansible groups
        ansible_host_vars      -- Ansible host vars - grouped by hosts
        '''
        yamlmap = {
            clustername : {
                'nodes' : nodesmap
            }
        }

        if len(inventory)>0:
            ansiblemap = {}

            ansiblemap['inventory'] = inventory

            if len(ansible_group_vars)>0:
                ansiblemap['group_vars'] = ansible_group_vars

            if len(ansible_host_vars)>0:
                ansiblemap['host_vars'] = ansible_host_vars

            yamlmap[clustername]['ansible'] = ansiblemap

        return yaml.dump(yamlmap, default_flow_style=False)

    def _get_object_attributes(self, instance):
        return [a for a in dir(instance) if not a.startswith('_') and not type(getattr(instance, a)) == types.MethodType]
