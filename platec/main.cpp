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

#include <GL/glut.h>

#include <cfloat>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <ctime>
#include <fstream> // For heightmap dumping.

#include <unistd.h> // AUTOMATION!
#include <sys/types.h> // AUTOMATION!

#define COLOR_STEP	1.5f
#define HEIGHT_TOP	(6.0f * COLOR_STEP)

#define MAX_MAP_SIDE	4096
#define MIN_MAP_SIDE	64
#define DEFAULT_MAP_SIDE 512

#define MAX_PLATES	1024
#define MIN_PLATES	2
#define DEFAULT_NUM_PLATES 10

#if 0
#define DEFAULT_AGGR_OVERLAP_ABS	5000
#define DEFAULT_AGGR_OVERLAP_REL	0.10f
#define DEFAULT_CYCLE_COUNT		2
#define DEFAULT_EROSION_PERIOD		60
#define DEFAULT_FOLDING_RATIO		0.001f
#define DEFAULT_SEA_LEVEL		0.65f
#else
#define DEFAULT_AGGR_OVERLAP_ABS	1000000
#define DEFAULT_AGGR_OVERLAP_REL	0.33f
#define DEFAULT_CYCLE_COUNT		2
#define DEFAULT_EROSION_PERIOD		60
#define DEFAULT_FOLDING_RATIO		0.02f
#define DEFAULT_SEA_LEVEL		0.65f
#endif

#define DRAW_MODE_HEIGHT	0
#define DRAW_MODE_AGE		1
#define DRAW_MODE_COUNT		2

extern lithosphere* platec_api_get_lithosphere(size_t);

static void render_heightmap(void);
static void render_agemap(void);

static size_t world_id;
static size_t num_plates = DEFAULT_NUM_PLATES;
static size_t map_side = DEFAULT_MAP_SIDE;
static size_t aggr_overlap_abs = DEFAULT_AGGR_OVERLAP_ABS;
static float  aggr_overlap_rel = DEFAULT_AGGR_OVERLAP_REL;
static size_t cycle_count = DEFAULT_CYCLE_COUNT;
static size_t erosion_period = DEFAULT_EROSION_PERIOD;
static float  folding_ratio = DEFAULT_FOLDING_RATIO;
static float sea_level = DEFAULT_SEA_LEVEL;
static size_t dump_topography = 0;
static size_t draw_mode = DRAW_MODE_HEIGHT;

void display(void)
{
	glClearColor(0,0,0,0);
	glClear(GL_COLOR_BUFFER_BIT);

	glBegin(GL_POINTS);
	switch (draw_mode)
	{
		case DRAW_MODE_HEIGHT: render_heightmap(); break;
		case DRAW_MODE_AGE: render_agemap(); break;
		default: break;
	}

	glEnd();
	glutSwapBuffers();

	if (dump_topography) {
		const float* map = platec_api_get_heightmap(world_id);
		std::ofstream out;
		char filename[64];

		sprintf(filename, "platec_%d.dump", rand());
		out.open(filename, std::ios::out | std::ios::binary);
		out.write((const char *)map, map_side*map_side*sizeof(float));
		out.close();

		printf("Heightmap dumped into %s\n", filename);
		dump_topography = 0;
	}
}

void keyboard(unsigned char key, int x, int y)
{
	switch (key)
	{
		case  9 /* TAB */     :
			draw_mode = (draw_mode + 1) % DRAW_MODE_COUNT;
			break;
		case 27 /* ESC */     : exit(0); break;
		case 32 /* SPACEBAR */: dump_topography = 1; break; 
		default: printf("key pressed (%u)\n", key); break;
	}
}

void reshape(int w, int h)
{
}

void update(int value)
{
	if (platec_api_is_finished(world_id))
	{
		return;

		/* const char* -> char* hack just to silence gcc warning. */
		char* params[] = { (char*)"%Y-%m-%d-%s.png", NULL };

		if (!fork())
		{

			execv("/usr/bin/scrot", params);
			puts("Execve failed!");
		}

		sleep(1);
		exit(0);
	}

	platec_api_step(world_id);
	const lithosphere* world = platec_api_get_lithosphere(world_id);

	char bf[64];
	sprintf(bf, "@%u/%u, #%u/%u, -f %1.3f, -a %u, -r %1.3f",
		world->getIterationCount(),
		world->getCycleCount(), world->getPlateCount(), num_plates,
		folding_ratio, aggr_overlap_abs, aggr_overlap_rel);

	glutSetWindowTitle(bf);
	glutPostRedisplay();

	glutTimerFunc(0*40, update, 0);
}

int main(int argc, char **argv)
{
	const char* a_arg = 0;
	const char* c_arg = 0;
	const char* e_arg = 0;
	const char* f_arg = 0;
	const char* l_arg = 0;
	const char* n_arg = 0;
	const char* r_arg = 0;
	const char* s_arg = 0;
	bool show_help = false;

	while (1)
	{
		// Initial : supresses warnings from getopt.
		// Each trailing : means there's an argument coming up.
		int opt = getopt(argc, argv, ":a:c:e:f:l:n:r:s:");

		if (opt == -1) // If we're done...
			break;

		switch (opt)
		{
			case 'a': a_arg = optarg; break;
			case 'c': c_arg = optarg; break;
			case 'e': e_arg = optarg; break;
			case 'f': f_arg = optarg; break;
			case 'h': show_help = true; break;
			case 'l': l_arg = optarg; break;
			case 'n': n_arg = optarg; break;
			case 'r': r_arg = optarg; break;
			case 's': s_arg = optarg; break;
			default: show_help = true; break;
		}
	}

	if (show_help)
	{
		printf("Usage: %s\n"
		       "\t[-a Number of overlapping pixels that causes "
				"continents to merge]\n"
		       "\t[-c Number of times plate system will be restarted]\n"
		       "\t[-e Number of iterations between successive runs "
				"of erosion algorithm]\n"
		       "\t[-f Percent of crust that will be folded during "
				"overlap]\n"
		       "\t[-h Show this help]\n"
		       "\t[-l Length of world map's side in pixels]\n"
		       "\t[-n Number of plates]\n"
		       "\t[-r Percent of the smaller continent's surface "
				"area that when\n"
				"\t\toverlapping leads to merging "
				"of the two continents]\n"
		       "\t[-s Percent of map area that's initially sea]\n",
			argv[0]);

		return 1;
	}

	#define CHECK_RANGE(_ARG, _DEST, _TYPE, _FORMAT, _C, _MIN, _MAX, \
	                    _DEFAULT) \
	do { \
		if (_ARG) \
		{ \
			_TYPE val; \
			if (sscanf(_ARG, _FORMAT, &val) != 1) \
				printf("Error while parsing argument of " \
					"%c: %s\n", _C, _ARG); \
			else \
			{ \
				if (val > _MAX) \
					printf("Value of %c is too large: " \
					    "setting it to " _FORMAT ".\n", \
					    _C, val = _MAX); \
				else if (val < _MIN) \
					printf("Value of %c is too small: " \
					    "setting it to " _FORMAT ".\n", \
					    _C, val = _MIN); \
				_DEST = val; \
			} \
		} \
	} while (0)

	CHECK_RANGE(l_arg, map_side, size_t, "%u", 'l', MIN_MAP_SIDE,
		MAX_MAP_SIDE, DEFAULT_MAP_SIDE);

	if (map_side & (map_side - 1))
		printf("Length of map's side must be a power "
		       "of two! Using default value %d.\n",
		       map_side = DEFAULT_MAP_SIDE);

	CHECK_RANGE(n_arg, num_plates, size_t, "%u", 'n', MIN_PLATES,
		MAX_PLATES, DEFAULT_NUM_PLATES);

	CHECK_RANGE(a_arg, aggr_overlap_abs, size_t, "%u", 'a', 0,
		MAX_MAP_SIDE * MAX_MAP_SIDE, DEFAULT_AGGR_OVERLAP_ABS);
	CHECK_RANGE(c_arg, cycle_count, size_t, "%u", 'c', 0,
		(size_t)(-1), DEFAULT_CYCLE_COUNT);
	CHECK_RANGE(e_arg, erosion_period, size_t, "%u", 'e', 0,
		(size_t)(-1), DEFAULT_EROSION_PERIOD);
	CHECK_RANGE(f_arg, folding_ratio, float, "%f", 'f', 0.0f,
		1.0f, DEFAULT_AGGR_OVERLAP_REL);
	CHECK_RANGE(r_arg, aggr_overlap_rel, float, "%f", 'r', 0.0f,
		1.0f, DEFAULT_FOLDING_RATIO);
	CHECK_RANGE(s_arg, sea_level, float, "%f", 's', 0.0f,
		CONTINENTAL_BASE, DEFAULT_SEA_LEVEL);

	printf("map:\t\t%u\nsea:\t\t%f\nplates:\t\t%u\nerosion period:\t%u\n"
	       "folding:\t%f\noverlap abs:\t%u\noverlap rel:\t%f\n"
	       "cycles:\t\t%u\n", map_side, sea_level, num_plates,
	       erosion_period, folding_ratio, aggr_overlap_abs,
	       aggr_overlap_rel, cycle_count);

	srand(time(0));

	world_id = platec_api_create(map_side, sea_level, erosion_period,
		folding_ratio, aggr_overlap_abs, aggr_overlap_rel, cycle_count,
		num_plates);

	glutInit(&argc, argv);

	glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA);  
	glutInitWindowPosition(0,0);
	glutInitWindowSize(map_side, map_side);
	glutCreateWindow("Plate Tectonics Demo");
	glutDisplayFunc(display);
	glutReshapeFunc(reshape);
	glutKeyboardFunc(keyboard);

	glutTimerFunc(1000, update, 0);
	glutMainLoop(); // Blocks until window is closed.

	platec_api_destroy(world_id);
	return 0;
}

static void render_agemap(void)
{
	const size_t* imap = platec_api_get_agemap(world_id);
	float* map = new float[map_side*map_side];
	const float* ptr = map;
	size_t min = (size_t)(-1);
	size_t max = 0;

	for (size_t i = 0; i < map_side*map_side; ++i)
		if (imap[i] < min)
			min = imap[i];
		else if (imap[i] > max)
			max = imap[i];

	for (size_t i = 0; i < map_side*map_side; ++i)
		map[i] = (imap[i] - min) / (float)(max - min);

	for (size_t y = 0; y < map_side; ++y)
		for (size_t x = 0; x < map_side; ++x)
		{
			float c = *ptr;

			glColor3f(c, c, c);
			glVertex3f((0.5 + 2 * x) / (float)map_side-1.0,
			           1.0-(0.5 + 2 * y) / (float)map_side,
			           0);
			++ptr;
		}

	delete[] map;
}

static void render_heightmap(void)
{
	const float* map = platec_api_get_heightmap(world_id);
	const float* ptr = map;

	for (size_t y = 0; y < map_side; ++y)
		for (size_t x = 0; x < map_side; ++x)
		{
			float c = *ptr;

			#if 0
			// Topographic color map:
			// 0.0:   0,   0,   0
			// 0.5:   0,   0, 255
			// 1.0:   0, 255, 255
			//
			// 0.0:   0, 255,   0
			// 1.0: 255, 255,   0
			// 2.5: 255, 128,   0
			// 3.0: 255,   0,   0
			// 4.0: 128,   0,   0
			// 5.0: 128,   0, 128 // Astral level 1
			// 6.0:   0,   0,   0 // Astral level 2

			if (c < 0.5)
				glColor3f(0, 0, 2 * c);
			else if (c < 1.0)
				glColor3f(0, 2 * (c - 0.5), 1.0);
			else
			{
			  c -= 1.0;
			  if (c < 1.0 * COLOR_STEP)
				glColor3f(c / COLOR_STEP,
					1.0, 0);
			  else if (c < 2.5 * COLOR_STEP)
				glColor3f(1.0, 1.0 - 0.5 *
					(c - 1.0 * COLOR_STEP) /
					(1.5 * COLOR_STEP), 0);
			  else if (c < 3.0 * COLOR_STEP)
				glColor3f(1.0, 0.5 -
					(c - 2.5 * COLOR_STEP) /
					COLOR_STEP, 0);
			  else if (c < 4.0 * COLOR_STEP)
				glColor3f(1.0 - 0.5 * (c - 3.0 *
					COLOR_STEP) / COLOR_STEP,
					0, 0);
			  else if (c < 5.0 * COLOR_STEP)
				glColor3f(0.5, 0, 0.5 * (c - 4.0 *
					COLOR_STEP) / COLOR_STEP);
			  else if (c < 6.0 * COLOR_STEP)
				glColor3f(0.5 - 0.5 * (c - 5.0 *
					COLOR_STEP) / COLOR_STEP,
					0, 0.5 - 0.5 * (c - 5.0 *
					COLOR_STEP) / COLOR_STEP);
			  else
				glColor3f(0,0,0);
			}
			#else
			// Satellite color map:
			// 0.0:   0,   0,  64
			// 0.5:   0,   0, 255
			// 1.0:   0, 255, 255
			//
			// 0.0:   0, 128,   0
			// 1.0:   0, 255,   0
			// 1.5: 255, 255,   0
			// 2.0: 255, 128,   0
			// 3.0  128,  64,   0
			// 5.0:  96,  96,  96
			// 8.0: 255, 255, 255 // Snow capped mountains

			if (c < 0.5)
				glColor3f(0.0, 0.0, 0.25 + 1.5 * c);
			else if (c < 1.0)
				glColor3f(0.0, 2 * (c - 0.5), 1.0);
			else
			{
			  c -= 1.0;
			  if (c < 1.0 * COLOR_STEP)
				glColor3f(0.0, 0.5 +
					0.5 * c / COLOR_STEP, 0.0);
			  else if (c < 1.5 * COLOR_STEP)
				glColor3f(2 * (c - 1.0 * COLOR_STEP) /
					COLOR_STEP, 1.0, 0.0);
			  else if (c < 2.0 * COLOR_STEP)
				glColor3f(1.0, 1.0 -
					(c - 1.5 * COLOR_STEP) /
					COLOR_STEP, 0);
			  else if (c < 3.0 * COLOR_STEP)
				glColor3f(1.0 - 0.5 * (c - 2.0 *
					COLOR_STEP) / COLOR_STEP,
					0.5 - 0.25 * (c - 2.0 *
					COLOR_STEP) / COLOR_STEP, 0);
			  else if (c < 5.0 * COLOR_STEP)
				glColor3f(0.5 - 0.125 * (c - 3.0 *
					COLOR_STEP) / (2*COLOR_STEP),
					0.25 + 0.125 * (c - 3.0 *
					COLOR_STEP) / (2*COLOR_STEP),
					0.375 * (c - 3.0 *
					COLOR_STEP) / (2*COLOR_STEP));
			  else if (c < 8.0 * COLOR_STEP)
				glColor3f(0.375 + 0.625 * (c - 5.0 *
					COLOR_STEP) / (3*COLOR_STEP),
					0.375 + 0.625 * (c - 5.0 *
					COLOR_STEP) / (3*COLOR_STEP),
					0.375 + 0.625 * (c - 5.0 *
					COLOR_STEP) / (3*COLOR_STEP));
			  else
			  {
				c -= 8.0 * COLOR_STEP;
				while (c > 2.0 * COLOR_STEP)
					c -= 2.0 * COLOR_STEP;

				glColor3f(1, 1 - c / 4.0, 1);
			  }
			}
			#endif

			if (c < 2*FLT_EPSILON) // FOR DEBUGGING!
				glColor3f(1.0,0,0);

			glVertex3f((0.5 + 2 * x) / (float)map_side-1.0,
			           1.0-(0.5 + 2 * y) / (float)map_side,
			           0);
			++ptr;
		}
}


