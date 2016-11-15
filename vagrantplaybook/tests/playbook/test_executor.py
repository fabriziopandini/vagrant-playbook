# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from nose import tools
from unittest import TestCase

from vagrantplaybook.errors import PlaybookLoadError, PlaybookParseError
from vagrantplaybook.playbook.executor import Executor

from vagrantplaybook.tests.playbook.sample.load import sample_load
from vagrantplaybook.tests.playbook.sample.load import sample_load_witherrors
from vagrantplaybook.tests.playbook.sample.parse import sample_execute_no_cluster
from vagrantplaybook.tests.playbook.sample.parse import sample_execute_cluster_empty
from vagrantplaybook.tests.playbook.sample.parse import sample_execute_cluster_not_object
from vagrantplaybook.tests.playbook.sample.parse import sample_execute_nodegroup_empty
from vagrantplaybook.tests.playbook.sample.parse import sample_execute_nodegroup_with_attributes
from vagrantplaybook.tests.playbook.sample.yaml import sample_yaml

class TestExecutor(TestCase):

    def setUp(self):
        self._executor = Executor()

    def test_load_from_file(self):
        # load_from_file reads a yml into an dict
        data = self._executor._load_from_file('vagrantplaybook/tests/playbook/sample/load_from_file.yml')
        assert isinstance(data, dict)

        self.assertIn('mesos', data)
        self.assertIn('master', data['mesos'])
        self.assertIn('slave', data['mesos'])
        self.assertIn('registry', data['mesos'])

        # load_from_file handles errors
        self.assertRaises(PlaybookLoadError, self._executor._load_from_file, 'vagrantplaybook/tests/playbook/sample/load_from_file_not_exists.yml')
        self.assertRaises(PlaybookLoadError, self._executor._load_from_file, 'vagrantplaybook/tests/playbook/sample/load_from_file_witherrors.yml')

    def test_load(self):
        # load_from_file reads a yml into an dict
        data = self._executor._load(sample_load)
        assert isinstance(data, dict)

        self.assertIn('mesos', data)
        self.assertIn('master', data['mesos'])
        self.assertIn('slave', data['mesos'])
        self.assertIn('registry', data['mesos'])

        # load_from_file handles errors
        self.assertRaises(PlaybookLoadError, self._executor._load, sample_load_witherrors)

    def _test_parse(self, data):
        return self._executor._parse(self._executor._load(data))

    def test_parse(self):
        # execute with no clusters gives errors
        self.assertRaises(PlaybookParseError, self._test_parse, sample_execute_no_cluster)

        # execute with invalid cluster gives errors
        self.assertRaises(PlaybookParseError, self._test_parse, sample_execute_cluster_empty)
        self.assertRaises(PlaybookParseError, self._test_parse, sample_execute_cluster_not_object)

        # execute with empty NodeGroup works
        cluster = self._test_parse(sample_execute_nodegroup_empty)
        self.assertEqual(len(cluster._node_groups), 1)
        self.assertEqual(cluster._node_groups["zookeeper"].instances, 1)

        # execute with NodeGroup works
        cluster = self._test_parse(sample_execute_nodegroup_with_attributes)
        self.assertEqual(len(cluster._node_groups), 1)
        self.assertEqual(cluster._node_groups["zookeeper"].instances, 3)

    def _test_compose(self, data):
        cluster = self._test_parse(data)
        nodes, inventory, ansible_group_vars, ansible_host_vars = self._executor._compose(cluster)
        return cluster, nodes, inventory, ansible_group_vars, ansible_host_vars

    def test_compose(self):
        return #no tests on compose (it is only a wrapper on cluster compose)

    def _test_yaml(self, data):
        cluster, nodes, inventory, ansible_group_vars, ansible_host_vars = self._test_compose(data)
        return self._executor._yaml(cluster, nodes, inventory, ansible_group_vars, ansible_host_vars)

    #def test_yaml(self):
    #    yaml =  self._test_yaml(sample_yaml)

    #    print(yaml)
