pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
modeldir = join_paths(pkgdatadir, 'ambience', 'model')

ambience_sources = [
    'ambience_device.py',
    'ambience_light.py',
    'ambience_group.py'
]

install_data(ambience_sources, install_dir: modeldir)