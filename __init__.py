bl_info = {
    "name": "PORT DragonFF 2.79 port",
    "author": "ported",
    "version": (2, 79, 0),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "description": "DragonFF port for Blender 2.79",
    "category": "Import-Export"
}

import bpy
from . import gui
from . import ops
from . import gtaLib
def register():
    try:
        gui.register()
    except Exception:
        pass
    try:
        ops.register()
    except Exception:
        pass
def unregister():
    try:
        ops.unregister()
    except Exception:
        pass
    try:
        gui.unregister()
    except Exception:
        pass
