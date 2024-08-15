"""
python-pianobar-wrapper:
    A program to wrap pianobar in python GUI with systray
    using the Mediator design pattern.

    Copyright (C) 2023 serverlinkdev@gmail.com

    This program is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, version 3 of the License, or
    (at your option) any later version.

    This program is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with this program.  If not, see <https://www.gnu.org/licenses/>
"""
from colorlog import ColoredFormatter
from constants.constants import MAIN, START
from mediator.concrete_mediator import ConcreteMediator
import logging
import os
import sys


def _start_logging(debug_on):
    """
    Configure the logging of this application

    Args:
        debug_on (bool): True, False
    """
    script_dir = os.path.dirname(os.path.abspath(__file__))
    log_file_path = os.path.join(script_dir, "logfile.log")

    # define log format with colors
    log_format = (
        '%(log_color)s%(asctime)s:%(levelname)s:%(message)s%(reset)s')

    color_formatter = ColoredFormatter(
        log_format,
        log_colors={
            'DEBUG': 'white',
            'INFO': 'yellow',
            'WARNING': 'light_white',
            'ERROR': 'red',
            'CRITICAL': 'light_white,bg_black',
        })

    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(color_formatter)
    logger.addHandler(console_handler)
    logger.info("Main: Logging to file: " + str(bool(debug_on)))
    if debug_on:
        logger.setLevel(logging.DEBUG)
        file_handler = logging.FileHandler("logfile.log", encoding="utf-8")
        file_handler.setFormatter(
            logging.Formatter('%(asctime)s:%(levelname)s:%(message)s'))
        logger.addHandler(file_handler)
        log_file_path = os.path.join(log_file_path, "logfile.log")
        logger.info(f"Main: Logging to file: {log_file_path}")
    logger.info("Main: Starting up!")


def start(debug_on, app_icon, app_name, theme):
    """
    Starts the entire application.

    Args:
        debug_on (bool): True, False
        app_icon (str): the icon you want to see in your desktop OS
        app_name (str): the name of the app you want to see in OS notification's
        theme (str): the ttkbootstrap theme for the application
    """
    _start_logging(debug_on)
    _cm = ConcreteMediator(app_icon=app_icon,
                           app_name=app_name,
                           theme=theme)
    _cm.notify(MAIN, event=START, event2=None)


if __name__ == '__main__':
    # App will completely shut down when you use "Quit" from the system tray
    start(debug_on=False,
          app_icon="smile.png",
          app_name="Python Pianobar Wrapper",
          theme="darkly")

# themes from:
# https://ttkbootstrap.readthedocs.io/en/version-0.5/themes.html
