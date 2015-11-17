Version 0.19-UNRELEASED

* Rivers and grayscale_heightmaps are generated as PNG images, filenames no longer have to be provided.
* The grayscale_heightmap is now stored as a proper 16 bit grayscale PNG.
* Modified color elevation routines so that depressions are still represented as land instead of ocean and heights are normalied.
* Speed of generation increased by almost a factor of 3 (due to update to Platec and making heavy use of numpy).
* World-generation is now deterministic, i.e. generation is 100% reproducible.
* Added support for exporting heightmaps using libgdal (see http://www.gdal.org/formats_list.html for possible formats).
* Added the ability to modify temperature and humidity ranges as well as the temperature/precipitation curve.
* Added the ability to generate scatter plots showing temperature and humidity of all terrestrial cells.
* Added small variations to the temperature-map based on basic orbital parameters.
* Added a satellite-like view of the world.
* Added support to save/load worlds in/from HDF5-format.
* Removed support for saving/loading worlds in/from pickle-format.

Version 0.18

* Merged Lands and WorldSynth into one WorldEngine
* River and its erosion are now taken into account
* Total restructuring of code including many bug fixes.
* Windows/OSX/Linux binary builds

Version 0.5.4

* Fix bug in sea representation for elevation map
* Fix plates operation
* [Technical] Increase test coverage


Version 0.5.3

* Saving generation parameters in world file (Russell Brinkmann)
* Revising command line options (Russell Brinkmann)
* Adding tracing statements about performance (Russell Brinkmann)


Version 0.5.2

* Basic GUI implemented, supporting all views and simulations


Version 0.5.1

* Packaging lands as a script
* Supporting protocol buffer serialization
* QT based Gui


Version 0.5.0

* Supporting python 3
* Initial GUI (only plates simulation)


Version 0.4.3

* Adopting plate-tectonics (my fork of platec) which permits rectangular plate calculations


Version 0.4.2

* Generation of rivers map
* Stefan Feltmann ported Lands to Pillow (removing PIL)


Version 0.4.1

* Generation of grayscale heightmap


Version 0.4.0

* Evan Sampson added Holdridge life zones model
