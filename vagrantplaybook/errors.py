from __future__ import (absolute_import, division, print_function)
__metaclass__ = type 

class ComposeError(Exception):
    ''' Base class for exceptions in this module. '''
    def __str__(self):
        return self.message

    def __repr__(self):
        return self.message

class ValueGeneratorError(ComposeError):
    ''' Class for handling errors raised by value generators in NodeGroup compose. '''

    def __init__(self, group_name, node_index, var, message):
        self.message = 'Error generating value "%s" for Node number %i, NodeGroup "%s" : %s' % (var, node_index, group_name, message)

class ValueGeneratorTypeError(ComposeError):
    ''' Class for handling errors raised by value generators in NodeGroup compose. '''

    def __init__(self, group_name, node_index, var, message):
        self.message = 'Invalid value for "%s" in Node number %i, NodeGroup "%s" : %s' % (var, node_index, group_name, message)

class ContextVarGeneratorError(ComposeError):
    ''' Class for handling errors raised by context var generators in Cluster compose. '''

    def __init__(self, ansible_group, var_name, message):
        self.message = 'Error generating context var "%s" for ansible_group "%s" : %s' % (var_name, ansible_group, message)

class GroupVarGeneratorError(ComposeError):
    ''' Class for handling errors raised by group var generators in Cluster compose. '''

    def __init__(self, ansible_group, var_name, message):
        self.message = 'Error generating group var "%s" for ansible_group "%s" : %s' % (var_name, ansible_group, message)

class HostVarGeneratorError(ComposeError):
    ''' Class for handling errors raised by host var generators in Cluster compose. '''

    def __init__(self, host, var_name, message):
        self.message = 'Error generating host var "%s" for host "%s" : %s' % (var_name, host, message)


class PlaybookLoadError(ComposeError):
    ''' Class for handling errors raised when loading playbook. '''

    def __init__(self, filename, message):
        self.message = 'Error loading playbook data from "%s": %s' % (filename, message)

class PlaybookParseError(ComposeError):
    ''' Class for handling errors raised when parsing playbook. '''

    def __init__(self, message):
        self.message = 'Error parsing playbook: %s' % (message)

class PlaybookCompileError(ComposeError):
    ''' Class for handling errors raised when parsing playbook. '''

    def __init__(self, cluster, message):
        self.message = 'Error compiling cluster "%s": %s ' % (cluster, message)
