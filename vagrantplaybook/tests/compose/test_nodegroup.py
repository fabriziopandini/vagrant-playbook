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
            boxname = "{{group_name}}{{node_index + 1}}",
            hostname = "{{group_name}}{{node_index + 1}}",
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

    def test_maybeprefix(self):
        # none or empty cluster names does not prefix
        self.assertEqual(self.ng._maybe_prefix(None, "mygroup"), "mygroup")
        self.assertEqual(self.ng._maybe_prefix("", "mygroup"), "mygroup")
        # any cluster (not none/empty) name do prefix
        self.assertEqual(self.ng._maybe_prefix("mycluster", "mygroup"), "mycluster-mygroup")

    def test_unwrap(self):
        # TODO: test unwrapping
        pass

    def test_generate(self):
        # generate preserve literal values
        self.assertEqual(self.ng._generate(self.templar, "myVar", 1, 0), 1)
        self.assertEqual(self.ng._generate(self.templar, "myVar", 1.1, 0), 1.1)
        self.assertEqual(self.ng._generate(self.templar, "myVar", "s", 0), "s")
        self.assertEqual(self.ng._generate(self.templar, "myVar", [], 0), [])
        self.assertEqual(self.ng._generate(self.templar, "myVar", {}, 0), {})

        # generate resolve vars in context for value generation
        self.assertEqual(self.ng._generate(self.templar, "myVar", "{{group_name}}", 0), "mygroup")
        self.assertEqual(self.ng._generate(self.templar, "myVar", "{{group_index}}", 0), 1)
        self.assertEqual(self.ng._generate(self.templar, "myVar", "{{node_index}}", 0), 0)

        # generate raise errors on invalid template
        self.assertRaises(ValueGeneratorError, self.ng._generate, self.templar, "myVar", "{{unknown_var}}", 0)

        # generate raise errors when generated value does not match expected type
        self.assertRaises(ValueGeneratorTypeError, self.ng._generate, self.templar, "myVar", "s", 0, type = compat_integer_types)

    def test_compose(self):
        #compose generates expected nodes (and generates all attributes values)
        nodes = list(self.ng.compose(self.templar, "mycluster", "mydomain", 10))

        self.assertEqual(len(nodes), 3)

        self.assertEqual(nodes[0].box, "mybox")
        self.assertEqual(nodes[0].boxname, "mycluster-mygroup1")
        self.assertEqual(nodes[0].hostname, "mycluster-mygroup1")
        self.assertEqual(nodes[0].fqdn, "mycluster-mygroup1.mydomain")
        self.assertEqual(nodes[0].aliases, "a1,a2")
        self.assertEqual(nodes[0].ip, "172.31.1.101")
        self.assertEqual(nodes[0].cpus, 1)
        self.assertEqual(nodes[0].memory, 256)
        self.assertEqual(nodes[0].ansible_groups, [])
        self.assertEqual(nodes[0].attributes, {})
        self.assertEqual(nodes[0].index, 10)
        self.assertEqual(nodes[0].group_index, 0)

        self.assertEqual(nodes[1].box, "mybox")
        self.assertEqual(nodes[1].boxname, "mycluster-mygroup2")
        self.assertEqual(nodes[1].hostname, "mycluster-mygroup2")
        self.assertEqual(nodes[1].fqdn, "mycluster-mygroup2.mydomain")
        self.assertEqual(nodes[1].aliases, "a1,a2")
        self.assertEqual(nodes[1].ip, "172.31.1.102")
        self.assertEqual(nodes[1].cpus, 1)
        self.assertEqual(nodes[1].memory, 256)
        self.assertEqual(nodes[1].ansible_groups, [])
        self.assertEqual(nodes[1].attributes, {})
        self.assertEqual(nodes[1].index, 11)
        self.assertEqual(nodes[1].group_index, 1)

        self.assertEqual(nodes[2].box, "mybox")
        self.assertEqual(nodes[2].boxname, "mycluster-mygroup3")
        self.assertEqual(nodes[2].hostname, "mycluster-mygroup3")
        self.assertEqual(nodes[2].fqdn, "mycluster-mygroup3.mydomain")
        self.assertEqual(nodes[2].aliases, "a1,a2")
        self.assertEqual(nodes[2].ip, "172.31.1.103")
        self.assertEqual(nodes[2].cpus, 1)
        self.assertEqual(nodes[2].memory, 256)
        self.assertEqual(nodes[2].ansible_groups, [])
        self.assertEqual(nodes[2].attributes, {})
        self.assertEqual(nodes[2].index, 12)
        self.assertEqual(nodes[2].group_index, 2)
