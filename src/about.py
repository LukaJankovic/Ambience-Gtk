# about.py
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

from gi.repository import Gtk, Gio, Adw

class AboutDialog(Gtk.AboutDialog):

    def __init__(self, parent, version):
        Gtk.AboutDialog.__init__(self)
        self.props.program_name = 'Ambience'
        self.props.version = version
        self.props.authors = ['Luka Jankovic']
        self.props.logo_icon_name = 'io.github.lukajankovic.ambience'
        self.props.modal = True
        self.props.website = 'https://github.com/LukaJankovic/Ambience'
        self.props.website_label = 'GitHub Page'
        self.props.copyright = '© 2020-2022 Luka Jankovic'
        self.add_credit_section('LifxLAN by', ['ML Clark'])
        self.set_transient_for(parent)
