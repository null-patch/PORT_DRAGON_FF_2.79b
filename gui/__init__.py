# gui/__init__.py — GUI module loader for DragonFF port (2.79)

from __future__ import absolute_import, print_function

from .gui import (
    DRAGONFF_OT_import_dff,
    DRAGONFF_OT_export_dff,
    DRAGONFF_PT_panel,
)

def get_classes():
    return [DRAGONFF_OT_import_dff, DRAGONFF_OT_export_dff, DRAGONFF_PT_panel]

def register():
    import bpy
    for cls in get_classes():
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print("gui.register failed for {}: {}".format(cls, e))

def unregister():
    import bpy
    for cls in reversed(get_classes()):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print("gui.unregister failed for {}: {}".format(cls, e))

