# main.py
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

import sys
import gi

gi.require_version('Gtk', '3.0')
gi.require_version('Handy', '1')

from gi.repository import Gtk, Gdk, Gio, Handy

from .ambience_window import AmbienceWindow
from .ambience_discovery import AmbienceDiscovery

class Application(Gtk.Application):

    win = None
    lan = None
    version = ""

    def __init__(self):
        super().__init__(application_id='io.github.lukajankovic.ambience',
                         flags=Gio.ApplicationFlags.FLAGS_NONE)

        about_action = Gio.SimpleAction.new("about", None)
        about_action.connect("activate", self.about)
        self.add_action(about_action)

        refresh_action = Gio.SimpleAction.new("refresh", None)
        refresh_action.connect("activate", self.do_refresh)
        self.add_action(refresh_action)

    def about(self, state, user_data):
        about = Gtk.AboutDialog(transient_for=self.win, modal=True)
        authors = ["Luka Jankovic"]
        api_authors = ["ML Clark"]

        about.set_program_name("Ambience")
        about.set_version(self.version)
        about.set_license_type(Gtk.License.GPL_3_0)
        about.set_website("https://github.com/LukaJankovic/Ambience")
        about.set_website_label("Github Page")
        about.set_copyright("© 2020-2022 Luka Jankovic")
        about.add_credit_section("Created by", authors)
        about.add_credit_section("LifxLAN by", api_authors)
        about.set_logo_icon_name("io.github.lukajankovic.ambience")

        about.show_all()

    def do_refresh(self, state, user_data):
        self.win.reload(self)

    def do_activate(self):
        self.win = self.props.active_window
        if not self.win:
            self.win = AmbienceWindow(self.lan, application=self)

        screen = Gdk.Screen.get_default()
        provider = Gtk.CssProvider()
        provider.load_from_resource("/io/github/lukajankovic/ambience/stylesheet.css")
        Gtk.StyleContext.add_provider_for_screen(screen, provider, Gtk.STYLE_PROVIDER_PRIORITY_APPLICATION)

        self.win.present()


def main(version):

    Handy.init()

    app = Application()
    app.version = version
    return app.run(sys.argv)
