/******************************************************************************
 *  PlaTec, a 2D terrain generator based on plate tectonics
 *  Copyright (C) 2012- Lauri Viitanen
 *
 *  This library is free software; you can redistribute it and/or
 *  modify it under the terms of the GNU Lesser General Public
 *  License as published by the Free Software Foundation; either
 *  version 2.1 of the License, or (at your option) any later version.
 *
 *  This library is distributed in the hope that it will be useful,
 *  but WITHOUT ANY WARRANTY; without even the implied warranty of
 *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the GNU
 *  Lesser General Public License for more details.
 *
 *  You should have received a copy of the GNU Lesser General Public
 *  License along with this library; if not, see http://www.gnu.org/licenses/
 *****************************************************************************/

#ifndef LITHOSPHERE_HPP
#define LITHOSPHERE_HPP

#include <cstring> // For size_t.
#include <stdexcept>
#include <vector>

#define CONTINENTAL_BASE 1.0f
#define OCEANIC_BASE     0.1f

class plate;

/**
 * Litosphere is the rigid outermost shell of a rocky planet.
 *
 * Litosphere is divided into several rigid areas i.e. plates. In time passing
 * the topography of the planet evolves as the result of plate dynamics.
 * Litosphere is the class responsibile for creating and managing all the
 * plates. It updates heightmap to match the current setup of plates and thus
 * offers caller an easy access to system's topography.
 * 
 */
class lithosphere
{
  public:

	/**
	 * Initialize system's height map i.e. topography.
	 *
	 * @param map_side_length Square height map's side's length in pixels.
	 * @param sea_level Amount of surcafe area that becomes oceanic crust.
	 * @param _erosion_period # of iterations between global erosion.
	 * @param _folding_ratio Percent of overlapping crust that's folded.
	 * @param aggr_ratio_abs # of overlapping points causing aggregation.
	 * @param aggr_ratio_rel % of overlapping area causing aggregation.
	 * @param num_cycles Number of times system will be restarted.
	 * @exception	invalid_argument Exception is thrown if map side length
	 *           	is not a power of two and greater than three.
	 */
	lithosphere(size_t map_side_length, float sea_level,
		size_t _erosion_period, float _folding_ratio,
		size_t aggr_ratio_abs, float aggr_ratio_rel,
		size_t num_cycles) throw(std::invalid_argument);

	~lithosphere() throw(); ///< Standard destructor.

	/**
	 * Split the current topography into given number of (rigid) plates.
	 *
	 * Any previous set of plates is discarded.
	 *
	 * @param num_plates Number of areas the surface is divided into.
	 */
	void createPlates(size_t num_plates) throw();

	size_t getCycleCount() const throw() { return cycle_count; }
	size_t getIterationCount() const throw() { return iter_count; }
	size_t getSideLength() const throw() { return map_side; }
	size_t getPlateCount() const throw(); ///< Return number of plates.
	const size_t* getAgemap() const throw(); ///< Return surface age map.
	const float* getTopography() const throw(); ///< Return height map.
	void update() throw(); ///< Simulate one step of plate tectonics.

	long seed;

  protected:
  private:

	/**
	 * Container for collision details between two plates.
	 *
	 * In simulation there's usually 2-5 % collisions of the entire map
	 * area. In a 512*512 map that means 5000-13000 collisions.
	 *
	 * When plate collisions are recorded and processed pair-by-pair, some
	 * of the information is lost if more than two plates collide at the
	 * same point (there will be no record of the two lower plates
	 * colliding together, just that they both collided with the tallest
	 * plate) ONLY IF ALL the collisions between ANY TWO plates of that
	 * group always include a third, taller/higher  plate. This happens
	 * most often when plates have long, sharp spikes i.e. in the
	 * beginning.
	 */
	class plateCollision
	{
	  public:

		plateCollision(size_t _index, size_t x, size_t y, float z)
			throw() : index(_index), wx(x), wy(y), crust(z) {}

		size_t index; ///< Index of the other plate involved in the event.
		size_t wx, wy; ///< Coordinates of collision in world space.
		float crust; ///< Amount of crust that will deform/subduct.
	};

	void restart() throw(); //< Replace plates with a new population.

	float* hmap; ///< Height map representing the topography of system.
	size_t* imap; ///< Plate index map of the "owner" of each map point.
	size_t* amap; ///< Age map of the system's surface (topography).
	plate** plates; ///< Array of plates that constitute the system.

	size_t aggr_overlap_abs; ///< # of overlapping pixels -> aggregation.
	float  aggr_overlap_rel; ///< % of overlapping area -> aggregation.
	size_t cycle_count; ///< Number of times the system's been restarted.
	size_t erosion_period; ///< # of iterations between global erosion.
	float  folding_ratio; ///< Percent of overlapping crust that's folded.
	size_t iter_count; ///< Iteration count. Used to timestamp new crust.
	size_t map_side; ///< Length of square height map's side in pixels.
	size_t max_cycles; ///< Max n:o of times the system'll be restarted.
	size_t max_plates; ///< Number of plates in the initial setting.
	size_t num_plates; ///< Number of plates in the current setting.

	std::vector<std::vector<plateCollision> > collisions;
	std::vector<std::vector<plateCollision> > subductions;

	float peak_Ek; ///< Max total kinetic energy in the system so far.
	size_t last_coll_count; ///< Iterations since last cont. collision.

};

#endif
