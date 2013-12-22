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

#include "sqrdmd.h"

#include <GL/glut.h>

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>

#define IMAGE_COLS	4
#define IMAGE_ROWS	IMAGE_COLS
#define IMAGE_SIZE	129
#define WINDOW_SIZE	(IMAGE_SIZE * IMAGE_COLS)

float* map;

void display(void)
{
	glClearColor(0,0,0,0);
	glClear(GL_COLOR_BUFFER_BIT);

	glBegin(GL_POINTS);
	{
		float* ptr = map;
		for (size_t y = 0; y < WINDOW_SIZE; ++y)
			for (size_t x = 0; x < WINDOW_SIZE; ++x)
			{
				if (*ptr < 0.0)
					glColor3f(1.0, 0.0, 0.0);
				else if (*ptr < 0.5)
					glColor3f(*ptr, *ptr, *ptr / 0.5);
				else
					glColor3f(*ptr, *ptr, *ptr);

				glVertex3f((0.5 + 2 * x) / (float)WINDOW_SIZE -
				           1.0, 1.0 - (0.5 + 2 * y) /
				           (float)WINDOW_SIZE, 0);
				++ptr;
			}
	} glEnd();

	glutSwapBuffers();
}

void keyboard(unsigned char key, int x, int y)
{
	switch (key)
	{
		case 27: exit(0); break;
		default: break;
	}
}

void reshape(int w, int h)
{
}

void update(int value)
{
	glutPostRedisplay();
}

int main(int argc, char **argv)
{
	srand(time(0));

	const size_t map_area = WINDOW_SIZE * WINDOW_SIZE;
	const size_t img_area = IMAGE_SIZE * IMAGE_SIZE;
	float* img = new float[img_area];
	float* tmp = new float[img_area];
	       map = new float[map_area];
	float minmin = 1 << 30;
	float maxmax = -minmin;
	float alpha = 0.6;

	memset(img, 0, img_area*sizeof(float));

	for (size_t y = 0; y < IMAGE_ROWS; ++y)
		for (size_t x = 0; x < IMAGE_COLS; ++x)
		{
			// Generate terrain where it is missing.
			sqrdmd(img, IMAGE_SIZE, alpha);
			alpha *= 0.92;

			// Find min and max heights of map.
			float min = img[0];
			float max = img[0];
			for (size_t i = 1; i < img_area; ++i)
			{
				min = (img[i] < min ? img[i] : min);
				max = (img[i] > max ? img[i] : max);
			}

			if (min < minmin) minmin = min;
			if (max > maxmax) maxmax = max;
			
			printf("min: %f, max: %f\n", min, max);

			// Scale map heights to [0, 1].
			for (size_t i = 0; i < img_area; ++i)
				img[i] = (img[i] - minmin) / (maxmax - minmin);

			// Find area of most coastline. Use step 2 for speed.
			size_t cx = 0;
			size_t cy = 0;
			size_t max_count = 0;
			for (size_t dy = 0; dy < IMAGE_SIZE/2; dy += 2)
			  for (size_t dx = 0; dx < IMAGE_SIZE/2; dx += 2)
			  {
			    size_t count = 0;

			    for (size_t j = 0; j < IMAGE_SIZE / 2; ++j)
			      for (size_t i = 0; i < IMAGE_SIZE / 2; ++i)
			      {
					// No overflow because value of
					// IMAGE_SIZE is odd.
					float c = img[(dy+j)*IMAGE_SIZE+dx+i];
					float r = img[(dy+j)*IMAGE_SIZE+dx+i+1];
					float b = img[(dy+j+1)*IMAGE_SIZE+dx+i];
					count += (c < 0.5 && r > 0.5) ||
					         (c > 0.5 && r < 0.5) ||
					         (c < 0.5 && b > 0.5) ||
					         (c > 0.5 && b < 0.5);
			      }

			    if (count > max_count)
			    {
			      max_count = count;
			      cx = dx;
			      cy = dy;
			    }
			  }
/*
			float land_min =  1 << 30;
			float land_max = -land_min;
			float sea_min =  land_min;
			float sea_max = -land_min;
			for (size_t y0 = 0; y0 < IMAGE_SIZE / 2; ++y0)
			  for (size_t x0 = 0; x0 < IMAGE_SIZE / 2; ++x0)
			  {
				float v = img[(cy + y0) * IMAGE_SIZE + cx+x0];
				if (v < 0.5)
				{
					sea_min = (v < sea_min ? v : sea_min);
					sea_max = (v > sea_max ? v : sea_max);
				}
				else
				{
					land_min = (v<land_min ? v : land_min);
					land_max = (v>land_max ? v : land_max);
				}
			  }

			for (size_t y0 = 0; y0 < IMAGE_SIZE / 2; ++y0)
			  for (size_t x0 = 0; x0 < IMAGE_SIZE / 2; ++x0)
			  {
				size_t index = (cy + y0) * IMAGE_SIZE +cx+x0;
				if (img[index] < 0.5)
					img[index] = ((img[index] - sea_min) /
						(sea_max - sea_min)) * 0.5;
				else
					img[index] = 0.5 + 0.5 *
						((img[index] - land_min) /
						(land_max - land_min));
			  }
*/
			// Copy map data to destination set.
			const size_t y0 = y * IMAGE_SIZE;
			const size_t x0 = x * IMAGE_SIZE;
			for (size_t j = 0; j < IMAGE_SIZE; ++j)
				for (size_t i = 0; i < IMAGE_SIZE; ++i)
					map[(y0+j)*WINDOW_SIZE+x0+i] =
						img[j*IMAGE_SIZE + i];

			// Draw zoom box onto map.
			cy += y0;
			cx += x0;
			for (size_t i = 0; i < IMAGE_SIZE / 2; ++i)
			{
				map[cy * WINDOW_SIZE + cx + i] = -1.0;
				map[(cy + IMAGE_SIZE / 2) * WINDOW_SIZE +
				                      cx + i] = -1.0;
				map[(cy + i) * WINDOW_SIZE + cx] = -1.0;
				map[(cy + i) * WINDOW_SIZE + cx +
				                IMAGE_SIZE / 2] = -1.0;
			}

			cx -= x0;
			cy -= y0;
			memcpy(tmp, img, img_area*sizeof(float));
			memset(img, 0, img_area*sizeof(float));

			// Copy zoomed area onto entire image.
			// Leave every 2nd pixel empty.
			for (size_t j = 0; j < IMAGE_SIZE / 2; ++j)
			  for (size_t i = 0; i < IMAGE_SIZE / 2; ++i)
			  {
			    size_t index = 2 * j * IMAGE_SIZE + 2 * i;
			    img[index] = tmp[(cy + j) * IMAGE_SIZE + cx + i];

			    // Restore original scale.
			    img[index] = minmin + img[index] * (maxmax-minmin);
			  }

			// TODO: Fill borders with copied values' averages.
		}

	delete[] img;
	glutInit(&argc, argv);

	glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGBA);  
	glutInitWindowPosition(0,0);
	glutInitWindowSize(WINDOW_SIZE, WINDOW_SIZE);
	glutCreateWindow("Square-diamond algorithm landscape zoom");
	glutDisplayFunc(display);
	glutReshapeFunc(reshape);
	glutKeyboardFunc(keyboard);

	glutTimerFunc(1000, update, 0);
	glutMainLoop(); // Blocks until window is closed.

	delete[] map;
	return 0;
}

