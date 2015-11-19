Biomes, Temperature, and Humidity
=================================

Worldengine uses a complex system to model the environment. For the ease of use for beginners Worldengine is setup to default to a planet with an ecological balance similar to Earth's.

While the system is technically complex, in that it has multiple integrated parts, it is not terribly difficult to understand. In this document we will first explain the general model used for placing biomes and then explain how the user can alter different variables to produce non-terrestrial planets.

Biomes
------

Worldengine implements a version of the `Holdridge life zones <https://en.wikipedia.org/wiki/Holdridge_life_zones>`_ model for the placement of biomes. While the standard Holdridge life zone model uses three axes Worldengine only concerns itself with the temperature and precipitation axes.

.. image:: https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/docs/Holdridge.png
   :align: center
   :width: 95%

As an example, an area of the planet that is **Boreal** in temperature and **Semiarid** in humidity will be classified as **Boreal Wet Forest**. 

While many people regard the |Koppen|_  system as superior it requires the ability to predict seasonal weather. This would require a highly complicated weather simulation system which Worldengine does not currently have. As a result all Temperature and Humidity values are given in terms of yearly averages.


.. |Koppen| replace:: K |o| ppen climate classification
.. _Koppen: https://en.wikipedia.org/wiki/K%C3%B6ppen_climate_classification

.. |o| unicode:: 0xf6 .. Latin small o with diaeresis
    :trim:

There are thirty nine different land biomes. Most cells hold a single biome and most biomes occupy a single cell. The notable exceptions are Polar Ice which occupies two cells and the biomes of the **Warm Temperate** and **Subtropical** regions, each of which occupy only half a cell.

Biomes are then grouped into larger and broader categories such as **Ice**, **Tropical Rain Forest**, and **Mixed Forests**. In the image above the various biomes of each category have been color coded and surrounded by thicker lines with a key to the different groups provided in the upper left corner.

Temperature and Humidity
------------------------

As mentioned above Temperature and Humidity are expressed in Worldengine as yearly averages. We do not yet have a complex weather simulating system that is capable of handling seasonal changes.

Worldengine works largely in unitless numbers. What this means is that a value of .5 for something such as Humidity does not mean that it has twice as much water as an area with a value of .25. All that can really be interpreted directly from this number is that it has a greater amount of water, but it is not possible to say exactly how much.

It is the command line options of **--temps** and **--humids** that convert those unitless values into the actual Temperature and Humidity ranges. The way these values work is to define what percentage of the total land terrain is to be considered a certain value or lower (where lower is considered to be either colder or drier depending upon which variable is specified).

As an example the default value for **--temps** is .126/.235/.406/.561/.634/.876. Thus, the first point of separation is at 12.6%. This in turn means that 12.6% of the land mass will be **Polar**. The next point of separation occurs at 23.5% which means that 23.5% of the land mass will be either **Polar** or **Subpolar** (and since 12.6% of the landmass is **Polar** that leaves only a remaining 10.9% to be **Subpolar**).

By altering these values one can make a planet that is either hotter or colder, wetter or drier. A **--temps** value of 0/.126/.235/.406/.561/.634 will result in a planet with no locations with a **Polar** climate and 36.6% of the planet having a **Tropical** climate (as opposed to 12.4% for the default).

Temperature/Humidity Curve and Scatter Plots
--------------------------------------------

One thing that many people may notice in the Holdridge life zones chart given above is that as regions get colder the maximum amount of water that they may receive decreases. If Worldengine were to simply generate values for Humidity independent of Temperature a significant portion of the simulated planet would receive too much average rain fall. While Worldengine is able to handle such an occurrence (it simply treats the terrain as recieving the maximum water possible) this still produces less than ideal results. To correct this problem Humidity undergoes a mathematical transformation designed to produce results more in line with those of a terrestrial planet.

At its heart the mathematical operation is not too complicated. Both Temperature values and Humidity values are normalized to a range of 0 to 1. The Temperature value is then fed into a function that returns a new value that also has a range of 0 to 1. The original Humidity value is multiplied by this number and the new Humidity value is determined.

If we assume for just a moment that the value of **-gv** is 1 then the Temperature function is relatively simple. It is a straight line that runs from **-go** to 1 as Temperature runs from 0 to 1. Thus, on the default settings (**-go** = .2) we would multiply the original Humidity value by .2 when Temperature is 0 and we would multiply it by 1 when the Temperature is 1. If we were to use a straight line (**-gv** = 1) then we would multiply by .6 when Temperature is .5, .4 when the Temperature is .25, etc. We do this because without the offset value (**-go**) we find that we are multiplying by numbers that are too small at the coldest end of the Temperature scale resulting in too much **Polar Desert** terrain.

While this offset gives us better results in the colder ranges we find that unfortunately it has a tendency to push the average rainfall up a bit too much in the middle ranges. In order to correct for this we use the following function:

.. math::
  f(Temperature) = Temperature ^{GV}

where "GV" is the **-gv** variable. This is the same basic function that is used in `gamma correction <https://en.wikipedia.org/wiki/Gamma_correction>`_ and so we have appropriated the term "gamma value" and "gamma offset" to describe our variables (although to be technical our function is not actually a gamma curve).

It should be noted for technical reasons that the curve is actually calculated first, then compressed and shifted by amounts determined by the offset variable (**-go**). This means that the value for f(Temperature) will always range from the offset variable to 1.

To ensure that the **-gv** and **-go** variables are producing a good curve it may be desirable to generate a scatter plot when the planet is being created.

.. image:: https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/scatter_plot_example.png
   :align: center

Each point on this plot is a single point on the landmass of the planet. The Temperature runs across the bottom, ranging from **Polar** to **Tropical** while the Humidity runs along the side, ranging from **Superarid** to **Superhumid**. Lines are drawn to show the dividing point between various Temperature and Humidity ranges. While the current routine does not label the rows and columns the following image is provided to help understand how they correspond to the chart:

.. image:: https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/images/examples/scatter_plot-labelled.png
   :align: center

Cells in grey are ones which do not technically occur in the standard Holdridge life zone model and as the example above shows there are certain areas of terrain in the example that are both **Polar** and **Semiarid**. Since there are not too many of them we will not concern ourselves as Worldengine will simply treat them as **Polar** and **Arid** (i.e. classify them as **Polar Ice**).

Biome Images
---------

The following is the color key for biome images, both showing the color and providing the hex code for the color:

.. image:: https://raw.githubusercontent.com/Mindwerks/worldengine-data/master/docs/Biomes.PNG
   :align: center