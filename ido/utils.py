from __future__ import absolute_import
import os
import shutil
import subprocess as sub
from functools import partial

if not hasattr(sub, 'check_output'):
    from subprocess import CalledProcessError, Popen, PIPE

    def check_output(*popenargs, **kwargs):
        r"""Run command with arguments and return its output as a byte string.

        If the exit code was non-zero it raises a CalledProcessError.  The
        CalledProcessError object will have the return code in the returncode
        attribute and output in the output attribute.

        The arguments are the same as for the Popen constructor.  Example:

        >>> check_output(["ls", "-l", "/dev/null"])
        'crw-rw-rw- 1 root root 1, 3 Oct 18  2007 /dev/null\n'

        The stdout argument is not allowed as it is used internally.
        To capture standard error in the result, use stderr=STDOUT.

        >>> check_output(["/bin/sh", "-c",
        ...               "ls -l non_existent_file ; exit 0"],
        ...              stderr=STDOUT)
        'ls: non_existent_file: No such file or directory\n'
        """
        if 'stdout' in kwargs:
            raise ValueError('stdout argument not allowed, it will be overridden.')
        process = Popen(stdout=PIPE, *popenargs, **kwargs)
        output, unused_err = process.communicate()
        retcode = process.poll()
        if retcode:
            cmd = kwargs.get("args")
            if cmd is None:
                cmd = popenargs[0]
            raise CalledProcessError(retcode, cmd, output=output)
        return output
else:
    check_output = sub.check_output

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
        from io import StringIO
        import tempfile
        from . import strip_color

        try:
            buf = tempfile.NamedTemporaryFile(mode='w+', delete=False)

            cwd = kwargs.pop('cwd', '')
            if not cwd:
                cwd = os.getcwd()

            kwargs['cwd'] = cwd
            kwargs['stdout'] = buf
            kwargs['stderr'] = buf
            kwargs['shell'] = True

            self.message(args[0], 'cmd', indent=4)

            p = sub.Popen(*args, **kwargs)
            p.wait()

            buf.seek(0)
            result = buf.read()

            if self.log:
                self.log.write(strip_color(result))
        finally:
            buf.close()

        if p.returncode:
            raise Exception("Execute command %s failed, return code is %d" % (args[0], p.returncode))

        return p.returncode, result

class TarxFunction(Function):
    """
    Execute tar command, default is 'tar xvfz filename', and it'll guess the extracted
    directory and return it
    """
    name = 'tarx'

    def __call__(self, filename, flags='xvfz'):
        sh = ShellFunction(self.build, self.log, self.verbose, self.message)
        sh('tar %s %s' % (flags, filename))
        paths = {}
        result = check_output('tar tf %s' % filename, shell=True, cwd=os.getcwd(),
                              universal_newlines=True)
        for line in result.splitlines():
            p = line.split('/', 1)[0]
            paths[p] = paths.setdefault(p, 0) + 1
        if not paths:
            return ''
        if len(paths) == 1:
            return list(paths.keys())[0]
        for x, y in reversed([(v, k) for k, v in paths.items()]):
            return y

class UnzipFunction(Function):
    """
    Execute unzip command, default is 'unzip filename', and it'll guess the extracted
    directory and return it. It'll overwrite existed by default.
    """
    name = 'unzip'

    def __call__(self, filename, flags=''):
        sh = ShellFunction(self.build, self.log, self.verbose, self.message)
        if 'o' not in flags:
            flags += 'o'
        if flags:
            flags = '-' + flags + ' '
        sh('unzip %s%s' % (flags, filename))
        paths = {}
        _in = False
        result = check_output('unzip -l %s' % filename, shell=True, cwd=os.getcwd(),
                              universal_newlines=True)
        for line in result.splitlines():
            line = line.lstrip()
            if line.lstrip().startswith('----'):
                if not _in:
                    _in = True
                    continue
                else:
                    break
            else:
                if not _in:
                    continue
                p = line.split()[3].split('/', 1)[0]
                paths[p] = paths.setdefault(p, 0) + 1
        if not paths:
            return ''
        if len(paths) == 1:
            return list(paths.keys())[0]
        for x, y in reversed([(v, k) for k, v in paths.items()]):
            return y

class ChdirFunction(Function):
    name = 'cd'

    def __call__(self, path):
        self.old_path = os.getcwd()
        os.chdir(path)
        self.message("cd %s" % path, 'cmd', indent=4)

        return self

    def __enter__(self):
        return self

    def __exit__(self, type, value, tb):
        os.chdir(self.old_path)

class MkdirFunction(Function):
    name = 'mkdir'

    def __call__(self, path):
        if not os.path.exists(path):
            os.makedirs(path)
            self.message("mkdirs %s" % path, 'cmd', indent=4)
        else:
            if self.verbose:
                self.message("Directory %s is alread existed!" % path, 'info',
                             indent=self.build.indent+4)

class WgetFunction(Function):
    name = 'wget'
    def __call__(self, filename, in_path=None):
        paths = [in_path, self.build.files, self.build.cache]
        self.message('wget %s' % filename, 'cmd', indent=4)
        _file = os.path.basename(filename)
        for p in paths:
            if not p: continue
            if os.path.exists(os.path.join(p, _file)):
                self.message("The file is already existed in %s directory!" % p, 'info', indent=4)
                return os.path.join(p, _file)

        in_path = in_path or self.build.files or self.build.cache
        check_output('wget -c -N '+filename, cwd=in_path, shell=True)

        return os.path.join(in_path, _file)

class CpFunction(Function):
    name = 'cp'
    def __call__(self, src, dst, in_path=None, wget=None):
        import shutil
        from glob import glob

        paths = [in_path, self.build.files, self.build.cache]
        for p in paths:
            if not p: continue
            d_src = os.path.join(p, src)
            for x in glob(d_src):
                shutil.copy(x, dst)
                self.message("cp %s %s" % (x, dst), 'cmd', indent=4)
                return os.path.basename(x)

        #not found
        if wget:
            message = partial(self.message, indent=4)
            w = WgetFunction(self.build, self.log, self.verbose, message)
            return w(wget)