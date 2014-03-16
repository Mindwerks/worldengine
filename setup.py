try:
    from setuptools import setup
except ImportError:
    from distutils.core import setup

config = {
    'description': 'world generator simulating plate tectonics, erosion, etc.',
    'author': 'Federico Tomassetti',
    'url': 'http://github.com/ftomassetti/lands',
    'download_url': 'Where to download it.',
    'author_email': 'f.tomassetti@gmail.com',
    'version': '0.1',
    'install_requires': ['nose'],
    'packages': ['lands'],
    'scripts': [],
    'name': 'lands'
}

setup(**config)
