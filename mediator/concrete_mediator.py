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
from constants.constants import (
    CONCRETE_MEDIATOR,
    GET_SONG_DATA,
    GET_STATION,
    GET_STATIONS,
    KEY_LISTENER,
    LOVE,
    MAIN,
    MAIN_WINDOW,
    MAIN_WINDOW_READY,
    MEDIA_NEXT,
    MEDIA_PLAY,
    NEW_SONG,
    NEW_STATION,
    PIANOBAR,
    QUIT,
    START,
    STATIONS,
    STATION_CHANGE_REQUESTED,
    SYSTRAY
)
from key_listener.key_listener import KeyListener
from main_window.main_window import MainWindow
from mediator.mediator import Mediator
from pianobar.pianobar import Pianobar
from systray.systray import Systray
import logging
import sys


class ConcreteMediator(Mediator):
    """
    A class which implements the Mediator pattern.

    User's of this class should only:
    - Instantiate
    - Set mediator
    - Call in to this class using 'notify' method.
    """

    _app_icon = None
    _app_name = None
    _key_listener = None
    _main_window = None
    _main_window_ready = False
    _pianobar = None
    _song_data = None
    _station = None
    _systray = None
    _theme = None

    def __init__(self, app_icon, app_name, theme):
        """
        Args:
        app_icon (str): the icon you want to see in your desktop OS
        app_name (str): the name of the app you want to see in OS notification's
        theme (str): the ttkbootstrap theme for the application
        """
        super().__init__()
        self._app_icon = app_icon
        self._app_name = app_name
        self._theme = theme

    def notify(self, sender, event, event2):
        """
        Consumers of this class should only communicate through here
        using the mediator design pattern.
        """
        logging.debug(f"{CONCRETE_MEDIATOR}: recv => sender={sender}, event={event}, event2={event2}")

        if sender == KEY_LISTENER:
            self._handle_events_key_listener(event, event2)
            return

        if sender == MAIN:
            self._handle_events_main(event, event2)
            return

        if sender == MAIN_WINDOW:
            self._handle_events_main_window(event, event2)
            return

        if sender == PIANOBAR:
            self._handle_events_pianobar(event, event2)
            return

        if sender == SYSTRAY:
            self._handle_events_systray(event, event2)

    def _get_stations(self):
        """
        Fetches the stations list, stores them and notifies the MainWindow
        """
        stations = self._pianobar.notify(CONCRETE_MEDIATOR,
                                         event=GET_STATIONS,
                                         event2=None)
        # TODO if stations is empty
        self._main_window.station_list = stations
        self._main_window.notify(CONCRETE_MEDIATOR, event=STATIONS, event2=None)

    def _handle_events_key_listener(self, event, event2):
        """
        Event handler for the KeyListener events
        """
        if event == MEDIA_PLAY:
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  event=MEDIA_PLAY,
                                  event2=None)
        elif event == MEDIA_NEXT:
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  event=MEDIA_NEXT,
                                  event2=None)

    def _handle_events_main(self, event, event2):
        """
        Event handler for the Main events
        """
        if event == START:
            self._start()

    def _handle_events_main_window(self, event, event2):
        """
        Event handler for the MainWindow events
        """
        if event == GET_SONG_DATA:
            self._main_window.notify(CONCRETE_MEDIATOR,
                                     event=NEW_SONG,
                                     event2=self._song_data)
        elif event == GET_STATION:
            self._main_window.notify(CONCRETE_MEDIATOR,
                                     event=NEW_STATION,
                                     event2=self._station)
        elif event == GET_STATIONS:
            self._get_stations()
        elif event == LOVE:
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  event=LOVE,
                                  event2=None)
        elif event == MAIN_WINDOW_READY:
            self._main_window_ready = True

        elif event == MEDIA_PLAY:
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  event=MEDIA_PLAY,
                                  event2=None)
        elif event == MEDIA_NEXT:
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  event=MEDIA_NEXT,
                                  event2=None)
        elif event == QUIT:
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  QUIT,
                                  event2=None)
        elif event == STATION_CHANGE_REQUESTED:
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  event=STATION_CHANGE_REQUESTED,
                                  event2=event2)

    def _handle_events_pianobar(self, event, event2):
        """
        Event handler for the Pianobar events
        """
        if event == NEW_STATION:
            if not self._main_window_ready:
                logging.debug(f"CONCRETE_MEDIATOR: storing new station to var.")
                self._station = event2
                return
            self._main_window.notify(CONCRETE_MEDIATOR,
                                     event=NEW_STATION,
                                     event2=event2)
        elif event == NEW_SONG:
            if not self._main_window_ready:
                logging.debug(f"CONCRETE_MEDIATOR: storing new song to var.")
                self._song_data = event2
                return
            self._main_window.notify(CONCRETE_MEDIATOR,
                                     event=NEW_SONG,
                                     event2=event2)

    def _handle_events_systray(self, event, event2):
        """
        Event handler for the Systray events
        """
        self._main_window.notify(CONCRETE_MEDIATOR, event, event2)

    def _start(self):
        self._start_key_listener()  # must be first to start
        # note you could add while/sleep loop here to debug key_listener alone

        # To test without pianobar running, but just the GUI
        # comment out this and in MainWindow: GetSongData, GetStations
        self._start_pianobar()
        if self._song_data is None:
            logging.critical(f"{CONCRETE_MEDIATOR}: no data app exiting now!")
            self._pianobar.notify(CONCRETE_MEDIATOR,
                                  QUIT,
                                  event2=None)
            sys.exit(1)

        self._start_systray()
        # to test tray we need some form of mainloop to keep app running
        # else tray exits right away, so uncomment this while loop, and
        # then comment out our call below to self._start_main_window()
        # while 1:
        #     time.sleep(1)
        #     print("yar")

        self._start_main_window()

    def _start_key_listener(self):
        """
        Starts the KeyListener class
        """
        self._key_listener = KeyListener()
        self._key_listener.mediator = self
        self._key_listener.notify(CONCRETE_MEDIATOR, event=START, event2=None)

    def _start_main_window(self):
        """
        Starts the MainWindow class
        """
        self._main_window = MainWindow(self._app_name, self._theme)
        self._main_window.mediator = self
        self._main_window.notify(CONCRETE_MEDIATOR, event=START, event2=None)

    def _start_pianobar(self):
        """
        Starts the pianobar class
        """
        self._pianobar = Pianobar()
        self._pianobar.mediator = self
        self._pianobar.notify(CONCRETE_MEDIATOR, event=START, event2=None)

    def _start_systray(self):
        """
        Starts the Systray class.
        """
        self._systray = Systray(self._app_icon, self._app_name)
        self._systray.mediator = self
        self._systray.notify(CONCRETE_MEDIATOR, event=START, event2=None)
