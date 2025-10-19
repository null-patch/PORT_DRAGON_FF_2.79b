# ------------------------------------------------------------
# DragonFF - Import / Export GUI
# Ported for Blender 2.79 compatibility
# Original author: Parik
# ------------------------------------------------------------

from __future__ import absolute_import, print_function
import bpy
from bpy.props import StringProperty

# ------------------------------------------------------------
# Import operator
# ------------------------------------------------------------
class DRAGONFF_OT_import_dff(bpy.types.Operator):
    """Import GTA RenderWare DFF file"""
    bl_idname = "import_scene.dragonff_dff"
    bl_label = "Import DFF (DragonFF)"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.dff", options={'HIDDEN'})

    def execute(self, context):
        try:
            from ..gtaLib import dff as dff_module
            dff_module.import_dff_to_blender(self.filepath, context)
            self.report({'INFO'}, "Imported: %s" % self.filepath)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, "Import failed: %s" % e)
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# ------------------------------------------------------------
# Export operator
# ------------------------------------------------------------
class DRAGONFF_OT_export_dff(bpy.types.Operator):
    """Export selected object to GTA RenderWare DFF"""
    bl_idname = "export_scene.dragonff_dff"
    bl_label = "Export DFF (DragonFF)"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.dff", options={'HIDDEN'})

    def execute(self, context):
        try:
            from ..gtaLib import dff as dff_module
            dff_module.export_dff_from_blender(context, self.filepath)
            self.report({'INFO'}, "Exported: %s" % self.filepath)
            return {'FINISHED'}
        except Exception as e:
            self.report({'ERROR'}, "Export failed: %s" % e)
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


# ------------------------------------------------------------
# UI Panel
# ------------------------------------------------------------
class DRAGONFF_PT_panel(bpy.types.Panel):
    bl_label = "DragonFF Tools"
    bl_idname = "DRAGONFF_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = "DragonFF"

    def draw(self, context):
        layout = self.layout
        layout.operator("import_scene.dragonff_dff", text="Import DFF")
        layout.operator("export_scene.dragonff_dff", text="Export DFF")


# ------------------------------------------------------------
# Menu entries (Import/Export)
# ------------------------------------------------------------
def import_dff_func(self, context):
    self.layout.operator(DRAGONFF_OT_import_dff.bl_idname, text="GTA DFF (.dff)")

def export_dff_func(self, context):
    self.layout.operator(DRAGONFF_OT_export_dff.bl_idname, text="GTA DFF (.dff)")


# ------------------------------------------------------------
# Registration
# ------------------------------------------------------------
classes = (DRAGONFF_OT_import_dff, DRAGONFF_OT_export_dff, DRAGONFF_PT_panel)

def get_classes():
    return classes

def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception as e:
            print("gui.py register failed for %s: %s" % (cls.__name__, e))

    try:
        bpy.types.INFO_MT_file_import.append(import_dff_func)
        bpy.types.INFO_MT_file_export.append(export_dff_func)
    except Exception:
        pass

def unregister():
    try:
        bpy.types.INFO_MT_file_import.remove(import_dff_func)
        bpy.types.INFO_MT_file_export.remove(export_dff_func)
    except Exception:
        pass

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception as e:
            print("gui.py unregister failed for %s: %s" % (cls.__name__, e))

