import bpy

# Minimal GUI module for DragonFF addon (2.79 compatible)
# Exposes property groups, panels, and menu hook functions referenced by root __init__.py

class DFFSceneProps(bpy.types.PropertyGroup):
    import_path = bpy.props.StringProperty(name="DFF Import Path", default="")

class DFFCollectionProps(bpy.types.PropertyGroup):
    note = bpy.props.StringProperty(name="Collection Note", default="")

class Light2DFXObjectProps(bpy.types.PropertyGroup):
    enabled = bpy.props.BoolProperty(name="2D Light Enabled", default=False)

class RoadSign2DFXObjectProps(bpy.types.PropertyGroup):
    text = bpy.props.StringProperty(name="Road Sign Text", default="")

class DFFMaterialProps(bpy.types.PropertyGroup):
    src_name = bpy.props.StringProperty(name="Source Name", default="")

class DFFObjectProps(bpy.types.PropertyGroup):
    model_name = bpy.props.StringProperty(name="Model Name", default="")

# Minimal operator panel for map import
class MapImportPanel(bpy.types.Panel):
    bl_label = "DragonFF Map Import"
    bl_idname = "SCENE_PT_dff_map_import"
    bl_space_type = 'VIEW_3D'
    bl_region_type = 'TOOLS'
    bl_category = 'DragonFF'

    def draw(self, context):
        layout = self.layout
        scene = context.scene
        layout.label(text="DragonFF Map Import")
        row = layout.row()
        row.operator('scene.dff_import_map', text='Import IPL Map')

# Menu hook functions expected by __init__.py
def import_dff_func(self, context):
    self.layout.operator('import_scene.dff', text='DragonFF (.dff)')

def export_dff_func(self, context):
    self.layout.operator('export_scene.dff', text='DragonFF (.dff)')

# Outliner and other optional menus
def export_col_outliner(self, context):
    self.layout.operator('export_scene.col', text='Export Collection (.col)')

def export_dff_outliner(self, context):
    self.layout.operator('export_scene.dff', text='Export DFF (.dff)')

def edit_armature_dff_func(self, context):
    self.layout.operator('object.dff_set_parent_bone', text='Set DFF Parent Bone')

def pose_dff_func(self, context):
    self.layout.operator('object.dff_generate_bone_props', text='Generate DFF Bone Props')

def add_object_dff_func(self, context):
    self.layout.operator('object.dff_add_collision_box', text='Add DFF Collision Box')

# Minimal State helper
class State:
    @staticmethod
    def hook_events():
        print('DragonFF: State.hook_events called')

    @staticmethod
    def unhook_events():
        print('DragonFF: State.unhook_events called')

# Exported names (so root __init__ can discover classes and functions)
__all__ = [
    'DFFSceneProps','DFFCollectionProps','Light2DFXObjectProps','RoadSign2DFXObjectProps',
    'DFFMaterialProps','DFFObjectProps','MapImportPanel',
    'import_dff_func','export_dff_func','export_col_outliner','export_dff_outliner',
    'edit_armature_dff_func','pose_dff_func','add_object_dff_func','State'
]

# Registration convenience: register classes when module is registered
def register():
    for cls in [DFFSceneProps,DFFCollectionProps,Light2DFXObjectProps,RoadSign2DFXObjectProps,
                DFFMaterialProps,DFFObjectProps,MapImportPanel]:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed([DFFSceneProps,DFFCollectionProps,Light2DFXObjectProps,RoadSign2DFXObjectProps,
                         DFFMaterialProps,DFFObjectProps,MapImportPanel]):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
