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
    GET_STATION,
    GET_STATIONS,
    GET_SONG_DATA,
    LOVE,
    MAIN_WINDOW,
    MAIN_WINDOW_READY,
    MEDIA_NEXT,
    MEDIA_PLAY,
    NEW_SONG,
    NEW_STATION,
    QUIT,
    SHOW,
    START,
    STATION_CHANGE_REQUESTED,
    STATIONS
)
from listbox_with_navigation.listbox_with_navigation import ListboxWithNavigation as ListBox
from mediator.base_component import BaseComponent
from PIL import Image, ImageTk
from song.song import Song
from ttkbootstrap import Style
from ttkbootstrap.constants import *
from typing import List, Tuple
import logging
import signal
import tkinter
import ttkbootstrap as ttk
import tkinter.font as tkFont


class MainWindow(BaseComponent):
    """
    A MainWindow class using ttkbootstrap using the Mediator design pattern.

    User's of this class should only:
    - Instantiate
    - Set mediator
    - Call in to this class using 'notify' method.
    """

    _album_label = None
    _app_name = None
    _artist_label = None
    _btn_change_station = None
    _btn_next = None
    _btn_play_pause = None
    _control_buttons = None
    _global_font = None
    _heart_color = None
    _heart_gray = None
    _heart_handle_color = None
    _heart_handle_gray = None
    _heart_img_label = None
    _heart_path_color = None
    _heart_path_gray = None
    _is_favorite = None
    _media_info_frame = None
    _msg_lbox = None
    _msg_lbox_lock = None
    _msg_lbox_scrollbar = None
    _song_label = None
    _station_label = None
    _style = None
    _theme = None
    _window = None
    mediator = None
    station_list: List[Tuple[int, str]] = []

    def __init__(self, app_name, theme):
        """
        Args:
            app_name (str): the name of the app to be used by the OS
            theme (str): the ttkbootstrap theme for the application
        """
        super().__init__()
        self._app_name = app_name
        self._theme = theme
        signal.signal(signal.SIGINT, self._quit)
        logging.info(f"{MAIN_WINDOW}: Starting up!")

    def notify(self, sender, event, event2):
        """
        Consumers of this class should only communicate through here
        using the mediator design pattern.
        """
        if sender == CONCRETE_MEDIATOR:  # guard! but it should always be CM
            logging.debug(f"{MAIN_WINDOW}: notify received event: {event}")
            if event == NEW_SONG:
                self._update_labels(event2)
            elif event == NEW_STATION:
                self._station_label.config(text=f"Station: {event2}")
            elif event == QUIT:
                self._quit()
            elif event == SHOW:
                self._show_window()
            elif event == START:
                self._start()
            elif event == STATIONS:
                self._update_station_listbox(self.station_list)

            # above with command pattern
            # events = {
            #     NEW_SONG: lambda e2=event2: self._update_labels(e2),
            #     NEW_STATION: lambda e2=event2: self._station_label.config(
            #         text=f"Station: {event2}"),
            #     QUIT: self._quit,
            #     SHOW: self._show_window,
            #     START: self._start,
            #     STATIONS: lambda: self._update_station_listbox(self.station_list)
            # }
            # if event in events.keys():
            #     events[event]()

    def _create_album_label(self):
        """
        Create the album label
        """
        self._album_label = ttk.Label(wraplength=400)
        self._album_label.pack(padx=10, pady=10)

    def _create_artist_label(self):
        """
        Create the artist label
        """
        self._artist_label = ttk.Label(wraplength=400)
        self._artist_label.pack(padx=10, pady=10)

    def _create_change_station_button(self):
        """
        Build and add a button to the MainWindow
        """
        self._btn_change_station = ttk.Button(self._window, text="Change",
                                              command=self._handle_change_station_btn_pressed,
                                              bootstyle=(DARK, OUTLINE))

        self._btn_change_station.pack(side=tkinter.LEFT, padx=5, pady=(0,10))  # 0 top, 10 bottom

    def _create_next_button(self):
        """
        Build and add a button to the MainWindow
        """
        self._btn_next = ttk.Button(self._window, text="Next",
                                    command=self._handle_next_btn_pressed,
                                    bootstyle=(DARK, OUTLINE))

        self._btn_next.pack(side=tkinter.LEFT, padx=5, pady=(0,10))  # 0 top, 10 bottom

    def _create_play_pause_button(self):
        """
        Build and add a button to the MainWindow
        """
        self._btn_play_pause = ttk.Button(self._window, text="Play/Pause",
                                          command=self._handle_play_pause_btn_pressed,
                                          bootstyle=(DARK, OUTLINE))

        self._btn_play_pause.pack(side=tkinter.LEFT, padx=7, pady=(0,10))  # 0 top, 10 bottom

    def _create_heart_image_handles(self):
        """
        Create the handles to the heart images
        """
        # color:
        self._heart_path_color = "heart.png"
        self._heart_handle_color = Image.open(self._heart_path_color)
        self._heart_color = ImageTk.PhotoImage(self._heart_handle_color)

        # gray:
        self._heart_path_gray = "heartGray.png"
        self._heart_handle_gray = Image.open(self._heart_path_gray)
        self._heart_gray = ImageTk.PhotoImage(self._heart_handle_gray)

    def _create_heart_label(self):
        """
        - Sets a gray heart image as default on the MainWindow at startup
        - Set a mouse double click event listener on the image
        """
        self._heart_img_label = ttk.Label(self._media_info_frame, image=self._heart_gray)
        self._heart_img_label.pack(side=tkinter.RIGHT, padx=5)
        self._heart_img_label.bind("<Double-Button-1>", self._handle_heart_double_click)

    def _create_song_label(self):
        """
        Create song label
        """
        self._song_label = ttk.Label(self._media_info_frame, wraplength=300)
        self._song_label.pack(side=tkinter.LEFT, padx=10, pady=10)

    def _create_station_label(self):
        """
        Create station label
        """
        self._station_label = ttk.Label(text="Station", wraplength=400)
        self._station_label.pack(padx=10, pady=10)

    def _create_station_listbox(self):
        """
        Build and add a Listbox to the MainWindow
        """

        listbox_frame = ttk.Frame(self._window)
        listbox_frame.pack(side=TOP, fill=BOTH, expand=True)
        self._msg_lbox_scrollbar = ttk.Scrollbar(listbox_frame, orient="vertical")
        self._msg_lbox_scrollbar.pack(side=RIGHT, fill=BOTH)

        self._msg_lbox = ListBox(listbox_frame).get_listbox()
        self._msg_lbox.pack(side=LEFT, fill=BOTH, expand=True)

        self._msg_lbox_scrollbar.config(command=self._msg_lbox.yview)
        self._msg_lbox.config(yscrollcommand=self._msg_lbox_scrollbar.set)

        num_visible_rows = 5
        self._msg_lbox.configure(height=num_visible_rows)

        # for testing
        # for values in range(100):
        #     self._msg_lbox.insert(END, values)

    def _create_ui(self):
        """
        Build the MainWindow
        """
        self._window = ttk.Window(themename=self._theme)
        self._window.title(self._app_name)
        # TODO needed?
        #While having a handle to the current Style isn't really used in this
        # app, having this is variable in our template helps, so that if we
        # change things for events in a _real_app_ we can revert with:
        #       self._style.theme_use(themename=self._theme)
        #
        # Some things might need tweaking, but saves a lot of work.
        self._style = Style()
        # make the buttons appear flat and dark
        self._style.configure("TButton", relief="flat", background="#222222")
        self._create_window_icon()
        self._set_global_font_defaults()
        self._create_frame_with_media_info_labels()
        self._create_station_listbox()
        self._create_frame_with_controls()
        self._get_data()

        # override the def behavior of clicking close window button to hide it!
        self._window.protocol("WM_DELETE_WINDOW", self._hide_window)
        logging.debug(f"{MAIN_WINDOW}: completed create UI")

    def _create_frame_with_media_info_labels(self):
        """
        Frame to hold the song label and the heart icon
        """
        self._media_info_frame = ttk.Frame(self._window)
        self._media_info_frame.pack(pady=10)
        self._create_heart_image_handles()
        self._create_heart_label()
        self._create_song_label()
        self._create_artist_label()
        self._create_album_label()
        self._create_station_label()

    def _create_frame_with_controls(self):
        """
        Frame to hold the controls buttons
        """
        self._control_buttons_frame = ttk.Frame(self._window)
        self._control_buttons_frame.pack(pady=(5, 5))  # 5 top, 5 bottom
        self._create_play_pause_button()
        self._create_next_button()
        self._create_change_station_button()

    def _create_window_icon(self):
        """
        Create a transparent icon and use that instead of Tk's default icon.

        The use of transparent is optional, you can use a real icon or the TK
        default if you like.
        """
        # Create a transparent icon image in memory, to get rid of ugly Tk icon.
        app_icon = Image.new('RGBA', (1, 1), (0, 0, 0, 0))
        icon_photo = ImageTk.PhotoImage(app_icon)
        self._window.iconphoto(True, icon_photo)

    def _dummy_function(self):
        """
        https://stackoverflow.com/questions/9998274/tkinter-keyboard-interrupt-isnt-handled-until-tkinter-frame-is-raised
        What you're seeing is caused by the way signal handlers are
        handled. You're stuck in the Tcl/Tk main loop, and signal handlers
        are only handled by the Python interpreter. A quick workaround
        is to use after() to schedule a dummy function to be called once a
        second or so -- this will make it appear that your signal is handled
        in a timely manner.

        --Guido van Rossum

        This function is used to yield control back to Python so we can catch
        SIGINT when the app is not in focus.
        """
        self._window.after(2000, self._dummy_function)

    def _get_data(self):
        """
        Request data from mediator to show in the GUI
        """
        logging.debug(f"{MAIN_WINDOW}: sending MAIN_WINDOW_READY signal.")
        self.mediator.notify(MAIN_WINDOW, event=MAIN_WINDOW_READY, event2=None)
        self.mediator.notify(MAIN_WINDOW, event=GET_STATION, event2=None)
        self.mediator.notify(MAIN_WINDOW, event=GET_SONG_DATA, event2=None)
        self.mediator.notify(MAIN_WINDOW, event=GET_STATIONS, event2=None)

    def _handle_change_station_btn_pressed(self):
        """
        Change the current Pandora station
        """
        # Get the indices of the selected items in the listbox
        selected_indices = self._msg_lbox.curselection()

        if selected_indices:
            # Retrieve the index of the first selected item
            index = selected_indices[0]

            # Retrieve the item from the listbox based on the index
            selected_item = self._msg_lbox.get(index)

            # Extract the station number from the selected item
            station_number = int(selected_item.split(":")[0])

            # Notify the mediator with the station number
            logging.debug(
                f"{MAIN_WINDOW}: changing to station: {station_number}")
            self.mediator.notify(MAIN_WINDOW, event=STATION_CHANGE_REQUESTED, event2=station_number)
        else:
            logging.critical(
                f"{MAIN_WINDOW}: could not determine which station you want to change to!")
            print("No station selected!")  # TODO

    def _handle_heart_double_click(self, event):
        """
        Handles double-clicking event on the heart graphic on the main GUI
        """
        self._is_favorite = not self._is_favorite
        if self._is_favorite:
            logging.debug(f"{MAIN_WINDOW}: marking song as loved.")
            self._swap_heart_image(self._is_favorite)
            self.mediator.notify(MAIN_WINDOW, LOVE, event2=None)
        else:
            logging.debug(f"{MAIN_WINDOW}: NOT marking song as loved.")

    def _handle_next_btn_pressed(self):
        """
        Notify the mediator that the MEDIA_NEXT button was pressed
        """
        logging.debug(f"{MAIN_WINDOW}: btn_next clicked event trigged")
        self.mediator.notify(MAIN_WINDOW, event=MEDIA_NEXT, event2=None)

    def _handle_play_pause_btn_pressed(self):
        """
        Notify the mediator that the MEDIA_PLAY button was pressed
        """
        logging.debug(f"{MAIN_WINDOW}: btn_play_pause clicked event trigged")
        self.mediator.notify(MAIN_WINDOW, event=MEDIA_PLAY, event2=None)

    def _hide_window(self):
        """
        Hide's the MainWindow
        """
        if self._window:
            logging.debug(f"{MAIN_WINDOW}: hiding MainWindow")
            self._window.withdraw()

    def _quit(self, signum=None, frame=None):
        """
        Tell mediator to quit and closes the MainWindow
        """
        self.mediator.notify(MAIN_WINDOW, event=QUIT, event2=None)
        if self._window:
            self._window.quit()
            logging.info("Goodbye from MainWindow!")

    def _set_global_font_defaults(self):
        """
        Set the global default font and size for all widgets created after
        this is function has been called.
        """
        self._global_font = tkFont.nametofont("TkDefaultFont")
        self._global_font.configure(size=18)

    def _show_window(self):
        """
        Shows the main window of our application and brings it to focus.
        """
        self._window.after(0, self._window.deiconify)
        # get the window to come to foreground on GNU/Linux
        self._window.lift()
        self._window.attributes("-topmost", True)
        self._window.focus_force()
        logging.debug(f"{MAIN_WINDOW}: showing MainWindow")

    def _start(self):
        """
        Create the main window and brings it to foreground
        """
        self._create_ui()
        self._window.after(1000, self._dummy_function)
        self._window.mainloop()

    def _swap_heart_image(self, is_favorite):
        """
        Swaps the heart image on the main ui
        """
        self._is_favorite = is_favorite
        if is_favorite:
            self._heart_img_label.config(image=self._heart_color)
        else:
            self._heart_img_label.config(image=self._heart_gray)

    def _update_labels(self, song_data):
        """
        Args:
            song_data (Song): a Song class obj
            extracts the values for the labels in the GUI
            sets the color of the heart icon in the GUI
        """
        album, artist, favorite, title = song_data.album, song_data.artist, song_data.favorite, song_data.title
        self._song_label.config(text=f"{title}")
        self._artist_label.config(text=f"By: {artist}")
        self._album_label.config(text=f"From: {album}")
        if favorite:
            logging.debug(f"{MAIN_WINDOW}: is favorite song")
            self._swap_heart_image(True)
        else:
            logging.debug(f"{MAIN_WINDOW}: is NOT favorite song")
            self._swap_heart_image(False)

    def _update_station_listbox(self, stations: List[Tuple[int, str]]):
        """
        Update the station listbox with the provided list of stations.
        """
        # Clear the listbox
        self._msg_lbox.delete(0, END)

        # Populate the listbox
        for number, name in stations:
            self._msg_lbox.insert(END, f"{number}: {name}")

        logging.debug(f"{MAIN_WINDOW}: finished populating stations listbox")


    # if we want to user a text box in lieu of labels for wrapping text
    # def create_wrapped_text(self): TODO test and add ?
    #     text = ("This is a long piece of text that will be wrapped "
    #             "automatically within the Text widget in Tkinter.")
    #
    #     wrapped_text = tk.Text(self._media_info_frame, wrap=tk.WORD, width=30,
    #                            height=5)
    #     wrapped_text.insert(tk.END, text)
    #     wrapped_text.config(state=tk.DISABLED)  # Make the Text widget read-only
    #     wrapped_text.pack()
