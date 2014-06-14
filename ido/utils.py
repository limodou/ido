import os
import shutil
import subprocess as sub

class Function(object):
    name = 'unname'
    def __init__(self, build, log=None, verbose=True, message=None):
        self.build = build
        self.verbose = verbose
        self.log = log
        self.message = message

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

def function(fname):
    """
    Make a function to Function class
    """
    def _f(func):
        class WrapFunction(Function):
            name = fname

            def __class__(self, *args, **kwargs):
                return func(*args, **kwargs)

        return WrapFunction

    return _f

class ShellFunction(Function):
    name = 'sh'
    def __call__(self, *args, **kwargs):
        cwd = kwargs.pop('cwd', '')
        if not cwd:
            cwd = os.getcwd()
        kwargs['cwd'] = cwd
        kwargs['stdout'] = self.log
        kwargs['stderr'] = self.log
        kwargs['shell'] = True

        self.message(args[0], 'run')

        p = sub.Popen(*args, **kwargs)
        p.wait()

        return p.returncode

ChdirFunction = function('cd')(os.chdir)