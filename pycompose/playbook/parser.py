# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import sys
import yaml
import types

from pycompose.ansible import ansible_unwrap, ansible_loader

from pycompose.errors import PlaybookLoadError, PlaybookParseError, PlaybookCompileError
from pycompose.compose.cluster import Cluster

class Parser:
    '''
    This class defines a Playbook parser and executor.
    It takes in input a yaml file with the definition of the cluster, and then
    execute it generating another yaml file containing the definition of all
    the nodes/VM in the cluster
    '''

    def __init__(self):
        self._loader = ansible_loader()

    def load_from_file(self, file_name):
        '''Loads a playbook from a yaml file.

        Keyword arguments:
        file_name       -- The yaml file name (and path),
        '''
        try:
            return self._loader.load_from_file(file_name)
        except Exception, e:
            raise PlaybookLoadError(file_name, e.message), None, sys.exc_info()[2]

    def load(self, yml_data):
        '''Loads a playbook from a yaml string.

        Keyword arguments:
        yml_data        -- The yaml string,
        '''
        try:
            return self._loader.load(yml_data, '<string>', show_content=True)
        except Exception, e:
            raise PlaybookLoadError('<string>', e.message), None, sys.exc_info()[2]

    def parse(self, loaded_data):
        '''Parse a plybook - represented as a AnsibleMapping - into a list of clusters and nodegroups.

        Keyword arguments:
        loaded_data     -- The AnsibleMapping representing the playbook,
        '''
        if not isinstance(loaded_data, dict):
            raise PlaybookParseError("Invalid cluster definition: please provide at least one cluster object.")

        # Parse the first level of the yaml document (loaded into a dictionary).
        # The first level is the list of clusters to be composed
        # Nb. the DataLoader provides guarantee that keys are unique within an element
        #  and therefore cluster name are uniques within cluster lists
        clusters = []
        for k1, v1 in loaded_data.iteritems():
            k1 = ansible_unwrap(k1)
            v1 = ansible_unwrap(v1)

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
                        raise PlaybookParseError("Error parsing cluster '%s': %s" % (k1, e.message))

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

            clusters.append(cluster)

        return clusters


    def compile(self, parsed_data):

        x = { 'nodes' : {} }

        for cluster in parsed_data:

            try:
                nodes, inventory, ansible_group_vars, ansible_host_vars = cluster.compose()
            except Exception, e:
                raise PlaybookCompileError(cluster.name, e.message), None, sys.exc_info()[2]

            for n in nodes:
                x['nodes'][n.hostname] = {
                    'box' : n.box,
                    'boxname' : n.boxname,
                    'hostname' : n.hostname,
                    'fqdn' : n.fqdn,
                    'aliases' : n.aliases,
                    'ip' : n.ip,
                    'cpus' : n.cpus,
                    'memory' : n.memory,
                    'ansible_groups' : n.ansible_groups,
                    'attributes' : n.attributes,
                    'index' : n.index,
                    'group_index' : n.group_index
                }

            #if len(ansible_group_vars)>0:


            #    if n.hostname in ansible_host_vars:
            #        x['nodes'][n.hostname]['host_vars'] = ansible_host_vars[n.hostname]

            #for g, h in ansible_groups_provision.iteritems():
            #    x['ansible_groups'][g] = {
            #        'hosts': h
            #    }

            #    if g in ansible_group_vars:
            #        x['ansible_groups'][g]['group_vars'] = ansible_group_vars[g]

        print(yaml.dump(x))

    def _get_object_attributes(self, instance):
        return [a for a in dir(instance) if not a.startswith('_') and not type(getattr(instance, a)) == types.MethodType]

# TODO: OK #1 vedere se necessario importare codice ansible o può essere usato come dipendenza "esterna"
# TODO: OK #2 capire meglio opzioni estensibilità del sistema di parsing - dove metto filtri custom etc. etc.
# TODO: #3 completare template to recipe e formato recipe
    # TODO: completare validazione di ansible_group_vars, ansible_context_vars, ansible_host_vars
# TODO: #4 estendere la parte ruby aggiungendo "from template" (chiama python e ottiene stream) e "from recipe" (prende recipe, valida e espone)
