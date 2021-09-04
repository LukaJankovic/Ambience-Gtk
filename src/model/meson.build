pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'ambience')

ambience_sources = [
    'ambience_device.py',
    'ambience_light.py',
    'ambience_group.py'
]

install_data(ambience_sources, install_dir: moduledir)