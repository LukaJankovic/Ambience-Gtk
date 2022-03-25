# ambience_window.py
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

from struct import error
import threading

from gi.repository import Gtk, Gdk, GLib, Adw

from .ambience_loader import *

from .ambience_discovery import AmbienceDiscovery

from ambience.widgets.ambience_flow_box import AmbienceFlowBox
from ambience.widgets.ambience_group_tile import AmbienceGroupTile
from ambience.widgets.ambience_light_tile import AmbienceLightTile
from ambience.widgets.ambience_edit_tile import AmbienceEditTile
from ambience.widgets.ambience_group_row import AmbienceGroupRow
from ambience.widgets.ambience_tile import AmbienceTile

from ambience.views.ambience_group_control import AmbienceGroupControl
from ambience.views.ambience_light_control import AmbienceLightControl

import threading

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ambience_window.ui')
class AmbienceWindow(Adw.ApplicationWindow):
    """
    Controls almost every aspect of the main window, including maintaining
    a list of lights and controling them.
    """
    __gtype_name__ = 'AmbienceWindow'

    main_leaflet = Gtk.Template.Child()

    title_label = Gtk.Template.Child()
    group_label_stack = Gtk.Template.Child()
    group_label_edit = Gtk.Template.Child()
    group_label_entry = Gtk.Template.Child()

    menu_box = Gtk.Template.Child()
    header_bar = Gtk.Template.Child()
    sidebar = Gtk.Template.Child()
    check_revealer = Gtk.Template.Child()
    remove_button = Gtk.Template.Child()

    group_header_bar = Gtk.Template.Child()
    back = Gtk.Template.Child()

    controls_deck = Gtk.Template.Child()
    tiles_box = Gtk.Template.Child()

    tiles_list = Gtk.Template.Child()

    new_group_popover = Gtk.Template.Child()
    new_group_entry = Gtk.Template.Child()
    new_group_button = Gtk.Template.Child()

    invalid_name = Gtk.Template.Child()

    add_group_button = Gtk.Template.Child()
    refresh_button = Gtk.Template.Child()

    etiles_revealer = Gtk.Template.Child()
    etiles_remove = Gtk.Template.Child()

    group_labels = []
    group_to_delete = []
    edit_devices_tiles = []
    editing = False
    should_update_sb_label = True

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

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        """
        Back button pressed. Goes back to group list.
        """
        self.sidebar.unselect_all()
        self.main_leaflet.set_visible_child(self.menu_box)

    @Gtk.Template.Callback("sidebar_selected")
    def sidebar_selected(self, sender, user_data):
        """
        0. Show loading spinner on refresh button (done)
        1. Load lights from file (dont separate / disable offline
        2. Load power and color in background, update UI (if light controls shown -> update those, jump to 3)
        3. Load capabilities and info in background, update UI (-||-)

        2-3 to be in global class, start ASAP, repeat every interval
        """
        self.should_update_sb_label = False
        self.group_label_edit.set_active(False)
        self.should_update_sb_label = True

        self.refresh_button.set_sensitive(False)
        self.clear_tiles()

        if not self.sidebar.get_selected_row():
            self.group_label_edit.set_visible(False)
            self.refresh_button.set_visible(False)
            return

        self.main_leaflet.set_visible_child_name("controls")

        self.active_group = self.sidebar.get_selected_row().group
        self.title_label.set_text(self.active_group.label)

        self.group_label_edit.set_visible(True)
        self.refresh_button.set_visible(True)

        if not self.active_group.get_devices():
            add_tile = AmbienceTile("Add devices...", self.manage_devices)

            add_category = AmbienceFlowBox()
            add_category.insert(add_tile, -1)

            self.tiles_list.add(add_category)
            return

        tile_size_group = Gtk.SizeGroup()
        tile_size_group.set_mode(Gtk.SizeGroupMode.HORIZONTAL)

        all_category = AmbienceFlowBox()
        all_tile = AmbienceGroupTile(self.active_group, self.group_edit)
        tile_size_group.add_widget(all_tile)

        all_category.insert(all_tile, -1)
        self.tiles_list.add(all_category)

        header_label = self.create_header_label()
        header_label.set_text("Lights")

        self.tiles_list.add(header_label)

        lights_category = AmbienceFlowBox()

        for device in self.active_group.get_devices():
            light_tile = AmbienceLightTile(device, self.tile_clicked)
            device.tile = light_tile
            tile_size_group.add_widget(light_tile)
            lights_category.insert(light_tile, -1)

        self.tiles_list.add(lights_category)

        def load_data_async():
            for device in self.active_group.devices:
                if device.get_online():
                    for _ in range(5):
                        try:
                            if not device.capabilities:
                                device.capabilities = device.get_capabilities()
                            
                            if not device.color:
                                device.color = device.get_color()
                            
                            if not device.label:
                                device.label = device.get_label()

                            if not device.power:
                                device.power = device.get_power()

                            if not device.info:
                                device.info = device.get_info()
                            break
                        except:
                            pass

                    device.available = True
                else:
                    device.available = False

                def enable_refresh_button():
                    self.refresh_button.set_sensitive(True)

                GLib.idle_add(device.tile.update)
            GLib.idle_add(all_tile.update)
            GLib.idle_add(enable_refresh_button)
        load_devices_thread = threading.Thread(target=load_data_async)
        load_devices_thread.daemon = True
        load_devices_thread.start()

    def show_edit_tiles(self):
        self.refresh_button.set_sensitive(False)
        self.etiles_remove.set_sensitive(False)
        self.clear_tiles()

        tile_size_group = Gtk.SizeGroup()
        tile_size_group.set_mode(Gtk.SizeGroupMode.HORIZONTAL)
        
        header_label = self.create_header_label()
        header_label.set_text("Lights")

        self.tiles_list.add(header_label)

        lights_category = AmbienceFlowBox()
        self.edit_devices_tiles = []

        for device in self.active_group.get_devices():

            def edit_checked(light, active):
                if not active and light in self.edit_devices_tiles:
                    self.edit_devices_tiles.remove(light)
                else:
                    self.edit_devices_tiles.append(light)

                self.etiles_remove.set_sensitive(len(self.edit_devices_tiles) > 0)

            tile = AmbienceEditTile(device, edit_checked)
            tile_size_group.add_widget(tile)
            lights_category.insert(tile, -1)

        add_tile = AmbienceTile("Add devices...", self.manage_devices)
        lights_category.insert(add_tile, -1)

        self.tiles_list.add(lights_category)

    @Gtk.Template.Callback("remove_devices")
    def remove_devices(self, sender):
        def perform_delete(_, response):
            if response == Gtk.ResponseType.YES:
                for tile in self.edit_devices_tiles:
                    self.active_group.remove_device(tile.device)
                    tile.destroy()

        confirm_dialog = Gtk.MessageDialog(self,
                                            0,
                                            Gtk.MessageType.WARNING,
                                            Gtk.ButtonsType.NONE,
                                            f"Are you sure you want to delete {len(self.edit_devices_tiles)} devices(s)?"
        )
        confirm_dialog.format_secondary_text(
            "This action cannot be reversed."
        )

        confirm_dialog.add_button("_Cancel", Gtk.ResponseType.CLOSE)
        confirm_dialog.add_button("_Delete", Gtk.ResponseType.YES)

        confirm_dialog.get_widget_for_response(Gtk.ResponseType.YES).get_style_context().add_class("destructive-action")
        confirm_dialog.get_widget_for_response(Gtk.ResponseType.YES).get_style_context().add_class("default")

        confirm_dialog.connect("response", perform_delete)

        confirm_dialog.run()
        confirm_dialog.destroy()

    def update_tiles(self, light=None):
        for child in self.tiles_list.get_children():
            if type(child) == AmbienceFlowBox:
                for tile in child.flowbox.get_children():
                    if (type(tile) == AmbienceLightTile and \
                       ((light and light.write_config() == tile.light.write_config()) or not light)) or \
                       (type(tile) == AmbienceGroupTile):
                        tile.update()

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

        while first_child := self.sidebar.get_first_child():
            self.sidebar.remove(first_child)

    def clear_tiles(self):
        """
        Empties the main view from tiles, headers, etc.
        """

        while first_child := self.tiles_list.get_first_child():
            self.tiles_list.remove(first_child)

    #@Gtk.Template.Callback()
    def create_group(self, sender, *args):
        label = self.new_group_entry.get_text()
        group = AmbienceLoader().get_group(label)
        group_row = AmbienceGroupRow(group)
        group_row.check_action = self.update_delete_list
        self.sidebar.insert(group_row, -1)

        self.new_group_popover.popdown()
        self.group_labels.append(label)
        self.new_group_entry.set_text("")

    @Gtk.Template.Callback("add_group_toggled")
    def add_group_toggled(self, sender):
        if sender.get_active():
            self.new_group_entry.set_text("")
            self.new_group_entry.grab_focus()
        self.invalid_name.set_reveal_child(False)
        self.new_group_entry.get_style_context().remove_class("error")

    #@Gtk.Template.Callback("new_group_entry_changed")
    def new_group_entry_changed(self, sender):
        if not self.new_group_entry.get_text():
            self.new_group_button.set_sensitive(False)
            return

        if self.new_group_entry.get_text() in self.group_labels:
            self.new_group_entry.get_style_context().add_class("error")
            self.new_group_button.set_sensitive(False) 
            self.invalid_name.set_reveal_child(True)
        else:
            self.new_group_button.set_sensitive(True)
            self.invalid_name.set_reveal_child(False)
            self.new_group_entry.get_style_context().remove_class("error")

    @Gtk.Template.Callback("toggle_edit")
    def toggle_edit(self, sender):
        self.group_label_edit.set_active(False)
        self.deselect_sidebar()

        self.editing = sender.get_active()
        
        self.check_revealer.set_reveal_child(self.editing)
        self.add_group_button.set_sensitive(not self.editing)

        self.remove_button.set_sensitive(False)

        if self.editing:

            self.header_bar.get_style_context().add_class("selection-mode")
            self.group_header_bar.get_style_context().add_class("selection-mode")

            self.sidebar.set_selection_mode(Gtk.SelectionMode.NONE)

            row = self.sidebar.get_first_child()
            while row:
                row.check.set_opacity(1)
                row.check.set_active(False)
                row = row.get_next_sibling()

            self.header_bar.set_title("0 Selected")

        else:
            self.header_bar.get_style_context().remove_class("selection-mode")
            self.group_header_bar.get_style_context().remove_class("selection-mode")

            self.sidebar.set_selection_mode(Gtk.SelectionMode.SINGLE)

            row = self.sidebar.get_first_child()
            while row:
                row.check.set_visible(False)
                row = row.get_next_sibling()

            self.header_bar.set_title("Ambience")

    def deselect_sidebar(self):
        self.clear_tiles()
        self.title_label.set_text("")
        self.sidebar.unselect_all()

        self.group_label_edit.set_visible(False)

        self.controls_deck.set_visible_child_name("tiles")

#    @Gtk.Template.Callback("manage_devices")
    def manage_devices(self, sender):
        """
        Opens the window for managing a group's devices.
        """

        def discovery_done(sender, user_data):
            self.sidebar_selected(self, None)

        discovery_window = AmbienceDiscovery(transient_for=self, modal=True, use_header_bar=1)
        discovery_window.group = self.active_group
        discovery_window.connect("response", discovery_done)
        discovery_window.show_all()

    def reload(self, sender):
        """
        Reloads data from config file and populates sidebar.
        """

        self.controls_deck.set_visible_child(self.tiles_box)
        self.clear_tiles()
        self.clear_sidebar()

        for group in AmbienceLoader().get_all_groups():
            group.generate_groups()
            group_row = AmbienceGroupRow(group)
            group_row.check_action = self.update_delete_list
            self.group_labels.append(group_row.get_title())
            self.sidebar.insert(group_row, -1)

    @Gtk.Template.Callback("reload_group")
    def reload_group(self, sender):
        for device in self.active_group.get_devices():
            device.capabilities = None
            device.color = None
            device.power = None
            device.info = None
        self.sidebar_selected(self, None)

    def reload_group_name(self):
        self.title_label.set_text(self.active_group.get_label())
        self.sidebar.get_selected_row().set_title(self.active_group.get_label())

    def group_label_valid(self, text):
        return text and not (text in self.group_labels and text != self.active_group.get_label())

    @Gtk.Template.Callback("group_label_edit_toggled")
    def group_label_edit_toggled(self, sender):
        self.etiles_revealer.set_reveal_child(sender.get_active())

        if sender.get_active():
            self.group_label_entry.set_text(self.active_group.get_label())
            self.group_label_entry.grab_focus()

            self.group_label_stack.set_visible_child_name("edit")

            self.show_edit_tiles()

        elif self.should_update_sb_label:
            text = self.group_label_entry.get_text()
            if self.group_label_valid(text):
                self.group_labels.remove(self.active_group.get_label())
                self.active_group = AmbienceLoader().rename_group(self.active_group, text)
                self.group_labels.append(self.active_group.get_label())
                self.reload_group_name()

                self.group_label_stack.set_visible_child_name("label")
                self.sidebar_selected(self, None)
        else:
            self.group_label_stack.set_visible_child_name("label")


    #
    # TODO: GtkEventConntrollerKey
    #
    #@Gtk.Template.Callback("group_edit_event")
    def group_edit_event(self, sender, event):
        if event.keyval == Gdk.KEY_Escape:
            self.group_label_entry.set_text(self.active_group.get_label())
            self.group_label_edit.set_active(False)

    @Gtk.Template.Callback("group_label_changed")
    def group_label_changed(self, sender):
        self.group_label_edit.set_sensitive(self.group_label_valid(self.group_label_entry.get_text()))

    @Gtk.Template.Callback("group_label_activate")
    def group_label_activate(self, sender):
        if self.group_label_valid(self.group_label_entry.get_text()):
            self.group_label_edit.set_active(False)

    # Light control

    def tile_clicked(self, tile):
        """
        Runs when a tile gets clicked. Switches to the light control page.
        """
        light_controls = AmbienceLightControl(tile.light,
                                              self.controls_deck,
                                              self.light_control_exit,
                                              self.update_tiles)
        light_controls.set_visible(True)

        self.controls_deck.insert_child_after(light_controls, self.tiles_box)
        self.controls_deck.navigate(Handy.NavigationDirection.FORWARD)
        light_controls.show()

    def group_edit(self, tile):
        group_controls = AmbienceGroupControl(tile.group,
                                              self.controls_deck,
                                              self.light_control_exit,
                                              self.update_tiles)

        group_controls.set_visible(True)

        self.controls_deck.insert_child_after(group_controls, self.tiles_box)
        self.controls_deck.navigate(Handy.NavigationDirection.FORWARD)
        group_controls.show()

    def light_control_exit(self, controls):
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

    def remove_group(self, row):
        AmbienceLoader().delete_group(row.group)
        self.group_labels.remove(row.group.get_label())
        self.sidebar.remove(row)

    def update_delete_list(self, row):
        if row.check.get_active():
            self.group_to_delete.append(row)
        elif row in self.group_to_delete:
            self.group_to_delete.remove(row)

        self.remove_button.set_sensitive(self.group_to_delete)
        self.header_bar.set_title(f"{len(self.group_to_delete)} Selected")

    @Gtk.Template.Callback("remove_groups_clicked")
    def remove_groups_clicked(self, sender):
        def perform_delete(_, response):
            if response == Gtk.ResponseType.YES:
                for group in self.group_to_delete:
                    self.remove_group(group)

            self.group_to_delete = []

            self.remove_button.set_sensitive(self.group_to_delete)
            self.header_bar.set_title(f"{len(self.group_to_delete)} Selected")

        confirm_dialog = Gtk.MessageDialog(self,
                                            0,
                                            Gtk.MessageType.WARNING,
                                            Gtk.ButtonsType.NONE,
                                            f"Are you sure you want to delete {len(self.group_to_delete)} group(s)?"
        )
        confirm_dialog.format_secondary_text(
            "This action cannot be reversed."
        )

        confirm_dialog.add_button("_Cancel", Gtk.ResponseType.CLOSE)
        confirm_dialog.add_button("_Delete", Gtk.ResponseType.YES)

        confirm_dialog.get_widget_for_response(Gtk.ResponseType.YES).get_style_context().add_class("destructive-action")
        confirm_dialog.get_widget_for_response(Gtk.ResponseType.YES).get_style_context().add_class("default")

        confirm_dialog.connect("response", perform_delete)

        confirm_dialog.run()
        confirm_dialog.destroy()

    # Initialization, startup

    def connect(self):
        self.new_group_entry.connect("activate", self.create_group)
        self.new_group_button.connect("clicked", self.create_group)

    def __init__(self, lan, **kwargs):
        super().__init__(**kwargs)

        self.connect()
        self.reload(self)
