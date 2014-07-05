from __future__ import absolute_import
import os
import shutil
import subprocess as sub
from functools import partial
from ._compat import reraise, u

class Function(object):
    name = ''
    def __init__(self, build, log=None, verbose=True, message=None):
        self.build = build
        self.verbose = verbose
        self.log = log
        self.message = message

    def __call__(self, *args, **kwargs):
        raise NotImplementedError

    def sh(self, cmd, echo=True, message='', log=None, **kwargs):
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

            if echo:
                msg = message or cmd
                self.message(msg, 'cmd', indent=4)

            p = sub.Popen(cmd, **kwargs)
            p.wait()

            buf.seek(0)
            result = buf.read()

            if log:
                log.write(strip_color(result))
        finally:
            buf.close()

        if p.returncode:
            raise Exception("Execute command %s failed, return code is %d" % (cmd, p.returncode))

        return u(result)

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

    def __call__(self, cmd, **kwargs):
        return self.sh(cmd, log=self.log, **kwargs)

class TarxFunction(Function):
    """
    Execute tar command, default is 'tar xvfz filename', and it'll guess the extracted
    directory and return it
    """
    name = 'tarx'

    def __call__(self, filename, flags='xvfz'):
        cmd = 'tar %s %s' % (flags, filename)
        self.sh(cmd, log=self.log)
        paths = {}
        result = self.sh('tar tf %s' % filename, echo=False)
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
        if 'o' not in flags:
            flags += 'o'
        if flags:
            flags = '-' + flags + ' '
        self.sh('unzip %s%s' % (flags, filename), log=self.log)
        paths = {}
        _in = False
        result = self.sh('unzip -l %s' % filename, echo=False)
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
        paths = [in_path, self.build.files]
        self.message('wget %s' % filename, 'cmd', indent=4)
        _file = os.path.basename(filename)
        for p in paths:
            if not p: continue
            if os.path.exists(os.path.join(p, _file)):
                self.message("The file is already existed in %s directory!" % p, 'info', indent=4)
                return os.path.join(p, _file)

        in_path = in_path or self.build.files
        self.sh('wget -c -N '+filename, cwd=in_path, log=self.log)

        return os.path.join(in_path, _file)

class CpFunction(Function):
    name = 'cp'
    def __call__(self, src, dst, in_path=None, wget=None):
        import shutil
        from glob import glob

        paths = [in_path, self.build.files]
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

class PipFunction(Function):
    name = 'pip'
    def __call__(self, packages=None, index=None, requirements=None, args=''):

        if args:
            args = ' '+args
        if requirements:
            cmd = ' '.join(['pip', 'install', '-f', self.build.files, args, '--no-index', '-r',
                   requirements])
            try:
                self.sh(cmd, log=self.log)
            except:
                self.message('pip install %s' % requirements, 'error', indent=8)
                if index:
                    o_index = '-i %s ' % index
                else:
                    o_index = ''
                cmd = ' '.join(['pip', 'install', o_index, args, '-r', requirements])
                self.sh(cmd, log=self.log)

            return
        elif not isinstance(packages, (tuple, list)):
            packages = [packages]

        for p in packages:
            self._install(p, index, args)

    def _install(self, package, index=None, args=''):
        from glob import glob

        cmd = ' '.join(['pip', 'install', '-f', self.build.files, '--no-index',
                        args, package])
        try:
            self.sh(cmd, log=self.log)
        except:
            self.message('pip install %s' % package, 'error', indent=8)
            #try to download first
            if index:
                o_index = '-i %s ' % index
            else:
                o_index = ''
            cmd = ' '.join(['pip', 'install', '-d', self.build.files,
                            o_index, args, package])
            self.message('pip download %s' % package, 'cmd', indent=4)
            self.sh(cmd, echo=False)
            cmd = ' '.join(['pip', 'install', '-f', self.build.files, '--no-index',
                            args, package])
            self.sh(cmd, log=self.log)
        return True
        
class ChecksumsFunction(Function):
    
    def __call__(self, filename, checksums, in_path=None):
        if not os.path.exists(filename):
            self.message("The file %s is not existed." % filename, 'error', indent=8)
            return

        self.message('%s %s %s' % (self.name, filename, checksums), 'cmd', indent=4)
        import hashlib
        if self.name == 'md5sum':
            m = getattr(hashlib, 'md5')
        else:
            m = getattr(hashlib, 'sha1')
        d = m(open(filename, 'rb').read()).hexdigest()
        if d != checksums:
            raise Exception("%s %s failed" % (self.name, filename))
        return True

class Md5sumFunction(ChecksumsFunction):
    name = 'md5sum'
    
class Sha1sumFunction(ChecksumsFunction):
    name = 'sha1sum'

class WhichFunction(Function):
    name = 'which'

    def __call__(self, command):
        result = self.sh('which %s' % command)
        return result
