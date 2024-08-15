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
from threading import Thread

from constants.constants import (
    CONCRETE_MEDIATOR,
    KEY_LISTENER,
    MEDIA_NEXT,
    MEDIA_PLAY,
    START
)
from mediator.base_component import BaseComponent
from pynput import keyboard
import logging


class KeyListener(BaseComponent):
    """
    A class which implements the Mediator pattern.

    Users of this class should only:
    - Instantiate
    - Set mediator
    - Call into this class using the 'notify' method.
    """
    _hotkeys = None
    _kb_next = keyboard.Key.media_next
    _kb_pp = keyboard.Key.media_play_pause
    _listener_thread = None
    _media_keys = (keyboard.Key.media_play_pause, keyboard.Key.media_next, keyboard.Key.media_previous)
    mediator = None

    def __init__(self):
        super().__init__()

    def notify(self, sender, event, event2):
        """
        Consumers of this class should only communicate through here
        using the mediator design pattern.
        """
        if sender == CONCRETE_MEDIATOR and event == START:
            logging.debug(f"{KEY_LISTENER}: Startup has been requested")
            self._start()

    def _handle_media_key(self, key):
        """
        Test and notify mediator if key is play/pause or next
        Args:
            key (keyboard.Key): the key to eval.
        """
        try:
            if key == self._kb_pp:
                logging.debug(f"{KEY_LISTENER}: Media Play/Pause pressed")
                self.mediator.notify(KEY_LISTENER, MEDIA_PLAY, event2=None)
            elif key == self._kb_next:
                logging.debug(f"{KEY_LISTENER}: Media Next pressed")
                self.mediator.notify(KEY_LISTENER, MEDIA_NEXT, event2=None)
        except AttributeError:
            logging.error(f"{KEY_LISTENER}: AttributeError with key {key}")

    def _on_press(self, key):
        """
        Test if the key pressed is of concern to us.
        """
        if key in self._media_keys:
            self._handle_media_key(key)

    def _run_listener(self):
        with keyboard.Listener(on_press=self._on_press) as listener:
            listener.join()

    def _start(self):
        logging.debug(f"{KEY_LISTENER}: Registering hotkeys")
        self._listener_thread = Thread(target=self._run_listener)
        self._listener_thread.daemon = True
        self._listener_thread.start()
        logging.debug(f"{KEY_LISTENER}: Listener thread started")
