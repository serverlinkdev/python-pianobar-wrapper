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
import os

from constants.constants import (
    CMD_NEXT,
    CMD_PLAY_PAUSE,
    CONCRETE_MEDIATOR,
    GET_STATIONS,
    LOVE,
    MEDIA_NEXT,
    MEDIA_PLAY,
    NEW_SONG,
    NEW_STATION,
    PIANOBAR,
    QUIT,
    START,
    STATION_CHANGE_REQUESTED
)
from mediator.base_component import BaseComponent
from song.song import Song
from typing import List, Tuple
import logging
import re
import subprocess
import threading
import time


class Pianobar(BaseComponent):
    """
    A class which implements the Mediator pattern.

    User's of this class should only:
    - Instantiate
    - Set mediator
    - Call in to this class using 'notify' method.
    """
    _fifo_path = None  # TODO hard coded value
    _lock = None
    _output_buffer = []
    _process = None
    _reader_thread = None
    _time_update = ""
    mediator = None

    def __init__(self):
        super().__init__()
        self._fifo_path = os.path.join(os.getenv('HOME'), '.config', 'pianobar','ctl')
        self._lock = threading.Lock()

    def notify(self, sender, event, event2):
        """
        Consumers of this class should only communicate through here
        using the mediator design pattern.
        """
        if sender == CONCRETE_MEDIATOR:
            logging.debug(f"{PIANOBAR}: notify received event: {event}")
            if event == GET_STATIONS:
                return self._get_stations()
            elif event == LOVE:
                # go to https://www.pandora.com/profile in web browser when
                # logged in, and then click "Thumbs Up" text on left in page
                # and the most recently thumbs up'd songs will appear at the
                # top of the page on the right hand side.
                self._send_command("+\n")
            elif event == MEDIA_PLAY:
                self._send_command(CMD_PLAY_PAUSE)
            elif event == MEDIA_NEXT:
                self._send_command(CMD_NEXT)
            elif event == QUIT:
                self._stop()
            elif event == START:
                self._start()
            elif event == STATION_CHANGE_REQUESTED:
                self._change_station(event2)

    def _change_station(self, station):
        """
        Sends the change station cmd to pianobar
        Args:
            station (int): an integer corresponding to the desired station
        """
        logging.debug(f"{PIANOBAR}: changing to station: {station}")
        self._send_command("s")
        time.sleep(1)  # wait for list to print out
        self._send_command(str(station))
        self._send_command("\n")
        self._send_command("\n")

    def _clear_buffer(self):
        with self._lock:
            self._output_buffer.clear()

    def _extract_song_data(self, text):
        """
        Extracts song information and sends it to Mediator for consumption

        Args:
            text: a string of text holding artist, album, track name, favorite

        Returns:
            song_obj (Song) : Complete Song object
            or
            None (None) : if no data found
        """
        logging.debug(f"{PIANOBAR}: extracting data from text: {text}")

        text = text.strip("|> ")

        if text is None:
            logging.critical(f"{PIANOBAR}: received None type for song data!")
            return None

        parts = text.split('"')
        # Check if the list has enough parts to extract song, artist, and album
        if len(parts) >= 7:
            title = parts[1]
            artist = parts[3]
            album = parts[5]
            is_favorite = False
            if text.strip('\n').endswith("<3"):
                logging.debug(f"{PIANOBAR}: is favorite song")
                is_favorite = True
            else:
                logging.debug(f"{PIANOBAR}: is NOT favorite song")
            logging.debug(f"{PIANOBAR}: extracted => song: {title}, artist: {artist}, album: {album}, favorite: {is_favorite}")
            song_data = Song(album=album, artist=artist, title=title, favorite=is_favorite)
            # return a Song object with structured data
            return song_data

        # Return None if the format is incorrect
        logging.critical(f"{PIANOBAR}: extracted no song data, improperly formatted string!")
        logging.critical(f"{PIANOBAR}: the improper string held: {text}")
        return None

    def _get_stations(self):
        """
        Returns: raw data holding the list of stations from pianobar
        """
        logging.debug(f"{PIANOBAR}: getting stations list")
        self._clear_buffer()
        self._send_command("s")
        time.sleep(1)  # wait for list to print out
        stations = self._parse_stations()
        self._send_command("\n")
        self._clear_buffer()
        return stations

    def _get_time_update(self):
        with self._lock:
            return self._time_update

    def _is_time_update(self, line):
        # Adjust this logic to accurately identify time update lines
        return line.strip().startswith('#')

    def _next_song(self):
        """
        Send the next song cmd to pianobar
        """
        logging.debug(f"{PIANOBAR}: sending next song command")
        self._send_command("n")

    def _parse_stations(self):
        """
        Returns: station_list (List[Tuple[int, str]]) a list of stations
        """
        station_list: List[Tuple[int, str]] = []
        for line in self._output_buffer:
            new_line = self._remove_ansi_escape_and_tabs(line)
            if new_line and new_line[0].isdigit() and ')' in new_line:
                number_end_index = new_line.find(')')
                if number_end_index != -1:
                    number_str = new_line[:number_end_index]
                    try:
                        number = int(number_str.strip())
                    except ValueError:
                        continue
                    # removing leading whitespace
                    station_name = new_line[number_end_index + 1:].strip()
                    station_name_cleaned = self._remove_ansi_escape_and_tabs(station_name)
                    if station_name_cleaned.startswith("q  "):
                        station_name_cleaned = station_name_cleaned.strip("q  ")
                    station_list.append((number, station_name_cleaned))
        logging.debug(f"{PIANOBAR}: returning station_list with contents:\n {station_list}")
        return station_list

    def _play_pause(self):
        """
        Sends play / pause cmd to pianobar
        """
        logging.debug(f"{PIANOBAR}: toggle play/pause")
        self._send_command("p")

    def _read_output(self):
        """
        Continuously reads the output from the pianobar and emits events
        of concern to the mediator.
        """
        for line in self._process.stdout:
            with self._lock:
                if self._is_time_update(line):
                    # TODO pass to GUI
                    self._time_update = line.strip()
                else:
                    self._output_buffer.append(line.strip())
                    line = self._remove_ansi_escape_and_tabs(line)
                    if "|>  Station " in line:  # handle station name updates
                        line = line.strip("|> ")
                        results = []
                        start_index = 0
                        while True:
                            start_index = line.find('"', start_index) + 1
                            if start_index == 0:
                                break
                            end_index = line.find('"', start_index)
                            if end_index == -1:
                                break
                            results.append(line[start_index:end_index])
                            start_index = end_index + 1
                        station = ' '.join(results)
                        # tell mediator we have a station change event
                        logging.debug(f"{PIANOBAR}: new station event! sending event2={station}")
                        self.mediator.notify(PIANOBAR, event=NEW_STATION, event2=station)
                    elif "|>  " in line:  # handle songs
                        logging.debug(f"{PIANOBAR}: new song event! begin parsing with event2={line}")
                        song_obj = self._extract_song_data(line)
                        if song_obj is None:
                            logging.debug(f"{PIANOBAR}: new song event recv 'None' for song obj!")
                        else:
                            logging.debug(f"{PIANOBAR}: new song event sending data to mediator!")
                            self.mediator.notify(PIANOBAR, event=NEW_SONG, event2=song_obj)

    def _remove_ansi_escape_and_tabs(self, text):
        """
        Args:
            text (str): raw text line from pianobar

        Returns:
            cleaned_text (str): a string stripped of the items at beginning
            of the raw line of text from pianobar
        """
        # pattern to match ANSI escape sequences and tab followed by space
        pattern = re.compile(r'(\x1b\[[0-?]*[ -/]*[@-~])|(\t\s*)')
        cleaned_text = pattern.sub('', text)
        return cleaned_text

    def _send_command(self, command):
        """
        Generic func to send commands to pianobar.

        Args:
            command (str): a command known by pianobar
        """
        logging.debug(f"{PIANOBAR}: writing cmd to pianobar: {command}")
        with open(self._fifo_path, "w") as fifo:
            fifo.write(command)

    def _start(self):
        """
        Starts a sub process running the pianobar application and sets up
        a way to read its output.
        """
        logging.debug(f"{PIANOBAR} Starting up!")
        # Start pianobar and capture its output
        self._process = subprocess.Popen(
            ['/usr/bin/pianobar'],
            stdout=subprocess.PIPE,
            stderr=subprocess.STDOUT,
            bufsize=1,
            text=True
        )
        self._reader_thread = threading.Thread(target=self._read_output)
        self._reader_thread.daemon = True
        self._reader_thread.start()
        # Wait for pianobar to connect
        time.sleep(5)

    def _stop(self):
        """
        Stop pianobar and exit the subprocess that contained it.
        """
        if self._process:
            logging.info(f"{PIANOBAR} Quitting!")
            self._send_command("q")  # quit
            self._process.wait()  # exit gracefully
