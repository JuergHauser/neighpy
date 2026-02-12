# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

neighpy is a Python implementation of the Neighbourhood Algorithm (Sambridge 1999), a two-phase method for global optimization and uncertainty quantification. It has two main classes: `NASearcher` (direct search/optimization) and `NAAppraiser` (posterior sampling via random walks through Voronoi cells).

## Build & Development

Uses Poetry for dependency management with `poetry-dynamic-versioning` for git-tag-based versioning.

```bash
poetry install                    # Install with dev dependencies
poetry install --with examples    # Include example notebook dependencies
poetry install --with docs        # Include documentation dependencies
```

## Testing

Tests use pytest. Some tests are stochastic (uses pytest-rerunfailures for flaky retries). Tests use scipy and shapely for geometric validation of Voronoi walks.

```bash
poetry run pytest tests/                        # Run all tests
poetry run pytest tests/test_search.py -v       # Run a single test file
poetry run pytest tests/test_search.py::test_name -v  # Run a single test
poetry run pytest tests/ --cov=neighpy          # With coverage
```

## Linting / Formatting

Black formatter enforced via pre-commit hooks:

```bash
pre-commit run --all-files    # Run formatter
pre-commit install            # Install as git hook
```

## Architecture

The package is small (3 modules) with a linear pipeline:

- **`search.py`** — `NASearcher`: Direct search phase. Optimizes an objective function by iteratively resampling within Voronoi cells of the best models. Uses joblib for parallel objective evaluations. Key parameters: `ns` (samples/iteration), `nr` (resample cells), `ni` (initial samples), `n` (iterations).

- **`appraise.py`** — `NAAppraiser`: Appraisal phase. Takes search results and performs Metropolis-Hastings random walks through the Voronoi tessellation to sample the posterior distribution. Computes mean, covariance, and their statistical errors. Supports parallel walkers.

- **`_mcintegrals.py`** — `MCIntegrals`: Internal helper for one-pass accumulation of Monte Carlo integrals (mean, covariance, error estimates) without storing all samples.

The workflow is: `NASearcher.run()` → feed `samples` and `objectives` into `NAAppraiser` → `NAAppraiser.run()` → access `mean`, `covariance`.

## CI

GitHub Actions runs pytest on {ubuntu, macOS} × {Python 3.10, 3.11}. Publishing to PyPI is triggered by version tags (`v*.*.*`).
