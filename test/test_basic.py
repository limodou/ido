import os, sys
sys.path.insert(0, '..')
from ido import call

def test_demo():
    """
    >>> call('ido install demo --nocolor') # doctest:+ELLIPSIS
    #   Found script file .../ido/packages/demo/install.py of demo
    --> Installing package demo
        ==> echo "This is a demo"
        ==> echo "BUILD" is /tmp/ido_packages_build
    Installing package demo completed.
    #   The shell command result can be see in /tmp/ido.log

    """

def test_view_demo():
    """
    >>> call('ido view demo -d --nocolor') # doctest:+ELLIPSIS
    #   Found script file .../ido/packages/demo/install.py of demo
    sh('echo "This is a demo"')
    sh('echo "BUILD" is '+BUILD)
    <BLANKLINE>
    """

def test_pkg1():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install pkg1 -i %s -f %s --nocolor' % (packages, files)) # doctest:+ELLIPSIS
    #   Found script file .../packages/pkg1/install.py of pkg1
    --> Installing package pkg1
        ==> cp .../files/a.tar.gz /tmp/ido_packages_build
        ==> cd /tmp/ido_packages_build
        ==> tar xvfz a.tar.gz
    Installing package pkg1 completed.
    #   The shell command result can be see in /tmp/ido.log
    >>> print (open('/tmp/ido_packages_build/a.txt').read())
    This is a demo.
    <BLANKLINE>
    """

def test_pkg2():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install pkg2 -i %s -f %s --nocolor' % (packages, files)) # doctest:+ELLIPSIS
    #   Found script file .../packages/pkg2/install.py of pkg2
    --> Installing package pkg2
        #   Found script file .../packages/pkg1/install.py of pkg1
        --> Installing package pkg1
            ==> cp .../files/a.tar.gz /tmp/ido_packages_build
            ==> cd /tmp/ido_packages_build
            ==> tar xvfz a.tar.gz
        Installing package pkg1 completed.
    Installing package pkg2 completed.
    #   The shell command result can be see in /tmp/ido.log
    """

def test_settings():
    """
    >>> path = os.path.dirname(__file__)
    >>> settings_file = os.path.join(path, 'settings.py')
    >>> call('ido install ido_init -c %s --nocolor' % settings_file) # doctest:+ELLIPSIS
    #   Found script file .../ido/packages/ido_init.py of ido_init
    --> Installing package ido_init
    PREFIX=/tmp/env
    HOME=/Users/limodou
    BUILD=/tmp/ido_packages_build
    FILES=/tmp
    CACHE=.../.ido/cache
    Installing package ido_init completed.
    #   The shell command result can be see in /tmp/ido.log

    """

def test_cd():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> call('ido install test_cd -i %s --nocolor' % packages) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_cd.py of test_cd
    --> Installing package test_cd
        ==> cd /usr
    True
    True
    Installing package test_cd completed.
    #   The shell command result can be see in /tmp/ido.log
    """

def test_unzip():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install test_unzip -i %s -f %s --nocolor' % (packages, files)) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_unzip.py of test_unzip
    --> Installing package test_unzip
        ==> cp .../files/pkg.zip /tmp/ido_packages_build
        ==> cd /tmp/ido_packages_build
        ==> unzip -o pkg.zip
        ==> cd pkg1
    True
    Installing package test_unzip completed.
    #   The shell command result can be see in /tmp/ido.log
    """
