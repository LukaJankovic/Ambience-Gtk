project('ambience',  
          version: '2.0',
    meson_version: '>= 0.50.0',
  default_options: [ 'warning_level=2',
                   ],
)

dependency('gtk4', version: '>= 3.24')
dependency('libhandy-1', version: '>= 1.2.2')

i18n = import('i18n')

subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
