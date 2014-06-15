import sys
sys.path.insert(0, '..')
from ido import call

def test_command_1():
    """
    >>> call('ido install demo --nocolor')
    << Installing package demo
       do: echo "This is a demo"
       do: echo "BUILD" is /tmp/ido_packages_build
          Installing package demo completed.
    The shell command result can be see in /tmp/ido.log

    """