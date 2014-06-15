![ci](https://travis-ci.org/limodou/ido.svg?branch=master)

# ido

## What's it?

ido is a command line tool, written in Python, and you can use it to install packages or
execute commands. It works like brew, yum, apt-get, etc.
But ido can be more easily used and extended to suit your needs.

## Features

* Simple core
* Color command output
* Packages or commands collection should be organized in a directory
* Installation script file is common Python source file
* Builtin rich functions and you can easily extend
* Packages installation aim user home first
* Depends files can be stored in disk depending on your installation script
* User can create tool themselves based on ido to customize their application requirements
* Written in Python, should be support 2.6, 2.7, 3.3, 3.4

## Install

```
pip install ido
```

This will only include the examples packages, such as demo, etc.

## Requirement

ido needs: The `future`, `colorama` packages, and they be installed automatically.

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
```


#### View a package installation script

```
ido view package
```

View the given package install.py content in editor or just display to console
(with `-d` option in command line).

### Package install script

A package should have a directory, and in it there must be a file called `install.py`.
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

You can also defined in environment variable `IDO_PACKAGES`, so the searching order is:

1. command line argument
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
filename = wget('http://zlib.net/zlib-1.2.8.tar.gz')
filename = cp(filename, BUILD)
cd(BUILD)
sh('tar xvfz %s' % filename)
cd('zlib-1.2.8')
sh('./configure --prefix=%s' % PREFIX)
sh('make')
```

This demo shows how to download zlib file from internet, and compile it. But I don't
write `make install`. Functions like `wget, cp, sh, cd` is builtin functions you can
use directly. `BUILD` , `PREFIX` is builtin variables which you can also use directly.

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
def cp(src, dst, in_path=None) -> filename
```

It'll copy source file to destination directory. And it also supports filename pattern
like: `'zlib*'`, etc. If the source filename is relative, it'll search the file according
to `in_path` or `-f` parameter of command line.

### sh

```
def sh(cmd)
```

It'll execute the command line in a shell.

### cd

```
def cd(path)
```

Changes current directory to `path`.

### mkdir

```
def mkdir(path)
```

It'll check if the `path` is already existed, if not then make directories using `os.makedirs`

## License

New BSD
