import bpy
# simple bridge: import gui operators if present
try:
    from ..gui.gui import DRAGONFF_OT_import_dff, DRAGONFF_OT_export_dff, DRAGONFF_PT_panel
    classes = [DRAGONFF_OT_import_dff, DRAGONFF_OT_export_dff, DRAGONFF_PT_panel]
except Exception:
    classes = []
def get_classes():
    return classes
def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            print("ops.register failed for", cls)
def unregister():
    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            print("ops.unregister failed for", cls)
