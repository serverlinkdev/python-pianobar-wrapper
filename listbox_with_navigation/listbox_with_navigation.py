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
import tkinter as tk


class ListboxWithNavigation:
    _listbox = None

    def __init__(self, root):
        self._listbox = tk.Listbox(root)
        self._listbox.bind("<Home>", self.on_home)
        self._listbox.bind("<End>", self.on_end)

    def on_end(self, event):
        # Navigate to the bottom of the list when pressing END key on KB
        self._listbox.select_clear(0, "end")
        last_index = self._listbox.size() - 1
        self._listbox.select_set(last_index)
        self._listbox.activate(last_index)
        self._listbox.see(last_index)

    def on_home(self, event):
        # Navigate to the top of the list when pressing HOME key on KB
        self._listbox.select_clear(0, "end")
        self._listbox.select_set(0)
        self._listbox.activate(0)
        self._listbox.see(0)

    def get_listbox(self):
        return self._listbox
