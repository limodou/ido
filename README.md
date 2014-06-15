![ci](https://travis-ci.org/limodou/ido.svg?branch=master)

# ido

## What's it?

ido is a command tool, it's written in python, and you can use it to install packages or
execute commands. So you can just treats it as something like brew, yum, apt-get, etc.
But ido can be more easy used and extended suit for your needs.

## Features

* Simple core
* color command output
* packages or commands collection should be origanize in a directory
* Installation script file is common Python source file
* Builtin rich functions and you can easily extend
* Packages installation aim user home first
* Depends files can be stored in disk depends on your installation script
* User can make themself tool based on ido to customize their application requirements
* Written in Python, should be support 2.6, 2.7, 3.3, 3.4

## Install

```
pip install ido
```

This will only include the examples packages, such as demo, etc.

## Requirement

ido need: future, colorama packages, and it'll be installed automatically.

ido should be run in python 2.6+.

## Usage

### Simple command

```
ido install demo
```

`demo` here is a demo package used to demonstrate the ido functionalities.

### Package install script

A package should be a directory, and there should be a file named `install.py`.
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
      will be `error`, `info`, or just omited.
* Color Objects
    * `Fore`, `Back`, `Style` They are colorama objects, so you can use them directly.

### Packages Index

All packages should be saved in a directory, I called it `index`, and ido can search package from them. ido
can support multiple source of index, the default is shipped in ido package, it's `ido/packages`
And ido also support other local directoires or url links, so you can pass them in command
line just like:

```
ido install zlib -i ~/packages
ido install jdk -i https://yourname/packages (Not implemented yet)
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
```

to see the help messages.

### Pass variables to script

If you have some viriables and want to pass them to install script, so you can define them
in command argument, just like:

```
ido install zlib -Evar1=demo1 -Evar2=demo2
```

### See exception

Sometime the script will throw exceptions, but they'll be hidden by default, and if you want
to see them you can just pass `-v` to see them.