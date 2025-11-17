# WorldEngine Development Guide

## Project Overview

WorldEngine is a procedural world generator that simulates realistic terrain through plate tectonics, erosion, climate systems, and biomes. It generates both world data files (protobuf/hdf5) and visualization images (PNG). The project emphasizes scientific simulation over gaming shortcuts.

## Architecture

### Core Data Flow (Pipeline Pattern)

World generation follows a strict sequential pipeline in `worldengine/generation.py`:

1. **Plates** (`plates.py` + PyPlatec C extension) → generates elevation and plate boundaries
2. **Temperature** → based on latitude and elevation
3. **Precipitation** → considering rain shadow effects and ocean proximity
4. **Erosion** → modifies elevation based on water flow
5. **Hydrology** → watermap and river systems via recursive droplet simulation
6. **Humidity** → combines precipitation, irrigation, and distance to water
7. **Permeability** → soil absorption rates
8. **Biome** → Holdridge life zones model classification
9. **Icecap** → polar ice coverage

Each simulation in `worldengine/simulations/` is a class with `is_applicable()` and `execute(world, seed)` methods. Simulations modify the World object's layers in-place.

### World Model (`worldengine/model/world.py`)

The `World` class is the central data structure:
- **Layers** stored as numpy arrays in `world.layers['name']` dict (elevation, ocean, precipitation, temperature, humidity, biome, etc.)
- **LayerWithThresholds** for categorical data (e.g., elevation thresholds: sea/plain/hill/mountain)
- **LayerWithQuantiles** for distribution-based data (e.g., humidity quantiles)
- **Generation metadata**: seed, n_plates, ocean_level, step, temps/humids thresholds

Access patterns:
- Direct: `world.layers['elevation'].data[y, x]` (numpy array indexing)
- Helper: `world.elevation_at((x, y))` (tuple coordinates)
- Boolean checks: `world.is_ocean((x, y))`, `world.has_biome()`

### Step System (`worldengine/step.py`)

Controls generation depth via `Step` enum:
- `plates`: Only plate simulation
- `precipitations`: Through precipitation/temperature
- `full`: Complete pipeline including biomes

Check flags: `step.include_precipitations`, `step.include_erosion`, `step.include_biome`

### Biomes (`worldengine/biome.py`)

Metaclass-based registry pattern:
- Each biome is a class inheriting from `Biome` (e.g., `class TropicalRainForest(Biome)`)
- Auto-registration via `_BiomeMetaclass` converts CamelCase to "tropical rain forest"
- Access: `Biome.by_name("boreal forest")`, `Biome.all_names()`
- Stored as strings in world.layers['biome'], converted to indices for protobuf serialization

## Key Development Patterns

### NumPy-First Operations

Always prefer vectorized NumPy operations over Python loops:

```python
# Good: Vectorized ocean detection
ocean = numpy.zeros(elevation.shape, dtype=bool)

# Avoid: Cell-by-cell iteration unless simulating physical processes
for y in range(height):
    for x in range(width):  # Only when simulating droplets, adjacency, etc.
```

### Seed Management

Deterministic generation requires careful seed handling:
- Main seed → numpy RNG → 100 sub-seeds (one per simulation)
- See `seed_dict` in `generate_world()` for allocation
- Never use global random state in simulations

### Coordinate Systems

Two conventions coexist:
- **Tuple style**: `(x, y)` for method parameters (e.g., `world.elevation_at((x, y))`)
- **NumPy style**: `[y, x]` for array indexing (e.g., `world.layers['elevation'].data[y, x]`)

### Serialization

Two formats supported:
- **Protobuf** (default): `World.proto` → `World_pb2.py` (regenerate with `protoc`)
- **HDF5**: `worldengine/hdf5_serialization.py` (requires h5py, optional dependency)

Loading worlds: `world = World.from_pickle_file(filename)` or `load_world_from_hdf5()`

## Testing

### Running Tests

```bash
# All tests
nosetests tests -v

# Specific test module
nosetests tests/biome_test.py -v

# With coverage
coverage run --source worldengine --branch $(which nosetests) tests -v
coverage report --omit=worldengine/tests/* --show-missing
```

### Test Structure

- Tests in `tests/*_test.py` use unittest framework
- `TestBase` in `tests/draw_test.py` provides common fixtures
- Visual regression via `tests/blessed_images/` (compare generated images)
- No mocking of NumPy/PyPlatec; tests use actual generation

## CLI Entry Point

`worldengine/cli/main.py` provides commands:
- `worldengine world -s SEED -n NAME` → generate world
- `worldengine ancient_map -w FILE` → render ancient-style map
- `worldengine info -w FILE` → display world metadata

All CLI commands route through functions that call `world_gen()` or draw operations.

## Critical Dependencies

- **PyPlatec**: C extension for plate tectonics (fails gracefully if unavailable)
- **NumPy**: All data is numpy arrays; version pinned for reproducibility
- **protobuf 3.0.0a3**: Exact version required for compatibility
- **pypng**: Image output (not PIL/Pillow)
- **noise**: Perlin/Simplex noise (package `noise`, function `snoise2`)

## Common Pitfalls

1. **Don't modify world.layers['X'].data shape** - all layers must stay (height, width)
2. **Ocean detection**: Use `world.is_ocean()` not `elevation <= sea_level` (accounts for threshold)
3. **Verbose output**: Check `get_verbose()` before expensive debug operations
4. **Border effects**: `place_oceans_at_map_borders()` intentionally lowers edges
5. **Anti-aliasing**: Applied to some layers (watermap) via `anti_alias()` to smooth artifacts
