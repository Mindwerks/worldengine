"""Vectorized simplex noise: a numpy port of the `noise` C extension.

Ported from _simplex.c / _noise.h of noise 1.2.2 by Casey Duncan (MIT), so that
existing world seeds keep producing identical worlds without a C dependency.
All arithmetic is float32 to match the C, which uses `float` throughout.
"""

import numpy

# Perlin's reference permutation, doubled so the index arithmetic never wraps.
# fmt: off
_PERM = numpy.array([
    151, 160, 137, 91, 90, 15, 131, 13, 201, 95, 96, 53, 194, 233, 7, 225, 140, 36, 103, 30, 69, 142, 8, 99, 37,
    240, 21, 10, 23, 190, 6, 148, 247, 120, 234, 75, 0, 26, 197, 62, 94, 252, 219, 203, 117, 35, 11, 32, 57,
    177, 33, 88, 237, 149, 56, 87, 174, 20, 125, 136, 171, 168, 68, 175, 74, 165, 71, 134, 139, 48, 27, 166, 77,
    146, 158, 231, 83, 111, 229, 122, 60, 211, 133, 230, 220, 105, 92, 41, 55, 46, 245, 40, 244, 102, 143, 54,
    65, 25, 63, 161, 1, 216, 80, 73, 209, 76, 132, 187, 208, 89, 18, 169, 200, 196, 135, 130, 116, 188, 159, 86,
    164, 100, 109, 198, 173, 186, 3, 64, 52, 217, 226, 250, 124, 123, 5, 202, 38, 147, 118, 126, 255, 82, 85,
    212, 207, 206, 59, 227, 47, 16, 58, 17, 182, 189, 28, 42, 223, 183, 170, 213, 119, 248, 152, 2, 44, 154,
    163, 70, 221, 153, 101, 155, 167, 43, 172, 9, 129, 22, 39, 253, 19, 98, 108, 110, 79, 113, 224, 232, 178,
    185, 112, 104, 218, 246, 97, 228, 251, 34, 242, 193, 238, 210, 144, 12, 191, 179, 162, 241, 81, 51, 145,
    235, 249, 14, 239, 107, 49, 192, 214, 31, 181, 199, 106, 157, 184, 84, 204, 176, 115, 121, 50, 45, 127, 4,
    150, 254, 138, 236, 205, 93, 222, 114, 67, 29, 24, 72, 243, 141, 128, 195, 78, 66, 215, 61, 156, 180
], dtype=numpy.int32)
# fmt: on
_PERM = numpy.concatenate([_PERM, _PERM])

# x and y components of GRAD3. noise2 indexes it modulo 12, so entries 12-15 are unused.
_GRAD_X = numpy.array([1, -1, 1, -1, 1, -1, 1, -1, 0, 0, 0, 0], dtype=numpy.float32)
_GRAD_Y = numpy.array([1, 1, -1, -1, 0, 0, 0, 0, 1, -1, 1, -1], dtype=numpy.float32)

_F2 = numpy.float32(0.3660254037844386)  # 0.5 * (sqrt(3.0) - 1.0)
_G2 = numpy.float32(0.21132486540518713)  # (3.0 - sqrt(3.0)) / 6.0
_HALF = numpy.float32(0.5)
_ONE = numpy.float32(1.0)
_TWO = numpy.float32(2.0)
_ZERO = numpy.float32(0.0)


def _noise2(x, y):
    """Single-octave 2D simplex noise, elementwise over float32 arrays."""
    s = (x + y) * _F2
    i = numpy.floor(x + s)
    j = numpy.floor(y + s)
    t = (i + j) * _G2

    # Displacements from the three simplex corners.
    x0 = x - (i - t)
    y0 = y - (j - t)
    i1 = (x0 > y0).astype(numpy.int32)
    j1 = 1 - i1  # C: j1 = x0 <= y0, exactly the complement of i1
    # Subtract as float32; mixing in the int32 arrays would promote the math to float64.
    x1 = x0 - i1.astype(numpy.float32) + _G2
    y1 = y0 - j1.astype(numpy.float32) + _G2
    x2 = x0 + _G2 * _TWO - _ONE
    y2 = y0 + _G2 * _TWO - _ONE

    ii = i.astype(numpy.int32) & 255
    jj = j.astype(numpy.int32) & 255
    g0 = _PERM[ii + _PERM[jj]] % 12
    g1 = _PERM[ii + i1 + _PERM[jj + j1]] % 12
    g2 = _PERM[ii + 1 + _PERM[jj + 1]] % 12

    n0 = _corner(x0, y0, g0)
    n1 = _corner(x1, y1, g1)
    n2 = _corner(x2, y2, g2)
    return (n0 + n1 + n2) * numpy.float32(70.0)


def _corner(x, y, g):
    """Contribution of one simplex corner, zero outside its radius of influence."""
    f = _HALF - x * x - y * y
    return numpy.where(f > _ZERO, f * f * f * f * (_GRAD_X[g] * x + _GRAD_Y[g] * y), _ZERO)


def snoise2(x, y, octaves=1, persistence=0.5, lacunarity=2.0, base=0.0):
    """Fractal 2D simplex noise over scalar or array coordinates.

    Value-for-value equivalent to noise.snoise2() for the untiled case. The
    repeatx/repeaty tiling path is not ported; nothing here uses it.
    """
    if octaves <= 0:
        raise ValueError("Expected octaves value > 0")

    x = numpy.asarray(x, dtype=numpy.float32)
    y = numpy.asarray(y, dtype=numpy.float32)
    z = numpy.float32(base)

    freq = _ONE
    amp = _ONE
    amp_max = _ONE
    total = _noise2(x + z, y + z)
    for _ in range(1, octaves):
        freq = freq * numpy.float32(lacunarity)
        amp = amp * numpy.float32(persistence)
        amp_max = amp_max + amp
        total = total + _noise2(x * freq + z, y * freq + z) * amp
    return total / amp_max
