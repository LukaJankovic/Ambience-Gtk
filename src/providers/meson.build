pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
providersdir = join_paths(pkgdatadir, 'ambience', 'providers')

providers_sources = [
    '__init__.py'
]

install_data(providers_sources, install_dir: providersdir)

subdir('lifx')