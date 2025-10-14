bl_info = {
    "name": "GTA DragonFF (2.79 port)",
    "author": "ported from Parik27 by you",
    "version": (2, 79, 0),
    "blender": (2, 79, 0),
    "location": "File > Import-Export",
    "description": "Import/Export GTA RenderWare formats (DFF/TXD/COL) - 2.79 port",
    "category": "Import-Export"
}

import bpy
import traceback

# Import submodules (best-effort; addon should still register even if some parts missing)
try:
    from . import ops
except Exception:
    ops = None
    print("DragonFF: failed to import ops module:\n" + traceback.format_exc())

try:
    from . import gui as gui_mod
except Exception:
    gui_mod = None
    print("DragonFF: failed to import gui module:\n" + traceback.format_exc())

try:
    from . import gtaLib
except Exception:
    gtaLib = None
    print("DragonFF: failed to import gtaLib module:\n" + traceback.format_exc())


# Helper wrappers for register/unregister that call bpy.utils functions
def _register_class(cls):
    try:
        bpy.utils.register_class(cls)
        return True
    except Exception:
        print("DragonFF: register_class failed for {}:\n{}".format(getattr(cls, "__name__", str(cls)), traceback.format_exc()))
        return False


def _unregister_class(cls):
    try:
        bpy.utils.unregister_class(cls)
        return True
    except Exception:
        print("DragonFF: unregister_class failed for {}:\n{}".format(getattr(cls, "__name__", str(cls)), traceback.format_exc()))
        return False


# Collect classes from ops and gui modules
_classes = []

def _collect_from_module(mod):
    collected = []
    if not mod:
        return collected
    # preferred: module exposes get_classes() or classes list
    if hasattr(mod, "get_classes") and callable(getattr(mod, "get_classes")):
        try:
            collected.extend(mod.get_classes())
        except Exception:
            print("DragonFF: get_classes() failed in {}:\n{}".format(getattr(mod, "__name__", str(mod)), traceback.format_exc()))
    elif hasattr(mod, "classes"):
        try:
            collected.extend(getattr(mod, "classes"))
        except Exception:
            print("DragonFF: failed to read 'classes' in {}:\n{}".format(getattr(mod, "__name__", str(mod)), traceback.format_exc()))
    else:
        # fallback: collect top-level types (Panles/Operators)
        try:
            for name in dir(mod):
                obj = getattr(mod, name)
                if isinstance(obj, type):
                    collected.append(obj)
        except Exception:
            print("DragonFF: fallback class collection failed for {}:\n{}".format(getattr(mod, "__name__", str(mod)), traceback.format_exc()))
    return collected

if ops:
    _classes.extend(_collect_from_module(ops))
if gui_mod:
    _classes.extend(_collect_from_module(gui_mod))


# Helper safe menu append/remove
def _append_menu(menu, func):
    if not menu or not func:
        return
    try:
        menu.append(func)
    except Exception:
        # non-fatal: log and continue
        print("DragonFF: menu append skipped for {} -> {}".format(getattr(menu, '__name__', str(menu)), getattr(func, '__name__', str(func))))
        print(traceback.format_exc())


def _remove_menu(menu, func):
    if not menu or not func:
        return
    try:
        menu.remove(func)
    except Exception:
        # ignore errors
        pass


# Safe pointer property assignment for Blender 2.79
def _safe_pointer(target, attr_name, prop_type):
    if not target or not attr_name or not prop_type:
        return
    try:
        setattr(target, attr_name, bpy.props.PointerProperty(type=prop_type))
    except Exception:
        # if assignment fails, ensure we don't leave a half-defined attribute
        try:
            if hasattr(target, attr_name):
                delattr(target, attr_name)
        except Exception:
            pass


def register():
    # Register classes; skip those that fail (e.g. gizmos not available on 2.79)
    for cls in _classes:
        _register_class(cls)

    # Pointer properties registration (use gui_mod-provided PropertyGroup classes if available)
    DFFSceneProps = getattr(gui_mod, 'DFFSceneProps', None) if gui_mod else None
    DFFCollectionProps = getattr(gui_mod, 'DFFCollectionProps', None) if gui_mod else None
    Light2DFX = getattr(gui_mod, 'Light2DFXObjectProps', None) if gui_mod else None
    RoadSign2DFX = getattr(gui_mod, 'RoadSign2DFXObjectProps', None) if gui_mod else None
    DFFMaterialProps = getattr(gui_mod, 'DFFMaterialProps', None) if gui_mod else None
    DFFObjectProps = getattr(gui_mod, 'DFFObjectProps', None) if gui_mod else None

    # Scene
    _safe_pointer(bpy.types.Scene, 'dff', DFFSceneProps)

    # Collection (2.80+) vs Group (2.79)
    if hasattr(bpy.types, 'Collection') and DFFCollectionProps:
        _safe_pointer(bpy.types.Collection, 'dff', DFFCollectionProps)
    elif hasattr(bpy.types, 'Group') and DFFCollectionProps:
        _safe_pointer(bpy.types.Group, 'dff', DFFCollectionProps)

    # Light ext props
    if hasattr(bpy.types, 'Light') and Light2DFX:
        _safe_pointer(bpy.types.Light, 'ext_2dfx', Light2DFX)

    # TextCurve for 2DFX road signs (if present)
    if hasattr(bpy.types, 'TextCurve') and RoadSign2DFX:
        _safe_pointer(bpy.types.TextCurve, 'ext_2dfx', RoadSign2DFX)

    # Material/Object props
    _safe_pointer(bpy.types.Material, 'dff', DFFMaterialProps)
    _safe_pointer(bpy.types.Object, 'dff', DFFObjectProps)

    # Menu registration: use GUI-provided menu functions if exposed
    import_func = getattr(gui_mod, 'import_dff_func', None) if gui_mod else None
    export_func = getattr(gui_mod, 'export_dff_func', None) if gui_mod else None

    # Try 2.80 topbar menus first, fallback to 2.79 menus
    if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
        _append_menu(getattr(bpy.types, 'TOPBAR_MT_file_import'), import_func)
        _append_menu(getattr(bpy.types, 'TOPBAR_MT_file_export'), export_func)
    else:
        _append_menu(getattr(bpy.types, 'INFO_MT_file_import', None), import_func)
        _append_menu(getattr(bpy.types, 'INFO_MT_file_export', None), export_func)

    # Additional optional menu hooks from gui_mod
    if gui_mod:
        if hasattr(bpy.types, 'OUTLINER_MT_collection') and getattr(gui_mod, 'export_col_outliner', None):
            _append_menu(getattr(bpy.types, 'OUTLINER_MT_collection'), getattr(gui_mod, 'export_col_outliner'))
        if hasattr(bpy.types, 'OUTLINER_MT_object') and getattr(gui_mod, 'export_dff_outliner', None):
            _append_menu(getattr(bpy.types, 'OUTLINER_MT_object'), getattr(gui_mod, 'export_dff_outliner'))
        if hasattr(bpy.types, 'VIEW3D_MT_edit_armature') and getattr(gui_mod, 'edit_armature_dff_func', None):
            _append_menu(getattr(bpy.types, 'VIEW3D_MT_edit_armature'), getattr(gui_mod, 'edit_armature_dff_func'))
        if hasattr(bpy.types, 'VIEW3D_MT_pose') and getattr(gui_mod, 'pose_dff_func', None):
            _append_menu(getattr(bpy.types, 'VIEW3D_MT_pose'), getattr(gui_mod, 'pose_dff_func'))
        if hasattr(bpy.types, 'VIEW3D_MT_add') and getattr(gui_mod, 'add_object_dff_func', None):
            _append_menu(getattr(bpy.types, 'VIEW3D_MT_add'), getattr(gui_mod, 'add_object_dff_func'))

    # Hook GUI events/state if available
    try:
        if gui_mod and hasattr(gui_mod, 'State') and hasattr(gui_mod.State, 'hook_events'):
            gui_mod.State.hook_events()
    except Exception:
        print("DragonFF: gui_mod.State.hook_events failed:\n{}".format(traceback.format_exc()))


def unregister():
    # Remove pointer properties if present (mirror of register)
    try:
        if hasattr(bpy.types, 'Scene') and hasattr(bpy.types.Scene, 'dff'):
            del bpy.types.Scene.dff
    except Exception:
        pass

    if hasattr(bpy.types, 'Collection'):
        try:
            if hasattr(bpy.types.Collection, 'dff'):
                del bpy.types.Collection.dff
        except Exception:
            pass
    elif hasattr(bpy.types, 'Group'):
        try:
            if hasattr(bpy.types.Group, 'dff'):
                del bpy.types.Group.dff
        except Exception:
            pass

    try:
        if hasattr(bpy.types, 'Light') and hasattr(bpy.types.Light, 'ext_2dfx'):
            del bpy.types.Light.ext_2dfx
    except Exception:
        pass

    if hasattr(bpy.types, 'TextCurve'):
        try:
            if hasattr(bpy.types.TextCurve, 'ext_2dfx'):
                del bpy.types.TextCurve.ext_2dfx
        except Exception:
            pass

    try:
        if hasattr(bpy.types, 'Material') and hasattr(bpy.types.Material, 'dff'):
            del bpy.types.Material.dff
    except Exception:
        pass
    try:
        if hasattr(bpy.types, 'Object') and hasattr(bpy.types.Object, 'dff'):
            del bpy.types.Object.dff
    except Exception:
        pass

    # Remove menus safely
    import_func = getattr(gui_mod, 'import_dff_func', None) if gui_mod else None
    export_func = getattr(gui_mod, 'export_dff_func', None) if gui_mod else None

    if hasattr(bpy.types, 'TOPBAR_MT_file_import'):
        _remove_menu(getattr(bpy.types, 'TOPBAR_MT_file_import'), import_func)
        _remove_menu(getattr(bpy.types, 'TOPBAR_MT_file_export'), export_func)
    else:
        _remove_menu(getattr(bpy.types, 'INFO_MT_file_import', None), import_func)
        _remove_menu(getattr(bpy.types, 'INFO_MT_file_export', None), export_func)

    # Unhook GUI events/state if available
    try:
        if gui_mod and hasattr(gui_mod, 'State') and hasattr(gui_mod.State, 'unhook_events'):
            gui_mod.State.unhook_events()
    except Exception:
        print("DragonFF: gui_mod.State.unhook_events failed:\n{}".format(traceback.format_exc()))

    # Unregister classes in reverse order
    for cls in reversed(_classes):
        _unregister_class(cls)

