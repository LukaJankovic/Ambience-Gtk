# ambience_group_row.py
#
# Copyright 2022 Luka Jankovic
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

from gi.repository import Gtk

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_group_row.ui')
class AmbienceGroupRow(Gtk.ListBoxRow):
    __gtype_name__ = 'AmbienceGroupRow'

    group = None
    check_action = None

    title = Gtk.Template.Child()
    check = Gtk.Template.Child()

    def get_title(self):
        return self.title.get_label()

    def set_title(self, label):
        self.title.set_label(label)

    @Gtk.Template.Callback("checked")
    def checked(self, sender):
        self.check_action(self)

    def __init__(self, group, **kwargs):
        super().__init__(**kwargs)

        self.group = group
        self.title.set_label(self.group.get_label())