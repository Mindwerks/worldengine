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

/** @file sqrdmd.h
 *
 *  @author Lauri Viitanen
 *  @date 2011-08-09
 */
#ifndef SQRDMD_H
#define SQRDMD_H

#ifdef	__cplusplus
extern "C" {
#endif

/**
 * @brief Scales the values of the map between [0, 1[.
 *
 *  @param	map Array containing height data.
 *  @param	size Number of elements in the map.
 */
extern void normalize(float* map, int size);

/**
 *  @brief Generates a two dimensional fractal height map.
 *
 *  Function calculates fractal values into given array with square-diamond
 *  algorithm. Values other than zero in target array are left unmodified.
 *  The gradient between each element of smoothness of map can be controlled
 *  with 'rgh' parameter so that value 0.0f produces completely flat/smooth
 *  map and value 1.0f produces completely random (noise) map.
 *
 *  @param	map Destination array to store the results.
 *  @param	size Length of map's side: 2^x + 1, x = 1, 2, 3 ...
 *  @param	rgh Amount of roughness/randomness in the final map.
 *  @return	Returns zero on success.
 */
extern int sqrdmd(float* map, int size, float rgh);

#ifdef	__cplusplus
}
#endif

#endif
