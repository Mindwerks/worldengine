try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

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
    'scripts'          : [],
    'name'             : 'lands'
}

setup(**config)
