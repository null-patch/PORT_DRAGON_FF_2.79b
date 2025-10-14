# gui.py — Blender 2.79 compatible UI/ops for DragonFF
import bpy
import os
import traceback
from bpy.props import StringProperty

MODULE_NAME = __name__

def _load_dff_module():
    """Best-effort import of the internal dff parser module."""
    try:
        # relative import; if running as a packaged addon this should work
        from .gtaLib import dff as dff_module
        return dff_module
    except Exception:
        # fallback: print traceback to system console for debugging
        print("DragonFF: failed to import gtaLib.dff module:\n{}".format(traceback.format_exc()))
        return None


class DRAGONFF_OT_import_dff(bpy.types.Operator):
    bl_idname = "import_scene.dragonff_dff"
    bl_label = "Import DFF (DragonFF)"
    bl_description = "Import a RenderWare DFF model (DragonFF port)"
    bl_options = {'REGISTER', 'UNDO'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.dff", options={'HIDDEN'})

    def execute(self, context):
        dff_module = _load_dff_module()

        if dff_module and hasattr(dff_module, 'import_dff_to_blender'):
            try:
                # many parser functions accept just filepath; pass context if available
                try:
                    dff_module.import_dff_to_blender(self.filepath, context)
                except TypeError:
                    # fallback if function signature expects only filepath
                    dff_module.import_dff_to_blender(self.filepath)
                self.report({'INFO'}, "Imported: {}".format(os.path.basename(self.filepath)))
                return {'FINISHED'}
            except Exception:
                err = traceback.format_exc()
                print("DragonFF: import failed:\n{}".format(err))
                self.report({'ERROR'}, "Import failed. See console for details.")
                return {'CANCELLED'}
        else:
            # fallback placeholder: create a cube and name it
            try:
                bpy.ops.mesh.primitive_cube_add()
                ob = bpy.context.active_object
                ob.name = "dragonff_stub_" + os.path.splitext(os.path.basename(self.filepath))[0]
            except Exception:
                print("DragonFF: placeholder creation failed:\n{}".format(traceback.format_exc()))
                self.report({'ERROR'}, "Parser not present and placeholder creation failed.")
                return {'CANCELLED'}

            self.report({'WARNING'}, "Parser not present — created placeholder object.")
            return {'FINISHED'}

    def invoke(self, context, event):
        # Open file browser
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class DRAGONFF_OT_export_dff(bpy.types.Operator):
    bl_idname = "export_scene.dragonff_dff"
    bl_label = "Export DFF (DragonFF)"
    bl_description = "Export selected object as RenderWare DFF (DragonFF port)"
    bl_options = {'REGISTER'}

    filepath = StringProperty(subtype='FILE_PATH')
    filter_glob = StringProperty(default="*.dff", options={'HIDDEN'})

    def execute(self, context):
        dff_module = _load_dff_module()

        if dff_module and hasattr(dff_module, 'export_dff_from_blender'):
            try:
                try:
                    dff_module.export_dff_from_blender(context, self.filepath)
                except TypeError:
                    # fallback if signature is different (filepath only)
                    dff_module.export_dff_from_blender(self.filepath)
                self.report({'INFO'}, "Exported: {}".format(os.path.basename(self.filepath)))
                return {'FINISHED'}
            except Exception:
                print("DragonFF: export failed:\n{}".format(traceback.format_exc()))
                self.report({'ERROR'}, "Export failed. See console for details.")
                return {'CANCELLED'}
        else:
            self.report({'WARNING'}, "Export function not implemented in dff module.")
            return {'CANCELLED'}

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {'RUNNING_MODAL'}


class DRAGONFF_PT_panel(bpy.types.Panel):
    bl_label = "DragonFF"
    bl_idname = "DRAGONFF_PT_panel"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'   # 2.79: 'TOOLS' region in the left toolbar
    bl_category = "DragonFF"

    def draw(self, context):
        layout = self.layout
        layout.operator("import_scene.dragonff_dff", text="Import DFF")
        layout.operator("export_scene.dragonff_dff", text="Export DFF")
        layout.separator()
        layout.label(text="This is a 2.79 port scaffold.")


def menu_func_import(self, context):
    self.layout.operator(DRAGONFF_OT_import_dff.bl_idname, text="GTA DFF (.dff)")


def menu_func_export(self, context):
    self.layout.operator(DRAGONFF_OT_export_dff.bl_idname, text="GTA DFF (.dff)")


# registration
classes = (
    DRAGONFF_OT_import_dff,
    DRAGONFF_OT_export_dff,
    DRAGONFF_PT_panel,
)


def register():
    for cls in classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            print("DragonFF: register failed for {}:\n{}".format(getattr(cls, '__name__', str(cls)), traceback.format_exc()))

    # Try appending to 2.8+ topbar menus first, fallback to 2.79 menus
    try:
        if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
            bpy.types.TOPBAR_MT_file_import.append(menu_func_import)
            bpy.types.TOPBAR_MT_file_export.append(menu_func_export)
        else:
            bpy.types.INFO_MT_file_import.append(menu_func_import)
            bpy.types.INFO_MT_file_export.append(menu_func_export)
    except Exception:
        # Last-ditch attempt: try both but ignore failures
        try:
            bpy.types.INFO_MT_file_import.append(menu_func_import)
            bpy.types.INFO_MT_file_export.append(menu_func_export)
        except Exception:
            print("DragonFF: failed to append import/export menus:\n{}".format(traceback.format_exc()))


def unregister():
    # Remove menus (try both names)
    try:
        if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
            try:
                bpy.types.TOPBAR_MT_file_import.remove(menu_func_import)
                bpy.types.TOPBAR_MT_file_export.remove(menu_func_export)
            except Exception:
                pass
        else:
            try:
                bpy.types.INFO_MT_file_import.remove(menu_func_import)
                bpy.types.INFO_MT_file_export.remove(menu_func_export)
            except Exception:
                pass
    except Exception:
        print("DragonFF: failed to remove menus:\n{}".format(traceback.format_exc()))

    for cls in reversed(classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            print("DragonFF: unregister failed for {}:\n{}".format(getattr(cls, '__name__', str(cls)), traceback.format_exc()))

