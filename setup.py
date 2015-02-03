from setuptools import setup, Extension, Command

execfile('lands/version.py')

config = {
    'description'      : 'World generator simulating plate tectonics, erosion, etc.',
    'author'           : 'Federico Tomassetti',
    'url'              : 'http://github.com/ftomassetti/lands',
    'download_url'     : 'http://github.com/ftomassetti/lands',
    'author_email'     : 'f.tomassetti@gmail.com',
    'version'          : __version__,
    'install_requires' : ['nose'],
    'packages'         : ['lands'],
    'entry_points'     : {
        'console_scripts': ['lands=lands.generator:main', 'landsgui=lands.gui.main:main'],
    },
    'name'             : 'lands'
}

setup(**config)
