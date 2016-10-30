# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

import json
from unittest import TestCase

from vagrantplaybook.ansible import ansible_loader

from vagrantplaybook.compose.cluster import Cluster

setup_done = False

class TestCluster(TestCase):

    def setUp(self):
        dataloader = ansible_loader()
        self.myCluster = Cluster("myCluster", loader = dataloader)

        g1 = self.myCluster.add_node_group("nodegroup_1", 1)
        g1.ansible_groups = ["ansiblegroup_A", "ansiblegroup_B"]

        g2 = self.myCluster.add_node_group("nodegroup_2", 2)
        g2.ansible_groups = ["ansiblegroup_B"]

        self.nodes = self.myCluster._get_nodes()
        self.ansible_groups = self.myCluster._get_ansible_groups(self.nodes)

    def test_attributes_validation(self):
        #TODO: test validation
        pass

    def test_add_nodes(self):
        # assert expected node groups are in the cluster
        self.assertEqual(len(self.myCluster._node_groups), 2)

        # assert node groups attributes gets default values/assigned values
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].index, 0) #computed
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].name, "nodegroup_1")
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].instances, 1)
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].box, self.myCluster.box)
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].boxname, "{{group_name}}{{node_index + 1}}")
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].hostname, "{{group_name}}{{node_index + 1}}")
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].aliases, "")
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].ip, "172.31.{{group_index}}.{{100 + node_index + 1}}")
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].cpus, 1)
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].memory, 256)
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].ansible_groups, ["ansiblegroup_A", "ansiblegroup_B"])
        self.assertEqual(self.myCluster._node_groups["nodegroup_1"].attributes, {})

        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].index, 1) #computed
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].name, "nodegroup_2")
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].instances, 2)
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].box, self.myCluster.box)
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].boxname, "{{group_name}}{{node_index + 1}}")
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].hostname, "{{group_name}}{{node_index + 1}}")
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].aliases, "")
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].ip, "172.31.{{group_index}}.{{100 + node_index + 1}}")
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].cpus, 1)
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].memory, 256)
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].ansible_groups, ["ansiblegroup_B"])
        self.assertEqual(self.myCluster._node_groups["nodegroup_2"].attributes, {})

    def test_get_nodes(self):
        '''_get_nodes transforms all nodegroups in nodes'''

        # assert expected nodes are in the cluster
        self.assertEqual(len(self.nodes), 3)

        hostnames = [n.hostname for n in self.nodes]
        self.assertIn("myCluster-nodegroup_11", hostnames)
        self.assertIn("myCluster-nodegroup_21", hostnames)
        self.assertIn("myCluster-nodegroup_22", hostnames)

    def test_get_ansible_inventory(self):
        inventory = self.myCluster._get_ansible_inventory(self.ansible_groups)

        # assert expected nodes are in the cluster
        self.assertEqual(len(inventory), 2)

        # ansiblegroup_A (with related nodes)
        self.assertIn("ansiblegroup_A", inventory)
        self.assertEqual(len(inventory["ansiblegroup_A"]), 1)
        self.assertIn("myCluster-nodegroup_11", inventory["ansiblegroup_A"])

        # ansiblegroup_B (with related nodes)
        self.assertIn("ansiblegroup_B", inventory)
        self.assertEqual(len(inventory["ansiblegroup_B"]), 3)
        self.assertIn("myCluster-nodegroup_11", inventory["ansiblegroup_B"])
        self.assertIn("myCluster-nodegroup_21", inventory["ansiblegroup_B"])
        self.assertIn("myCluster-nodegroup_22", inventory["ansiblegroup_B"])

    def test_get_ansible_groups(self):
        '''_get_ansible_groups re-arrange nodes into ansible_groups'''

        # assert expected nodes are in the cluster
        self.assertEqual(len(self.ansible_groups), 2)

        # ansiblegroup_A (with related nodes)
        self.assertIn("ansiblegroup_A", self.ansible_groups)
        self.assertEqual(len(self.ansible_groups["ansiblegroup_A"]), 1)
        hostnames = [n.hostname for n in self.ansible_groups["ansiblegroup_A"]]
        self.assertIn("myCluster-nodegroup_11", hostnames)

        # ansiblegroup_B (with related nodes)
        self.assertIn("ansiblegroup_B", self.ansible_groups)
        self.assertEqual(len(self.ansible_groups["ansiblegroup_B"]), 3)
        hostnames = [n.hostname for n in self.ansible_groups["ansiblegroup_B"]]
        self.assertIn("myCluster-nodegroup_11", hostnames)
        self.assertIn("myCluster-nodegroup_21", hostnames)
        self.assertIn("myCluster-nodegroup_22", hostnames)

    def test_get_context_vars(self):
        '''_get_context_vars computes context_vars'''

        # defines a sample set of context_vars generators
        self.myCluster.ansible_context_vars = {
            "ansiblegroup_A" : {
                "var1" : "{{ nodes | count }}"
            },
            "ansiblegroup_B" : {
                "var2" : "{{ nodes | count }}",
                "var3" : "literal"
            }
        }

        context_vars = self.myCluster._get_context_vars(self.ansible_groups)

        # assert expected context_vars are available
        self.assertEqual(len(context_vars), 3)

        self.assertEqual(context_vars["var1"], "1")
        self.assertEqual(context_vars["var2"], "3")
        self.assertEqual(context_vars["var3"], "literal")

    def test_get_ansible_group_vars(self):
        '''_get_ansible_group_vars computes group vars'''

        # defines a sample set of ansible_group_vars generators
        self.myCluster.ansible_group_vars = {
            "ansiblegroup_A" : {
                "var1" : "{{ nodes | count }}"
            },
            "ansiblegroup_B" : {
                "var2" : "{{ nodes | count }}",
                "var3" : "literal"
            }
        }

        group_vars = self.myCluster._get_ansible_group_vars(self.ansible_groups, {})

        # assert expected ansible_group_vars are available
        self.assertEqual(len(group_vars), 2)

        self.assertEqual(len(group_vars["ansiblegroup_A"]), 1)
        self.assertEqual(group_vars["ansiblegroup_A"]["var1"], "1")

        self.assertEqual(len(group_vars["ansiblegroup_B"]), 2)
        self.assertEqual(group_vars["ansiblegroup_B"]["var2"], "3")
        self.assertEqual(group_vars["ansiblegroup_B"]["var3"], "literal")


    def test_get_ansible_host_vars(self):
        '''_get_ansible_host_vars computes host vars'''

        # defines a sample set of ansible_host_vars generators
        self.myCluster.ansible_host_vars = {
            "ansiblegroup_A" : {
                "var1" : "{{ node.hostname }}"
            },
            "ansiblegroup_B" : {
                "var2" : "{{ node.ip }}"
            }
        }

        host_vars = self.myCluster._get_ansible_host_vars(self.nodes, {})

        # assert expected ansible_host_vars are available
        self.assertEqual(len(host_vars), 3)

        self.assertEqual(len(host_vars["myCluster-nodegroup_11"]), 2)
        self.assertEqual(host_vars["myCluster-nodegroup_11"]["var1"], "myCluster-nodegroup_11")
        self.assertEqual(host_vars["myCluster-nodegroup_11"]["var2"], "172.31.0.101")

        self.assertEqual(len(host_vars["myCluster-nodegroup_21"]), 1)
        self.assertEqual(host_vars["myCluster-nodegroup_21"]["var2"], "172.31.1.101")

        self.assertEqual(len(host_vars["myCluster-nodegroup_22"]), 1)
        self.assertEqual(host_vars["myCluster-nodegroup_22"]["var2"], "172.31.1.102")

    def test_execute(self):
        '''compose generate the cluster'''

        # defines a sample set of ansible_group_vars generators
        self.myCluster.ansible_group_vars = {
            "ansiblegroup_A" : {
                "var1" : "{{ nodes | count }}"
            },
            "ansiblegroup_B" : {
                "var2" : "{{ nodes | count }}",
                "var3" : "literal"
            }
        }

        # defines a sample set of ansible_host_vars generators
        self.myCluster.ansible_host_vars = {
            "ansiblegroup_A" : {
                "var1" : "{{ node.hostname }}"
            },
            "ansiblegroup_B" : {
                "var2" : "{{ node.ip }}"
            }
        }

        nodesmap, inventory, ansible_group_vars, ansible_host_vars = self.myCluster.compose()

        print (nodesmap)

        # assert expected nodes are available
        self.assertEqual(len(nodesmap), 3)
        # assert expected ansible_group_vars are available
        self.assertEqual(len(ansible_group_vars), 2)
        # assert expected ansible_host_vars are available
        self.assertEqual(len(ansible_host_vars), 3) # one for each node
