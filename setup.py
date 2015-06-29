from setuptools import setup, Extension, Command
from worldengine.version import __version__

config = {
    'name': 'worldengine',
    'description': 'World generator simulating plate tectonics, erosion, etc.',
    'author': 'Federico Tomassetti, Bret Curtis',
    'author_email': 'f.tomassetti@gmail.com, psi29a@gmail.com',
    'url': 'http://github.com/Mindwerks/worldengine',
    'download_url': 'https://github.com/Mindwerks/worldengine/releases',
    'version': __version__,
    'packages': ['worldengine', 'worldengine.cli', 'worldengine.gui',
                 'worldengine.simulations', 'worldengine.gui',
                 'worldengine.protobuf'],
    'entry_points': {
        'console_scripts': ['worldengine=worldengine.cli.main:main',
                            'worldenginegui=worldengine.gui.main:main'],
    },
    'install_requires': ['Pillow==2.8.2', 'PyPlatec==1.3.1.post1',
                         'argparse==1.2.1', 'noise==1.2.2', 'protobuf==2.6.0',
                         'numpy==1.9.2'],
    'license': 'MIT License'
}

setup(**config)
