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
     subtropical thorn woodland =   23862
                tropical desert =     691
             boreal rain forest =   96882
        tropical thorn woodland =   24645
            subpolar dry tundra =    3760
      warm temperate wet forest =   23299
            subpolar wet tundra =   24019
               boreal dry scrub =   12851
            tropical wet forest =   15462
           subpolar rain tundra =  124884
           tropical rain forest =    4904
                            ice =  116717
          tropical moist forest =   28446
            boreal moist forest =   31855
              boreal wet forest =   47660
         subtropical dry forest =   34480
        subtropical rain forest =   14396
       subtropical moist forest =   32074
    cool temperate desert scrub =   16883
          cool temperate steppe =   43037
          subpolar moist tundra =   11698
            tropical dry forest =   38013
       tropical very dry forest =   39541
       subtropical desert scrub =    8649
          tropical desert scrub =   10797
    warm temperate moist forest =   34994
    warm temperate desert scrub =   10969
     warm temperate rain forest =   14289
    cool temperate moist forest =   54388
      cool temperate wet forest =   59129
      warm temperate dry forest =   34319
                          ocean = 3030132
          cool temperate desert =    6157
             subtropical desert =    1471
          warm temperate desert =    2239
     cool temperate rain forest =   59685
         subtropical wet forest =   22955
                  boreal desert =    6617
     warm temperate thorn scrub =   25617
                   polar desert =    1838
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

Requirements
============

Libjpeg is required by PIL

Contributors
============

[Evan Sampson](https://github.com/esampson) contributed the amazing implementation of the Holdridge life zones model
and improved a lot the ancient-looking-map, biome, precipitation and temperature generators. Thanks a million!
