from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

__version__ = '0.1'

import os, sys
import datetime
import inspect
import traceback
from optparse import make_option
from .commands import call, register_command, Command, get_answer, get_input

from colorama import init, Fore, Back, Style
init(autoreset=True)

class Error(Exception): pass

class ObjectDict(dict):
    """Makes a dictionary behave like an object, with attribute-style access.
    """
    def __getattr__(self, name):
        try:
            return self[name]
        except KeyError:
            raise AttributeError(name)

    def __setattr__(self, name, value):
        self[name] = value

class InstallCommand(Command):
    """
    Install a package, the package will be searched order by:

    """
    name = 'install'
    help = ("Install or execute a pacage")
    args = '[package, package...]'
    option_list = (
        make_option('-i', '--index', dest='index', default=[], action='append',
            help='Package index link, it can be a directory or an url.'),
        make_option('-E', dest='vars', default=[], action='append', metavar='ENV_VAR',
            help='Define variables and will passed to installation scripts.'),
        make_option('-p', '--prefix', dest='prefix', default='',
            help='Prefix value when compile and install source packages.'),
        make_option('-l', '--log', dest='log', default='',
            help='Log filename the shell outut will be written in it.'),
        make_option('-f', '--files', dest='files', default='',
            help='Source packages storage directory.'),
   )

    def collection_index(self, options):
        """
        Collection index link to self.indexes, the order should be:
        1. command argument
        2. environment
        3. default packages directory
        """

        self.indexes = options.index
        if 'IDO_PACKAGES' in os.environ:
            self.indexes.append(os.environ['IDO_PACKAGES'])

        self.indexes.append(os.path.join(os.path.dirname(__file__), 'packages').replace('\\', '/'))

    def find_package_script(self, package):
        for i in self.indexes:
            install_script = os.path.join(i, package, 'install.py')
            #test if is locally
            if os.path.exists(install_script):
                return install_script, open(install_script).read()

            #test if is in the net

    def handle(self, options, global_options, *args):
        self.verbose = global_options.verbose
        self.log = None
        if options.log:
            self.log = open(options.log, 'w')
        elif not self.verbose:
            now = datetime.datetime.now()
            # log_file = '/tmp/ido.%s.log' % now.strftime("%Y%m%d%H%M%S")
            log_file = '/tmp/ido.log'
            self.log = open(log_file, 'w')

        self.collection_index(options)

        self.quiet = True
        self.install('ido_init')
        self.quiet = False

        try:
            for p in args:
                self.install(p, True)
        finally:
            if self.log:
                log_file = self.log.name
                self.log.close()
                self.log = None
                self.message("The shell command result can be see in %s" % log_file)

    def make_env(self, script, code):
        from . import utils

        d = {}
        self.build = d['BUILD'] = '/tmp/ido_packages_build'
        self.cache = d['CACHE'] = os.path.expandvars('$HOME/.ido/cache')
        #PREFIX will be used to install package with prefix=
        #it can be set in environment variables as IDO_PREFIX
        #or passed in command argumanet -p --prefix
        self.prefix = d['PREFIX'] = self.options.prefix or os.environ.get('IDO_PREFIX', '')
        self.home = d['HOME'] = os.environ['HOME']
        self.files = d['FILES'] = self.options.files or os.environ.get('IDO_FILES', '')
        d['install'] = self.install

        for k in dir(utils):
            v = getattr(utils, k)
            if inspect.isclass(v) and issubclass(v, utils.Function):
                if not v.name: continue
                inst = v(build=self, log=self.log, verbose=self.global_options.verbose,
                         message=self.message)
                d[inst.name] = inst

        d['os'] = os
        d['sys'] = sys

        d['message'] = self.message

        d['Fore'] = Fore
        d['Back'] = Back
        d['Style'] = Style

        d['__name__'] = script
        d['__loader__'] = ObjectDict(get_source=lambda name: code)

        for x in self.options.vars:
            k, v = (x.split('=') + [''])[:2]
            d[k] = v

        return d

    def install(self, package, first=False):
        from future.utils import exec_

        script = self.find_package_script(package)
        if script:
            script, code = script
        else:
            if first:
                self.message("Can't find the installation script of package %s" % (Fore.GREEN+Style.BRIGHT+package), 'error')
                return
            else:
                raise Error("Can't find the installation script of package %s" % package)

        self.message("Installing package %s" % (Fore.GREEN+package), 'install')
        try:
            d = self.make_env(script, code)
            c_code = compile(code, script, 'exec', dont_inherit=True)
            exec_(c_code, d)
            self.message("Installing package %s completed." % package, 'info')
            flag = True
        except Exception as e:
            flag = False
            if self.verbose:
                type, value, tb = sys.exc_info()
                txt =  ''.join(traceback.format_exception(type, value, tb))
                print (txt)
            if first:
                self.message("Installing package %s failed." % package, 'error')
            else:
                raise

    def message(self, msg, _type=''):

        if self.quiet:
            return

        RESET = Fore.RESET + Back.RESET + Style.RESET_ALL

        if _type == 'error':
            print (Fore.RED+'Error: '+msg)
        elif _type == 'cmd':
            print (Fore.BLUE+Style.BRIGHT+'   do: '+Fore.MAGENTA+msg)
        elif _type == 'install':
            print (Fore.BLUE+Style.BRIGHT+'<< '+msg)
        elif _type == 'info':
            print (Fore.GREEN+'      '+msg)
        else:
            print (msg)

        if self.log:
            self.log.write(msg)
            self.log.write('\n')

register_command(InstallCommand)

def main():
    call('ido', __version__)
