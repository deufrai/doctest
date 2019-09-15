# ALS - Astro Live Stacker
# Copyright (C) 2019  Sébastien Durand (Dragonlost) - Gilles Le Maréchal (Gehelem)
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
"""
Provides application defaults and high level access to user settings
"""
import logging
import os
import sys
from configparser import ConfigParser, DuplicateOptionError, ParsingError

# config file path. We use the pseudo-standard hidden file in user's home
from als.ui import dialogs

_CONFIG_FILE_PATH = os.path.expanduser("~/.als.cfg")

# keys used to retrieve config values
_SCAN_FOLDER_PATH = "scan_folder_path"
_WORK_FOLDER_PATH = "work_folder_path"
_LOG_LEVEL = "log_level"
_WWW_SERVER_PORT = "www_server_port"
_WINDOW_GEOMETRY = "window_geometry"

# keys used to describe logging level
_LOG_LEVEL_DEBUG = "DEBUG"
_LOG_LEVEL_INFO = "INFO"
_LOG_LEVEL_WARNING = "WARNING"
_LOG_LEVEL_ERROR = "ERROR"
_LOG_LEVEL_CRITICAL = "CRITICAL"

# store of matches between human readable log levels and logging module constants
_LOG_LEVELS = {
    _LOG_LEVEL_DEBUG:       logging.DEBUG,
    _LOG_LEVEL_INFO:        logging.INFO,
    _LOG_LEVEL_WARNING:     logging.WARNING,
    _LOG_LEVEL_ERROR:       logging.ERROR,
    _LOG_LEVEL_CRITICAL:    logging.CRITICAL,
}

# application default values
_DEFAULTS = {
    _SCAN_FOLDER_PATH:    os.path.expanduser("~/als/scan"),
    _WORK_FOLDER_PATH:    os.path.expanduser("~/als/work"),
    _LOG_LEVEL:           "INFO",
    _WWW_SERVER_PORT:     "8000",
    _WINDOW_GEOMETRY: "50,100,1024,800"
}
_MAIN_SECTION_NAME = "main"

_CONFIG_PARSER = ConfigParser()


def is_debug_log_on():
    """
    Checks if loglevel is DEBUG

    :return: True if loglevel is DEBUG, False otherwise
    """
    return _get(_LOG_LEVEL) == 'DEBUG'


def set_debug_log(debug_active):
    """
    Sets logldevel to debug if debug_active is True, otherwise set loglevel to info

    :param debug_active: set loglevel to debug
    :type debug_active: bool
    """
    if debug_active:
        _set(_LOG_LEVEL, _LOG_LEVEL_DEBUG)
    else:
        _set(_LOG_LEVEL, _LOG_LEVEL_INFO)


def get_www_server_port_number():
    """
    Retrieves the configured web server port number.

    :return: The configured port number, or its default value if config entry
             is not parsable as an int.
    """
    try:
        return int(_get(_WWW_SERVER_PORT))
    except ValueError:
        return _DEFAULTS[_WWW_SERVER_PORT]


def set_www_server_port_number(port_number):
    """
    Sets server port number.

    :param port_number: the port number
    :type port_number: int
    """
    _set(_WWW_SERVER_PORT, port_number)


def get_work_folder_path():
    """
    Retrieves work folder path.

    :return: the work folder path
    :rtype: str
    """
    return _get(_WORK_FOLDER_PATH)


def set_work_folder_path(path):
    """
    Sets the work folder path.

    :param path: the work folder path
    :type path: str
    """
    _set(_WORK_FOLDER_PATH, path)


def get_scan_folder_path():
    """
    Retrieves scan folder path.

    :return: the scan folder path
    :rtype: str
    """
    return _get(_SCAN_FOLDER_PATH)


def set_scan_folder_path(path):
    """
    Sets the scan folder path.

    :param path: the scan folder path
    :type path: str
    """
    _set(_SCAN_FOLDER_PATH, path)


def get_window_geometry():
    """
    Retrieves main window geometry.

    :return: a tuple of 4 integers describing :

    - x coordinate of top left corner
    - y coordinate of top left corner
    - width of the window
    - height of the window
    """
    return tuple([int(value) for value in _get(_WINDOW_GEOMETRY).split(",")])


def set_window_geometry(geometry_tuple):
    """
    Sets main window geometry.

    :param geometry_tuple:
    :type geometry_tuple: tuple

    The geometry_tuple tuple must contain 4 integers describing :

    - x coordinate of top left corner
    - y coordinate of top left corner
    - width of the window
    - height of the window
    """
    _set(_WINDOW_GEOMETRY, ",".join([str(value) for value in geometry_tuple]))


def save():
    """
    Saves settings to disk.

    :except os_error: Saving could not be done
    """
    try:
        with open(_CONFIG_FILE_PATH, "w") as config_file:
            _CONFIG_PARSER.write(config_file)
        _LOGGER.info("User configuration saved")
    except OSError as os_error:
        _LOGGER.error("Could not save settings. Error : %s", os_error)
        dialogs.error_box("Settings not saved", f"Your settings could not be saved\n\nDetails : {os_error}")


def _get(key):
    """
    Retrieves the value of a specific config entry.

    :param key: the key identifying the config entry
    :type key: str

    :return: the value of the config entry identified by key, or it's default value if key is not found
    """
    # we rely on the fallback mechanism to get our predefined defaults
    # if no user config is found
    return _CONFIG_PARSER.get(_MAIN_SECTION_NAME, key, fallback=_DEFAULTS[key])


def _set(key, value):
    """
    Sets the value of a config entry identified by a key *only* when value differs from default or stored one

    :param key: config entry key
    :type key: str
    :param value: config entry value
    :type value: any
    """
    if value != _get(key):
        _CONFIG_PARSER.set(_MAIN_SECTION_NAME, key, value)


# ConfigParser.read won't raise an exception if read fails because of missing file
# so if app starts and no user settings file exists, we simply
# get an "empty" config
# if config file is invalid, we raise a ValueError with details
try:
    _CONFIG_PARSER.read(_CONFIG_FILE_PATH)
except DuplicateOptionError as duplicate_error:
    raise ValueError(duplicate_error)
except ParsingError as parsing_error:
    raise ValueError(parsing_error)

# init logging system
logging.basicConfig(level=_LOG_LEVELS[_get(_LOG_LEVEL)],
                    format='%(asctime)s - %(levelname)s - %(name)s - %(message)s',
                    stream=sys.stdout)
_LOGGER = logging.getLogger(__name__)

# in here, we maintain a list of third party loggers for which we don't want to see anything but WARNING & up
_THIRD_PARTY_LOG_POLLUTERS = [
    'watchdog.observers.inotify_buffer',
]

for third_party_log_polluter in _THIRD_PARTY_LOG_POLLUTERS:
    logging.getLogger(third_party_log_polluter).setLevel(logging.WARNING)

# add our main section if not already present (i.e. previous read failed)
if not _CONFIG_PARSER.has_section(_MAIN_SECTION_NAME):
    _LOGGER.debug('adding main section to config')
    _CONFIG_PARSER.add_section(_MAIN_SECTION_NAME)

# cleanup unused options
for option in _CONFIG_PARSER.options(_MAIN_SECTION_NAME):
    if option not in _DEFAULTS.keys():
        _LOGGER.debug("Removed obsolete config option : '%s'", option)
        _CONFIG_PARSER.remove_option(_MAIN_SECTION_NAME, option)

_LOGGER.debug("User config file dump - START")
for option in _CONFIG_PARSER.options(_MAIN_SECTION_NAME):
    _LOGGER.debug("%s = %s", option, _get(option))
_LOGGER.debug("User config file dump - END")
