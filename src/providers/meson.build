providersdir = join_paths(moduledir, 'providers')

providers_sources = [
    '__init__.py',
]

install_data(providers_sources, install_dir: providersdir)

c = run_command('list_providers.sh')
providers = c.stdout().strip().split('\n')
foreach provider : providers
    subdir(provider)
endforeach

providers_string = ' '.join(providers)
conf = configuration_data({'PROVIDERS' : providers_string})
configure_file(
    input: 'ambience_providers.py.in',
    output: 'ambience_providers.py',
    configuration: conf,
    install: true,
    install_dir: providersdir
)