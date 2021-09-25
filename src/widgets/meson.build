pkgdatadir = join_paths(get_option('prefix'), get_option('datadir'), meson.project_name())
widgetsdir = join_paths(pkgdatadir, 'ambience', 'widgets')

widgets_sources = [
  'ambience_flow_box.py',
  'ambience_light_tile.py',
  'ambience_group_tile.py',
]

install_data(widgets_sources, install_dir: widgetsdir)