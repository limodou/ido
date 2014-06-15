import os, sys
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

def test_pkg1():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install pkg1 -i %s -f %s --nocolor' % (packages, files))
    << Installing package pkg1
       do: tar xvfz a.tar.gz
          Installing package pkg1 completed.
    The shell command result can be see in /tmp/ido.log
    >>> print (open('/tmp/ido_packages_build/a.txt').read())
    This is a demo.
    <BLANKLINE>
    """

def test_pkg2():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install pkg2 -i %s -f %s --nocolor' % (packages, files))
    << Installing package pkg2
    << Installing package pkg1
       do: tar xvfz a.tar.gz
          Installing package pkg1 completed.
          Installing package pkg2 completed.
    The shell command result can be see in /tmp/ido.log
    """