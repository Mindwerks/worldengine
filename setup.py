from setuptools import setup

# from pip.req import parse_requirements
# import pip.download

# parse_requirements() returns generator of pip.req.InstallRequirement objects
# install_reqs = parse_requirements("requirements.txt",
# session=pip.download.PipSession())

# reqs is a list of requirement
# e.g. ['django==1.5.1', 'mezzanine==1.4.6']
# reqs = [str(ir.req) for ir in install_reqs]

with open("worldengine/version.py") as f:
    exec(f.read())  # noqa: S102 - defines __version__

config = {
    "name": "worldengine",
    "description": "World generator simulating plate tectonics, erosion, etc.",
    "author": "Federico Tomassetti, Bret Curtis",
    "author_email": "f.tomassetti@gmail.com, psi29a@gmail.com",
    "url": "http://github.com/Mindwerks/worldengine",
    "download_url": "https://github.com/Mindwerks/worldengine/releases",
    "version": __version__,
    "packages": [
        "worldengine",
        "worldengine.cli",
        "worldengine.simulations",
        "worldengine.protobuf",
        "worldengine.imex",
    ],
    "entry_points": {
        "console_scripts": ["worldengine=worldengine.cli.main:main"],
    },
    "install_requires": ["PyPlatec==1.4.3", "pypng>=0.20220715.0", "numpy>=1.24.0", "noise==1.2.2", "protobuf>=4.21.0"],
    "python_requires": ">=3.9",
    "classifiers": [
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Topic :: Games/Entertainment :: Simulation",
        "Topic :: Scientific/Engineering",
    ],
    "license": "MIT License",
}

setup(**config)
