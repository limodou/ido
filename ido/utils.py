import os
import shutil
import subprocess as sub

class Function(object):
    name = ''
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

            def __call__(self, *args, **kwargs):
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

        self.message(args[0], 'cmd')

        p = sub.Popen(*args, **kwargs)
        p.wait()

        return p.returncode

ChdirFunction = function('cd')(os.chdir)

@function('mkdir')
def mkdir(path):
    if not os.path.exists(path):
        os.makedirs(path)

class WgetFunction(Function):
    name = 'wget'
    def __call__(self, filename, in_path=None):
        paths = [in_path, self.build.files, self.build.cache]
        self.message('wget %s' % filename, 'cmd')
        _file = os.path.basename(filename)
        for p in paths:
            if not p: continue
            if os.path.exists(os.path.join(p, _file)):
                self.message("The file is already existed in %s directory!" % p, 'info')
                return os.path.join(p, _file)

        in_path = in_path or self.build.files or self.build.cache
        sub.check_output('wget -c -N '+filename, cwd=in_path, shell=True)

        return os.path.join(in_path, _file)

class CpFunction(Function):
    name = 'cp'
    def __call__(self, src, dst, in_path=None):
        import shutil
        from glob import glob

        paths = [in_path, self.build.files, self.build.cache]
        for p in paths:
            if not p: continue
            d_src = os.path.join(p, src)
            for x in glob(d_src):
                shutil.copy(x, dst)
                return os.path.basename(x)