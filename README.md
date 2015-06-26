### _Announcement: Lands and WorldSynth have been merged to create WorldEngine_

Lands has been recently merged with [WorldSynth](https://github.com/psi29a/worldsynth).
We are now working on merging the code, taking the best of the two projects.

We started a [google group](https://groups.google.com/forum/?hl=en#!forum/worldengine): if you have ideas, problems, suggestions or want to contribute please [join us](https://groups.google.com/forum/?hl=en#!forum/worldengine)!

---

WorldEngine - a world generator
=========================

[![Build Status](https://travis-ci.org/Mindwerks/worldengine.svg?branch=master)](https://travis-ci.org/Mindwerks/worldengine) [![Build status](https://ci.appveyor.com/api/projects/status/io4ljim2ra83df23?svg=true)](https://ci.appveyor.com/project/ftomassetti/worldengine)


_Last Lands version: 0.5.3, Last WorldSynth version: 0.12, First WorldEngine version will be 0.18_

You can generate worlds data (heighmap, biome, etc.) and images for your own worlds.

For example:

```bash
# WorldEngine
worldengine world -s 1 -n seed1

# Lands 0.5.1 or next
lands world -s 1 -n seed1

# Lands 0.5.0 or previous
python lands/generator.py world -s 1 -n seed1
```

Worlds are generated using plate simulations, erosion, rain shadows, Holdridge life zones model and plenty of other phenomenons.

Once a world it can be used for simulation civs evolution (see project [civs](https://github.com/ftomassetti/civs)).

For a generated world is also possible to generate additional maps, for example ancient looking map:

```bash
# WorldEngine
worldengine ancient_map -w seed1.world

# Lands 0.5.1 or next
lands ancient_map -w seed1.world

# Lands 0.5.0 or previous
python lands/generator.py ancient_map -w seed1.world
```

![](https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/ancient_map_seed1.png)

Gui
===

An experimental (and limited!) GUI is available. 

```
worldenginegui
```

Note: it requires to install QT (available here [http://qt-project.org/](http://qt-project.org/))

Install
=======

### Using pip

```
# Currently not yet released on pypi, you may want to still use Lands or WorldSynth
# or alternatively download the source
pip install worldengine
```

### From source code

```
git clone or download the code

# before using worldengine: if you plan to change the code
python setup.py develop 

# for unit-testing: also clone worldengine-data
git clone git@github.com:Mindwerks/worldengine-data.git ../worldengine-data
nosetest tests

# before using worldengine: if you want just to install worldengine
# on unix-ish system you could have to prepend sudo
python setup.py install
```

### _On Windows_

If you want to install Worldengine on Windows you can read these [instructions](https://github.com/Mindwerks/worldengine/wiki/Installing-Worldengine-on-Windows).

Executable file is also available under [releases](https://github.com/Mindwerks/worldengine/releases), but is currently out of date.

Note: you need also a copy of the worldengine src directory in the same folder as the exe.

Dependencies
============

The gui is based on QT, so you will need to install them

Output
======

The program produces a binary format with all the data of the generated world and a set of images. For examples seed 1 produces.

## Elevation Map

![](https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/world_seed_1_elevation.png)

## Precipitation Map

![](https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/world_seed_1_precipitation.png)

## Temperature Map

![](https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/world_seed_1_temperature.png)

## Biome Map

![](https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/world_seed_1_biome.png)

## Ocean Map

![](https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/world_seed_1_ocean.png)

Usage
=====

```
worldengine [options] [world|plates|ancient_map|info]
```
_Note that options were changed in version 0.5.3_

### General options

| Short     | Long | Description |
|-----------|------|-------------|
| -o DIR    | --output-dir=DIR | generate files in DIR default = '.' |
| -n STR    | --worldname=STR | set world name to STR |
| -b        | --protocol-buffer | save world using protocol buffer format (smaller file) |
| -s N      | --seed=N | use SEED to initialize the pseudo-random generation |
| -t STR    | --step=STR | use STEP to specify how far to proceed in the world generation process. Valid values are: plates precipitations full |
| -x N      | --width=N | WIDTH of the world to be generated |
| -y N      | --height=N | HEIGHT of the world to be generated |
| -q N   | --number-of-plates=N | number of plates |
|       | --recursion-limit=N | you need that just if you encounter an error while generating very large maps |
| -v    | --verbose | Enable verbose messages |
| --bw  | --black-and-white | Draw maps in black and white |

### Options valid only for generate

| Short     | Long | Description |
|-----------|------|-------------|
| -r FILE   | --rivers=FILE | produce a map of rivers, after the option it expects the name of the file where to generate the map  |
| --gs=FILE  | --grayscale-heightmap=FILE | produce a grayscale heightmap, after the option it expects the name of the file where to generate the heightmap |
|   | --ocean_level=N   |  elevation cut off for sea level (default = 1.0) |

### Options valid only for ancient map operations

| Short     | Long | Description |
|-----------|------|-------------|
| -w FILE   | --worldfile=FILE | WORLD_FILE to be loaded |
| -g FILE   | --generatedfile=FILE | name of the GENERATED_FILE |
| -f N   | --resize-factor=N | resize factor |

For example these commands:

```python
worldengine world -s 4 -n an_example -p 2048 -q 25 -x 2048 -y 2048
```

Produce this output

```
Worldengine - world generator
-----------------------
 seed              : 4
 name              : seed3
 width             : 2048
 height            : 2048
 plates resolution : 2048
 number of plates  : 25
 operation         : world generation
 step              : full

starting (it could take a few minutes) ...
...plates simulated
...elevation noise added
...elevation level calculated
...precipations calculated
...erosion calculated
...humidity calculated
...permeability level calculated

Biome obtained:
     subtropical thorn woodland =   16353
                tropical desert =     188
             boreal rain forest =   69472
        tropical thorn woodland =   19680
            subpolar dry tundra =    6316
      warm temperate wet forest =   17799
            subpolar wet tundra =   24453
          subpolar moist tundra =   15104
            tropical wet forest =   18441
           subpolar rain tundra =   79723
           tropical rain forest =    5906
                            ice =   85254
          tropical moist forest =   28871
        subtropical rain forest =   14733
            boreal moist forest =   24395
              boreal wet forest =   35212
         subtropical dry forest =   26259
       subtropical desert scrub =    3256
       subtropical moist forest =   25220
    cool temperate desert scrub =   11162
          cool temperate steppe =   25604
               boreal dry scrub =   13403
            tropical dry forest =   22415
       tropical very dry forest =   27033
          tropical desert scrub =    2473
    warm temperate moist forest =   27704
    warm temperate desert scrub =    4861
     warm temperate rain forest =   10774
    cool temperate moist forest =   42770
      cool temperate wet forest =   52813
      warm temperate dry forest =   29992
                          ocean = 3314282
          cool temperate desert =    2950
             subtropical desert =     287
          warm temperate desert =     709
     cool temperate rain forest =   46844
         subtropical wet forest =   18280
                  boreal desert =    5445
     warm temperate thorn scrub =   16175
                   polar desert =    1693

Producing ouput:
* world data saved in './an_example.world'
* ocean image generated in './an_example_ocean.png'
* precipitation image generated in './an_example_precipitation.png'
* temperature image generated in './an_example_temperature.png'
* biome image generated in './an_example_biome.png'
* elevation image generated in './an_example_elevation.png'
...done

```

This is the corresponding ancient map

```python
worldengine ancient_map -w an_example.world
```

![](https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/ancient_map_large.png)

Algorithm
=========

The world generation algorithm goes through different phases:
* plates simulation: it is the best way to get proper mountain chains. For this [pyplatec](https://github.com/Mindwerks/pyplatec) is used
* noise techniques are used at different steps
* precipitations are calculated considering latitude and rain shadow effects
* erosion is calculated
* humidity in each zone is calculated
* terrain permeability is calculated
* biome is calculated using the [Holdridge life zones](http://en.wikipedia.org/wiki/Holdridge_life_zones) model

Install dependencies
====================

Using virtualenv you can install the dependencies in this way

Python 2:
```bash
virtualenv venv
source venv/bin/activate    
pip install -r requirements2.txt
```

Python 3:
```bash
pyvenv venv3
source venv3/bin/activate    
pip3 install -r requirements3.txt
```

Do you have problems or suggestions for improvements?
=====================================================

Please write to us!
You can write us at:
 * f _dot_ tomassetti _at_ gmail _dot_ com
 * psi29a _at_ gmail _dot_ com
Thank you, all the feedback is precious for us!

Requirements
============

Libjpeg and libtiff are required by PIL

Contributors
============

The merged project is maintained by [Bret Curtis](https://github.com/psi29a) and [Federico Tomassetti](https://github.com/ftomassetti).

All contributions, questions, ideas are more than welcome!
Feel free to open an issue or write in our [google group](https://groups.google.com/forum/?hl=en#!forum/lands_worldsynth).

We would like to thank you great people who helped us while working on WorldEngine and the projects from which it was derived:

* [Evan Sampson](https://github.com/esampson) contributed the amazing implementation of the Holdridge life zones model and improved a lot the ancient-looking-map, biome, precipitation and temperature generators. Thanks a million!

* [Ryan](https://github.com/SourceRyan) contributed the Windows binary version and discussed Lands on Reddit bringing a lot of users. Thanks a million!

* [stefan-feltmann](https://github.com/stefan-feltmann) made Lands depends on pillow instead that on PIL (which is deprecated). This could also help when moving to Python 3. Thanks a million!

* [Russell Brinkmann](https://github.com/rbb) helped saving the generation parameters in the generated world (so that we can use it to generate the same world again, for example), improved the command line options and added tracing information (useful for understanding the performance of the various generation steps)

License
=======

WorldEngine is available under the MIT License. You should find the LICENSE in the root of the project.
