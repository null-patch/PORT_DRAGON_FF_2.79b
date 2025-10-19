# ------------------------------------------------------------
# DragonFF - GTA Car Colors (carcols.dat) reader
# Ported for Blender 2.79 compatibility
# Original author: Parik
# ------------------------------------------------------------

from __future__ import absolute_import, print_function
import os

# ------------------------------------------------------------
# Utility: Parse carcols.dat (GTA car color data)
# ------------------------------------------------------------
def load_carcols(filepath):
    """Parses a GTA carcols.dat file and returns a dictionary:
       { car_id: [ (r, g, b), (r, g, b), ... ] }
    """
    carcols = {}
    if not os.path.isfile(filepath):
        print("carcol.py: File not found ->", filepath)
        return carcols

    with open(filepath, "r") as f:
        for line in f:
            line = line.strip()
            if not line or line.startswith("#") or line.startswith(";"):
                continue

            # Format: car_id, r1,g1,b1, r2,g2,b2, ...
            parts = [p.strip() for p in line.split(",") if p.strip()]
            if len(parts) < 4:
                continue

            try:
                car_id = parts[0]
                rgb_values = []
                nums = [int(v) for v in parts[1:]]
                for i in range(0, len(nums), 3):
                    rgb_values.append((nums[i], nums[i+1], nums[i+2]))
                carcols[car_id] = rgb_values
            except Exception as e:
                print("carcol.py: Failed parsing line:", line, "->", e)
    return carcols


# ------------------------------------------------------------
# Helpers to apply car colors to Blender materials
# ------------------------------------------------------------
def get_car_color(carcols, car_id, index=0):
    """Return (r,g,b) tuple for given car_id and color index."""
    if car_id not in carcols:
        return None
    colors = carcols[car_id]
    if index < len(colors):
        return colors[index]
    return colors[0] if colors else None


def apply_car_color(material, color):
    """Apply an RGB color (0-255) to a Blender material diffuse color."""
    try:
        r, g, b = color
        material.diffuse_color = (r / 255.0, g / 255.0, b / 255.0)
    except Exception as e:
        print("carcol.py: apply_car_color failed:", e)


# ------------------------------------------------------------
# Example workflow (non-executed)
# ------------------------------------------------------------
# colors = load_carcols("/path/to/carcols.dat")
# color = get_car_color(colors, "infernus", 0)
# mat = bpy.data.materials.new("CarPaint")
# apply_car_color(mat, color)

