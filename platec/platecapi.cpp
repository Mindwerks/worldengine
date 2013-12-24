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
#include "platecapi.hpp"
#include <stdlib.h>

#include <vector>

class platec_api_list_elem
{
  public:
	platec_api_list_elem(size_t _id, lithosphere* _data) :
		data(_data), id(_id) { }

	lithosphere* data;
	size_t id;
};

extern lithosphere* platec_api_get_lithosphere(size_t);

static std::vector<platec_api_list_elem> lithospheres;
static size_t last_id = 1;

#include <stdio.h>

void* platec_api_create(size_t map_side, float sea_level,
                         size_t erosion_period, float folding_ratio,
                         size_t aggr_overlap_abs, float aggr_overlap_rel,
                         size_t cycle_count, size_t num_plates)
{
	/* Miten nykyisen opengl-mainin koodit refaktoroidaan tänne?
	 *    parametrien tarkistus, kommentit eli dokumentointi, muuta? */

	lithosphere* litho = new lithosphere(map_side, sea_level,
		erosion_period, folding_ratio, aggr_overlap_abs,
		aggr_overlap_rel, cycle_count);
	litho->createPlates(num_plates);

	platec_api_list_elem elem(++last_id, litho);
	lithospheres.push_back(elem);

	litho->seed = rand();
	
	return litho;
}

void platec_api_destroy(size_t id)
{
	for (size_t i = 0; i < lithospheres.size(); ++i)
		if (lithospheres[i].id == id) {
			lithospheres.erase(lithospheres.begin()+i);
			break;
		}
}

const size_t* platec_api_get_agemap(size_t id)
{
	lithosphere* litho = platec_api_get_lithosphere(id);
	if (!litho)
		return NULL;

	return litho->getAgemap();
}

#include <stdio.h>

const float* platec_api_get_heightmap(void *pointer)
{
	lithosphere* litho = (lithosphere*)pointer;
	const float *res = litho->getTopography();
	return res;
}

size_t platec_api_get_side_length(size_t id)
{
	lithosphere* litho = platec_api_get_lithosphere(id);
	if (!litho)
		return 0;

	return litho->getSideLength();
}

lithosphere* platec_api_get_lithosphere(size_t id)
{
	for (size_t i = 0; i < lithospheres.size(); ++i)
		if (lithospheres[i].id == id)
			return lithospheres[i].data;

	return NULL;
}

size_t platec_api_is_finished(void *pointer)
{
	lithosphere* litho = (lithosphere*)pointer;

	return litho->getPlateCount() == 0;
}

void platec_api_step(void *pointer)
{	
   
	lithosphere* litho = (lithosphere*)pointer;
	srand(litho->seed);

	litho->update();
	
	litho->seed = rand();
}

