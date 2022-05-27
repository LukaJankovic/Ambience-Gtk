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

from gi.repository import Gtk, Adw


@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/src/ui/row.ui')
class AmbienceRow(Gtk.ListBoxRow):
    """Sidebar rows supporting editing."""
    
    __gtype_name__ = 'AmbienceRow'
    
    stack = Gtk.Template.Child()
    label = Gtk.Template.Child()
    entry = Gtk.Template.Child()
    
    group = None
    
    def __init__(self, group, **kwargs):
        super().__init__(**kwargs)
        
        self.group = group
        
        self.label.set_text(self.group.label)
        self.entry.set_text(self.group.label)
        
        self.stack.set_visible_child_name('label')
        
        # Add controller for right click detection
        gesture = Gtk.GestureSingle()
        gesture.set_button(3)
        gesture.connect("end", self.begin_edit)
        self.add_controller(gesture)
        
    @Gtk.Template.Callback("entry_activate_cb")
    def entry_activate_cb(self, sender):
        """Edit entry pressed enter.
        
        Args:
            sender: the entry which activated
        """
        
        self.end_edit()
        
    def begin_edit(self, sender, user_data):
        """The row was i.e. right-clicked, change modes.
        
        Args:
            sender:     the entry which activated
            user_data:  optional user data (not used)
        """
        
        self.stack.set_visible_child_name('edit')
        self.entry.grab_focus()

        # Set current row active TODO: fix
        #self.get_parent().select_row(self)

    def end_edit(self):
        """The row should end editing."""
        
        self.stack.set_visible_child_name('label')
