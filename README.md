[![PyPI version](https://badge.fury.io/py/neighpy.svg)](https://badge.fury.io/py/neighpy) ![Conda Version](https://img.shields.io/conda/vn/conda-forge/neighpy?color=green)
 [![test](https://github.com/auggiemarignier/neighpy/actions/workflows/tests.yaml/badge.svg)](https://github.com/auggiemarignier/neighpy/actions/workflows/tests.yaml) [![docs](https://readthedocs.org/projects/neighpy/badge/?version=latest)](https://neighpy.readthedocs.io/en/latest/?badge=latest)

> **This fork exists solely to test replacing `joblib` parallelism with a user-provided thread/process pool, inspired by how [pyTransC](https://github.com/inlab-geo/pyTransC) handles parallelism. The user passes any object with a `map(func, iterable)` method (e.g. `ThreadPoolExecutor`, `ProcessPoolExecutor`, `MPIPool`) to `run(pool=...)`, removing the `joblib` dependency entirely.**

> [!WARNING]
> **This branch is likely to not work well with [CoFI](https://github.com/inlab-geo/cofi).**

# neighpy

``neighphy`` is a Python implementation of the Neighbourhood Algorithm for the optimisation and appraisal of high-dimensional loss surfaces.
First presented in two papers by M. Sambridge at the Australian National University in 1999, it has since been widely used, particularly in the geophysical community, for the optimisation of complex, high-dimensional functions.

This implementation hopes to replace the original Fortran code with a more modern, user-friendly and flexible Python package.
It is a very simple implementation, with just two classes to implement the two phases of the algorithm: the `neighpy.search.NASearcher` class for the optimisation phase, and the `neighpy.appraise.NAAppraiser` class for the appraisal phase

## Installation

```bash
pip install neighpy
```

## Basic Usage

```python
import numpy as np
from neighpy import NASearcher, NAAppraiser

def objective(x):
    # Objective function to be minimised
    return np.linalg.norm(data - predict_data(x))

# Bounds of the parameter space
bounds = ((-5, 5), (-5, 5))

# Initialise direct search phase
searcher = NASearcher(
    objective,
    ns=100, # number of samples per iteration
    nr=10, # number of cells to resample
    ni=100, # size of initial random search
    n=20, # number of iterations
    bounds=bounds
)

# Run the direct search phase
from concurrent.futures import ProcessPoolExecutor

with ProcessPoolExecutor(max_workers=4) as pool:
    searcher.run(pool=pool) # results stored in searcher.samples and searcher.objectives

# Initialise the appraisal phase
appraiser = NAAppraiser(
    searcher.samples, # points of parameter space already sampled
    np.exp(-searcher.objectives), # objective function values (as a probability distribution)
    bounds=bounds,
    n_resample=500000, # number of desired new samples
    n_walkers=10 # number of parallel walkers
)

# Run the appraisal phase
with ProcessPoolExecutor(max_workers=4) as pool:
    appraiser.run(pool=pool)  # Results stored in appraiser.samples
```

## Forward Pool

If your objective function can parallelise its own internal work (e.g. a forward solver), you can pass a `forward_pool` to `run()`. The objective function accesses it via `get_forward_pool()`:

```python
from neighpy import NASearcher, get_forward_pool
from concurrent.futures import ProcessPoolExecutor

def objective(x):
    pool = get_forward_pool()  # None when no pool is set
    if pool is not None:
        results = list(pool.map(forward_model, chunks))
    else:
        results = [forward_model(c) for c in chunks]
    return compute_misfit(results)

searcher = NASearcher(objective, ns=100, nr=10, ni=100, n=20, bounds=bounds)

# pool parallelises Voronoi walks, forward_pool is available inside the objective
with ProcessPoolExecutor(max_workers=4) as walk_pool, \
     ProcessPoolExecutor(max_workers=2) as fwd_pool:
    searcher.run(pool=walk_pool, forward_pool=fwd_pool)
```

This follows the same pattern as [pyTransC](https://github.com/inlab-geo/pyTransC)'s forward pool context. Any object with a `map(func, iterable)` method works (`ThreadPoolExecutor`, `ProcessPoolExecutor`, `MPIPool`, etc.).

## Licence

This code is distributed under a [GNU General Public License](https://www.gnu.org/licenses/gpl-3.0.en.html).

## Contributing

If you have any questions, please to open an issue in this repository.

### Contributing from this fork

This is a fork of [auggiemarignier/neighpy](https://github.com/auggiemarignier/neighpy).

**Push your branch to the fork:**

```bash
git push -u origin feature/processpool-experiment
```

**Open a pull request to the original repo:**

```bash
gh pr create --repo auggiemarignier/neighpy
```

**Stay up to date with the original repo:**

```bash
git fetch upstream
git merge upstream/main
```
