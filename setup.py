from setuptools import setup, Extension, Command
#from pip.req import parse_requirements
#import pip.download

# parse_requirements() returns generator of pip.req.InstallRequirement objects
#install_reqs = parse_requirements("requirements2.txt", session=pip.download.PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
#reqs = [str(ir.req) for ir in install_reqs]

execfile('lands/version.py')

config = {
    'description'      : 'World generator simulating plate tectonics, erosion, etc.',
    'author'           : 'Federico Tomassetti',
    'url'              : 'http://github.com/ftomassetti/lands',
    'download_url'     : 'http://github.com/ftomassetti/lands',
    'author_email'     : 'f.tomassetti@gmail.com',
    'version'          : __version__,
    'install_requires' : ['nose'],
    'packages'         : ['lands', 'lands.cli', 'lands.gui', 'lands.simulations', 'lands.gui', 'lands.protobuf'],
    'entry_points'     : {
        'console_scripts': ['lands=lands.cli.main:main', 'landsgui=lands.gui.main:main'],
    },
    'install_requires':  ['Pillow==2.6.1', 'PyPlatec==1.2.10', 'langgen==0.1.2', 'argparse==1.2.1', 'noise==1.2.1', 'nose==1.3.1', 'wsgiref==0.1.2', 'protobuf==2.6.0'],
    'name'             : 'lands'
}

setup(**config)
