import os, sys
sys.path.insert(0, '..')
from ido import call

def test_demo():
    """
    >>> call('ido install demo --nocolor') # doctest:+ELLIPSIS
    #   Found script file .../ido/packages/demo/install.ido of demo
    --> Installing package demo
        ==> echo "This is a demo"
        ==> echo "BUILD" is /tmp/ido_packages_build
    Installing package demo completed.
    #   The shell command result can be see in /tmp/ido.log

    """

def test_view_demo():
    """
    >>> call('ido view demo -d --nocolor') # doctest:+ELLIPSIS
    #   Found script file .../ido/packages/demo/install.ido of demo
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
    #   Found script file .../packages/pkg1/install.ido of pkg1
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
    #   Found script file .../packages/pkg2/install.ido of pkg2
    --> Installing package pkg2
        #   Found script file .../packages/pkg1/install.ido of pkg1
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
    #   Found script file .../ido/packages/ido_init.ido of ido_init
    --> Installing package ido_init
    PREFIX=/tmp/env
    BUILD=/tmp/ido_packages_build
    FILES=/tmp
    Installing package ido_init completed.
    #   The shell command result can be see in /tmp/ido.log

    """

def test_cd():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> call('ido install test_cd -i %s --nocolor' % packages) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_cd.ido of test_cd
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
    #   Found script file .../packages/test_unzip.ido of test_unzip
    --> Installing package test_unzip
        ==> cp .../files/pkg.zip /tmp/ido_packages_build
        ==> cd /tmp/ido_packages_build
        ==> unzip -o pkg.zip
        ==> cd pkg1
    True
    Installing package test_unzip completed.
    #   The shell command result can be see in /tmp/ido.log
    """

def test_createindex():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> call('ido createindex %s --nocolor' % packages) # doctest:+ELLIPSIS
    #   Index .../packages/index.txt created successful!
    """

def test_search():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> call('ido search pkg1 -i %s --nocolor' % packages) # doctest:+ELLIPSIS
    pkg1
    <BLANKLINE>
    """

def test_call():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> call('ido call test_call -i %s -t abc a b c --nocolor' % packages) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_call.ido of test_call
    --> Installing package test_call
    ['a', 'b', 'c']
    abc
    Installing package test_call completed.
    #   The shell command result can be see in /tmp/ido.log
    """

def test_info():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> call('ido info test_call -i %s --nocolor' % packages) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_call.ido of test_call
    --> Help package test_call
    Usage: ido call test_call [options] args
    <BLANKLINE>
    Options:
      -t TEST, --test=TEST  Test.
    """

def test_current_directory_search():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> os.chdir(packages)
    >>> call('ido info test_call --nocolor') # doctest:+ELLIPSIS
    #   Found script file .../packages/test_call.ido of test_call
    --> Help package test_call
    Usage: ido call test_call [options] args
    <BLANKLINE>
    Options:
      -t TEST, --test=TEST  Test.
    """

def test_md5():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install test_md5 -i %s -f %s --nocolor' % (packages, files)) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_md5.ido of test_md5
    --> Installing package test_md5
        ==> cp .../files/a.tar.gz /tmp/ido_packages_build
        ==> cd /tmp/ido_packages_build
        ==> md5sum a.tar.gz 831ba95422bf8356a303e1cdafe95ba5
    Installing package test_md5 completed.
    #   The shell command result can be see in /tmp/ido.log
    """

def test_md5_error():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install test_md5_error -i %s -f %s --nocolor' % (packages, files)) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_md5_error.ido of test_md5_error
    --> Installing package test_md5_error
        ==> cp .../files/a.tar.gz /tmp/ido_packages_build
        ==> cd /tmp/ido_packages_build
        ==> md5sum a.tar.gz 831ba95422bf8356a303e1cdafe95ba4
    Error: Installing package test_md5_error failed.
    #   The shell command result can be see in /tmp/ido.log
    """

def test_sha1():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> files = os.path.join(path, 'files')
    >>> call('ido install test_sha1 -i %s -f %s --nocolor' % (packages, files)) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_sha1.ido of test_sha1
    --> Installing package test_sha1
        ==> cp .../files/a.tar.gz /tmp/ido_packages_build
        ==> cd /tmp/ido_packages_build
        ==> sha1sum a.tar.gz 0f2f008da2728f3bace799f257c299ab15ae0c15
    Installing package test_sha1 completed.
    #   The shell command result can be see in /tmp/ido.log
    """

def test_whick():
    """
    >>> path = os.path.dirname(__file__)
    >>> packages = os.path.join(path, 'packages')
    >>> call('ido install test_which -i %s --nocolor' % packages) # doctest:+ELLIPSIS
    #   Found script file .../packages/test_which.ido of test_which
    --> Installing package test_which
        ==> which ls
        ==> which notexisted
    Error: Installing package test_which failed.
    #   The shell command result can be see in /tmp/ido.log
    """
