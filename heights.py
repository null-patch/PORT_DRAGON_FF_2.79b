# ------------------------------------------------------------
# DragonFF - Heightmap utilities
# Ported for Blender 2.79 compatibility
# Original author: Parik
# ------------------------------------------------------------

from __future__ import absolute_import, print_function
import os

def read_heights(filepath):
    """Read numeric height values from a .dat or .txt file."""
    heights = []
    if not os.path.isfile(filepath):
        print("heights.py: file not found ->", filepath)
        return heights

    try:
        with open(filepath, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#") or line.startswith(";"):
                    continue
                parts = line.split()
                try:
                    vals = [float(p) for p in parts]
                    heights.append(vals)
                except Exception:
                    continue
    except Exception as e:
        print("heights.py: read_heights failed:", e)
    return heights


def write_heights(filepath, data):
    """Write a 2D list of height values to file."""
    try:
        with open(filepath, "w") as f:
            for row in data:
                f.write(" ".join(str(v) for v in row) + "\n")
    except Exception as e:
        print("heights.py: write_heights failed:", e)

