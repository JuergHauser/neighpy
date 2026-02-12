"""Forward pool context for objective function access.

Provides a process-local global variable that allows the user's objective
function to access a pool for parallelising its own internal computation
(e.g. a forward solver).  Follows the same pattern as pyTransC's
``forward_context`` module.

Usage inside a user-defined objective function::

    from neighpy import get_forward_pool

    def my_objective(x):
        pool = get_forward_pool()  # None when no pool is set
        if pool is not None:
            results = list(pool.map(forward_model, chunks))
        else:
            results = [forward_model(c) for c in chunks]
        ...
"""

_forward_pool = None


def set_forward_pool(pool):
    """Set the forward pool in the current process."""
    global _forward_pool
    if pool is not None and not hasattr(pool, "map"):
        raise ValueError("Forward pool must have a 'map' method")
    _forward_pool = pool


def get_forward_pool():
    """Get the forward pool from the current process.

    Returns ``None`` if no pool has been set.
    """
    return _forward_pool


def clear_forward_pool():
    """Clear the forward pool from the current process."""
    global _forward_pool
    _forward_pool = None
