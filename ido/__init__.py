from __future__ import print_function, absolute_import, unicode_literals
import os, sys
import datetime
import inspect
import traceback
import re
from optparse import make_option
from .commands import register_command, Command, get_answer, get_input, \
    CommandManager, OptionParser, NewOptionParser, NewFormatter
from colorama import init, Fore, Back, Style
from functools import partial

__version__ = '0.4'

#init(autoreset=True)

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

def import_(path):
    """
    Import string format module, e.g. 'uliweb.orm' or an object
    return module object and object
    """
    if isinstance(path, str):
        v = path.split(':')
        if len(v) == 1:
            x = path.rsplit('.', 1)
            if len(x) == 2:
                module, func = x
            else:
                module, func = x[0], ''
        else:
            module, func = v
        mod = __import__(module)
        f = mod
        if func:
            for x in func.split('.'):
                f = getattr(f, x)
    else:
        f = path
    return f

r_ansi = re.compile(r'\x1b\[\d+\w(;\d+\w)*')
def strip_color(msg):
    msg = r_ansi.sub('', msg)
    return msg

class BaseCommandMixin(object):
    quiet = False
    log = None
    indent = 0

    def find_package_script(self, indexes, package):
        files = [os.path.join(package, 'install.py'), '%s.py' % package]
        r =  self._find_files(indexes, files)
        if r:
            self.message('Found script file %s of %s' % (r[0], Fore.GREEN+Style.BRIGHT+package), 'prompt')
        return r

    def _find_files(self, indexes, files):
        import requests

        for i in indexes:
            #test if is locally
            for f in files:
                filename = os.path.join(i, f)
                if os.path.exists(filename):
                    return filename, open(filename).read()
            #test if is in the net
            if '://' in i:
                for f in files:
                    try:
                        filename = os.path.join(i, f)
                        r = requests.get(filename)
                        if r.status_code == 404:
                            continue
                        return filename, r.content
                    except Exception as e:
                        if self.verbose:
                            type, value, tb = sys.exc_info()
                            txt =  ''.join(traceback.format_exception(type, value, tb))
                            print (txt)
                        self.message('Get %s error!' % filename, 'error')
                        continue


    def collection_index(self):
        """
        Collection index link to self.indexes, the order should be:
        1. command argument
        2. environment
        3. default packages directory
        """

        indexes = self.options.index
        if 'IDO_INDEXES' in os.environ:
            indexes.extend(os.environ['IDO_INDEXES'].split(';'))

        indexes.append(os.path.join(os.path.dirname(__file__), 'packages').replace('\\', '/'))
        return indexes

    def message(self, msg, _type='', indent=0):

        if self.quiet:
            return

        indent = self.indent + indent

        RESET = Fore.RESET + Back.RESET + Style.RESET_ALL

        if _type == 'error':
            t = (Fore.RED + ' '*indent + 'Error: ' + msg)
        elif _type == 'cmd':
            t = (Fore.BLUE + Style.BRIGHT + ' '*indent + '==> ' + Fore.MAGENTA + msg)
        elif _type == 'install':
            t = (Fore.BLUE + Style.BRIGHT + ' '*indent + '--> ' + msg)
        elif _type == 'info':
            t = (Fore.WHITE + ' '*indent + msg)
        elif _type == 'prompt':
            t = (Fore.YELLOW + ' '*indent + '#   ' + msg)
        else:
            t = (msg)

        if self.options.nocolor:
            print (strip_color(t))
        else:
            print (t+Fore.RESET+Back.RESET+Style.RESET_ALL)

        if self.log:
            self.log.write(strip_color(t))
            self.log.write('\n')

    def read_settings(self, config):
        e = {}
        settings_file = os.path.expanduser(config)
        if os.path.exists(settings_file):
            if self.global_options.verbose:
                self.message("Using settings file %s" % settings_file, 'prompt')
            code = open(settings_file).read()
            self.settings = self.exec_code(settings_file, code, e)
        else:
            self.settings = {}

    def exec_code(self, filename, code, env):
        from ._compat import exec_

        try:
            env['__name__'] = filename
            env['__loader__'] = ObjectDict(get_source=lambda name: code)

            c_code = compile(code, filename, 'exec', dont_inherit=True)
            exec_(c_code, env)
            return env
        except Exception as e:
            if self.global_options.verbose or self.options.error:
                type, value, tb = sys.exc_info()
                txt =  ''.join(traceback.format_exception(type, value, tb))
                print (txt)
            raise

class InstallCommandMixin(object):
    def make_env(self, script, code, args=None, options=None):
        from . import utils

        #load settings file
        d = {}
        d['INDEXES'] = self.indexes
        self.build = d['BUILD'] = '/tmp/ido_packages_build'
        self.cache = d['CACHE'] = os.path.expandvars('$HOME/.ido/cache')
        #PREFIX will be used to install package with prefix=
        #it can be set in environment variables as IDO_PREFIX
        #or passed in command argumanet -p --prefix
        self.prefix = d['PREFIX'] = os.path.abspath(os.path.expanduser(os.path.expandvars(self.options.prefix \
                                    or self.settings.get('PREFIX', '') \
                                    or os.environ.get('IDO_PREFIX', ''))))
        self.home = d['HOME'] = os.environ['HOME']
        self.files = d['FILES'] = os.path.abspath(os.path.expanduser(os.path.expandvars(self.options.files \
                                    or self.settings.get('FILES', '') \
                                    or os.environ.get('IDO_FILES', ''))))
        d['install'] = partial(self.install, indent=self.indent+4)

        for k in dir(utils):
            v = getattr(utils, k)
            if inspect.isclass(v) and issubclass(v, utils.Function):
                if not v.name: continue
                inst = v(build=self, log=self.log, verbose=self.global_options.verbose,
                         message=partial(self.message, indent=self.indent))
                d[inst.name] = inst

        d['os'] = os
        d['sys'] = sys

        d['message'] = partial(self.message, indent=self.indent)

        d['Fore'] = Fore
        d['Back'] = Back
        d['Style'] = Style

        for x in self.options.vars:
            k, v = (x.split('=') + [''])[:2]
            d[k] = v

        d['make_option'] = make_option

        #process settings pre_load
        if 'PRE_LOAD' in self.settings:
            for path, name in self.settings['PRE_LOAD']:
                mod = import_(path)
                #import all
                if name == '*':
                    for k in getattr(mod, '__all__', []):
                        d[k] = getattr(mod, k)
                #import multi vars
                elif isinstance(name, (tuple, list)):
                    for k in name:
                        d[k] = getattr(mod, k)
                #rename
                else:
                    d[name] = mod

        return d


    def install(self, package, first=False, indent=0, callback=None, prompt='Installing'):
        old_indent = self.indent
        self.indent = indent

        script = self.find_package_script(self.indexes, package)
        if script:
            script, code = script
        else:
            if first:
                self.message("Can't find the installation script of package %s" % (Fore.GREEN+Style.BRIGHT+package), 'error')
                return
            else:
                raise Error("Can't find the installation script of package %s" % package)

        self.message("%s package %s" % (prompt, Fore.GREEN+package), 'install')
        d = self.make_env(script, code)
        try:
            self.exec_code(script, code, d)

            if callback:
                result = callback(script, code, d)
            else:
                result = True
            if result:
                self.message("%s package %s completed." % (prompt, package), 'info')
        except Exception as e:
            if first:
                if self.global_options.verbose or self.options.error:
                    type, value, tb = sys.exc_info()
                    txt =  ''.join(traceback.format_exception(type, value, tb))
                    print (txt)
                self.message("%s package %s failed." % (prompt, package), 'error')
            else:
                raise
        finally:
            self.indent = old_indent

    def callback(self, args=[]):
        def _f(script, code, env):
            option_list = env.get('option_list', [])
            if option_list:
                parser = OptionParser(prog=self.prog_name,
                    usage='',
                    version='',
                    add_help_option = False,
                    option_list=option_list)
                options, vargs = parser.parse_args(args)
            else:
                options = object()
                vargs = []
            call_func = env.get('call')
            if call_func:
                call_func(vargs, options)
            return True
        return _f

class InstallCommand(BaseCommandMixin, InstallCommandMixin, Command):
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
        make_option('--nocolor', dest='nocolor', default=False, action='store_true',
            help='Output result without color.'),
        make_option('-c', '--config', dest='config', default='~/.ido/settings.py',
            help="Config file."),
        make_option('-e', '--error', dest='error', default=False, action='store_true',
            help="Display error messages."),
   )

    def handle(self, options, global_options, *args):
        if len(args) == 0:
            self.message("You should give at least one package name.", 'error')
            return

        self.verbose = global_options.verbose
        self.log = None
        self.indent = 0
        if options.log:
            self.log = open(options.log, 'w')
        elif not self.verbose:
            now = datetime.datetime.now()
            # log_file = '/tmp/ido.%s.log' % now.strftime("%Y%m%d%H%M%S")
            log_file = '/tmp/ido.log'
            self.log = open(log_file, 'w')

        self.indexes = self.collection_index()

        self.read_settings(options.config)
        if 'INDEXES' in self.settings:
            for p in self.settings['INDEXES']:
                if p not in self.indexes:
                    self.indexes.insert(0, p)

        self.indexes = [os.path.abspath(p) for p in self.indexes]

        if not self.verbose:
            self.quiet = True
        else:
            self.quiet = False
        self.install('ido_init')
        self.quiet = False

        try:
            for p in args:
                self.install(p, True, callback=self.callback())
        finally:
            if self.log:
                log_file = self.log.name
                self.log.close()
                self.log = None
                self.message("The shell command result can be see in %s" % (Fore.BLUE+Style.BRIGHT+log_file), 'prompt')


register_command(InstallCommand)

class ViewPackageCommand(BaseCommandMixin, Command):
    """
    View install.py of a package

    """
    name = 'view'
    help = ("View install.py of a package")
    args = 'package'
    option_list = (
        make_option('-i', '--index', dest='index', default=[], action='append',
            help='Package index link, it can be a directory or an url.'),
        make_option('-e', '--editor', dest='editor', default='vi',
            help='Editor used to open install.py of the package.'),
        make_option('-d', '--display', dest='display', default=False, action='store_true',
            help='Just display install.py content but not edit it.'),
        make_option('--nocolor', dest='nocolor', default=False, action='store_true',
            help='Output result without color.'),
   )

    def handle(self, options, global_options, *args):
        if len(args) == 0:
            self.message("You should give at least one package name.", 'error')
            return

        indexes = self.collection_index()

        script = self.find_package_script(indexes, args[0])
        if script:
            script, code = script
            if options.display:
                print (code)
            else:
                if os.path.exists(script):
                    os.system('%s %s' % (options.editor, script))
                else:
                    _file = '/tmp/%s' % script.replace('/', '_')
                    self.message('The file is not existed locally so save it to %s' % _file)
                    open(_file, 'w').write(code)
                    os.system('%s %s' % (options.editor, _file))
        else:
            self.message("Can't find the installation script of package %s" % (Fore.GREEN+Style.BRIGHT+args[0]), 'error')


register_command(ViewPackageCommand)

class SearchPackageCommand(BaseCommandMixin, Command):
    """
    View install.py of a package

    """
    name = 'search'
    help = ("search a package from indexes")
    args = 'package'
    option_list = (
        make_option('-i', '--index', dest='index', default=[], action='append',
            help='Package index link, it can be a directory or an url.'),
        make_option('--nocolor', dest='nocolor', default=False, action='store_true',
            help='Output result without color.'),
   )

    def handle(self, options, global_options, *args):
        if len(args) == 0:
            self.message("You should give at least one package name.", 'error')
            return

        indexes = self.collection_index()

        package = args[0]
        for script, content in self._find_files(indexes, ['index.txt']):
            if self.global_options.verbose:
                print ('index is %s:' % script)
            for line in content.splitlines():
                if package in line and not line.startswith('_'):
                    print (line.strip(), sep=' ')
        print ()

    def _find_files(self, indexes, files):
        import requests

        for i in indexes:
            #test if is in the net
            if '://' in i:
                for f in files:
                    try:
                        filename = os.path.join(i, f)
                        r = requests.get(filename)
                        if r.status_code == 404:
                            continue
                        yield filename, r.content
                    except Exception as e:
                        if self.verbose:
                            type, value, tb = sys.exc_info()
                            txt =  ''.join(traceback.format_exception(type, value, tb))
                            print (txt)
                        self.message('Get %s error!' % filename, 'error')
                        continue
            #test if is locally
            else:
                for f in files:
                    filename = os.path.join(i, f)
                    if os.path.exists(filename):
                        yield filename, open(filename).read()

        raise StopIteration

register_command(SearchPackageCommand)

class CreateIndexPackageCommand(BaseCommandMixin, Command):
    """
    View install.py of a package

    """
    name = 'createindex'
    help = ("Create index.txt for an index.")
    args = '[index-directory]'
    option_list = (
        make_option('--nocolor', dest='nocolor', default=False, action='store_true',
            help='Output result without color.'),
   )

    def handle(self, options, global_options, *args):
        if len(args) == 0:
            path = os.path.join(os.path.dirname(__file__), 'packages').replace('\\', '/')
        else:
            path = args[0]

        if not os.path.exists(path):
            self.message("Directory %s is not existed." % path, 'error')
            return

        packages = []
        for f in os.listdir(path):
            if f.startswith('_'):
                continue
            if os.path.isdir(os.path.join(path, f)):
                script = os.path.join(path, f, 'install.py')
                if os.path.exists(script):
                    packages.append(f)
            else:
                if f.endswith('.py'):
                    packages.append(f[:-3])
        index_file = os.path.join(path, 'index.txt')
        with open(index_file, 'w') as f:
            f.write('\n'.join(packages))
            f.write('\n')

        self.message("Index %s created successful!" % index_file, 'prompt')

register_command(CreateIndexPackageCommand)

class CallCommand(BaseCommandMixin, InstallCommandMixin, CommandManager):
    """
    Run a package and it supports options

    """
    name = 'call'
    help = ("Install or execute a pacage with options")
    args = '[options] package'
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
        make_option('--nocolor', dest='nocolor', default=False, action='store_true',
            help='Output result without color.'),
        make_option('-c', '--config', dest='config', default='~/.ido/settings.py',
            help="Config file."),
        make_option('-e', '--error', dest='error', default=False, action='store_true',
            help="Display error messages."),
   )

    def execute(self):
        """
        Given the command-line arguments, this figures out which subcommand is
        being run, creates a parser appropriate to that command, and runs it.
        """
        # Preprocess options to extract --settings and --pythonpath.
        # These options could affect the commands that are available, so they
        # must be processed early.
        parser = NewOptionParser(prog=self.prog_name,
                             usage=self.usage_info,
#                             version=self.get_version(),
                             formatter = NewFormatter(),
                             add_help_option = False,
                             option_list=self.option_list)

        options, args = parser.parse_args(self.argv)
        self.options = options
        if len(args) == 0:
            self.message("You should give at least one package name.", 'error')
            return

        subcommand = args[0]

        self.handle(args[1:], self.options, self.global_options, subcommand)

    def handle(self, args, options, global_options, subcommand):
        self.verbose = global_options.verbose
        self.log = None
        self.indent = 0
        if options.log:
            self.log = open(options.log, 'w')
        elif not self.verbose:
            now = datetime.datetime.now()
            # log_file = '/tmp/ido.%s.log' % now.strftime("%Y%m%d%H%M%S")
            log_file = '/tmp/ido.log'
            self.log = open(log_file, 'w')

        self.indexes = self.collection_index()

        self.read_settings(options.config)
        if 'INDEXES' in self.settings:
            for p in self.settings['INDEXES']:
                if p not in self.indexes:
                    self.indexes.insert(0, p)

        if not self.verbose:
            self.quiet = True
        else:
            self.quiet = False
        self.install('ido_init')
        self.quiet = False

        try:
            self.install(subcommand, True, callback=self.callback(args))
        finally:
            if self.log:
                log_file = self.log.name
                self.log.close()
                self.log = None
                self.message("The shell command result can be see in %s" % (Fore.BLUE+Style.BRIGHT+log_file), 'prompt')

register_command(CallCommand)

class InfoCommand(CallCommand):
    name = 'info'
    help = ("Display command line options infomation of an package command")
    args = 'package'

    def handle(self, args, options, global_options, subcommand):
        self.indexes = self.collection_index()

        self.read_settings(options.config)
        if 'INDEXES' in self.settings:
            for p in self.settings['INDEXES']:
                if p not in self.indexes:
                    self.indexes.insert(0, p)

        def callback(script, code, env):
            usage = env.get('usage', '[options] args args')
            option_list = env.get('option_list', [])
            if option_list:
                parser = OptionParser(prog=self.prog_name,
                    usage='ido call '+subcommand + ' ' + usage,
                    version='',
                    add_help_option = False,
                    option_list=option_list)
                options, vargs = parser.parse_args(args)
            else:
                options = object()
                vargs = []
            parser.print_help()
            return False

        self.install(subcommand, True, callback=callback, prompt="Help")

register_command(InfoCommand)

def call(args=None):
    from .commands import execute_command_line, get_commands

    if isinstance(args, str):
        import shlex
        args = shlex.split(args)

    execute_command_line(args or sys.argv, get_commands(), prog_name='ido')

def main():
    from .commands import call

    call('ido', __version__)
