# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from nose import tools
from unittest import TestCase

from vagrantplaybook.compat import compat_integer_types
from vagrantplaybook.ansible import ansible_loader, ansible_tempar

from vagrantplaybook.errors import ValueGeneratorError, ValueGeneratorTypeError
from vagrantplaybook.compose.nodegroup import NodeGroup

class TestNodeGroup(TestCase):

    def setUp(self):
        # a sample cluster
        self.ng = NodeGroup(
            index = 1,
            name = "mygroup",
            instances = 3,
            box = "mybox",
            boxname = "{% if cluster_node_prefix %}{{cluster_node_prefix}}-{% endif %}{{group_name}}{{node_index + 1}}",
            hostname = "{% if cluster_node_prefix %}{{cluster_node_prefix}}-{% endif %}{{group_name}}{{node_index + 1}}",
            fqdn = "{% if cluster_node_prefix %}{{cluster_node_prefix}}-{% endif %}{{group_name}}{{node_index + 1}}{% if cluster_domain %}.{{cluster_domain}}{% endif %}",
            aliases = ["a1", "a2"],
            ip = "172.31.{{group_index}}.{{100 + node_index + 1}}",
            cpus = 1,
            memory = 256,
            ansible_groups = [],
            attributes = {}
        )

        #creates the ansible templar
        dataloader = ansible_loader()
        self.templar = ansible_tempar(dataloader)

    def test_attributes_validation(self):
        #TODO: test validation
        pass

    def test_unwrap(self):
        # TODO: test unwrapping
        pass

    def test_generate(self):
        # generate preserve literal values
        self.assertEqual(self.ng._generate(self.templar, "myVar", 1, dict())[0], 1)
        self.assertEqual(self.ng._generate(self.templar, "myVar", 1.1, dict())[0], 1.1)
        self.assertEqual(self.ng._generate(self.templar, "myVar", "s", dict())[0], "s")
        self.assertEqual(self.ng._generate(self.templar, "myVar", [], dict())[0], [])
        self.assertEqual(self.ng._generate(self.templar, "myVar", {}, dict())[0], {})

        # generate resolve vars in context for value generation
        self.assertEqual(self.ng._generate(self.templar, "myVar", "{{group_name}}", dict(group_name="mygroup"))[0], "mygroup")
        self.assertEqual(self.ng._generate(self.templar, "myVar", "{{group_index}}", dict(group_index=1))[0], 1)
        self.assertEqual(self.ng._generate(self.templar, "myVar", "{{node_index}}", dict(node_index=0))[0], 0)

        # generate popolate dict
        available_variables = self.ng._generate(self.templar, "myVar", 1, dict())[1]

        self.assertIn("myVar", available_variables)
        self.assertEqual(available_variables["myVar"], 1)

        # generate raise errors on invalid template
        self.assertRaises(ValueGeneratorError, self.ng._generate, self.templar, "myVar", "{{unknown_var}}", dict(node_index=0))

        # generate raise errors when generated value does not match expected type
        self.assertRaises(ValueGeneratorTypeError, self.ng._generate, self.templar, "myVar", "s", dict(node_index=0), type = compat_integer_types)

    def test_compose(self):
        #compose generates expected nodes (and generates all attributes values)
        nodes = list(self.ng.compose(self.templar, "mycluster", "myprefix", "mydomain", 10))

        self.assertEqual(len(nodes), 3)

        self.assertEqual(nodes[0].box, "mybox")
        self.assertEqual(nodes[0].boxname, "myprefix-mygroup1")
        self.assertEqual(nodes[0].hostname, "myprefix-mygroup1")
        self.assertEqual(nodes[0].fqdn, "myprefix-mygroup1.mydomain")
        self.assertEqual(nodes[0].aliases, ['a1', 'a2'])
        self.assertEqual(nodes[0].ip, "172.31.1.101")
        self.assertEqual(nodes[0].cpus, 1)
        self.assertEqual(nodes[0].memory, 256)
        self.assertEqual(nodes[0].ansible_groups, [])
        self.assertEqual(nodes[0].attributes, {})
        self.assertEqual(nodes[0].index, 10)
        self.assertEqual(nodes[0].group_index, 0)

        self.assertEqual(nodes[1].box, "mybox")
        self.assertEqual(nodes[1].boxname, "myprefix-mygroup2")
        self.assertEqual(nodes[1].hostname, "myprefix-mygroup2")
        self.assertEqual(nodes[1].fqdn, "myprefix-mygroup2.mydomain")
        self.assertEqual(nodes[1].aliases, ['a1', 'a2'])
        self.assertEqual(nodes[1].ip, "172.31.1.102")
        self.assertEqual(nodes[1].cpus, 1)
        self.assertEqual(nodes[1].memory, 256)
        self.assertEqual(nodes[1].ansible_groups, [])
        self.assertEqual(nodes[1].attributes, {})
        self.assertEqual(nodes[1].index, 11)
        self.assertEqual(nodes[1].group_index, 1)

        self.assertEqual(nodes[2].box, "mybox")
        self.assertEqual(nodes[2].boxname, "myprefix-mygroup3")
        self.assertEqual(nodes[2].hostname, "myprefix-mygroup3")
        self.assertEqual(nodes[2].fqdn, "myprefix-mygroup3.mydomain")
        self.assertEqual(nodes[2].aliases, ['a1', 'a2'])
        self.assertEqual(nodes[2].ip, "172.31.1.103")
        self.assertEqual(nodes[2].cpus, 1)
        self.assertEqual(nodes[2].memory, 256)
        self.assertEqual(nodes[2].ansible_groups, [])
        self.assertEqual(nodes[2].attributes, {})
        self.assertEqual(nodes[2].index, 12)
        self.assertEqual(nodes[2].group_index, 2)
