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

#define _USE_MATH_DEFINES // Winblow$.
#include <cfloat> // FT_EPSILON
#include <cmath> // sin, cos
#include <cstdlib> // rand
#include <cstdio> // DEBUG print
#include <vector>

#include "plate.hpp"

#define INITIAL_SPEED_X 1
#define DEFORMATION_WEIGHT 2

using namespace std;

/*
// http://en.wikipedia.org/wiki/Methods_of_computing_square_roots
static float invSqrt(float x)
{
	float xhalf = 0.5f*x;
        union { float x; int i; } u;

        u.x = x;
        u.i = 0x5f3759df - (u.i >> 1);
        x = u.x * (1.5f - xhalf * u.x * u.x);
        return x;
}

static float fastSqrt(float x)
{
	return 1.0f / invSqrt(x);
}
*/
plate::plate(const float* m, size_t w, size_t h, size_t _x, size_t _y,
             size_t plate_age, size_t _world_side) throw() :
             width(w), height(h), world_side(_world_side),
             mass(0), left(_x), top(_y), cx(0), cy(0), dx(0), dy(0)
{
	const size_t A = w * h; // A as in Area.
	const double angle = 2 * M_PI * rand() / (double)RAND_MAX;
	size_t i, j, k;

	if (!m)
		return;

	map = new float[A];
	age = new size_t[A];
	segment = new size_t[A];

	velocity = 1;
	rot_dir = rand() & 1 ? 1 : -1;
	vx = cos(angle) * INITIAL_SPEED_X;
	vy = sin(angle) * INITIAL_SPEED_X;
	memset(segment, 255, A * sizeof(size_t));

	for (j = k = 0; j < height; ++j)
		for (i = 0; i < width; ++i, ++k)
		{
			// Clone map data and count crust mass.
			mass += map[k] = m[k];

			// Calculate center coordinates weighted by mass.
			cx += i * m[k];
			cy += j * m[k];

			// Set the age of ALL points in this plate to same
			// value. The right thing to do would be to simulate
			// the generation of new oceanic crust as if the plate
			// had been moving to its current direction until all
			// plate's (oceanic) crust receive an age.
			age[k] = plate_age & -(m[k] > 0);
		}

	// Normalize center of mass coordinates.
	cx /= mass;
	cy /= mass;
}

plate::~plate() throw()
{
	delete[] map; map = 0;
	delete[] age; age = 0;
	delete[] segment; segment = 0;
}

size_t plate::addCollision(size_t wx, size_t wy) throw()
{
	size_t lx = wx, ly = wy;
	size_t index = getMapIndex(&lx, &ly);
	size_t seg = seg_data.size();

	#ifdef DEBUG
	if (index >= width * height)
	{
		puts("Continental collision out of map bounds!");
		exit(1);
	}
	#endif

	seg = segment[index];

	if (seg >= seg_data.size())
		seg = createSegment(lx, ly);

	#ifdef DEBUG
	if (seg >= seg_data.size())
	{
		puts("Could not create segment!");
		exit(1);
	}
	#endif

	++seg_data[seg].coll_count;
	return seg_data[seg].area;
}

void plate::addCrustByCollision(size_t x, size_t y, float z, size_t t) throw()
{
	// Add crust. Extend plate if necessary.
	setCrust(x, y, getCrust(x, y) + z, t);

	size_t index = getMapIndex(&x, &y);
	
	#ifdef DEBUG
	if (index >= width * height)
	{
		puts("Aggregation went overboard!");
		exit(1);
	}
	#endif

	segment[index] = activeContinent;
	segmentData& data = seg_data[activeContinent];

	++data.area;
	if (y < data.y0) data.y0 = y;
	if (y > data.y1) data.y1 = y;
	if (x < data.x0) data.x0 = x;
	if (x > data.x1) data.x1 = x;
}

void plate::addCrustBySubduction(size_t x, size_t y, float z, size_t t,
	float dx, float dy) throw()
{
	// TODO: Create an array of coordinate changes that would create
	//       a circle around current point. Array is static and it is
	//       initialized at the first call to this function.
	//       After all points of the circle are checked around subduction
	//       point the one with most land mass around it will be chosen as
	//       "most in land" point and subducting crust is added there.
	//       However to achieve a little more "natural" look normal
	//       distributed randomness is added around the "center" point.
	//       Benefits:
	//           NEVER adds crust aoutside plate.
	//           ALWAYS goes inland as much as possible
	//       Drawbacks:
	//           Additional logic required
	//           Might place crust on other continent on same plate!
	size_t index = getMapIndex(&x, &y);

	#ifdef DEBUG
	if (index >= width * height) // Should never be true!
	{
		puts("Subduction origin not on plate!");
		printf("%u, %u @ [%f, %f]x[%u, %u]\n", x, y, left, top,
			width, height);
		exit(1);
	}
	#endif

	// Take vector difference only between plates that move more or less
	// to same direction. This makes subduction direction behave better.
	//
	// Use of "this" pointer is not necessary, but it make code clearer.
	// Cursed be those who use "m_" prefix in member names! >(
	float dot = this->vx * dx + this->vy * dy;
	dx -= this->vx * (dot > 0);
	dy -= this->vy * (dot > 0);

	float offset = (float)rand() / (float)RAND_MAX;
	offset *= offset * offset * (2 * (rand() & 1) - 1);
	dx = 10 * dx + 3 * offset;
	dy = 10 * dy + 3 * offset;

	x = (size_t)((int)x + dx);
	y = (size_t)((int)y + dy);

	if (width == world_side) x &= width - 1;
	if (height == world_side) y &= height - 1;

	index = y * width + x;
	if (index < width * height && map[index] > 0)
	{
		t = (map[index] * age[index] + z * t) / (map[index] + z);
		age[index] = t * (z > 0);

		map[index] += z;
		mass += z;
	}
}

float plate::aggregateCrust(plate* p, size_t wx, size_t wy) throw()
{
	size_t lx = wx, ly = wy;
	const size_t index = getMapIndex(&lx, &ly);

	#ifdef DEBUG
	if (index >= width * height)
	{
		puts("Trying to aggregate beyond plate limits!");
		exit(1);
	}
	#endif

	const size_t seg_id = segment[index];

	// This check forces the caller to do things in proper order!
	//
	// Usually continents collide at several locations simultaneously.
	// Thus if this segment that is being merged now is removed from
	// segmentation bookkeeping, then the next point of collision that is
	// processed during the same iteration step would cause the test
	// below to be true and system would experience a premature abort.
	//
	// Therefore, segmentation bookkeeping is left intact. It doesn't
	// cause significant problems because all crust is cleared and empty
	// points are not processed at all.
	#ifdef DEBUG
	if (seg_id >= seg_data.size())
	{
		puts("Trying to aggregate without deforming first!");
		printf("%u %u\n", wx, wy);
		exit(1);
	}
	#endif

	// One continent may have many points of collision. If one of them
	// causes continent to aggregate then all successive collisions and
	// attempts of aggregation would necessarily change nothing at all,
	// because the continent was removed from this plate earlier!
	if (seg_data[seg_id].area == 0)
		return 0;	// Do not process empty continents.

	p->selectCollisionSegment(wx, wy);

	// Wrap coordinates around world edges to safeguard subtractions.
	wx += world_side;
	wy += world_side;

//	printf("Aggregating segment [%u, %u]x[%u, %u] vs. [%u, %u]@[%u, %u]\n",
//		seg_data[seg_id].x0, seg_data[seg_id].y0,
//		seg_data[seg_id].x1, seg_data[seg_id].y1,
//		width, height, lx, ly);

	float old_mass = mass;

	// Add all of the collided continent's crust to destination plate.
	for (size_t y = seg_data[seg_id].y0; y <= seg_data[seg_id].y1; ++y)
	  for (size_t x = seg_data[seg_id].x0; x <= seg_data[seg_id].x1; ++x)
	  {
		const size_t i = y * width + x;
		if ((segment[i] == seg_id) & (map[i] > 0))
		{
			p->addCrustByCollision(wx + x - lx, wy + y - ly,
				map[i], age[i]);

			mass -= map[i];
			map[i] = 0;
		}
	  }

	seg_data[seg_id].area = 0; // Mark segment as non-exitent.
	return old_mass - mass;
}

void plate::applyFriction(float deformed_mass) throw()
{
	// Remove the energy that deformation consumed from plate's kinetic
	// energy: F - dF = ma - dF => a = dF/m.
	if (mass > 0)
	{
		float vel_dec = DEFORMATION_WEIGHT * deformed_mass / mass;
		vel_dec = vel_dec < velocity ? vel_dec : velocity;

		// Altering the source variable causes the order of calls to
		// this function to have difference when it shouldn't!
		// However, it's a hack well worth the outcome. :)
		velocity -= vel_dec;
	}
}

void plate::collide(plate& p, size_t wx, size_t wy, float coll_mass) throw()
{
	const float coeff_rest = 0.0; // Coefficient of restitution.
	                              // 1 = fully elastic, 0 = stick together.

	// Calculate the normal to the curve/line at collision point.
	// The normal will point into plate B i.e. the "other" plate.
	//
	// Plates that wrap over world edges can mess the normal vector.
	// This could be solved by choosing the normal vector that points the
	// shortest path beween mass centers but this causes problems when
	// plates are like heavy metal balls at a long rod and one plate's ball
	// collides at the further end of other plate's rod. Sure, this is
	// nearly never occurring situation but if we can easily do better then
	// why not do it?
	//
	// Better way is to select that normal vector that points along the
	// line that passes nearest the point of collision. Because point's
	// distance from line segment is relatively cumbersome to perform, the
	// vector is constructed as the sum of vectors <massCenterA, P> and
	// <P, massCenterB>. This solution works because collisions always
	// happen in the overlapping region of the two plates.
	size_t apx = wx, apy = wy, bpx = wx, bpy = wy;
	float ap_dx, ap_dy, bp_dx, bp_dy, nx, ny;
	size_t index = getMapIndex(&apx, &apy);
	size_t p_index = p.getMapIndex(&bpx, &bpy);

	if (index >= width * height || p_index >= p.width * p.height)
	{
	#ifdef DEBUG
		printf("@%u, %u: out of colliding map's bounds!\n", wx, wy);
		exit(1);
	#endif
	}

	ap_dx = (int)apx - (int)cx;
	ap_dy = (int)apy - (int)cy;
	bp_dx = (int)bpx - (int)p.cx;
	bp_dy = (int)bpy - (int)p.cy;
	nx = ap_dx - bp_dx;
	ny = ap_dy - bp_dy;

	if (nx * nx + ny * ny <= 0)
		return; // Avoid division by zero!

	// Scaling is required at last when impulses are added to plates!
	float n_len = sqrt(nx * nx + ny * ny);
	nx /= n_len;
	ny /= n_len;

	// Compute relative velocity between plates at the collision point.
	// Because torque is not included, calc simplifies to v_ab = v_a - v_b.
	const float rel_vx = vx - p.vx;
	const float rel_vy = vy - p.vy;

	// Get the dot product of relative velocity vector and collision vector.
	// Then get the projection of v_ab along collision vector.
	// Note that vector n must be a unit vector!
	const float rel_dot_n = rel_vx * nx + rel_vy * ny;

	if (rel_dot_n <= 0)
	{
//		printf("n=%.2f, %.2f r=%.2f, %.2f, dot=%.4f\n",
//			nx, ny, rel_vx, rel_vy, rel_dot_n);
		return; // Exit if objects are moving away from each other.
	}

	// Calculate the denominator of impulse: n . n * (1 / m_1 + 1 / m_2).
	// Use the mass of the colliding crust for the "donator" plate.
	float denom = (nx * nx + ny * ny) * (1.0/mass + 1.0/coll_mass);

	// Calculate force of impulse.
	float J = -(1 + coeff_rest) * rel_dot_n / denom;

	// Compute final change of trajectory.
	// The plate that is the "giver" of the impulse should receive a
	// force according to its pre-collision mass, not the current mass!
	dx += nx * J / mass;
	dy += ny * J / mass;
	p.dx -= nx * J / (coll_mass + p.mass);
	p.dy -= ny * J / (coll_mass + p.mass);

	// In order to prove that the code above works correctly, here is an
	// example calculation with ball A (mass 10) moving right at velocity
	// 1 and ball B (mass 100) moving up at velocity 1. Collision point
	// is at rightmost point of ball A and leftmost point of ball B.
	// Radius of both balls is 2.
	// ap_dx =  2;
	// ap_dy =  0;
	// bp_dx = -2;
	// bp_dy =  0;
	// nx = 2 - -2 = 4;
	// ny = 0 -  0 = 0;
	// n_len = sqrt(4 * 4 + 0) = 4;
	// nx = 4 / 4 = 1;
	// ny = 0 / 4 = 0;
	//
	// So far so good, right? Normal points into ball B like it should.
	//
	// rel_vx = 1 -  0 = 1;
	// rel_vy = 0 - -1 = 1;
	// rel_dot_n = 1 * 1 + 1 * 0 = 1;
	// denom = (1 * 1 + 0 * 0) * (1/10 + 1/100) = 1 * 11/100 = 11/100;
	// J = -(1 + 0) * 1 / (11/100) = -100/11;
	// dx = 1 * (-100/11) / 10 = -10/11;
	// dy = 0;
	// p.dx = -1 * (-100/11) / 100 = 1/11;
	// p.dy = -0;
	//
	// So finally:
	// vx = 1 - 10/11 = 1/11
	// vy = 0
	// p.vx = 0 + 1/11 = 1/11
	// p.vy = -1
	//
	// We see that in with restitution 0, both balls continue at same
	// speed along X axis. However at the same time ball B continues its
	// path upwards like it should. Seems correct right?
}

void plate::erode(float lower_bound) throw()
{
  vector<size_t> sources_data;
  vector<size_t> sinks_data;
  vector<size_t>* sources = &sources_data;
  vector<size_t>* sinks = &sinks_data;

  float* tmp = new float[width*height];
  memcpy(tmp, map, width*height*sizeof(float));

  // Find all tops.
  for (size_t y = 0; y < height; ++y)
    for (size_t x = 0; x < width; ++x)
    {
	const size_t index = y * width + x;

	if (map[index] < lower_bound)
		continue;

	// Build masks for accessible directions (4-way).
	// Allow wrapping around map edges if plate has world wide dimensions.
	size_t w_mask = -((x > 0) | (width == world_side));
	size_t e_mask = -((x < width - 1) | (width == world_side));
	size_t n_mask = -((y > 0) | (height == world_side));
	size_t s_mask = -((y < height - 1) | (height == world_side));

	// Calculate the x and y offset of neighbour directions.
	// If neighbour is out of plate edges, set it to zero. This protects
	// map memory reads from segment faulting.
    	size_t w = (world_side + x - 1) & (world_side - 1) & w_mask;
    	size_t e = (world_side + x + 1) & (world_side - 1) & e_mask;
    	size_t n = (world_side + y - 1) & (world_side - 1) & n_mask;
    	size_t s = (world_side + y + 1) & (world_side - 1) & s_mask;

	// Calculate offsets within map memory.
	w = y * width + w;
	e = y * width + e;
	n = n * width + x;
	s = s * width + x;

	// Extract neighbours heights. Apply validity filtering: 0 is invalid.
	float w_crust = map[w] * (w_mask & (map[w] < map[index]));
	float e_crust = map[e] * (e_mask & (map[e] < map[index]));
	float n_crust = map[n] * (n_mask & (map[n] < map[index]));
	float s_crust = map[s] * (s_mask & (map[s] < map[index]));

	// This location is either at the edge of the plate or it is not the
	// tallest of its neightbours. Don't start a river from here.
	if (w_crust * e_crust * n_crust * s_crust == 0)
		continue;

	sources->push_back(index);
    }

  size_t* isDone = new size_t[width*height];
  memset(isDone, 0, width*height*sizeof(size_t));

  // From each top, start flowing water along the steepest slope.
  while (!sources->empty())
  {
    while (!sources->empty())
    {
	const size_t index = sources->back();
	const size_t y = index / width;
	const size_t x = index - y * width;

	sources->pop_back();

	if (map[index] < lower_bound)
		continue;

	// Build masks for accessible directions (4-way).
	// Allow wrapping around map edges if plate has world wide dimensions.
	size_t w_mask = -((x > 0) | (width == world_side));
	size_t e_mask = -((x < width - 1) | (width == world_side));
	size_t n_mask = -((y > 0) | (height == world_side));
	size_t s_mask = -((y < height - 1) | (height == world_side));

	// Calculate the x and y offset of neighbour directions.
	// If neighbour is out of plate edges, set it to zero. This protects
	// map memory reads from segment faulting.
    	size_t w = (world_side + x - 1) & (world_side - 1) & w_mask;
    	size_t e = (world_side + x + 1) & (world_side - 1) & e_mask;
    	size_t n = (world_side + y - 1) & (world_side - 1) & n_mask;
    	size_t s = (world_side + y + 1) & (world_side - 1) & s_mask;

	// Calculate offsets within map memory.
	w = y * width + w;
	e = y * width + e;
	n = n * width + x;
	s = s * width + x;

	// Extract neighbours heights. Apply validity filtering: 0 is invalid.
	float w_crust = map[w] * (w_mask & (map[w] < map[index]));
	float e_crust = map[e] * (e_mask & (map[e] < map[index]));
	float n_crust = map[n] * (n_mask & (map[n] < map[index]));
	float s_crust = map[s] * (s_mask & (map[s] < map[index]));

	// If this is the lowest part of its neighbourhood, stop.
	if (w_crust + e_crust + n_crust + s_crust == 0)
		continue;

	w_crust += (w_crust == 0) * map[index];
	e_crust += (e_crust == 0) * map[index];
	n_crust += (n_crust == 0) * map[index];
	s_crust += (s_crust == 0) * map[index];

	// Find lowest neighbour.
	float lowest_crust = w_crust;
	size_t dest = index - 1;

	if (e_crust < lowest_crust)
	{
		lowest_crust = e_crust;
		dest = index + 1;
	}

	if (n_crust < lowest_crust)
	{
		lowest_crust = n_crust;
		dest = index - width;
	}

	if (s_crust < lowest_crust)
	{
		lowest_crust = s_crust;
		dest = index + width;
	}

	// if it's not handled yet, add it as new sink.
	if (dest < width * height && !isDone[dest])
	{
		sinks->push_back(dest);
		isDone[dest] = 1;
	}

	// Erode this location with the water flow.
	tmp[index] -= (tmp[index] - lower_bound) * 0.2;
    }

    vector<size_t>* v_tmp = sources;
    sources = sinks;
    sinks = v_tmp;
    sinks->clear();
  }

  delete[] isDone;

  // Add random noise (10 %) to heightmap.
  for (size_t i = 0; i < width*height; ++i)
  {
    float alpha = 0.2 * rand() / (float)RAND_MAX;
    tmp[i] += 0.1 * tmp[i] - alpha * tmp[i];
  }

  memcpy(map, tmp, width*height*sizeof(float));
  memset(tmp, 0, width*height*sizeof(float));
  mass = 0;
  cx = cy = 0;

  for (size_t y = 0; y < height; ++y)
    for (size_t x = 0; x < width; ++x)
    {
	const size_t index = y * width + x;
	mass += map[index];
	tmp[index] += map[index]; // Careful not to overwrite earlier amounts.

	// Update the center coordinates weighted by mass.
	cx += x * map[index];
	cy += y * map[index];

	if (map[index] < lower_bound)
		continue;

	// Build masks for accessible directions (4-way).
	// Allow wrapping around map edges if plate has world wide dimensions.
	size_t w_mask = -((x > 0) | (width == world_side));
	size_t e_mask = -((x < width - 1) | (width == world_side));
	size_t n_mask = -((y > 0) | (height == world_side));
	size_t s_mask = -((y < height - 1) | (height == world_side));

	// Calculate the x and y offset of neighbour directions.
	// If neighbour is out of plate edges, set it to zero. This protects
	// map memory reads from segment faulting.
    	size_t w = (world_side + x - 1) & (world_side - 1) & w_mask;
    	size_t e = (world_side + x + 1) & (world_side - 1) & e_mask;
    	size_t n = (world_side + y - 1) & (world_side - 1) & n_mask;
    	size_t s = (world_side + y + 1) & (world_side - 1) & s_mask;

	// Calculate offsets within map memory.
	w = y * width + w;
	e = y * width + e;
	n = n * width + x;
	s = s * width + x;

	// Extract neighbours heights. Apply validity filtering: 0 is invalid.
	float w_crust = map[w] * (w_mask & (map[w] < map[index]));
	float e_crust = map[e] * (e_mask & (map[e] < map[index]));
	float n_crust = map[n] * (n_mask & (map[n] < map[index]));
	float s_crust = map[s] * (s_mask & (map[s] < map[index]));

	// This location has no neighbours (ARTIFACT!) or it is the lowest
	// part of its area. In either case the work here is done.
	if (w_crust + e_crust + n_crust + s_crust == 0)
		continue;

	// The steeper the slope, the more water flows along it.
	// The more downhill (sources), the more water flows to here.
	// 1+1+10 = 12, avg = 4, stdev = sqrt((3*3+3*3+6*6)/3) = 4.2, var = 18,
	//	1*1+1*1+10*10 = 102, 102/4.2=24
	// 1+4+7 = 12, avg = 4, stdev = sqrt((3*3+0*0+3*3)/3) = 2.4, var = 6,
	//	1*1+4*4+7*7 = 66, 66/2.4 = 27
	// 4+4+4 = 12, avg = 4, stdev = sqrt((0*0+0*0+0*0)/3) = 0, var = 0,
	//	4*4+4*4+4*4 = 48, 48/0 = inf -> 48
	// If there's a source slope of height X then it will always cause
	// water erosion of amount Y. Then again from one spot only so much
	// water can flow.
	// Thus, the calculated non-linear flow value for this location is
	// multiplied by the "water erosion" constant.
	// The result is max(result, 1.0). New height of this location could
	// be e.g. h_lowest + (1 - 1 / result) * (h_0 - h_lowest).

	// Calculate the difference in height between this point and its
	// nbours that are lower than this point.
	float w_diff = map[index] - w_crust;
	float e_diff = map[index] - e_crust;
	float n_diff = map[index] - n_crust;
	float s_diff = map[index] - s_crust;

	float min_diff = w_diff;
	min_diff -= (min_diff - e_diff) * (e_diff < min_diff);
	min_diff -= (min_diff - n_diff) * (n_diff < min_diff);
	min_diff -= (min_diff - s_diff) * (s_diff < min_diff);

	// Calculate the sum of difference between lower neighbours and
	// the TALLEST lower neighbour.
	float diff_sum = (w_diff - min_diff) * (w_crust > 0) +
	                 (e_diff - min_diff) * (e_crust > 0) +
	                 (n_diff - min_diff) * (n_crust > 0) +
	                 (s_diff - min_diff) * (s_crust > 0);

	#ifdef DEBUG
	if (diff_sum < 0)
	{
		puts("Erosion differense sum is negative!");
		printf("%f > %f %f %f %f\n", min_diff, w_diff, e_diff,
			n_diff, s_diff);
		exit(1);
	}
	#endif

	if (diff_sum < min_diff)
	{
		// There's NOT enough room in neighbours to contain all the
		// crust from this peak so that it would be as tall as its
		// tallest lower neighbour. Thus first step is make ALL
		// lower neighbours and this point equally tall.
		tmp[w] += (w_diff - min_diff) * (w_crust > 0);
		tmp[e] += (e_diff - min_diff) * (e_crust > 0);
		tmp[n] += (n_diff - min_diff) * (n_crust > 0);
		tmp[s] += (s_diff - min_diff) * (s_crust > 0);
		tmp[index] -= min_diff;

		min_diff -= diff_sum;

		// Spread the remaining crust equally among all lower nbours.
		min_diff /= 1 + (w_crust > 0) + (e_crust > 0) +
			(n_crust > 0) + (s_crust > 0);

		tmp[w] += min_diff * (w_crust > 0);
		tmp[e] += min_diff * (e_crust > 0);
		tmp[n] += min_diff * (n_crust > 0);
		tmp[s] += min_diff * (s_crust > 0);
		tmp[index] += min_diff;
	}
	else
	{
		float unit = min_diff / diff_sum;

		// Remove all crust from this location making it as tall as
		// its tallest lower neighbour.
		tmp[index] -= min_diff;

		// Spread all removed crust among all other lower neighbours.
		tmp[w] += unit * (w_diff - min_diff) * (w_crust > 0);
		tmp[e] += unit * (e_diff - min_diff) * (e_crust > 0);
		tmp[n] += unit * (n_diff - min_diff) * (n_crust > 0);
		tmp[s] += unit * (s_diff - min_diff) * (s_crust > 0);
	}
    }

  delete[] map;
  map = tmp;

  if (mass > 0)
  {
    cx /= mass;
    cy /= mass;
  }
}

void plate::getCollisionInfo(size_t wx, size_t wy, size_t* count,
                             float* ratio) const throw()
{
	size_t lx = wx, ly = wy;
	size_t index = getMapIndex(&lx, &ly);
	size_t seg = seg_data.size();

	*count = 0;
	*ratio = 0;

	#ifdef DEBUG
	if (index >= width * height)
	{
		puts("getCollisionInfo: out of map bounds!");
		exit(1);
	}
	#endif

	seg = segment[index];
	#ifdef DEBUG
	if (seg >= seg_data.size())
	{
		puts("getCollisionInfo: no segment found!");
		exit(1);
	}
	#endif

	*count = seg_data[seg].coll_count;
	*ratio = (float)seg_data[seg].coll_count /
		(float)(1 + seg_data[seg].area); // +1 avoids DIV with zero.
}

size_t plate::getContinentArea(size_t wx, size_t wy) const throw()
{
	const size_t index = getMapIndex(&wx, &wy);

	#ifdef DEBUG
	if (index >= width * height)
	{
		puts("getContinentArea: out of map bounds!");
		exit(1);
	}

	if (segment[index] >= seg_data.size())
	{
		puts("getContinentArea: no segment found!");
		exit(1);
	}
	#endif

	return seg_data[segment[index]].area;
}

float plate::getCrust(size_t x, size_t y) const throw()
{
	const size_t index = getMapIndex(&x, &y);
	return index < (size_t)(-1) ? map[index] : 0;
}

size_t plate::getCrustTimestamp(size_t x, size_t y) const throw()
{
	const size_t index = getMapIndex(&x, &y);
	return index < (size_t)(-1) ? age[index] : 0;
}

void plate::getMap(const float** c, const size_t** t) const throw()
{
	if (c) *c = map;
	if (t) *t = age;
}

void plate::move() throw()
{
	float len;

	// Apply any new impulses to the plate's trajectory.
	vx += dx;
	vy += dy;
	dx = 0;
	dy = 0;

	// Force direction of plate to be unit vector.
	// Update velocity so that the distance of movement doesn't change.
	len = sqrt(vx*vx+vy*vy);
	vx /= len;
	vy /= len;
	velocity += len - 1.0;
	velocity *= velocity > 0; // Round negative values to zero.

	// Apply some circular motion to the plate.
	// Force the radius of the circle to remain fixed by adjusting
	// anglular velocity (which depends on plate's velocity).
	float alpha = rot_dir * velocity / (world_side * 0.33);
	float _cos = cos(alpha * velocity);
	float _sin = sin(alpha * velocity);
	float _vx = vx * _cos - vy * _sin;
	float _vy = vy * _cos + vx * _sin;
	vx = _vx;
	vy = _vy;

	// Location modulations into range [0, world_side[ are a have to!
	// If left undone SOMETHING WILL BREAK DOWN SOMEWHERE in the code!

	#ifdef DEBUG
	if (left < 0 || left > world_side || top < 0 || top > world_side)
	{
		puts("Location coordinates out of world map bounds (PRE)!");
		exit(1);
	}
	#endif

	left += vx * velocity;
	left += left > 0 ? 0 : world_side;
	left -= left < world_side ? 0 : world_side;

	top += vy * velocity;
	top += top > 0 ? 0 : world_side;
	top -= top < world_side ? 0 : world_side;

	#ifdef DEBUG
	if (left < 0 || left > world_side || top < 0 || top > world_side)
	{
		puts("Location coordinates out of world map bounds (POST)!");
		printf("%f, %f, %f; %f, %f\n", vx, vy, velocity, left, top);
		exit(1);
	}
	#endif
}

void plate::resetSegments() throw()
{
	memset(segment, -1, sizeof(size_t) * width * height);
	seg_data.clear();
}

void plate::setCrust(size_t x, size_t y, float z, size_t t) throw()
{
	if (z < 0) // Do not accept negative values.
		z = 0;

	size_t _x = x;
	size_t _y = y;
	size_t index = getMapIndex(&_x, &_y);

	if (index >= width*height)
	{
		#ifdef DEBUG
		if (z <= 0)
		{
			printf("Extending plate for nothing!");
			exit(1);
		}
		#endif

		const size_t ilft = left;
		const size_t itop = top;
		const size_t irgt = ilft + width - 1;
		const size_t ibtm = itop + height - 1;

		x &= world_side - 1; // HACK!
		y &= world_side - 1; // Just to be safe...

		// Calculate distance of new point from plate edges.
		const size_t _lft = ilft - x;
		const size_t _rgt = (world_side & -(x < ilft)) + x - irgt;
		const size_t _top = itop - y;
		const size_t _btm = (world_side & -(y < itop)) + y - ibtm;

		// Set larger of horizontal/vertical distance to zero.
		// A valid distance is NEVER larger than world's side's length!
		size_t d_lft = _lft & -(_lft <  _rgt) & -(_lft < world_side);
		size_t d_rgt = _rgt & -(_rgt <= _lft) & -(_rgt < world_side);
		size_t d_top = _top & -(_top <  _btm) & -(_top < world_side);
		size_t d_btm = _btm & -(_btm <= _top) & -(_btm < world_side);

		// Scale all changes to multiple of 8.
		d_lft = ((d_lft > 0) + (d_lft >> 3)) << 3;
		d_rgt = ((d_rgt > 0) + (d_rgt >> 3)) << 3;
		d_top = ((d_top > 0) + (d_top >> 3)) << 3;
		d_btm = ((d_btm > 0) + (d_btm >> 3)) << 3;

		// Make sure plate doesn't grow bigger than the system it's in!
		if (width + d_lft + d_rgt > world_side)
		{
			d_lft = 0;
			d_rgt = world_side - width;
		}

		if (height + d_top + d_btm > world_side)
		{
			d_top = 0;
			d_btm = world_side - height;
		}

		#ifdef DEBUG
		if (d_lft + d_rgt + d_top + d_btm == 0)
		{
			printf("[%u, %u]x[%u, %u], [%u, %u]/[%u, %u]\n",
				(size_t)left, (size_t)top, (size_t)left+width,
				(size_t)top+height,
				x + world_side * (x < world_side),
				y + world_side * (y < world_side),
				x % world_side, y % world_side);

			puts("Index out of bounds, but nowhere to grow!");
			exit(1);
		}
		#endif

		const size_t old_width = width;
		const size_t old_height = height;
		
		left -= d_lft;
		left += left >= 0 ? 0 : world_side;
		width += d_lft + d_rgt;

		top -= d_top;
		top += top >= 0 ? 0 : world_side;
		height += d_top + d_btm;

//		printf("%ux%u + [%u,%u] + [%u, %u] = %ux%u\n",
//			old_width, old_height,
//			d_lft, d_top, d_rgt, d_btm, width, height);

		float* tmph = new float[width*height];
		size_t* tmpa = new size_t[width*height];
		size_t* tmps = new size_t[width*height];
		memset(tmph, 0, width*height*sizeof(float));
		memset(tmpa, 0, width*height*sizeof(size_t));
		memset(tmps, 255, width*height*sizeof(size_t));

		// copy old plate into new.
		for (size_t j = 0; j < old_height; ++j)
		{
			const size_t dest_i = (d_top + j) * width + d_lft;
			const size_t src_i = j * old_width;
			memcpy(&tmph[dest_i], &map[src_i], old_width *
				sizeof(float));
			memcpy(&tmpa[dest_i], &age[src_i], old_width *
				sizeof(size_t));
			memcpy(&tmps[dest_i], &segment[src_i], old_width *
				sizeof(size_t));
		}

		delete[] map;
		delete[] age;
		delete[] segment;
		map = tmph;
		age = tmpa;
		segment = tmps;

		// Shift all segment data to match new coordinates.
		for (size_t s = 0; s < seg_data.size(); ++s)
		{
			seg_data[s].x0 += d_lft;
			seg_data[s].x1 += d_lft;
			seg_data[s].y0 += d_top;
			seg_data[s].y1 += d_top;
		}

		_x = x, _y = y;
		index = getMapIndex(&_x, &_y);

		#ifdef DEBUG
		if (index >= width * height)
		{
			printf("Index out of bounds after resize!\n"
				"[%u, %u]x[%u, %u], [%u, %u]/[%u, %u]\n",
				(size_t)left, (size_t)top, (size_t)left+width,
				(size_t)top+height,
				x, y, x % world_side, y % world_side);
			exit(1);
		}
		#endif
	}

	// Update crust's age.
	// If old crust exists, new age is mean of original and supplied ages.
	// If no new crust is added, original time remains intact.
	const size_t old_crust = -(map[index] > 0);
	const size_t new_crust = -(z > 0);
	t = (t & ~old_crust) | ((size_t)((map[index] * age[index] + z * t) /
		(map[index] + z)) & old_crust);
	age[index] = (t & new_crust) | (age[index] & ~new_crust);

	mass -= map[index];
	map[index] = z;		// Set new crust height to desired location.
	mass += z;		// Update mass counter.
}

void plate::selectCollisionSegment(size_t coll_x, size_t coll_y) throw()
{
	size_t index = getMapIndex(&coll_x, &coll_y);

	activeContinent = seg_data.size();
	#ifdef DEBUG
	if (index >= width * height)
	{
		puts("Collision segment cannot be set outside plate!");
		exit(1);
	}
	#endif

	activeContinent = segment[index];

	#ifdef DEBUG
	if (activeContinent >= seg_data.size())
	{
		puts("Collision happened at unsegmented location!");
		exit(1);
	}
	#endif
}

///////////////////////////////////////////////////////////////////////////////
/// Private methods ///////////////////////////////////////////////////////////
///////////////////////////////////////////////////////////////////////////////

size_t plate::createSegment(size_t x, size_t y) throw()
{
	const size_t origin_index = y * width + x;
	const size_t ID = seg_data.size();

	if (segment[origin_index] < ID)
		return segment[origin_index];

	size_t canGoLeft = x > 0 && map[origin_index - 1] >= CONT_BASE;
	size_t canGoRight = x < width - 1 && map[origin_index+1] >= CONT_BASE;
	size_t canGoUp = y > 0 && map[origin_index - width] >= CONT_BASE;
	size_t canGoDown = y < height - 1 &&
		map[origin_index + width] >= CONT_BASE;
	size_t nbour_id = ID;

	// This point belongs to no segment yet.
	// However it might be a neighbour to some segment created earlier.
	// If such neighbour is found, associate this point with it.
	if (canGoLeft && segment[origin_index - 1] < ID)
		nbour_id = segment[origin_index - 1];
	else if (canGoRight && segment[origin_index + 1] < ID)
		nbour_id = segment[origin_index + 1];
	else if (canGoUp && segment[origin_index - width] < ID)
		nbour_id = segment[origin_index - width];
	else if (canGoDown && segment[origin_index + width] < ID)
		nbour_id = segment[origin_index + width];

	if (nbour_id < ID)
	{
		segment[origin_index] = nbour_id;
		++seg_data[nbour_id].area;

		if (y < seg_data[nbour_id].y0) seg_data[nbour_id].y0 = y;
		if (y > seg_data[nbour_id].y1) seg_data[nbour_id].y1 = y;
		if (x < seg_data[nbour_id].x0) seg_data[nbour_id].x0 = x;
		if (x > seg_data[nbour_id].x1) seg_data[nbour_id].x1 = x;

		return nbour_id;
	}

	size_t lines_processed;
	segmentData data(x, y, x, y, 0);

	std::vector<size_t>* spans_todo = new std::vector<size_t>[height];
	std::vector<size_t>* spans_done = new std::vector<size_t>[height];

	segment[origin_index] = ID;
	spans_todo[y].push_back(x);
	spans_todo[y].push_back(x);

	do
	{
	  lines_processed = 0;
	  for (size_t line = 0; line < height; ++line)
	  {
		size_t start, end;

		if (spans_todo[line].size() == 0)
			continue;

		do // Find an unscanned span on this line.
		{
			end = spans_todo[line].back();
			spans_todo[line].pop_back();

			start = spans_todo[line].back();
			spans_todo[line].pop_back();

			// Reduce any done spans from this span.
			for (size_t j = 0; j < spans_done[line].size();
			     j += 2)
			{
				// Saved coordinates are AT the point
				// that was included last to the span.
				// That's why equalities matter.

				if (start >= spans_done[line][j] &&
				    start <= spans_done[line][j+1])
					start = spans_done[line][j+1] + 1;

				if (end >= spans_done[line][j] &&
				    end <= spans_done[line][j+1])
					end = spans_done[line][j] - 1;
			}

			// Unsigned-ness hacking!
			// Required to fix the underflow of end - 1.
			start |= -(end >= width);
			end -= (end >= width);

		} while (start > end && spans_todo[line].size());

		if (start > end) // Nothing to do here anymore...
			continue;

		// Calculate line indices. Allow wrapping around map edges.
		const size_t row_above = ((line - 1) & -(line > 0)) |
			((height - 1) & -(line == 0));
		const size_t row_below = (line + 1) & -(line < height - 1);
		const size_t line_here = line * width;
		const size_t line_above = row_above * width;
		const size_t line_below = row_below * width;

		// Extend the beginning of line.
		while (start > 0 && segment[line_here+start-1] > ID &&
			map[line_here+start-1] >= CONT_BASE)
		{
			--start;
			segment[line_here + start] = ID;

			// Count volume of pixel...
		}

		// Extend the end of line.
		while (end < width - 1 &&
			segment[line_here + end + 1] > ID &&
			map[line_here + end + 1] >= CONT_BASE)
		{
			++end;
			segment[line_here + end] = ID;

			// Count volume of pixel...
		}

		// Check if should wrap around left edge.
		if (width == world_side && start == 0 &&
			segment[line_here+width-1] > ID &&
			map[line_here+width-1] >= CONT_BASE)
		{
			segment[line_here + width - 1] = ID;
			spans_todo[line].push_back(width - 1);
			spans_todo[line].push_back(width - 1);

			// Count volume of pixel...
		}

		// Check if should wrap around right edge.
		if (width == world_side && end == width - 1 &&
			segment[line_here+0] > ID &&
			map[line_here+0] >= CONT_BASE)
		{
			segment[line_here + 0] = ID;
			spans_todo[line].push_back(0);
			spans_todo[line].push_back(0);

			// Count volume of pixel...
		}

		data.area += 1 + end - start; // Update segment area counter.

		// Record any changes in extreme dimensions.
		if (line < data.y0) data.y0 = line;
		if (line > data.y1) data.y1 = line;
		if (start < data.x0) data.x0 = start;
		if (end > data.x1) data.x1 = end;

		if (line > 0 || height == world_side)
		for (size_t j = start; j <= end; ++j)
		  if (segment[line_above + j] > ID &&
		      map[line_above + j] >= CONT_BASE)
		  {
			size_t a = j;
			segment[line_above + a] = ID;

			// Count volume of pixel...

			while (++j < width &&
			       segment[line_above + j] > ID &&
			       map[line_above + j] >= CONT_BASE)
			{
				segment[line_above + j] = ID;

				// Count volume of pixel...
			}

			size_t b = --j; // Last point is invalid.

			spans_todo[row_above].push_back(a);
			spans_todo[row_above].push_back(b);
			++j; // Skip the last scanned point.
		  }

		if (line < height - 1 || height == world_side)
		for (size_t j = start; j <= end; ++j)
		  if (segment[line_below + j] > ID &&
		      map[line_below + j] >= CONT_BASE)
		  {
			size_t a = j;
			segment[line_below + a] = ID;

			// Count volume of pixel...

			while (++j < width &&
			       segment[line_below + j] > ID &&
			       map[line_below + j] >= CONT_BASE)
			{
				segment[line_below + j] = ID;

				// Count volume of pixel...
			}

			size_t b = --j; // Last point is invalid.

			spans_todo[row_below].push_back(a);
			spans_todo[row_below].push_back(b);
			++j; // Skip the last scanned point.
		  }

		spans_done[line].push_back(start);
		spans_done[line].push_back(end);
		++lines_processed;
	  }
	} while (lines_processed > 0);

	delete[] spans_todo;
	delete[] spans_done;
	seg_data.push_back(data);
//	printf("Created segment [%u, %u]x[%u, %u]@[%u, %u].\n",
//		data.x0, data.y0, data.x1, data.y1, x, y);

	return ID;
}

size_t plate::getMapIndex(size_t* px, size_t* py) const throw()
{
	size_t x = *px;
	size_t y = *py;
	const size_t ilft = (size_t)(int)left;
	const size_t itop = (size_t)(int)top;
	const size_t irgt = ilft + width;
	const size_t ibtm = itop + height;

	x &= world_side - 1; // Sometimes input is beyond map dimensions.
	y &= world_side - 1; // Scale it to fit within world map.

	///////////////////////////////////////////////////////////////////////
	// If you think you're smart enough to optimize this then PREPARE to be
	// smart as HELL to debug it!
	///////////////////////////////////////////////////////////////////////

	const size_t xOkA = (x >= ilft) & (x < irgt);
	const size_t xOkB = (x + world_side >= ilft) &
	                      (x +world_side < irgt);
	const size_t xOk = xOkA | xOkB;

	const size_t yOkA = (y >= itop) & (y < ibtm);
	const size_t yOkB = (y + world_side >= itop) &
	                      (y +world_side < ibtm);
	const size_t yOk = yOkA | yOkB;

	x += world_side & -(x < ilft); // Point is within plate's map: wrap
	y += world_side & -(y < itop); // it around world edges if necessary.

	x -= ilft; // Calculate offset within local map.
	y -= itop;

	size_t failMask = -(!xOk | !yOk);

	#ifdef DEBUG
	if (failMask)
	{
		bool X_OK = (*px >= ilft && *px < irgt) || 
			(*px+world_side >= ilft && *px+world_side < irgt);
		bool Y_OK = (*py >= itop && *py < ibtm) || 
			(*py+world_side >= itop && *py+world_side < ibtm);

		if (X_OK && Y_OK)
		{
			puts("MapIndex has an error, goddamn!");
			exit(1);
		}
	}
	else if (y >= height || x >= width)
	{
		printf("Map Index error: %u <= %u < %u, %u <= %u < %u\n",
			0, x, width, 0, y, height);
		printf("%u <= %u < %u, %u <= %u < %u\n", ilft, *px, irgt,
			itop, *py, ibtm);
		exit(1);
	}
	#endif

	*px = x & ~failMask;
	*py = y & ~failMask;
	return (y * width + x) | failMask;
}

