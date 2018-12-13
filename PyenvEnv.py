import os
import os.path

import sublime
import sublime_plugin


PLUGIN_NAME = 'PyenvEnv'
SETTINGS_PREFIX = PLUGIN_NAME + '.'
SETTINGS_FILE = PLUGIN_NAME + '.sublime-settings'

DEBUG = 0


def get_setting(name, default=None, view=None):
    if view is None:
        view = sublime.active_window().active_view() 

    view_settings = view.settings()

    name_with_prefix = SETTINGS_PREFIX + name
    if view_settings.has(name_with_prefix):
        return view_settings.get(name_with_prefix)

    settings = sublime.load_settings(SETTINGS_FILE)
    return settings.get(name, default)


def echo(msg):
    if DEBUG or get_setting('debug'):
        print("{}: {}".format(PLUGIN_NAME, msg))


def get_pyenv_home(default=None, view=None):
    """Returns the home of pyenv."""
    pyenv_home = get_setting('pyenv_home', view=view)
    if pyenv_home:
        echo("Using pyenv_home from settings: {}".format(pyenv_home))
        return pyenv_home

    pyenv_home = os.environ.get('PYENV_ROOT')
    if pyenv_home:
        echo("Using PYENV_ROOT environment: {}".format(pyenv_home))
        return pyenv_home

    return default


def find_pyenv_python(version, view=None):
    """Returns the path to python executable."""
    pyenv_home = get_pyenv_home(view=view)
    if not pyenv_home:
        echo("Unable to find pyenv")
        return None

    home = os.path.expanduser(os.path.join(pyenv_home, 'versions', version))
    if not os.path.isdir(os.path.realpath(home)):
        echo("'{}' is not directory".format(home))
        return None

    python = get_setting('python', view=view) or 'python'
    path_to_python = os.path.expanduser(os.path.join(home, 'bin', python))
    if not os.path.isfile(os.path.realpath(path_to_python)):
        echo("'{}' does not exists".format(path_to_python))
        return None

    echo("Found '{}'".format(path_to_python))
    return path_to_python


def get_home(view=None):
    """Returns home dir."""
    home = get_setting('home', None)
    if home:
        echo("Have 'home' setting")
        return home

    window = sublime.active_window()
    
    sublime_vars = window.extract_variables()

    # When try project path
    home = sublime_vars.get('project_path')
    if home:
        echo("Using project path: {}".format(home))
        return home

    # After that try filename
    if view is None:
        view = window.active_view()

    file_name = view.file_name()
    if file_name:
        echo("Using file dir: {}".format(file_name))
        return os.path.dirname(file_name)


def find_python_version_dotfile(view=None):
    """Returns the path of the .python-version dotfile."""
    home = get_home(view=view)
    echo("Searching for '.python-version' in '{}'".format(home))

    search_parent = get_setting('search_parent', True, view=view)
    
    home = os.path.abspath(os.path.expanduser(home))
    while True:
        version_dotfile = os.path.join(home, '.python-version')
        if os.path.isfile(version_dotfile):
            echo("'{}' found".format(version_dotfile))
            return version_dotfile

        if not search_parent:
            echo("Searching in parent dir is disabled")
            break

        parent = os.path.dirname(home)
        if not parent or parent == home:
            break

        home = parent

    echo("'.python-version' not found")
    return None


def read_python_version_from_dotfile(view=None):
    """Returns python versions from python-version dotfile."""
    dotfile = find_python_version_dotfile(view=view)
    if not dotfile:
        return

    no_comments = get_setting('no_comments', True, view=view)

    with open(dotfile, 'r') as dotfile_file:
        line = dotfile_file.readline()
        if no_comments:
            line = line.split('#', 1)[0]

        for version in line.split():
            echo("'{}' is read from '.python-version'".format(version))
            yield version


def get_python_versions_from_settings(view=None):
    python_versions = get_setting('python_version', view=view)
    echo("python_version setting: {}".format(python_versions))
    if not python_versions:
        return None

    if not isinstance(python_versions, (list, tuple)):
        python_versions = [python_versions]

    return python_versions


def python_versions(view=None):
    python_versions = get_python_versions_from_settings(view=view)
    if python_versions:
        if not isinstance(python_versions, (list, tuple)):
            python_versions = [python_versions]

        return python_versions

    return read_python_version_from_dotfile(view=view)


def find_all_python_homes(view=None):
    """Returns all python homes."""
    for version in python_versions(view=view):
        python = find_pyenv_python(version, view=view)
        if python:
            yield python


def find_python_home(default=None, view=None):
    """Returns first available python version path."""
    return next(find_all_python_homes(view=view), default)


def set_python_env(python_home, view=None):
    """Set python environment variables."""
    python_home_envname = get_setting('python_home_envname', view=view)
    if not python_home_envname:
        return

    if not isinstance(python_home_envname, (list, tuple)):
        python_home_envname = [python_home_envname]

    for envname in python_home_envname:
        envval = os.path.expandvars(python_home)
        os.environ[envname] = envval
        echo("setenv {}='{}'".format(envname, envval))


def merge_dict(*dicts):
    """Recursive dict merge."""
    dst = {}
    for src in dicts:
        for k in src:
            if k in dst and isinstance(dst[k], MutableMapping) and isinstance(
                src[k], MutableMapping
            ):
                dst[k] = merge_dict(dst[k], src[k])
            else:
                dst[k] = src[k]
    return dst


def dict_patch(path, value):
    """Return dictionary patch.

    Used for merging.
    """
    if not path:
        return value

    if isinstance(path, str):
        path = path.split(".")

    curr = result = {}
    for k in path[:-1]:
        curr[k] = {}
        curr = curr[k]

    curr[path[-1]] = value
    return result


def update_project_data(view=None):
    """Update project data variables."""
    new_data = get_setting('project_data', view=view)
    if not new_data:
        return

    data = sublime.active_window().project_data()
    for key, value in new_data.items():
        value = os.path.expanduser(value)
        patch = dict_patch(key, value)
        echo("Updating project with: {}".format(patch))
        merge_dict(data, patch)

    sublime.active_window().set_project_data(data)


def valid_file(view=None):
    if not view:
        view = sublime.active_window().active_view() 

    file_name = view.file_name()

    unsaved_is_valid = get_setting('unsaved_is_valid', True)
    if not file_name:
        echo("File is unsaved: {}".format(unsaved_is_valid))
        return unsaved_is_valid

    valid_file_ext = get_setting('valid_file_ext')
    if not valid_file_ext:
        return True  # everything is valid

    if not isinstance(valid_file_ext, (list, tuple)):
        valid_file_ext = [valid_file_ext]

    _, file_name_ext = os.path.splitext(file_name)
    if file_name_ext not in valid_file_ext:
        echo("File '{}' is not valid".format(file_name))
        return False

    return True


def valid_syntax(view=None):
    if view is None:
        view = sublime.active_window().active_view() 

    syntax = view.settings().get('syntax')

    valid_syntax = get_setting('valid_syntax')
    if not valid_syntax:
        return True  # everything is valid

    if not isinstance(valid_syntax, (list, tuple)):
        valid_syntax = [valid_syntax]

    if syntax not in valid_syntax:
        echo("Syntax '{}' is not valid".format(syntax))
        return False

    return True


class PyEnvVirtualEnvListener(sublime_plugin.EventListener):
    def __init__(self, *args, **kwargs):
        super(PyEnvVirtualEnvListener, self).__init__(*args, **kwargs)

        self.active_project = sublime.active_window().project_file_name()

    def on_activated(self, view):
        if not (valid_syntax(view) or valid_file(view)):
            return

        # shortcut
        python_home_envname = get_setting('python_home_envname', view=view)
        if not python_home_envname:
            echo("'python_home_envname' is not set")
            return

        python_home = find_python_home(view=view)
        if not python_home:
            return

        set_python_env(python_home)
        update_project_data(view=view)

    def on_post_save(self, view):
        if view.file_name() == sublime.active_window().project_file_name():
            update_project_data(view=view)
