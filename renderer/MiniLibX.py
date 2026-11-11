"""Optional MiniLibX integration point.

The mandatory renderer is the portable terminal one.  This module only
reports whether the Linux-only MiniLibX Python bindings are available.
"""

from importlib.util import find_spec

MLX_AVAILABLE = find_spec("mlx") is not None

__all__ = ["MLX_AVAILABLE"]
