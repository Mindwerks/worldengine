Lands - a world generator
=========================

[![Build Status](https://travis-ci.org/ftomassetti/lands.svg?branch=master)](https://travis-ci.org/ftomassetti/lands)

You can generate worlds data (heighmap, biome, etc.) and images for your own worlds.

For example:

```python
python lands/generator.py world -s 1 -n seed1
```

Worlds are generated using plate simulations, erosion, rain shadows, Holdridge life zones model and plenty of other phenomenons.

Once a world it can be used for simulation civs evolution (see project [civs](https://github.com/ftomassetti/civs).

For a generated world is also possible to generate additional maps, for example ancient looking map:

```python
python lands/generator.py ancient_map -w seed2.world
```

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/ancient_map_seed2.png)

Output
======

The program produces a binary format with all the data of the generated world and a set of images. For examples seed 1 produes.

## Elevation Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_elevation.png)


## Ocean Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_ocean.png)

## Biome Map

![](https://raw.githubusercontent.com/ftomassetti/lands/master/examples/world_seed_1_biome.png)

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
and improved a lot the ancient-looking-map generator. Thanks a million!
