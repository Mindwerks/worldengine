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

#include "lithosphere.hpp"
#include "plate.hpp"
#include "sqrdmd.h"

#include <cfloat>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <vector>

#define BOOL_REGENERATE_CRUST	1

using namespace std;

/**
 * Wrapper for growing plate from a seed. Contains plate's dimensions.
 *
 * Used exclusively in plate creation phase.
 */
class plateArea
{
  public:
	vector<size_t> border; ///< Plate's unprocessed border pixels.
	size_t btm; ///< Most bottom pixel of plate.
	size_t lft; ///< Most left pixel of plate.
	size_t rgt; ///< Most right pixel of plate.
	size_t top; ///< Most top pixel of plate.
	size_t wdt; ///< Width of area in pixels.
	size_t hgt; ///< Height of area in pixels.
};

static const float SQRDMD_ROUGHNESS = 0.5f;
static const float SUBDUCT_RATIO = 0.5f;
 
static const float BUOYANCY_BONUS_X = 3;
static const size_t MAX_BUOYANCY_AGE = 20;
static const float MULINV_MAX_BUOYANCY_AGE = 1.0f / (float)MAX_BUOYANCY_AGE;

static const float RESTART_ENERGY_RATIO = 0.15;
static const float RESTART_SPEED_LIMIT = 2.0;
static const size_t NO_COLLISION_TIME_LIMIT = 10;

size_t findBound(const size_t* map, size_t length, size_t x0, size_t y0,
                 int dx, int dy);
size_t findPlate(plate** plates, float x, float y, size_t num_plates);

lithosphere::lithosphere(size_t map_side_length, float sea_level,
	size_t _erosion_period, float _folding_ratio, size_t aggr_ratio_abs,
	float aggr_ratio_rel, size_t num_cycles) throw(invalid_argument) :
	hmap(0), plates(0), aggr_overlap_abs(aggr_ratio_abs),
	aggr_overlap_rel(aggr_ratio_rel), cycle_count(0),
	erosion_period(_erosion_period), folding_ratio(_folding_ratio),
	iter_count(0), map_side(map_side_length + 1), max_cycles(num_cycles),
	max_plates(0), num_plates(0)
{
	const size_t A = map_side * map_side;
	float* tmp = new float[A];
	memset(tmp, 0, A * sizeof(float));

	if (sqrdmd(tmp, map_side, SQRDMD_ROUGHNESS) < 0)
	{
		delete[] tmp;
		throw invalid_argument("Failed to generate height map.");
	}

	float lowest = tmp[0], highest = tmp[0];
	for (size_t i = 1; i < A; ++i)
	{
		lowest = lowest < tmp[i] ? lowest : tmp[i];
		highest = highest > tmp[i] ? highest : tmp[i];
	}

	for (size_t i = 0; i < A; ++i) // Scale to [0 ... 1]
		tmp[i] = (tmp[i] - lowest) / (highest - lowest);

	float sea_threshold = 0.5;
	float th_step = 0.5;

	// Find the actual value in height map that produces the continent-sea
	// ratio defined be "sea_level".
	while (th_step > 0.01)
	{
		size_t count = 0;
		for (size_t i = 0; i < A; ++i)
			count += (tmp[i] < sea_threshold);

		th_step *= 0.5;
		if (count / (float)A < sea_level)
			sea_threshold += th_step;
		else
			sea_threshold -= th_step;
	}

	sea_level = sea_threshold;
	for (size_t i = 0; i < A; ++i) // Genesis 1:9-10.
	{
//		if (tmp[i] < sea_level)
//			tmp[i] /= sea_level;
//		else
//			tmp[i] = 1.0+(tmp[i] - sea_level) * 20;
		tmp[i] = (tmp[i] > sea_level) *
			(tmp[i] + CONTINENTAL_BASE) + 
			(tmp[i] <= sea_level) * OCEANIC_BASE;
	}

	// Scalp the +1 away from map side to get a power of two side length!
	// Practically only the redundant map edges become removed.
	--map_side;
	hmap = new float[map_side*map_side];
	for (size_t i = 0; i < map_side; ++i)
		memcpy(&hmap[i*map_side], &tmp[i*(map_side+1)],
		      map_side*sizeof(float));

	imap = new size_t[map_side*map_side];
	amap = new size_t[map_side*map_side];

	delete[] tmp;
}

lithosphere::~lithosphere() throw()
{
	delete[] plates; plates = 0;
	delete[] amap;   amap = 0;
	delete[] imap;   imap = 0;
	delete[] hmap;   hmap = 0;
}

void lithosphere::createPlates(size_t num_plates) throw()
{
	const size_t map_area = map_side * map_side;
	this->max_plates = this->num_plates = num_plates;

	std::vector<plateCollision> vec;
	vec.reserve(map_side*4); // == map's circumference.

	collisions.reserve(num_plates);
	subductions.reserve(num_plates);

	for (size_t i = 0; i < num_plates; ++i)
	{
		collisions.push_back(vec);
		subductions.push_back(vec);
	}

	// Initialize "Free plate center position" lookup table.
	// This way two plate centers will never be identical.
	for (size_t i = 0; i < map_area; ++i)
		imap[i] = i;

	// Select N plate centers from the global map.
	plateArea* area = new plateArea[num_plates];
	for (size_t i = 0; i < num_plates; ++i)
	{
		// Randomly select an unused plate origin.
		const size_t p = imap[(size_t)rand() % (map_area - i)];
		const size_t y = p / map_side;
		const size_t x = p - y * map_side;

		area[i].lft = area[i].rgt = x; // Save origin...
		area[i].top = area[i].btm = y;
		area[i].wdt = area[i].hgt = 1;

		area[i].border.reserve(8);
		area[i].border.push_back(p); // ...and mark it as border.

		// Overwrite used entry with last unused entry in array.
		imap[p] = imap[map_area - i - 1];
	}

	size_t* owner = imap; // Create an alias.
	memset(owner, 255, map_area * sizeof(size_t));

	// "Grow" plates from their origins until surface is fully populated.
	size_t max_border = 1;
	size_t i;
	while (max_border)
		for (max_border = i = 0; i < num_plates; ++i)
		{
			const size_t N = area[i].border.size();
			max_border = max_border > N ? max_border : N;

			if (N == 0)
				continue;

			const size_t j = rand() % N;
			const size_t p = area[i].border[j];
			const size_t cy = p / map_side;
			const size_t cx = p - cy * map_side;

			const size_t lft = cx > 0 ? cx - 1 : map_side - 1;
			const size_t rgt = cx < map_side - 1 ? cx + 1 : 0;
			const size_t top = cy > 0 ? cy - 1 : map_side - 1;
			const size_t btm = cy < map_side - 1 ? cy + 1 : 0;

			const size_t n = top * map_side +  cx; // North.
			const size_t s = btm * map_side +  cx; // South.
			const size_t w =  cy * map_side + lft; // West.
			const size_t e =  cy * map_side + rgt; // East.

			if (owner[n] >= num_plates)
			{
				owner[n] = i;
				area[i].border.push_back(n);

				if (area[i].top == ((top + 1) & (map_side-1)))
				{
					area[i].top = top;
					area[i].hgt++;
				}
			}

			if (owner[s] >= num_plates)
			{
				owner[s] = i;
				area[i].border.push_back(s);

				if (btm == ((area[i].btm + 1) & (map_side-1)))
				{
					area[i].btm = btm;
					area[i].hgt++;
				}
			}

			if (owner[w] >= num_plates)
			{
				owner[w] = i;
				area[i].border.push_back(w);

				if (area[i].lft == ((lft + 1) & (map_side-1)))
				{
					area[i].lft = lft;
					area[i].wdt++;
				}
			}

			if (owner[e] >= num_plates)
			{
				owner[e] = i;
				area[i].border.push_back(e);

				if (rgt == ((area[i].rgt + 1) & (map_side-1)))
				{
					area[i].rgt = rgt;
					area[i].wdt++;
				}
			}

			// Overwrite processed point with unprocessed one.
			area[i].border[j] = area[i].border.back();
			area[i].border.pop_back();
		}

	plates = new plate*[num_plates];

	// Extract and create plates from initial terrain.
	for (size_t i = 0; i < num_plates; ++i)
	{
		area[i].wdt = area[i].wdt<map_side ? area[i].wdt : map_side-1;
		area[i].hgt = area[i].hgt<map_side ? area[i].hgt : map_side-1;

		const size_t x0 = area[i].lft;
		const size_t x1 = 1 + x0 + area[i].wdt;
		const size_t y0 = area[i].top;
		const size_t y1 = 1 + y0 + area[i].hgt;
		const size_t width = x1 - x0;
		const size_t height = y1 - y0;
		float* plt = new float[width * height];

//		printf("plate %u: (%u, %u)x(%u, %u)\n", i, x0, y0, width,
//			height);

		// Copy plate's height data from global map into local map.
		for (size_t y = y0, j = 0; y < y1; ++y)
			for (size_t x = x0; x < x1; ++x, ++j)
			{
				size_t k = (y & (map_side - 1)) * map_side +
				           (x & (map_side - 1));
				plt[j] = hmap[k] * (owner[k] == i);
			}

		// Create plate.
		plates[i] = new plate(plt, width, height, x0, y0, i, map_side);
		delete[] plt;
	}

	iter_count = num_plates + MAX_BUOYANCY_AGE;
	peak_Ek = 0;
	last_coll_count = 0;
	delete[] area;
}

size_t lithosphere::getPlateCount() const throw()
{
	return num_plates;
} 

const size_t* lithosphere::getAgemap() const throw()
{
	return amap;
}

const float* lithosphere::getTopography() const throw()
{
	return hmap;
}

void lithosphere::update() throw()
{
	float totalVelocity = 0;
	float systemKineticEnergy = 0;

	for (size_t i = 0; i < num_plates; ++i)
	{
		totalVelocity += plates[i]->getVelocity();
		systemKineticEnergy += plates[i]->getMomentum();
	}

	if (systemKineticEnergy > peak_Ek)
		peak_Ek = systemKineticEnergy;

//	printf("%f > %f, ", totalVelocity, RESTART_SPEED_LIMIT);
//	printf("%f/%f = %f > %f\n", systemKineticEnergy, peak_Ek,
//		systemKineticEnergy / peak_Ek, RESTART_ENERGY_RATIO);

	// If there's no continental collisions during past iterations,
	// then interesting activity has ceased and we should restart.
	// Also if the simulation has been going on for too long already,
	// restart, because interesting stuff has most likely ended.
	if (totalVelocity < RESTART_SPEED_LIMIT ||
	    systemKineticEnergy / peak_Ek < RESTART_ENERGY_RATIO ||
	    last_coll_count > NO_COLLISION_TIME_LIMIT ||
	    iter_count > 600)
	{
		restart();
		return;
	}

	const size_t map_area = map_side * map_side;
	const size_t* prev_imap = imap;
	imap = new size_t[map_area];

	// Realize accumulated external forces to each plate.
	for (size_t i = 0; i < num_plates; ++i)
	{
		plates[i]->resetSegments();

		if (erosion_period > 0 && iter_count % erosion_period == 0)
			plates[i]->erode(CONTINENTAL_BASE);

		plates[i]->move();
	}

//	static size_t max_collisions = 0;	// DEBUG!!!
	size_t oceanic_collisions = 0;
	size_t continental_collisions = 0;

	// Update height and plate index maps.
	// Doing it plate by plate is much faster than doing it index wise:
	// Each plate's map's memory area is accessed sequentially and only
	// once as opposed to calculating "num_plates" indices within plate
	// maps in order to find out which plate(s) own current location.
	memset(hmap,   0, map_area * sizeof(float));
	memset(imap, 255, map_area * sizeof(size_t));
	for (size_t i = 0; i < num_plates; ++i)
	{
	  const size_t x0 = (size_t)plates[i]->getLeft();
	  const size_t y0 = (size_t)plates[i]->getTop();
	  const size_t x1 = x0 + plates[i]->getWidth();
	  const size_t y1 = y0 + plates[i]->getHeight();

	  const float*  this_map;
	  const size_t* this_age;
	  plates[i]->getMap(&this_map, &this_age);

	  // Copy first part of plate onto world map.
	  for (size_t y = y0, j = 0; y < y1; ++y)
	    for (size_t x = x0; x < x1; ++x, ++j)
	    {
		const size_t x_mod = x & (map_side - 1);
		const size_t y_mod = y & (map_side - 1);

		const size_t k = y_mod * map_side + x_mod;

		if (this_map[j] < 2 * FLT_EPSILON) // No crust here...
			continue;

		if (imap[k] >= num_plates) // No one here yet?
		{
			// This plate becomes the "owner" of current location
			// if it is the first plate to have crust on it.
			hmap[k] = this_map[j];
			imap[k] = i;
			amap[k] = this_age[j];

			continue;
		}

		// DO NOT ACCEPT HEIGHT EQUALITY! Equality leads to subduction
		// of shore that 's barely above sea level. It's a lot less
		// serious problem to treat very shallow waters as continent...
		const bool prev_is_oceanic = hmap[k] < CONTINENTAL_BASE;
		const bool this_is_oceanic = this_map[j] < CONTINENTAL_BASE;

		const size_t prev_timestamp = plates[imap[k]]->
			getCrustTimestamp(x_mod, y_mod);
		const size_t this_timestamp = this_age[j];
		const size_t prev_is_bouyant = (hmap[k] > this_map[j]) |
			((hmap[k] + 2 * FLT_EPSILON > this_map[j]) &
			 (hmap[k] < 2 * FLT_EPSILON + this_map[j]) &
			 (prev_timestamp >= this_timestamp));

		// Handle subduction of oceanic crust as special case.
		if (this_is_oceanic & prev_is_bouyant)
		{
			// This plate will be the subducting one.
			// The level of effect that subduction has
			// is directly related to the amount of water
			// on top of the subducting plate.
			const float sediment = SUBDUCT_RATIO * OCEANIC_BASE *
				(CONTINENTAL_BASE - this_map[j]) /
				CONTINENTAL_BASE;

			// Save collision to the receiving plate's list.
			plateCollision coll(i, x_mod, y_mod, sediment);
			subductions[imap[k]].push_back(coll);
			++oceanic_collisions;

			// Remove subducted oceanic lithosphere from plate.
			// This is crucial for
			// a) having correct amount of colliding crust (below)
			// b) protecting subducted locations from receiving
			//    crust from other subductions/collisions.
			plates[i]->setCrust(x_mod, y_mod, this_map[j] -
				OCEANIC_BASE, this_timestamp);

			if (this_map[j] <= 0)
				continue; // Nothing more to collide.
		}
		else if (prev_is_oceanic)
		{
			const float sediment = SUBDUCT_RATIO * OCEANIC_BASE *
				(CONTINENTAL_BASE - hmap[k]) /
				CONTINENTAL_BASE;

			plateCollision coll(imap[k], x_mod, y_mod, sediment);
			subductions[i].push_back(coll);
			++oceanic_collisions;

			plates[imap[k]]->setCrust(x_mod, y_mod, hmap[k] -
				OCEANIC_BASE, prev_timestamp);
			hmap[k] -= OCEANIC_BASE;

			if (hmap[k] <= 0)
			{
				imap[k] = i;
				hmap[k] = this_map[j];
				amap[k] = this_age[j];

				continue;
			}
		}

		// Record collisions to both plates. This also creates
		// continent segment at the collided location to plates.
		size_t this_area = plates[i]->addCollision(x_mod, y_mod);
		size_t prev_area = plates[imap[k]]->addCollision(x_mod, y_mod);

		// At least two plates are at same location. 
		// Move some crust from the SMALLER plate onto LARGER one.
		if (this_area < prev_area)
		{
			plateCollision coll(imap[k], x_mod, y_mod,
				this_map[j] * folding_ratio);

			// Give some...
			hmap[k] += coll.crust;
			plates[imap[k]]->setCrust(x_mod, y_mod, hmap[k],
				this_age[j]);

			// And take some.
			plates[i]->setCrust(x_mod, y_mod, this_map[j] *
				(1.0 - folding_ratio), this_age[j]);

			// Add collision to the earlier plate's list.
			collisions[i].push_back(coll);
			++continental_collisions;
		}
		else
		{
			plateCollision coll(i, x_mod, y_mod,
				hmap[k] * folding_ratio);

			plates[i]->setCrust(x_mod, y_mod,
				this_map[j]+coll.crust, amap[k]);

			plates[imap[k]]->setCrust(x_mod, y_mod, hmap[k]
				* (1.0 - folding_ratio), amap[k]);

			collisions[imap[k]].push_back(coll);
			++continental_collisions;

			// Give the location to the larger plate.
			hmap[k] = this_map[j];
			imap[k] = i;
			amap[k] = this_age[j];
		}
	    }
	}

//	size_t total_collisions = oceanic_collisions + continental_collisions;
//	if (total_collisions > max_collisions)
//		max_collisions = total_collisions;
//	printf("%5u + %5u = %5u collisions (%f %%) (max %5u (%f %%)). %c\n",
//		oceanic_collisions, continental_collisions, total_collisions,
//		(float)total_collisions / (float)(map_side * map_side),
//		max_collisions, (float)max_collisions /
//		(float)(map_side * map_side), '+' + (2 & -(iter_count & 1)));

	// Update the counter of iterations since last continental collision.
	last_coll_count = (last_coll_count + 1) &
		-(continental_collisions == 0);

	for (size_t i = 0; i < num_plates; ++i)
	{
		for (size_t j = 0; j < subductions[i].size(); ++j)
		{
			const plateCollision& coll = subductions[i][j];

			#ifdef DEBUG
			if (i == coll.index)
			{
				puts("when subducting: SRC == DEST!");
				exit(1);
			}
			#endif

			// Do not apply friction to oceanic plates.
			// This is a very cheap way to emulate slab pull.
			// Just perform subduction and on our way we go!
			plates[i]->addCrustBySubduction(
				coll.wx, coll.wy, coll.crust, iter_count,
				plates[coll.index]->getVelX(),
				plates[coll.index]->getVelY());
		}

		subductions[i].clear();
	}

	for (size_t i = 0; i < num_plates; ++i)
	{
		for (size_t j = 0; j < collisions[i].size(); ++j)
		{
			const plateCollision& coll = collisions[i][j];
			size_t coll_count, coll_count_i, coll_count_j;
			float coll_ratio, coll_ratio_i, coll_ratio_j;

			#ifdef DEBUG
			if (i == coll.index)
			{
				puts("when colliding: SRC == DEST!");
				exit(1);
			}
			#endif

			// Collision causes friction. Apply it to both plates.
			plates[i]->applyFriction(coll.crust);
			plates[coll.index]->applyFriction(coll.crust);
//			hmap[coll.wy * map_side + coll.wx] = 0;

			plates[i]->getCollisionInfo(coll.wx, coll.wy,
				&coll_count_i, &coll_ratio_i);
			plates[coll.index]->getCollisionInfo(coll.wx,
				coll.wy, &coll_count_j, &coll_ratio_j);

			// Find the minimum count of collisions between two
			// continents on different plates.
			// It's minimum because large plate will get collisions
			// from all over where as smaller plate will get just
			// a few. It's those few that matter between these two
			// plates, not what the big plate has with all the
			// other plates around it.
			coll_count = coll_count_i;
			coll_count -= (coll_count - coll_count_j) &
				-(coll_count > coll_count_j);

			// Find maximum amount of collided surface area between
			// two continents on different plates.
			// Like earlier, it's the "experience" of the smaller
			// plate that matters here.
			coll_ratio = coll_ratio_i;
			coll_ratio += (coll_ratio_j - coll_ratio) *
				(coll_ratio_j > coll_ratio);

//			printf("min(%u, %u) = %u, max(%f, %f) = %f\n",
//				coll_count_i, coll_count_j, coll_count,
//				coll_ratio_i, coll_ratio_j, coll_ratio);

			if ((coll_count > aggr_overlap_abs) |
			    (coll_ratio > aggr_overlap_rel))
			{
				float amount = plates[i]->aggregateCrust(
						plates[coll.index],
						coll.wx, coll.wy);

				// Calculate new direction and speed for the
				// merged plate system, that is, for the
				// receiving plate!
				plates[coll.index]->collide(*plates[i],
					coll.wx, coll.wy, amount);
			}
		}

		collisions[i].clear();
	  }

	size_t* indexFound = new size_t[num_plates];
	memset(indexFound, 0, sizeof(size_t)*num_plates);

	// Fill divergent boundaries with new crustal material, molten magma.
	for (size_t y = 0, i = 0; y < BOOL_REGENERATE_CRUST * map_side; ++y)
	  for (size_t x = 0; x < map_side; ++x, ++i)
		if (imap[i] >= num_plates)
		{
			// The owner of this new crust is that neighbour plate
			// who was located at this point before plates moved.
			imap[i] = prev_imap[i];

			#ifdef DEBUG
			if (imap[i] >= num_plates)
			{
				puts("Previous index map has no owner!");
				exit(1);
			}
			#endif

			// If this is oceanic crust then add buoyancy to it.
			// Magma that has just crystallized into oceanic crust
			// is more buoyant than that which has had a lot of
			// time to cool down and become more dense.
			amap[i] = iter_count;
			hmap[i] = OCEANIC_BASE * BUOYANCY_BONUS_X;

			plates[imap[i]]->setCrust(x, y, OCEANIC_BASE,
				iter_count);

			// DEBUG!
//			size_t lx = x, ly = y;
//			plates[imap[i]]->getMapIndex(&lx, &ly);
//			size_t px = (size_t) plates[imap[i]]->left + lx;
//			size_t py = (size_t) plates[imap[i]]->top + ly;
//
//			if ((py & (map_side - 1)) * map_side +
//				(px & (map_side - 1)) != i)
//			{
//				puts("Added sea floor to odd place!");
//				exit(1);
//			}
		}
		else if (++indexFound[imap[i]] && hmap[i] <= 0)
		{
			puts("Occupied point has no land mass!");
			exit(1);
		}

	// Remove empty plates from the system.
	for (size_t i = 0; i < num_plates; ++i)
		if (num_plates == 1)
			puts("ONLY ONE PLATE LEFT!");
		else if (indexFound[i] == 0)
		{
			delete plates[i];
			plates[i] = plates[num_plates - 1];
			indexFound[i] = indexFound[num_plates - 1];

			// Life is seldom as simple as seems at first.
			// Replace the moved plate's index in the index map
			// to match its current position in the array!
			for (size_t j = 0; j < map_side * map_side; ++j)
				if (imap[j] == num_plates - 1)
					imap[j] = i;

			--num_plates;
			--i;
		}

	delete[] indexFound;

	// Add some "virginity buoyancy" to all pixels for a visual boost! :)
	for (size_t i = 0; i < (BUOYANCY_BONUS_X > 0) * map_area; ++i)
	{
		// Calculate the inverted age of this piece of crust.
		// Force result to be minimum between inv. age and
		// max buoyancy bonus age.
		size_t crust_age = iter_count - amap[i];
		crust_age = MAX_BUOYANCY_AGE - crust_age;
		crust_age &= -(crust_age <= MAX_BUOYANCY_AGE);

		hmap[i] += (hmap[i] < CONTINENTAL_BASE) * BUOYANCY_BONUS_X *
		           OCEANIC_BASE * crust_age * MULINV_MAX_BUOYANCY_AGE;
	}

/*	size_t i = 0;
	const size_t x0 = (size_t)plates[i]->getLeft();
	const size_t y0 = (size_t)plates[i]->getTop();
	const size_t x1 = x0 + plates[i]->getWidth();
	const size_t y1 = y0 + plates[i]->getHeight();

	const float*  this_map;
	const size_t* this_age;
	plates[i]->getMap(&this_map, &this_age);

	// Show only plate[0]'s segments, draw everything else dark blue.
	if (iter_count < 300)
	for (size_t y = y0, j = 0; y < y1; ++y)
	  for (size_t x = x0; x < x1; ++x, ++j)
	  {
		const size_t x_mod = x & (map_side - 1);
		const size_t y_mod = y & (map_side - 1);

		const size_t k = y_mod * map_side + x_mod;

		if (this_map[j] < 2 * FLT_EPSILON) // No crust here...
		{
			hmap[k] = 4*FLT_EPSILON;
			continue;
		}

		float Q = (plates[i]->segment[j] < plates[i]->seg_data.size());
		hmap[k] = (this_map[j] * Q);
	  }*/

	delete[] prev_imap;
	++iter_count;
}

void lithosphere::restart() throw()
{
	const size_t map_area = map_side * map_side;

	cycle_count += max_cycles > 0; // No increment if running for ever.
	if (cycle_count > max_cycles)
		return;

	// Update height map to include all recent changes.
	memset(hmap, 0, map_area * sizeof(float));
	for (size_t i = 0; i < num_plates; ++i)
	{
	  const size_t x0 = (size_t)plates[i]->getLeft();
	  const size_t y0 = (size_t)plates[i]->getTop();
	  const size_t x1 = x0 + plates[i]->getWidth();
	  const size_t y1 = y0 + plates[i]->getHeight();

	  const float*  this_map;
	  const size_t* this_age;
	  plates[i]->getMap(&this_map, &this_age);

	  // Copy first part of plate onto world map.
	  for (size_t y = y0, j = 0; y < y1; ++y)
	    for (size_t x = x0; x < x1; ++x, ++j)
	    {
		const size_t x_mod = x & (map_side - 1);
		const size_t y_mod = y & (map_side - 1);
		const float h0 = hmap[y_mod * map_side + x_mod];
		const float h1 = this_map[j];
		const size_t a0 = amap[y_mod * map_side + x_mod];
		const size_t a1 =  this_age[j];

		amap[y_mod * map_side + x_mod] = (h0 *a0 +h1 *a1) /(h0 +h1);
		hmap[y_mod * map_side + x_mod] += this_map[j];
	    }
	}

	// Delete plates.
	delete[] plates;
	plates = 0;
	num_plates = 0;

	// create new plates IFF there are cycles left to run!
	// However, if max cycle count is "ETERNITY", then 0 < 0 + 1 always.
	if (cycle_count < max_cycles + !max_cycles)
	{
		createPlates(num_plates = max_plates);

		// Restore the ages of plates' points of crust!
		for (size_t i = 0; i < num_plates; ++i)
		{
		  const size_t x0 = (size_t)plates[i]->getLeft();
		  const size_t y0 = (size_t)plates[i]->getTop();
		  const size_t x1 = x0 + plates[i]->getWidth();
		  const size_t y1 = y0 + plates[i]->getHeight();
			
		  const float*  this_map;
		  const size_t* this_age_const;
		  size_t* this_age;

		  plates[i]->getMap(&this_map, &this_age_const);
		  this_age = (size_t *)this_age_const;

		  for (size_t y = y0, j = 0; y < y1; ++y)
		    for (size_t x = x0; x < x1; ++x, ++j)
		    {
			const size_t x_mod = x & (map_side - 1);
			const size_t y_mod = y & (map_side - 1);

			this_age[j] = amap[y_mod * map_side + x_mod];
		    }
		}

		return;
	}

	// Add some "virginity buoyancy" to all pixels for a visual boost.
	for (size_t i = 0; i < (BUOYANCY_BONUS_X > 0) * map_area; ++i)
	{
		size_t crust_age = iter_count - amap[i];
		crust_age = MAX_BUOYANCY_AGE - crust_age;
		crust_age &= -(crust_age <= MAX_BUOYANCY_AGE);

		hmap[i] += (hmap[i] < CONTINENTAL_BASE) * BUOYANCY_BONUS_X *
		           OCEANIC_BASE * crust_age * MULINV_MAX_BUOYANCY_AGE;
	}

	///////////////////////////////////////////////////////////////////////
	// This is the LAST cycle! ////////////////////////////////////////////
	///////////////////////////////////////////////////////////////////////

	size_t A = (map_side + 1)*(map_side + 1);
	float* tmp = new float[A];
	float* original = new float[A];

	memcpy(original, hmap, map_area * sizeof(float));

	float h_lowest = hmap[0], h_highest = hmap[0];
	for (size_t i = 1; i < map_area; ++i) // Record elevation extremes.
	{
		h_lowest = h_lowest < hmap[i] ? h_lowest : hmap[i];
		h_highest = h_highest > hmap[i] ? h_highest : hmap[i];
	}

	for (size_t y = 0; y < map_side; y += 8)
	{
		for (size_t x = 0; x < map_side; x += 8)
		{
			size_t i = y * map_side + x;
			hmap[i] = (RAND_MAX / 8) * (hmap[i] - h_lowest) /
				(h_highest - h_lowest);

			for (size_t j = i+1; j < i+8; ++j)
				hmap[j] = 0;
		}

		memset(&hmap[(y+1)*map_side], 0, map_side * sizeof(float));
		memset(&hmap[(y+2)*map_side], 0, map_side * sizeof(float));
		memset(&hmap[(y+3)*map_side], 0, map_side * sizeof(float));

		for (size_t i = 0; i < 4; ++i)
			hmap[(y+4)*map_side+i] = 
			hmap[(y+4)*map_side+map_side-i-1] = 0;

		for (size_t x = 4; x < map_side-4; x += 8)
		{
			size_t i = (y+4) * map_side + x;
			hmap[i] = (RAND_MAX / 8) * (hmap[i] - h_lowest) /
				(h_highest - h_lowest);

			for (size_t j = i+1; j < i+8; ++j)
				hmap[j] = 0;
		}

		memset(&hmap[(y+5)*map_side], 0, map_side * sizeof(float));
		memset(&hmap[(y+6)*map_side], 0, map_side * sizeof(float));
		memset(&hmap[(y+7)*map_side], 0, map_side * sizeof(float));
	}

	for (size_t y = 0; y < map_side; ++y) // Copy map into fractal buffer.
	{
		memcpy(&tmp[y*(map_side+1)], &hmap[y*map_side],
			map_side*sizeof(float));

		tmp[y*(map_side+1) + map_side] = hmap[y*map_side];
	}

	// Copy last line - the one that "wraps around" the top edge.
	memcpy(&tmp[map_side*(map_side+1)], &hmap[0],
		map_side*sizeof(float));
	tmp[map_side*(map_side+1) + map_side] = hmap[0];

	// Finally create some fractal slopes!
	if (sqrdmd(tmp, map_side + 1, SQRDMD_ROUGHNESS) < 0)
	{
		delete[] tmp;
		throw invalid_argument("Failed to fractalize heightmap.");
	}

	normalize(tmp, A);

	float h_range = h_highest - h_lowest;
	for (size_t i = 0; i < A; ++i) // Restore original height range.
		tmp[i] = h_lowest + tmp[i] * h_range;

	for (size_t y = 0; y < map_side; ++y)
		for (size_t x = 0; x < map_side; ++x)
			if (original[y*map_side+x] > CONTINENTAL_BASE)
			{
				float new_height = tmp[y*(map_side+1)+x] *
					1.0 + original[y*map_side+x] * 0.0;
				float alpha = sqrt((original[y*map_side+x] -
					CONTINENTAL_BASE) / (h_highest -
					CONTINENTAL_BASE));

				hmap[y*map_side+x] = alpha * new_height +
					(1.0f-alpha) * original[y*map_side+x];
			}
			else
				hmap[y*map_side+x] = original[y*map_side+x];

	// Add some random noise to the map.
	memset(tmp, 0, A * sizeof(float));

	if (sqrdmd(tmp, map_side + 1, SQRDMD_ROUGHNESS) < 0)
	{
		delete[] tmp;
		throw invalid_argument("Failed to generate height map again.");
	}

	normalize(tmp, A);

	// Shrink the fractal map by 1 pixel from right and bottom.
	// This makes it same size as lithosphere's height map.
	for (size_t i = 0; i < map_side; ++i)
		memmove(&tmp[i*map_side], &tmp[i*(map_side+1)],
		      map_side*sizeof(float));

	for (size_t i = 0; i < map_area; ++i)
	{
		if (hmap[i] > CONTINENTAL_BASE)
			hmap[i] += tmp[i] * 2 * 0;
//			hmap[i] = CONTINENTAL_BASE +
//				0.5 * (tmp[i] - 0.5) * CONTINENTAL_BASE +
//				0.1 * tmp[i] * (h_highest - CONTINENTAL_BASE) +
//				0.9 * (hmap[i] - CONTINENTAL_BASE);
		else
			hmap[i] = 0.8 *hmap[i] + 0.2 *tmp[i] *CONTINENTAL_BASE;
	}

	// Add a smoothing factor to sea floor.
	memcpy(original, hmap, map_area * sizeof(float));

	h_lowest = hmap[0], h_highest = hmap[0];
	for (size_t i = 1; i < map_area; ++i) // Record elevation extremes.
	{
		h_lowest = h_lowest < hmap[i] ? h_lowest : hmap[i];
		h_highest = h_highest > hmap[i] ? h_highest : hmap[i];
	}

	for (size_t y = 0; y < map_side; y += 4)
	{
		for (size_t x = 0; x < map_side; x += 4)
		{
			size_t i = y * map_side + x;
			hmap[i] = 4.0f * RAND_MAX * (hmap[i] - h_lowest) /
				(h_highest - h_lowest);

			for (size_t j = i+1; j < i+4; ++j)
				hmap[j] = 0;
		}

		memset(&hmap[(y+1)*map_side], 0, map_side * sizeof(float));

		for (size_t i = 0; i < 2; ++i)
			hmap[(y+2)*map_side+i] = 
			hmap[(y+2)*map_side+map_side-i-1] = 0;

		for (size_t x = 2; x < map_side-2; x += 4)
		{
			size_t i = (y+2) * map_side + x;
			hmap[i] = 4.0f * RAND_MAX * (hmap[i] - h_lowest) /
				(h_highest - h_lowest);

			for (size_t j = i+1; j < i+4; ++j)
				hmap[j] = 0;
		}

		memset(&hmap[(y+3)*map_side], 0, map_side * sizeof(float));
	}

	for (size_t y = 0; y < map_side; ++y) // Copy map into fractal buffer.
	{
		memcpy(&tmp[y*(map_side+1)], &hmap[y*map_side],
			map_side*sizeof(float));

		tmp[y*(map_side+1) + map_side] = hmap[y*map_side];
	}

	// Copy last line - the one that "wraps around" the top edge.
	memcpy(&tmp[map_side*(map_side+1)], &hmap[0],
		map_side*sizeof(float));
	tmp[map_side*(map_side+1) + map_side] = hmap[0];

	// Finally create some fractal slopes!
	if (sqrdmd(tmp, map_side + 1, SQRDMD_ROUGHNESS) < 0)
	{
		delete[] tmp;
		throw invalid_argument("Failed to fractalize heightmap.");
	}

	normalize(tmp, A);

	h_range = h_highest - h_lowest;
	for (size_t i = 0; i < A; ++i) // Restore original height range.
		tmp[i] = h_lowest + tmp[i] * h_range;

	for (size_t y = 0; y < map_side; ++y)
		for (size_t x = 0; x < map_side; ++x)
			if (original[y*map_side+x] < CONTINENTAL_BASE)
				hmap[y*map_side+x] = tmp[y*(map_side+1)+x];
			else
				hmap[y*map_side+x] = original[y*map_side+x];

	delete[] tmp;
}

