import sys
sys.path.insert(0, '..')
from ido import call

def test_demo():
    """
    >>> call('ido install demo --nocolor') # doctest:+ELLIPSIS
    << Installing package demo
       do: echo "This is a demo"
       do: echo "BUILD" is /tmp/ido_packages_build
          Installing package demo completed.
    The shell command result can be see in /tmp/ido.log

    """

def test_view_demo():
    """
    >>> call('ido view demo -d')
    sh('echo "This is a demo"')
    sh('echo "BUILD" is '+BUILD)
    <BLANKLINE>
    """