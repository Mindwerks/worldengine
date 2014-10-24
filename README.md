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
python lands/generator.py world -s 4 -n seed3 -p 2048 -q 25 -x 2048 -y 2048
python lands/generator.py ancient_map -w seed3.world
```

Produce this output

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
