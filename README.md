[![Build Status](https://travis-ci.org/jkr78/PyenvEnv.svg)](https://travis-ci.org/jkr78/PyenvEnv)

[Pyenv](https://github.com/pyenv/) python versions in sublime text.

## Installation

Install this sublime text 2/3 package via [Package Control](https://packagecontrol.io/) search for package: "[**PyenvEnv**](https://packagecontrol.io/packages/PyenvEnv)"

### or manually install

- `cd <Packages directory>`   (for example on Mac it is `~/Library/Application\ Support/Sublime\ Text\ 2/Packages` or `~/Library/Application\ Support/Sublime\ Text\ 3/Packages`)
- `git clone https://github.com/jkr78/PyenvEnv.git`

## Usage

Plugin will try to find `pyenv` python version and set environment variable specified in `PyenvEnv.python_home_envname` to python home path.

Use this environment variable when configuring SublimeLinter, Jedi, Build System and etc.

## Default configuration

**PyenvEnv.python_home_envname** - none

`Environment name (or list of names) python home will be set to.`

**PyenvEnv.valid_syntax** - none

`Syntax name this plugin is valid for (ex. "Packages/Python/Python.sublime-syntax")`

**PyenvEnv.valid_file_ext** - none

`File extensions this plugin will work with (ex. ".py").`

**PyenvEnv.unsaved_is_valid** - true

`Set environment variable for unsaved files.`

**PyenvEnv.python_version** - none

`Default python version. If not set - plugin will try to search for .python-version.`

**PyenvEnv.debug** - false

`Output debug information to console.`

**PyenvEnv.pyenv_home** - null

`Overwrite pyenv home variable. If not PYENV_ROOT environment will be used.`

**PyenvEnv.home** - null

`Overwrite home directory. If not project directory or file's directory will be used.`

**PyenvEnv.python** - null

`Set python executable name.`

**PyenvEnv.search_parent** - true

`Search .python-version file in parent directories.`

**PyenvEnv.no_comments** - true

`Do not skip comments in .python-version.`

## Others

Inspired by: https://packagecontrol.io/packages/Environment%20Settings
