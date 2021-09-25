pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
lifxdir = join_paths(pkgdatadir, 'ambience', 'providers', 'lifx')

lifx_sources = [
    '__init__.py',
    'ambience_lifx_device_type.py',
    'ambience_lifx_lan.py',
    'ambience_lifx_light.py'
]

install_data(lifx_sources, install_dir: lifxdir)
