# SPDX-License-Identifier: AGPL-3.0-or-later
# pylint: disable=missing-module-docstring, too-many-branches
# from typing import Optional: This line imports the Optional type hint from the typing module. Optional[X] is equivalent to Union[X, None].

from typing import Optional  # from os import environ: This line imports the environ object from the os module. environ is a mapping object representing the string environment.
from os import environ  # from os.path import dirname, join, abspath, isfile: This line imports the dirname, join, abspath, and isfile functions from the os.path module.
from os.path import dirname, join, abspath, isfile
from collections.abc import Mapping  # import yaml: This line imports the yaml module, which provides functions to parse and generate YAML data.
from itertools import filterfalse
  # from searx.exceptions import SearxSettingsException: This line imports the SearxSettingsException class from the searx.exceptions module.
import yaml

from searx.exceptions import SearxSettingsException  # def existing_filename_or_none(file_name: str) -> Optional[str]: This function checks if a file exists and returns the filename if it does, or None otherwise.


searx_dir = abspath(dirname(__file__))

  # def load_yaml(file_name): This function opens a YAML file and returns its contents as a Python object. If an error occurs while opening the file or parsing the YAML data, it raises a SearxSettingsException.
def existing_filename_or_none(file_name: str) -> Optional[str]:
    if isfile(file_name):
        return file_name
    return None


def load_yaml(file_name):
    try:  # def get_default_settings_path(): This function returns the path to the default settings file.
        with open(file_name, 'r', encoding='utf-8') as settings_yaml:
            return yaml.safe_load(settings_yaml)
    except IOError as e:
        raise SearxSettingsException(e, file_name) from e  # def get_user_settings_path() -> Optional[str]: This function returns the path to the user settings file. The path is determined based on environment variables and the existence of certain files.
    except yaml.YAMLError as e:
        raise SearxSettingsException(e, file_name) from e


def get_default_settings_path():
    return existing_filename_or_none(join(searx_dir, 'settings.yml'))


def get_user_settings_path() -> Optional[str]:
    """Get an user settings file.
    By descending priority:
    1. ``environ['SEARXNG_SETTINGS_PATH']``
    2. ``/etc/searxng/settings.yml`` except if ``SEARXNG_DISABLE_ETC_SETTINGS`` is ``true`` or ``1``  # def update_dict(default_dict, user_dict): This function updates a dictionary with the contents of another dictionary.
    3. ``None``
    """

    # check the environment variable SEARXNG_SETTINGS_PATH
    # if the environment variable is defined, this is the last check
    if 'SEARXNG_SETTINGS_PATH' in environ:  # def update_settings(default_settings, user_settings): This function updates the settings with the user settings. It handles special cases for the ‘use_default_settings’ and ‘engines’ keys.
        return existing_filename_or_none(environ['SEARXNG_SETTINGS_PATH'])

    # if SEARXNG_DISABLE_ETC_SETTINGS don't look any further
    if environ.get('SEARXNG_DISABLE_ETC_SETTINGS', '').lower() in ('1', 'true'):
        return None

    # check /etc/searxng/settings.yml
    # (continue with other locations if the file is not found)
    return existing_filename_or_none('/etc/searxng/settings.yml')


def update_dict(default_dict, user_dict):
    for k, v in user_dict.items():
        if isinstance(v, Mapping):
            default_dict[k] = update_dict(default_dict.get(k, {}), v)
        else:
            default_dict[k] = v
    return default_dict


def update_settings(default_settings, user_settings):
    # merge everything except the engines
    for k, v in user_settings.items():
        if k not in ('use_default_settings', 'engines'):
            if k in default_settings and isinstance(v, Mapping):
                update_dict(default_settings[k], v)
            else:
                default_settings[k] = v

    categories_as_tabs = user_settings.get('categories_as_tabs')
    if categories_as_tabs:
        default_settings['categories_as_tabs'] = categories_as_tabs

    # parse the engines
    remove_engines = None
    keep_only_engines = None
    use_default_settings = user_settings.get('use_default_settings')
    if isinstance(use_default_settings, dict):
        remove_engines = use_default_settings.get('engines', {}).get('remove')
        keep_only_engines = use_default_settings.get('engines', {}).get('keep_only')

    if 'engines' in user_settings or remove_engines is not None or keep_only_engines is not None:
        engines = default_settings['engines']

        # parse "use_default_settings.engines.remove"
        if remove_engines is not None:
            engines = list(filterfalse(lambda engine: (engine.get('name')) in remove_engines, engines))

        # parse "use_default_settings.engines.keep_only"
        if keep_only_engines is not None:
            engines = list(filter(lambda engine: (engine.get('name')) in keep_only_engines, engines))

        # parse "engines"
        user_engines = user_settings.get('engines')
        if user_engines:
            engines_dict = dict((definition['name'], definition) for definition in engines)
            for user_engine in user_engines:
                default_engine = engines_dict.get(user_engine['name'])
                if default_engine:
                    update_dict(default_engine, user_engine)
                else:
                    engines.append(user_engine)

        # store the result
        default_settings['engines'] = engines

    return default_settings


def is_use_default_settings(user_settings):
    use_default_settings = user_settings.get('use_default_settings')
    if use_default_settings is True:
        return True
    if isinstance(use_default_settings, dict):
        return True
    if use_default_settings is False or use_default_settings is None:
        return False
    raise ValueError('Invalid value for use_default_settings')


def load_settings(load_user_settings=True):
    default_settings_path = get_default_settings_path()
    user_settings_path = get_user_settings_path()
    if user_settings_path is None or not load_user_settings:
        # no user settings
        return (load_yaml(default_settings_path), 'load the default settings from {}'.format(default_settings_path))

    # user settings
    user_settings = load_yaml(user_settings_path)
    if is_use_default_settings(user_settings):
        # the user settings are merged with the default configuration
        default_settings = load_yaml(default_settings_path)
        update_settings(default_settings, user_settings)
        return (
            default_settings,
            'merge the default settings ( {} ) and the user settings ( {} )'.format(
                default_settings_path, user_settings_path
            ),
        )

    # the user settings, fully replace the default configuration
    return (user_settings, 'load the user settings from {}'.format(user_settings_path))
