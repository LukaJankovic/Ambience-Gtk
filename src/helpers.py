from lifxlan import *

# Helper functions for converting values to / from api
def decode(nr):
    """
    Convert from 16 bit unsigned integer to range between 0 and 100.
    """
    return (nr / 65535) * 100

def decode_circle(nr):
    """
    Convert from 16 bit unsined integer to range between 0 and 365.
    """
    return (nr / 65535) * 365

def encode(nr):
    """
    Convert from range 0 to 100 to 16 bit unsigned integer limit
    """
    return (nr / 100) * 65535

def encode_circle(nr):
    """
    Convert from range 0 to 365 to 16 bit unsigned integer limit
    """
    return (nr / 365) * 65535

def rgb_to_hex(r, g, b):
    return '#{:02x}{:02x}{:02x}'.format(int(r * 255), int(g * 255), int(b * 255))

def fetch_light_data(light, finished_callback):
    light.label = light.get_label()
    light.product = light.get_product()
    light.power = light.get_power()

    light.has_color = light.supports_color()
    light.has_temp = light.supports_temperature()
    light.has_infrar = light.supports_infrared()

    (hue, saturation, brightness, temperature) = light.get_color()

    light.brightness = decode(brightness)
    
    if light.has_color:
        light.hue = decode_circle(hue)
        light.saturation = decode(saturation)

    if light.has_temp:
        light.temperature = temperature

    if light.has_infrar:
        light.infrared = decode(light.get_infrared())

    light.ip = light.get_ip_addr()
    light.group = light.get_group_label()
    light.location = light.get_location_label()

    finished_callback(light)