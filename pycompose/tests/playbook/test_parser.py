# -*- coding: utf-8 -*-
from __future__ import (absolute_import, division, print_function)
__metaclass__ = type

from nose import tools
from unittest import TestCase

from pycompose.errors import PlaybookLoadError, PlaybookParseError
from pycompose.playbook.parser import Parser

from pycompose.tests.playbook.sample.load import sample_load
from pycompose.tests.playbook.sample.load import sample_load_witherrors
from pycompose.tests.playbook.sample.parse import sample_execute_no_cluster
from pycompose.tests.playbook.sample.parse import sample_execute_cluster_empty
from pycompose.tests.playbook.sample.parse import sample_execute_cluster_not_object
from pycompose.tests.playbook.sample.parse import sample_execute_nodegroup_empty
from pycompose.tests.playbook.sample.parse import sample_execute_nodegroup_with_attributes
from pycompose.tests.playbook.sample.compile import sample_compile_base

class TestNodeGroup(TestCase):

    def setUp(self):
        self._parser = Parser()

    def test_load_from_file(self):
        # load_from_file reads a yml into an dict
        data = self._parser.load_from_file('pycompose/tests/playbook/sample/load_from_file.yml')
        assert isinstance(data, dict)

        self.assertIn('mesos', data)
        self.assertIn('master', data['mesos'])
        self.assertIn('slave', data['mesos'])
        self.assertIn('registry', data['mesos'])

        # load_from_file handles errors
        self.assertRaises(PlaybookLoadError, self._parser.load_from_file, 'pycompose/tests/playbook/sample/load_from_file_not_exists.yml')
        self.assertRaises(PlaybookLoadError, self._parser.load_from_file, 'pycompose/tests/playbook/sample/load_from_file_witherrors.yml')

    def test_load(self):
        # load_from_file reads a yml into an dict
        data = self._parser.load(sample_load)
        assert isinstance(data, dict)

        self.assertIn('mesos', data)
        self.assertIn('master', data['mesos'])
        self.assertIn('slave', data['mesos'])
        self.assertIn('registry', data['mesos'])

        # load_from_file handles errors
        self.assertRaises(PlaybookLoadError, self._parser.load, sample_load_witherrors)

    def _test_parse(self, data):
        return self._parser.parse(self._parser.load(data))

    def test_parse(self):
        # execute with no clusters gives errors
        self.assertRaises(PlaybookParseError, self._test_parse, sample_execute_no_cluster)

        # execute with invalid cluster gives errors
        self.assertRaises(PlaybookParseError, self._test_parse, sample_execute_cluster_empty)
        self.assertRaises(PlaybookParseError, self._test_parse, sample_execute_cluster_not_object)

        # execute with empty NodeGroup works
        clusters = self._test_parse(sample_execute_nodegroup_empty)
        self.assertEqual(len(clusters), 1)
        self.assertEqual(len(clusters[0]._node_groups), 1)
        self.assertEqual(clusters[0]._node_groups["zookeeper"].instances, 1)

        # execute with NodeGroup works
        clusters = self._test_parse(sample_execute_nodegroup_with_attributes)
        self.assertEqual(len(clusters[0]._node_groups), 1)
        self.assertEqual(clusters[0]._node_groups["zookeeper"].instances, 3)

    def _test_compile(self, data):
        return self._parser.compile(self._test_parse(data))

    def test_compile(self):
        # execute with no clusters gives errors

        self._test_compile(sample_compile_base)
