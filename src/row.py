# row.py
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

from gi.repository import Gtk, Gdk, Adw


@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/src/ui/row.ui')
class AmbienceRow(Gtk.ListBoxRow):
    """Sidebar rows supporting editing."""
    
    __gtype_name__ = 'AmbienceRow'
    
    stack = Gtk.Template.Child()
    label = Gtk.Template.Child()
    entry = Gtk.Template.Child()
    
    group = None
    config = None
    
    def __init__(self, group, config, **kwargs):
        super().__init__(**kwargs)
        
        self.group = group
        self.config = config
        
        self.label.set_text(self.group.label)
        self.entry.set_text(self.group.label)
        
        self.stack.set_visible_child_name('label')
        
        # Add controller for right click detection
        gesture = Gtk.GestureSingle()
        gesture.set_button(3) # TODO: fix magic number
        gesture.connect("end", self.begin_edit)
        self.add_controller(gesture)
        
        # Add controller for esc key detection
        esc = Gtk.EventControllerKey()
        esc.connect("key-released", self.entry_key_release_cb)
        self.entry.add_controller(esc)

    @Gtk.Template.Callback("entry_activate_cb")
    def entry_activate_cb(self, sender):
        """Edit entry pressed enter.
        
        Args:
            sender: the entry which activated
        """
        
        if self.validate_name(sender.get_text(), self.config):
            self.group.label = sender.get_text()
            self.label.set_text(self.group.label)
            self.end_edit()
        
    @Gtk.Template.Callback("entry_changed_cb")
    def entry_changed_cb(self, sender):
        """Edit entry text changed.

        Args:
            sender: the entry which changed
        """

        if not self.validate_name(sender.get_text(), self.config):
            sender.add_css_class("error")
        else:
            sender.remove_css_class("error")

    def entry_key_release_cb(self, sender, keycode, state, user_data):
        """Called whenever a key is pressed. Used to check if esc was pressed.

        Args:
            sender:     sender that triggered the event
            keycode:    raw keycode of released key
            state:      state of modifier keys
            user_data:  optional user data (not used)
        """

        if keycode == Gdk.KEY_Escape:
            self.end_edit()

    def begin_edit(self, sender, user_data):
        """The row was i.e. right-clicked, change modes.
        
        Args:
            sender:     the entry which activated
            user_data:  optional user data (not used)
        """
        
        # Set current row active
        self.get_parent().select_row(self)

        self.stack.set_visible_child_name('edit')

        self.entry.set_text(self.group.label)
        self.entry.grab_focus()

    def end_edit(self):
        """The row should end editing."""
        
        self.stack.set_visible_child_name('label')

    def validate_name(self, name, config):
        """Checks if the group name is free to use."""

        if len(name) == 0:
            return False

        for group in config.groups:
            if group.label == name and group.label != self.group.label:
                return False
        return True
