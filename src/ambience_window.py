# ambience_window.py
#
# Copyright 2021 Luka Jankovic
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

from struct import error
import threading

from gi.repository import Gtk, GLib, Handy
from .ambience_loader import *
from .ambience_group import *
from .ambience_light_tile import *
from .ambience_group_tile import *
from .ambience_light_control import *
import threading

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_window.ui')
class AmbienceWindow(Handy.ApplicationWindow):
    """
    Controls almost every aspect of the main window, including maintaining
    a list of lights and controling them.
    """
    __gtype_name__ = 'AmbienceWindow'

    main_popover = Gtk.Template.Child()
    main_leaflet = Gtk.Template.Child()

    title_label = Gtk.Template.Child()

    menu_box = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()
    refresh_stack = Gtk.Template.Child()
    refresh = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()

    group_header_bar = Gtk.Template.Child()
    back = Gtk.Template.Child()

    controls_deck = Gtk.Template.Child()
    tiles_box = Gtk.Template.Child()

    loading_stack = Gtk.Template.Child()
    tiles_list = Gtk.Template.Child()

    refresh_spinner = Gtk.Template.Child()
    tiles_spinner = Gtk.Template.Child()

    def create_header_label(self):
        """
        Returns a GtkLabel suitable to be used as a header in the tiles list.
        """
        label = Gtk.Label()
        label.get_style_context().add_class("title-3")
        label.set_visible(True)
        label.set_margin_start(6)
        label.set_margin_end(6)
        label.set_margin_top(6)
        label.set_margin_bottom(6)
        label.set_alignment(0, 0)

        return label

    @Gtk.Template.Callback("notify_fold_cb")
    def notify_fold_cb(self, sender, user_data):
        """
        Window switched between normal and mobile (folded) state.
        """
        pass

    @Gtk.Template.Callback("notify_visible_child_name")
    def notify_visible_child_name(self, sender, user_data):
        if sender.get_visible_child_name() == "menu":
            self.go_back(sender)

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        """
        Back button pressed. Goes back to group list.
        """
        self.sidebar.unselect_all()
        self.refresh_stack.set_visible_child_name("refresh")
        self.main_leaflet.set_visible_child(self.menu_box)

    @Gtk.Template.Callback("sidebar_selected")
    def sidebar_selected(self, sender, user_data):
        """
        Group in sidebar selected by user.
        """
        self.refresh_stack.set_visible_child_name("loading")
        self.refresh_spinner.start()

        self.clear_controls()
        self.clear_tiles()

        active_group = AmbienceLoader().get_group(self.sidebar.get_selected_row().get_title())

        all_category = AmbienceFlowBox()
        all_tile = AmbienceGroupTile(active_group)
        all_tile.clicked_callback = self.group_edit
        all_category.insert(all_tile, -1)

        self.tiles_list.add(all_category)

        def create_category(lights, title):
            lights_label = self.create_header_label()
            lights_label.set_text(title)

            self.tiles_list.add(lights_label)

            lights_category = AmbienceFlowBox()

            for light in lights:
                lights_category.insert(AmbienceLightTile(light, self.tile_clicked), -1)

            self.tiles_list.add(lights_category)

        if len(active_group.online) > 0:
            create_category(active_group.online, "Lights")

        if len(active_group.offline) > 0:
            create_category(active_group.offline, "Offline")

        self.refresh_stack.set_visible_child_name("refresh")
        self.refresh_spinner.stop()

    def clear_controls(self):
        """
        Removes control views from deck.
        """
        self.controls_deck.set_visible_child_name("tiles")
        for child in self.controls_deck.get_children()[1:]:
            self.controls_deck.remove(child)

    def clear_sidebar(self):
        """
        Empties the sidebar.
        """

        for sidebar_item in self.sidebar.get_children():
            self.sidebar.remove(sidebar_item)

    def clear_tiles(self):
        """
        Empties the main view from tiles, headers, etc.
        """

        for group_item in self.tiles_list.get_children():
            self.tiles_list.remove(group_item)

    @Gtk.Template.Callback("reload")
    def reload(self, sender):
        """
        Reloads data from config file and populates sidebar.
        """
        self.clear_tiles()
        self.clear_sidebar()

        self.groups = AmbienceLoader().get_group_labels()

        for group in self.groups:
            group_item = Handy.ActionRow()
            group_item.set_visible(True)
            group_item.set_title(group)
            
            self.sidebar.insert(group_item, -1)

    # Light control

    def tile_clicked(self, tile):
        """
        Runs when a tile gets clicked. Switches to the light control page.
        """
        light_controls = AmbienceLightControl(tile.light,
                                              self.controls_deck,
                                              self.light_control_exit)
        light_controls.set_visible(True)

        self.controls_deck.insert_child_after(light_controls, self.tiles_box)
        self.controls_deck.navigate(Handy.NavigationDirection.FORWARD)
        light_controls.show()

    def group_edit(self):

        group_controls = AmbienceGroupControl(self.active_row.group,
                                              self.online,
                                              self.controls_deck,
                                              self.light_control_exit)

        group_controls.set_visible(True)

        self.controls_deck.insert_child_after(group_controls, self.tiles_box)
        self.controls_deck.navigate(Handy.NavigationDirection.FORWARD)
        group_controls.show()

    def light_control_exit(self, controls):
        self.remove_request = controls
        self.controls_deck.navigate(Handy.NavigationDirection.BACK)

    # Group management
    def get_group_value(self, prop):
        value = -1
        for light in self.online:
            if value == -1:
                value = light.__dict__[prop]
            elif not value == light.__dict__[prop]:
                break

        if value == -1:
            return None
        return value

    # Initialization, startup

    def __init__(self, lan, **kwargs):
        super().__init__(**kwargs)
        self.reload(self)
