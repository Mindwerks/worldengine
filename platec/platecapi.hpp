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

#ifndef PLATECAPI_H
#define PLATECAPI_H

#ifdef	__cplusplus
extern "C" {
#endif

void*  platec_api_create(size_t, float, size_t, float,
                          size_t, float, size_t, size_t);
void    platec_api_destroy(size_t);
const size_t* platec_api_get_agemap(size_t);
const float* platec_api_get_heightmap(void*);
size_t platec_api_get_side_length(size_t);
size_t  platec_api_is_finished(void*);
void    platec_api_step(void*);

#ifdef	__cplusplus
}
#endif

#endif
