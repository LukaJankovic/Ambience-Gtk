import threading

from gi.repository import Gtk, Gdk, GLib

from .helpers import *

@Gtk.Template(resource_path='/io/github/lukajankovic/ambience/ui/ambience_group_control.ui')
class AmbienceGroupControl(Gtk.Box):
    __gtype_name__ = 'AmbienceGroupControl'

    main_stack = Gtk.Template.Child()

    hue_row = Gtk.Template.Child()
    saturation_row = Gtk.Template.Child()
    kelvin_row = Gtk.Template.Child() 
    infrared_row = Gtk.Template.Child()

    hue_scale = Gtk.Template.Child()
    saturation_scale = Gtk.Template.Child()
    brightness_scale = Gtk.Template.Child()
    kelvin_scale = Gtk.Template.Child()
    kelvin_adj = Gtk.Template.Child()
    infrared_scale = Gtk.Template.Child()

    power_switch = Gtk.Template.Child()

    light_label = Gtk.Template.Child()
    light_sub_label = Gtk.Template.Child()

    group = None
    online = None
    deck = None
    back_callback = None
    capabilities = {}
    has_infrared = False

    def __init__(self, group, online, deck, back_callback, **kwargs):
        self.group = group
        self.online = online
        self.deck = deck
        self.back_callback = back_callback

        super().__init__(**kwargs)

    def show(self):
        self.update_active = True
        self.main_stack.set_visible_child_name("loading")

        self.light_label.set_label(self.group["label"])

        if len(self.online) == 1:
            self.light_sub_label.set_label("One light online")
        else:
            self.light_sub_label.set_label(str(len(self.online)) + " lights online")

        def capabilities_callback():
            GLib.idle_add(self.update_controls)

        fetch_thread = threading.Thread(target=self.get_capabilities, args=(capabilities_callback,)) 
        fetch_thread.daemon = True
        fetch_thread.start()

    
    def get_capabilities(self, callback):
        self.capabilities = {"color": True, "temperature": True, "infrared": True}

        for light in self.online:
            if not light.supports_color():
                self.capabilities["color"] = False 
            if not light.supports_temperature():
                self.capabilities["temperature"] = False 
            if not light.supports_infrared():
                self.capabilities["infrared"] = False 

        callback()

    def update_controls(self):
        self.update_active = True

        if power := self.get_group_value("power"):
            self.power_switch.set_active(power)

        if brightness := self.get_group_value("brightness"):
            self.brightness_scale.set_value(brightness)

        if self.capabilities["color"]:
            self.hue_row.set_visible(True)
            self.saturation_row.set_visible(True)

            if hue := self.get_group_value("hue"):
                self.hue_scale.set_value(hue)

            if saturation := self.get_group_value("saturation"):
                self.saturation_scale.set_value(saturation)

        if self.capabilities["temperature"]:
            self.kelvin_row.set_visible(True)

            if temperature := self.get_group_value("temperature"):
                self.kelvin_scale.set_value(temperature)

        if self.capabilities["infrared"]:
            self.has_infrared = True
            self.infrared_row.set_visible(True)

            if infrared := self.get_group_value("infrared"):
                self.infrared_scale.set_value(infrared)

        self.update_active = False 
        self.main_stack.set_visible_child_name("controls")

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

    @Gtk.Template.Callback("push_color")
    def push_color(self, sender):
        """
        Color data changed by the user, push it to the group.
        """
        if self.update_active:
            return

        hue = self.hue_scale.get_value()
        saturation = self.saturation_scale.get_value()
        brightness = self.brightness_scale.get_value()
        kelvin = self.kelvin_scale.get_value()

        Group(self.online).set_color((encode_circle(hue),
                                      encode(saturation),
                                      encode(brightness),
                                      kelvin), rapid=True)

        if self.has_infrared:
            self.group.set_infrared(encode(self.infrared_scale.get_value()))

    @Gtk.Template.Callback("set_light_power")
    def set_light_power(self, sender, user_data):
        Group(self.online).set_power(sender.get_active(), rapid=True)

    @Gtk.Template.Callback("go_back")
    def go_back(self, sender):
        self.back_callback(self)