pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
moduledir = join_paths(pkgdatadir, 'ambience')

python = import('python')

conf = configuration_data()
conf.set('PYTHON', python.find_installation('python3').path())
conf.set('VERSION', meson.project_version())
conf.set('localedir', join_paths(get_option('prefix'), get_option('localedir')))
conf.set('pkgdatadir', pkgdatadir)

configure_file(
  input: 'ambience.in',
  output: 'ambience',
  configuration: conf,
  install: true,
  install_dir: get_option('bindir')
)

ambience_sources = [
  '__init__.py',
  'main.py',
  'ambience_window.py',
  'ambience_light_control.py',
  'ambience_group_control.py',
  'ambience_discovery.py',
  'ambience_light_tile.py',
  'ambience_group_tile.py',
  'ambience_settings.py',
  'light_item.py',
  'discovery_item.py',
  'product_list.py',
  'helpers.py'
]

install_data(ambience_sources, install_dir: moduledir)

subdir('model')
subdir('lifx')
subdir('backend')