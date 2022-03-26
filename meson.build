project('ambience',  
          version: '1.5.1',
    meson_version: '>= 0.50.0',
  default_options: [ 'warning_level=2',
                   ],
)

dependency('gtk+-3.0', version: '>= 3.24')
dependency('libhandy-1', version: '>= 1.2.2')

i18n = import('i18n')

subdir('data')
subdir('src')
subdir('po')

meson.add_install_script('build-aux/meson/postinstall.py')
