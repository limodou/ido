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

This will only include the common packages, such as jdk, git, etc.

## Usage

### Settings

Some options can be set in ~/.ido/settings.py and you can also overwrite most of them in command line parameters or ENV variables

```
IDO_PREFIX = '$HOME/env' #install prefix parameter
IDO_FILES = '$HOME/packages' #source files
```


### Simple command

```
ido install jdk
```