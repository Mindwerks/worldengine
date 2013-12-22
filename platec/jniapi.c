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

#include "jniapi.h"
#include "platecapi.hpp"

#include <stdlib.h>
#include <time.h>

JNIEXPORT jint JNICALL Java_Platec_create
  (JNIEnv *env, jobject obj, jint num_plates, jint side_length,
   jfloat sea_level, jint cycle_count, jint erosion_period,
   jfloat folding_ratio, jint aggr_overlap_abs, jfloat aggr_overlap_rel)
{
	srand(time(0));

	return (jint)platec_api_create((size_t)side_length, (float)sea_level,
		(size_t)erosion_period, (float)folding_ratio,
		(size_t)aggr_overlap_abs, (float)aggr_overlap_rel,
		(size_t)cycle_count, (size_t)num_plates);
}

JNIEXPORT void JNICALL Java_Platec_step
  (JNIEnv *env, jobject obj, jint id)
{
	platec_api_step((size_t)id);
}

JNIEXPORT jboolean JNICALL Java_Platec_isFinished
  (JNIEnv *env, jobject obj, jint id)
{
	return platec_api_is_finished((size_t)id) ? JNI_TRUE : JNI_FALSE;
}

JNIEXPORT jfloatArray JNICALL Java_Platec_getAgemap
  (JNIEnv *env, jobject obj, jint id)
{
	const size_t* map = platec_api_get_agemap((size_t)id);
	size_t side = platec_api_get_side_length((size_t)id);;
	size_t size = side * side;
	size_t i;

	jfloatArray result;
	result = (*env).NewFloatArray(size);
	if (result == NULL)
		return NULL; /* out of memory error thrown */

	size_t min_age = map[0];
	size_t max_age = map[0];
	for (i = 1; i < size; i++)
		if (map[i] < min_age)
			min_age = map[i];
		else if (map[i] > max_age)
			max_age = map[i];
	max_age -= min_age;

	jfloat* temp = (jfloat*)malloc(size * sizeof(jfloat));
	for (i = 0; i < size; i++)
		temp[i] = (map[i] - min_age) / (float)max_age;

	(*env).SetFloatArrayRegion(result, 0, size, temp);
	free(temp);

	return result;
}

JNIEXPORT jfloatArray JNICALL Java_Platec_getHeightmap
  (JNIEnv *env, jobject obj, jint id)
{
	const float* map = platec_api_get_heightmap((size_t)id);
	size_t side = platec_api_get_side_length((size_t)id);;
	size_t size = side * side;
	size_t i;

	jfloatArray result;
	result = (*env).NewFloatArray(size);
	if (result == NULL)
		return NULL; /* out of memory error thrown */

	jfloat* temp = (jfloat*)malloc(size * sizeof(jfloat));
	for (i = 0; i < size; i++)
		temp[i] = map[i];

	(*env).SetFloatArrayRegion(result, 0, size, temp);
	free(temp);

	return result;
}

JNIEXPORT void JNICALL Java_Platec_destroy
  (JNIEnv *env, jobject obj, jint id)
{
	platec_api_destroy((size_t)id);
}

