from setuptools import setup, Extension, Command
# from pip.req import parse_requirements
# import pip.download

# parse_requirements() returns generator of pip.req.InstallRequirement objects
# install_reqs = parse_requirements("requirements.txt",
# session=pip.download.PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
# reqs = [str(ir.req) for ir in install_reqs]

exec(open('worldengine/version.py').read())

config = {
    'name': 'worldengine',
    'description': 'World generator simulating plate tectonics, erosion, etc.',
    'author': 'Federico Tomassetti, Bret Curtis',
    'author_email': 'f.tomassetti@gmail.com, psi29a@gmail.com',
    'url': 'http://github.com/Mindwerks/worldengine',
    'download_url': 'https://github.com/Mindwerks/worldengine/releases',
    'version': __version__,
    'packages': ['worldengine', 'worldengine.cli', 'worldengine.simulations',
                 'worldengine.protobuf', 'worldengine.imex'],
    'entry_points': {
        'console_scripts': ['worldengine=worldengine.cli.main:main'],
    },
    'install_requires': ['PyPlatec==1.4.0', 'pypng>=0.0.18', 'numpy>=1.9.2, <= 1.10.0.post2',
                         'argparse==1.2.1', 'noise==1.2.2', 'protobuf==3.0.0a3'],
    'license': 'MIT License'
}

setup(**config)
