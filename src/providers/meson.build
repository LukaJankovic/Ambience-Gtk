pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'ambience')

lifx_sources = [
    'lifx/ambience_lifx_lan.py',
    'lifx/ambience_lifx_light.py',
]

ambience_sources = []
ambience_sources += lifx_sources

install_data(ambience_sources, install_dir: moduledir)