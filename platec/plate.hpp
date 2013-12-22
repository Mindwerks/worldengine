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

#ifndef PLATE_HPP
#define PLATE_HPP

#include <cstring>
#include <vector>

#define CONT_BASE 1.0 ///< Height limit that separates seas from dry land.

class plate
{
	public:

	/// Initializes plate with the supplied height map.
	///
	/// @param	m	Pointer to array to height map of terrain.
	/// @param	w	Width of height map in pixels.
	/// @param	h	Height of height map in pixels.
	/// @param	_x	X of height map's left-top corner on world map.
	/// @param	_y	Y of height map's left-top corner on world map.
	/// @param	world_side Length of world map's either side in pixels.
	plate(const float* m, size_t w, size_t h, size_t _x, size_t _y,
	      size_t plate_age, size_t world_side)
		throw();

	~plate() throw(); ///< Default destructor for plate.

	/// Increment collision counter of the continent at given location.
	///
	/// @param	wx	X coordinate of collision point on world map.
	/// @param	wy	Y coordinate of collision point on world map.
	/// @return	Surface area of the collided continent (HACK!)
	size_t addCollision(size_t wx, size_t wy) throw();

	/// Add crust to plate as result of continental collision.
	///
	/// @param	x	Location of new crust on global world map (X).
	/// @param	y	Location of new crust on global world map (Y).
	/// @param	z	Amount of crust to add.
	/// @param	t	Time of creation of new crust.
	void addCrustByCollision(size_t x, size_t y, float z, size_t t) throw();

	/// Simulates subduction of oceanic plate under this plate.
	///
	/// Subduction is simulated by calculating the distance on surface
	/// that subducting sediment will travel under the plate until the
	/// subducting slab has reached certain depth where the heat triggers
	/// the melting and uprising of molten magma. 
	///
	/// @param	x	Origin of subduction on global world map (X).
	/// @param	y	Origin of subduction on global world map (Y).
	/// @param	z	Amount of sediment that subducts.
	/// @param	t	Time of creation of new crust.
	/// @param	dx	Direction of the subducting plate (X).
	/// @param	dy	Direction of the subducting plate (Y).
	void addCrustBySubduction(size_t x, size_t y, float z, size_t t,
		float dx, float dy) throw();

	/// Add continental crust from this plate as part of other plate.
	///
	/// Aggregation of two continents is the event where the collided
	/// pieces of crust fuse together at the point of collision. It is
	/// crucial to merge not only the collided pieces of crust but also
	/// the entire continent that's part of the colliding tad of crust
	/// However, because one plate can contain many islands and pieces of
	/// continents, the merging must be done WITHOUT merging the entire
	/// plate and all those continental pieces that have NOTHING to do with
	/// the collision in question.
	///
	/// @param	p	Pointer to the receiving plate.
	/// @param	wx	X coordinate of collision point on world map.
	/// @param	wy	Y coordinate of collision point on world map.
	/// @return	Amount of crust aggregated to destination plate.
	float aggregateCrust(plate* p, size_t wx, size_t wy) throw();

	/// Decrease the speed of plate amount relative to its total mass.
	///
	/// Method decreses the speed of plate due to friction that occurs when
	/// two plates collide. The amount of reduction depends of the amount
	/// of mass that causes friction (i.e. that has collided) compared to
	/// the total mass of the plate. Thus big chunk of crust colliding to
	/// a small plate will halt it but have little effect on a huge plate.
	///
	/// @param	deforming_mass Amount of mass deformed in collision.
	void applyFriction(float deforming_mass) throw();

	/// Method collides two plates according to Newton's laws of motion.
	///
	/// The velocity and direction of both plates are updated using
	/// impulse forces following the collision according to Newton's laws
	/// of motion. Deformations are not applied but energy consumed by the
	/// deformation process is taken away from plate's momentum.
	///
	/// @param	p	Plate to test against.
	/// @param	wx	X coordinate of collision point on world map.
	/// @param	wy	Y coordinate of collision point on world map.
	/// @param	coll_mass Amount of colliding mass from source plate.
	void collide(plate& p, size_t xw, size_t wy, float coll_mass) throw();

	/// Apply plate wide erosion algorithm.
	///
	/// Plates total mass and the center of mass are updated.
	///
	/// @param	lower_bound Sets limit below which there's no erosion.
	void erode(float lower_bound) throw();

	/// Retrieve collision statistics of continent at given location.
	///
	/// @param	wx	X coordinate of collision point on world map.
	/// @param	wy	Y coordinate of collision point on world map.
	/// @param[in, out] count Destination for the count of collisions.
	/// @param[in, out] count Destination for the % of area that collided.
	void getCollisionInfo(size_t wx, size_t wy, size_t* count,
	                        float* ratio) const throw();

	/// Retrieve the surface area of continent lying at desired location.
	///
	/// @param	wx	X coordinate of collision point on world map.
	/// @param	wy	Y coordinate of collision point on world map.
	/// @return	Area of continent at desired location or 0 if none.
	size_t getContinentArea(size_t wx, size_t wy) const throw();

	/// Get the amount of plate's crustal material at some location.
	///
	/// @param	x	Offset on the global world map along X axis.
	/// @param	y	Offset on the global world map along Y axis.
	/// @return		Amount of crust at requested location.
	float getCrust(size_t x, size_t y) const throw();

	/// Get the timestamp of plate's crustal material at some location.
	///
	/// @param	x	Offset on the global world map along X axis.
	/// @param	y	Offset on the global world map along Y axis.
	/// @return		Timestamp of creation of crust at the location.
	///                     Zero is returned if location contains no crust.
	size_t getCrustTimestamp(size_t x, size_t y) const throw();

	/// Get pointers to plate's data.
	///
	/// @param	c	Adress of crust height map is stored here.
	/// @param	t	Adress of crust timestamp map is stored here.
	void getMap(const float** c, const size_t** t) const throw();

	void move() throw(); ///< Moves plate along it's trajectory.

	/// Clear any earlier continental crust partitions.
	///
	/// Plate has an internal bookkeeping of distinct areas of continental
	/// crust for more realistic collision responce. However as the number
	/// of collisions that plate experiences grows, so does the bookkeeping
	/// of a continent become more and more inaccurate. Finally it results
	/// in striking artefacts that cannot overlooked.
	///
	/// To alleviate this problem without the need of per iteration
	/// recalculations plate supplies caller a method to reset its
	/// bookkeeping and start clean.
	void resetSegments() throw();

	/// Remember the currently processed continent's segment number.
	///
	/// @param	coll_x	Origin of collision on global world map (X).
	/// @param	coll_y	Origin of collision on global world map (Y).
	void selectCollisionSegment(size_t coll_x, size_t coll_y) throw();

	/// Set the amount of plate's crustal material at some location.
	///
	/// If amount of crust to be set is negative, it'll be set to zero.
	///
	/// @param	x	Offset on the global world map along X axis.
	/// @param	y	Offset on the global world map along Y axis.
	/// @param	z	Amount of crust at given location.
	/// @param	t	Time of creation of new crust.
	void setCrust(size_t x, size_t y, float z, size_t t) throw();

	float getMass() const throw() { return mass; }
	float getMomentum() const throw() { return mass * velocity; }
	size_t getHeight() const throw() { return height; }
	float  getLeft() const throw() { return left; }
	float  getTop() const throw() { return top; }
	float getVelocity() const throw() { return velocity; }
	float getVelX() const throw() { return vx; }
	float getVelY() const throw() { return vy; }
	size_t getWidth() const throw() { return width; }
	bool   isEmpty() const throw() { return mass <= 0; }

	protected:
	private:

	/// Container for details about a segmeted crust area on this plate.
	class segmentData
	{
	  public:
		segmentData(size_t _x0, size_t _y0, size_t _x1, size_t _y1,
		            size_t _area) : x0(_x0), x1(_x1), y0(_y0), y1(_y1),
		                          area(_area), coll_count(0) {}

		size_t x0, x1; ///< Left and right bounds of this segment. 
		size_t y0, y1; ///< Top and bottom bounds for this segment.
		size_t area; ///< Number of locations this area consists of.
		size_t coll_count; ///< Number of collisions on this segment.
	};

	/// Separate a continent at (X, Y) to its own partition.
	///
	/// Method analyzes the pixels 4-ways adjacent at the given location
	/// and labels all connected continental points with same segment ID.
	///
	/// @param	x	Offset on the local height map along X axis.
	/// @param	y	Offset on the local height map along Y axis.
	/// @return	ID of created segment on success, otherwise -1.
	size_t createSegment(size_t wx, size_t wy) throw();

	/// Translate world coordinates into offset within plate's height map.
	///
	/// Iff the global world map coordinates are within plate's height map,
	/// the values of passed coordinates will be altered to contain the
	/// X and y offset within the plate's height map. Otherwise values are
	/// left intact.
	///
	/// @param[in, out] x	Offset on the global world map along X axis.
	/// @param[in, out] y	Offset on the global world map along Y axis.
	/// @return		Offset in height map or -1 on error.
	size_t getMapIndex(size_t* x, size_t* y) const throw();

	float* map; ///< Bitmap of plate's structure/height.
	size_t* age; ///< Bitmap of plate's soil's age: timestamp of creation.
	size_t width, height; ///< Height map's dimensions along X and Y axis.
	size_t world_side; ///< Container world map's either side in pixels.

	float mass; ///< Amount of crust that constitutes the plate.
	float left, top; ///< Height map's left-top corner in world coords.
	float cx, cy; ///< X and Y components of the center of mass of plate.

	float velocity; ///< Plate's velocity.
	float vx, vy; ///< X and Y components of plate's direction unit vector.
	float dx, dy; ///< X and Y components of plate's acceleration vector.
	float rot_dir; ///< Direction of rotation: 1 = CCW, -1 = ClockWise.

	std::vector<segmentData> seg_data; ///< Details of each crust segment.
	size_t* segment; ///< Segment ID of each piece of continental crust.
	size_t activeContinent; ///< Segment ID of the cont. that's processed.
};

#endif
