from lifxlan import *

MAX_RETRIES = 3

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

def fetch_data_async(light_function, callback):
    retries = 0
    return_data = None

    while retries < MAX_RETRIES:
        try:
            return_data = light_function()
            callback(return_data, True)
        except WorkflowException:
            print("invalid response for ", light_function)
            retries += 1

    callback(None, False)

def fetch_data_sync(light_function):
    retries = 0
    return_data = None

    while retries < MAX_RETRIES:
        try:
            return_data = light_function()
            return return_data
        except WorkflowException:
            print("invalid response for ", light_function)
            retries += 1

    return None

def fetch_all_data(light, finished_callback, data=None):
    
    def call_callback(success):
        if data is not None:
            finished_callback(light, success, data)
        else:
            finished_callback(light, success)

    light.label = fetch_data_sync(light.get_label)
    if light.label is None:
        call_callback(False)
        return

    light.product = fetch_data_sync(light.get_product)
    if light.product is None:
        call_callback(False)
        return

    light.power = fetch_data_sync(light.get_power)
    if light.power is None:
        call_callback(False)
        return

    light.has_color = fetch_data_sync(light.supports_color)
    if light.has_color is None:
        call_callback(False)
        return

    light.has_temp = fetch_data_sync(light.supports_temperature)
    if light.has_temp is None:
        call_callback(False)
        return

    light.has_infrar = fetch_data_sync(light.supports_infrared)
    if light.has_infrar is None:
        call_callback(False)
        return

    color_res = fetch_data_sync(light.get_color)
    if color_res is None:
        call_callback(False)
        return

    hue = color_res[0]
    saturation = color_res[1]
    brightness = color_res[2]
    temperature = color_res[3]

    light.brightness = decode(brightness)
    
    if light.has_color:
        light.hue = decode_circle(hue)
        light.saturation = decode(saturation)

    if light.has_temp:
        light.temperature = temperature

    if light.has_infrar:
        light.infrared = decode(light.get_infrared())

    light.ip = fetch_data_sync(light.get_ip_addr)
    if light.ip is None:
        call_callback(False)
        return

    light.group = fetch_data_sync(light.get_group_label)
    if light.group is None:
        call_callback(False)
        return

    light.location = fetch_data_sync(light.get_location_label)
    if light.location is None:
        call_callback(False)
        return

    call_callback(True)