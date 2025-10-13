"""
Compatibility-aware __init__.py for DragonFF addon
Provides runtime guards so the addon can be enabled on Blender 2.79 and 2.80+
This file was created to add 2.79 compatibility fallbacks for menus, collections/groups,
and to tolerate missing gizmo APIs by skipping class registration failures.
"""

import bpy
import importlib
from bpy.utils import register_class, unregister_class

# Try to import the gui module from the addon package; be tolerant if it's not present
try:
    from . import gui as gui_mod
except Exception:
    try:
        gui_mod = importlib.import_module('gui')
    except Exception:
        gui_mod = None

bl_info = {
    "name": "GTA DragonFF (2.79 compat)",
    "author": "Parik / null-patch",
    "version": (0, 0, 2),
    # Declare minimum to 2.79 — runtime guards handle API differences.
    "blender": (2, 79, 0),
    "category": "Import-Export",
    "location": "File > Import/Export",
    "description": "Importer and Exporter for GTA Formats (2.79 compatibility)",
}

# Collect candidate classes from gui_mod if available. We register any 'type' found in the module
# and rely on try/except during register to skip unsupported classes (like gizmos on 2.79).
_classes = []
if gui_mod is not None:
    for name in dir(gui_mod):
        obj = getattr(gui_mod, name)
        if isinstance(obj, type):
            _classes.append(obj)

# Helper safe menu append/remove
def _append_menu(menu, func):
    if not func:
        return
    try:
        menu.append(func)
    except Exception:
        print("DragonFF: menu append skipped for {} -> {}".format(getattr(menu, '__name__', str(menu)), getattr(func, '__name__', str(func))))

def _remove_menu(menu, func):
    if not func:
        return
    try:
        menu.remove(func)
    except Exception:
        pass


def register():
    # Register classes; skip those that fail (gizmos etc on 2.79)
    for cls in _classes:
        try:
            register_class(cls)
        except Exception as e:
            print("DragonFF: skipping registration of {}: {}".format(getattr(cls, '__name__', str(cls)), e))

    # Pointer properties with fallbacks for older Blender (2.79)
    def safe_pointer(target, attr_name, prop_type):
        if prop_type is None:
            return
        try:
            setattr(target, attr_name, bpy.props.PointerProperty(type=prop_type))
        except Exception:
            try:
                delattr(target, attr_name)
            except Exception:
                pass

    # Attempt to assign well-known property groups from gui_mod if they exist.
    DFFSceneProps = getattr(gui_mod, 'DFFSceneProps', None) if gui_mod else None
    DFFCollectionProps = getattr(gui_mod, 'DFFCollectionProps', None) if gui_mod else None
    Light2DFX = getattr(gui_mod, 'Light2DFXObjectProps', None) if gui_mod else None
    RoadSign2DFX = getattr(gui_mod, 'RoadSign2DFXObjectProps', None) if gui_mod else None
    DFFMaterialProps = getattr(gui_mod, 'DFFMaterialProps', None) if gui_mod else None
    DFFObjectProps = getattr(gui_mod, 'DFFObjectProps', None) if gui_mod else None

    safe_pointer(bpy.types.Scene, 'dff', DFFSceneProps)

    # Collection vs Group fallback
    if hasattr(bpy.types, 'Collection') and DFFCollectionProps:
        safe_pointer(bpy.types.Collection, 'dff', DFFCollectionProps)
    elif hasattr(bpy.types, 'Group') and DFFCollectionProps:
        safe_pointer(bpy.types.Group, 'dff', DFFCollectionProps)

    if hasattr(bpy.types, 'Light') and Light2DFX:
        safe_pointer(bpy.types.Light, 'ext_2dfx', Light2DFX)

    if hasattr(bpy.types, 'TextCurve') and RoadSign2DFX:
        safe_pointer(bpy.types.TextCurve, 'ext_2dfx', RoadSign2DFX)

    safe_pointer(bpy.types.Material, 'dff', DFFMaterialProps)
    safe_pointer(bpy.types.Object, 'dff', DFFObjectProps)

    # Menu registration: try 2.80 names first, fallback to 2.79 names
    import_func = getattr(gui_mod, 'import_dff_func', None) if gui_mod else None
    export_func = getattr(gui_mod, 'export_dff_func', None) if gui_mod else None

    if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
        _append_menu(bpy.types.TOPBAR_MT_file_import, import_func)
        _append_menu(bpy.types.TOPBAR_MT_file_export, export_func)
    else:
        _append_menu(bpy.types.INFO_MT_file_import, import_func)
        _append_menu(bpy.types.INFO_MT_file_export, export_func)

    # Additional menu hooks if provided
    if gui_mod:
        if hasattr(bpy.types, 'OUTLINER_MT_collection') and getattr(gui_mod, 'export_col_outliner', None):
            _append_menu(bpy.types.OUTLINER_MT_collection, getattr(gui_mod, 'export_col_outliner'))
        if hasattr(bpy.types, 'OUTLINER_MT_object') and getattr(gui_mod, 'export_dff_outliner', None):
            _append_menu(bpy.types.OUTLINER_MT_object, getattr(gui_mod, 'export_dff_outliner'))
        if hasattr(bpy.types, 'VIEW3D_MT_edit_armature') and getattr(gui_mod, 'edit_armature_dff_func', None):
            _append_menu(bpy.types.VIEW3D_MT_edit_armature, getattr(gui_mod, 'edit_armature_dff_func'))
        if hasattr(bpy.types, 'VIEW3D_MT_pose') and getattr(gui_mod, 'pose_dff_func', None):
            _append_menu(bpy.types.VIEW3D_MT_pose, getattr(gui_mod, 'pose_dff_func'))
        if hasattr(bpy.types, 'VIEW3D_MT_add') and getattr(gui_mod, 'add_object_dff_func', None):
            _append_menu(bpy.types.VIEW3D_MT_add, getattr(gui_mod, 'add_object_dff_func'))

    # Hook events if the gui exposes a State helper
    try:
        if gui_mod and hasattr(gui_mod, 'State') and hasattr(gui_mod.State, 'hook_events'):
            gui_mod.State.hook_events()
    except Exception:
        pass


def unregister():
    # Remove properties (mirror register logic)
    try:
        del bpy.types.Scene.dff
    except Exception:
        pass

    if hasattr(bpy.types, 'Collection'):
        try:
            del bpy.types.Collection.dff
        except Exception:
            pass
    elif hasattr(bpy.types, 'Group'):
        try:
            del bpy.types.Group.dff
        except Exception:
            pass

    try:
        del bpy.types.Light.ext_2dfx
    except Exception:
        pass

    if hasattr(bpy.types, 'TextCurve'):
        try:
            del bpy.types.TextCurve.ext_2dfx
        except Exception:
            pass

    try:
        del bpy.types.Material.dff
    except Exception:
        pass
    try:
        del bpy.types.Object.dff
    except Exception:
        pass

    # Remove menus safely
    import_func = getattr(gui_mod, 'import_dff_func', None) if gui_mod else None
    export_func = getattr(gui_mod, 'export_dff_func', None) if gui_mod else None
    if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
        _remove_menu(bpy.types.TOPBAR_MT_file_import, import_func)
        _remove_menu(bpy.types.TOPBAR_MT_file_export, export_func)
    else:
        _remove_menu(bpy.types.INFO_MT_file_import, import_func)
        _remove_menu(bpy.types.INFO_MT_file_export, export_func)

    # Unhook events
    try:
        if gui_mod and hasattr(gui_mod, 'State') and hasattr(gui_mod.State, 'unhook_events'):
            gui_mod.State.unhook_events()
    except Exception:
        pass

    # Unregister classes
    for cls in reversed(_classes):
        try:
            unregister_class(cls)
        except Exception as e:
            print("DragonFF: skipping unregistration of {}: {}".format(getattr(cls, '__name__', str(cls)), e))


# End of __init__.py
