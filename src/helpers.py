
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