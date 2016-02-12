from __future__ import print_function

from argparse import Action
import os

# http://stackoverflow.com/questions/10551117/setting-options-from-environment-variables-when-using-argparse
class EnvDefault(Action):
    """Inspects the environment for a variable
    before looking for a command line value"""
    def __init__(self, envvar, required=True, default=None, **kwargs):
        if not default and envvar:
            if envvar in os.environ:
                default = os.environ[envvar]
        if required and default:
            required = False
        super(EnvDefault, self).__init__(default=default, required=required,
                                         **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        setattr(namespace, self.dest, values)
