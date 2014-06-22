![ci](https://travis-ci.org/limodou/ido.svg?branch=master)

# ido

## What's it?

ido is a command line tool, written in Python, and you can use it to install packages or
execute commands. It works like brew, yum, apt-get, etc.
But ido can be more easily used and extended to suit your needs.

## Features

* Simple core
* Color command output
* Packages or commands collection should be organized in a directory or a python file
* Installation script file is common Python source file
* Installation script can be searched from local disk or net
* Builtin rich functions and you can easily extend
* Packages installation aim user home first
* Depends files can be searched from disk
* User can create tool themselves based on ido to suit for their application needs
* Some configuration can be saved in settings.py
* Written in Python, should be support 2.6, 2.7, 3.3, 3.4

## Install

```
pip install ido
```

This will only include the examples packages, such as demo, zlib, nginx, redis, etc.

## Requirement

ido needs: The `future`, `colorama`, `requests` packages, and they be installed automatically.

ido currently supports Python 2.6+.

## Usage

### Install a package

```
ido install package
```

`package` is a name which you want to install to your environment. You can
try `ido install demo` see the demo package.

The usage of this command is:

```
ido help install

Usage: ido install [options] [package, package...]

Install or execute a pacage

Options:
  -i INDEX, --index=INDEX
                        Package index link, it can be a directory or an url.
  -E ENV_VAR            Define variables and will passed to installation
                        scripts.
  -p PREFIX, --prefix=PREFIX
                        Prefix value when compile and install source packages.
  -l LOG, --log=LOG     Log filename the shell outut will be written in it.
  -f FILES, --files=FILES
                        Source packages storage directory.
  --nocolor             Output result without color.
  -c CONFIG, --config=CONFIG
                        Config file.
```


#### View a package installation script

```
ido view package
```

View the given package install.py content in editor or just display to console
(with `-d` option in command line).

```
ido help view

Usage: ido view [options] package

View install.py of a package

Options:
  -i INDEX, --index=INDEX
                        Package index link, it can be a directory or an url.
  -e EDITOR, --editor=EDITOR
                        Editor used to open install.py of the package.
  -d, --display         Just display install.py content but not edit it.
  --nocolor             Output result without color.
```

### Package install script

A package should have a directory named `<package>` and in it there must be a file called `install.py`.
Or just a python file which named `<package>.py`.
Do you can write script just with python at all.

The `install.py` is just a common python file, but it'll be executed with `exec()`,
and ido will pass some builtin variables such as:

* BUILD The value will be '/tmp/ido_packages_build', and it'll used to compile source packages.
* PREFIX Can be passed in command line option `-p` or `--prefix` , or defined in environment
  variable `IDO_PREFIX`, and script can use it as value of `./configure --prefix`.
* HOME Current user HOME directory.

There are also some builtin functions, objects or modules, such as:

* Modules
    * os
    * sys
* Functions
    * `sh()` Used to execute shell command, `sh('ls')`
    * `cd()` Used to change current directory, `cd(BUILD)`
    * `mkdir()` Used to make directories, `mkdir('/tmp/a/b')`
    * `wget()` Used to download a file from internet, `wget('http://zlib.net/zlib-1.2.8.tar.gz')`
    * `cp()` Used to copy a source file(can use fnmatch to match the filename) to destination directory or file, `cp('zlib*', BUILD)`
    * `install()` Used to install other package, `install('zlib')`
    * `message()` Used to output colored message, `message(msg, 'error')`, the second argument
      will be `error`, `info`, `prompt` or just omitted.
* Color Objects
    * `Fore`, `Back`, `Style` They are colorama objects, so you can use them directly.

### Packages Index

Packages should be saved in a directory, I called it `index`, and ido can search package from them. ido
can support multiple source of index, the default is shipped in ido package, it's `ido/packages`
And ido also support other local directoires or url links, so you can pass them in command
line just like:

```
ido install zlib -i ~/packages
ido install zlib -i https://yourname/packages (Not implemented yet)
ido install zlib -i ~/packages -i https://yourname/packages
```

You can also defined in environment variable `IDO_INDEXES`, so the searching order is:

1. command line argument
1. settings file
1. environment variable
1. default `ido/packages`

### Command options

You can just type:

```
ido
#or
ido help
```

to see the help messages.

### Pass variables to script

If you have some variables and want to pass them to install script, so you can define them
in command argument, eg:

```
ido install zlib -Evar1=demo1 -Evar2=demo2
```

### See exception

Sometimes the script will throw exceptions, but they'll be hidden by default, and if you want
to see them you can just pass `-v` to see them.

## Build your own packages system

For now, ido ships with only a few packages, so it seems that it's useless. But you can use it
to build your own packages system, to make it useful.

You can give index url or directory like this:

```
ido install yourpackage -i local_directory -i http://remote_url
```

So you can make packages in index directory and install them as you wish.

## zlib demo

There is already some basic or demo packages in ido, such as zlib, you can find
it at `ido/packages/zlib` , and there is an `install.py` file in it. The content
is :

```
filename = cp('zlib*', BUILD, wget='http://zlib.net/zlib-1.2.8.tar.gz')
cd(BUILD)
cd(tar(filename))
sh('./configure --prefix=%s' % PREFIX)
sh('make install')
```

This demo shows how to copy zlib file to build directory, and if not existed, it'll
download zlib file from internet, then compile it, and install it. Functions
like `cp`, `sh`, `cd`, `tar` is builtin functions you can
use directly. `BUILD` , `PREFIX` is builtin variables which you can also use directly.

In order to compatible with `call` command, you could wrap the script with a `cal()` function,
just like:

```
def call(args, options):
    filename = cp('zlib*', BUILD, wget='http://zlib.net/zlib-1.2.8.tar.gz')
    cd(BUILD)
    cd(tar(filename))
    sh('./configure --prefix=%s' % PREFIX)
    sh('make install')
```

So that you could define command line options in it and call it via `ido call package`.

There different between them is: `install` can install multi packages, and with no options.
But `call` can only install one package, but you could provide options to it. So for simple
script, `install` is enough, but for complex script, you could use `call`.

## Builtin Funtions

### wget

```
def wget(filename, in_path=None) -> filename
```

It'll try to download the remote file. But ido also can cache the downloaded file in
`CACHE` directory, and it's `$HOME/.ido/cache` by default. So if a file is already
downloaded, it'll not download it again. Besides CACHE directory, if you give `in_path`
parameter to wget function or just give `-f files_directory`
in the command line, ido will also search files in these directories, so the order of search
a filename which need to be downloaded is:

1. `in_path` parameter directory
1. directory of `-f` parameter of command line
1. CACHE directory

IF wget download or just find an existed file, it'll return the real filename of it, so
you can use the returned filename later.

### cp

```
def cp(src, dst, in_path=None, wget=None) -> filename
```

It'll copy source file to destination directory. And it also supports filename pattern
like: `'zlib*'`, etc. If the source filename is relative, it'll search the file according
to `in_path` or `-f` parameter of command line. And if the filename is not found, then
it'll use `wget` command to download according `wget` parameter, for example:

```
filename = cp('zlib*', BUILD, wget='http://zlib.net/zlib-1.2.8.tar.gz')
```

If the command is successful, it'll only return the basename of the filen. For example: `zlib-1.2.8.tar.gz`
without the path.

### sh

```
def sh(cmd)
```

It'll execute the command line in a shell.

### cd

```
def cd(path)
```

Changes current directory to `path`. And it also support `with` statement, for example:

```
with cd('/tmp'):
    #do
#it'll change back to old path
```

### mkdir

```
def mkdir(path)
```

It'll check if the `path` is already existed, if not then make directories using `os.makedirs`

### tarx

```
def tarx(filename, flags='xvfz')
```

It'll extract tarball file to current directory, if you want to create tarbar file,
you should use `sh('tar cvfz test.tar.gz files')` command.

And it'll return the extracted directory after extracing the tarbar file. So you can change
dirctory after extract tarbar easily `cd(tarx(filename))`

### unzip

```
def unzip(filename, flags='')
```

It'll extract zip file to current directory, if you want to create zip file,
you should use `sh('zip zipfile files')` command.

And it'll return the extracted directory after extracing the zip file. So you can change
dirctory after extract tarbar easily `cd(unzip(filename))`

It'll automatically add `-o` (overwrite exsited files) for you, so if you don't like
these, you should use `sh('unzip zipfile')`

## Settings

Some global vairables can be also saved in a settings file, you can use `-c /path/settings.py`
to specify a settings file otherwise it'll use `~/.ido/settings.py` by default. And you should
know, after you first installed ido, there should not be a default settings.py, so you should
give it through command line option or create it in `~/.ido` by yourself.

Settings file is a pure python file, and the content of it should look like:

```
INDEXES = []
PREFIX = '$HOME/env'
FILES = '$HOME/files'
PRE_LOAD = [('sh', 'SH')]
```

`PREFIX` and `FILES` just like the environment variables `IDO_PREFIX` and `IDO_FILES` or command
line options `-p --prefix` and `-f --files`.

`PRE_LOAD` used to pretend import some object from given module path, the example above menas:
import `sh` module and alias it as `SH` , so that you can use `SH` directly in your installation
script.

And the format of `PRE_LOAD` could be:

```
PRE_LOAD = [
    ('module_path', 'alias_name'),
    ('module_path', '*'),
    ('module_path', ['a', 'b']),
]
```

The example above demonstrates three formats:

1. import `module_path` and alias it as `alias_name`, for example: ('os.path', 'PATH')
2. import `module_path` and add objects which defined in `__all__` to script namespace
3. import `module_path` and only add objects `a` and `b` to script namespace

So if you have third party module want to used in script, you can do like above.

There is an example settings file in ido source named `settings.py.example`

## Searching and Create Index

If you don't know if there is a package which you want to install, you could use

```
ido search pattern
```

Here `pattern` could be a complete package name or substring of a package name. Using
this command, there should be an `index.txt` file exsisted in package directory, it's just
a plain text file, and each package should be a line in it. When searching, it'll skip
`_` beginned name, such as `_init.py`

For `index.txt` you can create by hand, or you can run `ido createindex [package_directory]`,
ido will created for you. If you omit the `package_directory` argument, it'll search `packages`
diretory of ido installation directory, anc save `index.txt` in it.

## Run package installation script with arguments

If you want to install a package with some customized arguments, so how to do that?

First, you should change your script just like:

```
option_list = (
    make_option('-t', '--test', dest='test',
        help='Test.'),
)

def call(args, options):
    print (args)
    print (options.test)
```

You should define option_list first, it just uses optparse module to make options, so `make_option`
will imported automatically, you can directly use it.

Second, you should define a function named `call(args, options)`, it just like you invoke
`options, args= parser.parser_args(argv)`

And if you want to see the options of a package script, you could:

```
ido info test_call
```

You should know, the code of `install` and `call` is some different. But you can always write
your code in `def call(args, options):` function.

## Builtin Packages

* ido_init It'll create BUILD and CACHE directory, and output the environment variables
* demo  A demo package
* nginx Install nginx via source
* redis Install redis via source
* zlib Install redis via zlib

## License

New BSD

## Change Log

* 0.1
    * First release
* 0.2
    * Improve cd function, supports `with` statement
    * Index could be a link, so you can execute command from net
    * Improve `tarx` and `unzip`
    * Improve `cp`, add `wget` parameter, so if file not found, it'll download according `wget`
      parameter via `wget` tool
    * Add settings config support
    * Add `nginx`, `pcre`, `redis` examples
* 0.3
    * Add `search` and `createindex` subcommands, you can create an index file to a
      packages directory, and use `ido search package` to search if the package existed
    * Add `call` and `info` subcommands, you can make command options to a package script
