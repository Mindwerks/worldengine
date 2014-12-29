Lands - a world generator
=========================

[![Build Status](https://travis-ci.org/ftomassetti/lands.svg?branch=master)](https://travis-ci.org/ftomassetti/lands)

You can generate worlds data (heighmap, biome, etc.) and images for your own worlds.

For example:

```python
python lands/generator.py world -s 1 -n seed1
```

Worlds are generated using plate simulations, erosion, rain shadows, Holdridge life zones model and plenty of other phenomenons.

Once a world it can be used for simulation civs evolution (see project [civs](https://github.com/ftomassetti/civs)).

For a generated world is also possible to generate additional maps, for example ancient looking map:

```python
python lands/generator.py ancient_map -w seed1.world
```

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/ancient_map_seed1.png)

Install
=======

*Windows*

Executable file is available under [releases](https://github.com/ftomassetti/lands/releases)

Note: you need also a copy of the lands src directory in the same folder as the exe.

If you want to build Lands on Windows you can read these [instructions](https://github.com/ftomassetti/lands/wiki/Lands-on-Windows).

Note: the problem could crash after generating the files, it is a known problem but you should have anyway your nice maps generated! We are working on a fix for that

*Linux*

1. Install python 2.7
2. Install pip
3. Git clone / download the repository
4. Run pip install -r requirements.txt
5. You should be good to go!

Output
======

The program produces a binary format with all the data of the generated world and a set of images. For examples seed 1 produces.

## Elevation Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_elevation.png)

## Precipitation Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_precipitation.png)

## Temperature Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_temperature.png)

## Biome Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_biome.png)

## Ocean Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_ocean.png)

Usage
=====

| Short | Long | Description |
|-------|------|-------------|
| -o    | --output | generate files in OUTPUT |
| -n    | --worldname | set WORLDNAME |
| -s    | --seed | use SEED to initialize the pseudo-random generation |
| -t    | --step | use STEP to specify how far to proceed in the world generation process |
| -x    | --width | WIDTH of the world to be generated |
| -y    | --height | HEIGHT of the world to be generated |
| -w    | --worldfile | WORLD_FILE to be loaded (for ancient_map operation) |
| -g    | --generatedfile | name of the GENERATED_FILE (for ancient_map operation) |
| -f    | --resize-factor | resize factor |
| -p    | --plates-resolution | plates resolution |
| -q    | --number-of-plates | number of plates |
| --gs  | --grayscale-heightmap | produce a grayscale heightmap, after the option it expects the name of the file where to generate the heightmap (e.g., --gs bw.png) |
| -r    | --rivers | produce a map of reivers, after the option it expects the name of the file where to generate the map (e.g., -r rivers.png) |

For example these commands:

```python
python lands/generator.py world -s 4 -n an_example -p 2048 -q 25 -x 2048 -y 2048
```

Produce this output

```
Lands - world generator
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
python lands/generator.py ancient_map -w an_example.world
```

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/ancient_map_large.png)

Algorithm
=========

The world generation algorithm goes through different phases:
* plates simulation: it is the best way to get proper mountain chains. For this [pyplatec](https://github.com/ftomassetti/pyplatec) is used
* noise techniques are used at different steps
* precipitations are calculated considering latitude and rain shadow effects
* erosion is calculated
* humidity in each zone is calculated
* terrain permeability is calculated
* biome is calculated using the [Holdridge life zones](http://en.wikipedia.org/wiki/Holdridge_life_zones) model

Install dependencies
====================

Using virtualenv you can install the dependencies in this way

```python
virtualenv venv
source venv/bin/activate    
pip install -r requirements.txt
```

Do you have problems or suggestions for improvements?
=====================================================

Please write to me!
You can write at f _dot_ tomassetti _at_ gmail _dot_ com
Thank you, all the feedback is precious for me!

Requirements
============

Libjpeg is required by PIL

Contributors
============

All contributions, questions, ideas are more than welcome!
Feel free to open an issue or drop me an e-mail.

I would like to thank you great people who helped me while working on Lands:

* [Evan Sampson](https://github.com/esampson) contributed the amazing implementation of the Holdridge life zones model and improved a lot the ancient-looking-map, biome, precipitation and temperature generators. Thanks a million!

* [Ryan](https://github.com/SourceRyan) contributed the Windows binary version and discussed Lands on Reddit bringing a lot of users. Thanks a million!

* [stefan-feltmann](https://github.com/stefan-feltmann) made Lands depends on pillow instead that on PIL (which is deprecated). This could also help when moving to Python 3. Thanks a million!

License
=======

Lands is available under the MIT License. You should find the LICENSE in the root of the project.
