import bpy

class IMPORT_OT_dff(bpy.types.Operator):
    bl_idname = 'import_scene.dff'
    bl_label = 'Import DFF'
    bl_options = {'REGISTER', 'UNDO'}

    filepath = bpy.props.StringProperty(name='File Path', subtype='FILE_PATH')

    def execute(self, context):
        print('DragonFF: IMPORT_OT_dff called, filepath=', self.filepath)
        # Placeholder: real DFF parsing should be implemented in gtaLib
        return {'FINISHED'}

class EXPORT_OT_dff(bpy.types.Operator):
    bl_idname = 'export_scene.dff'
    bl_label = 'Export DFF'

    def execute(self, context):
        print('DragonFF: EXPORT_OT_dff called')
        return {'FINISHED'}

class EXPORT_OT_col(bpy.types.Operator):
    bl_idname = 'export_scene.col'
    bl_label = 'Export COL'

    def execute(self, context):
        print('DragonFF: EXPORT_OT_col called')
        return {'FINISHED'}

class SCENE_OT_dff_import_map(bpy.types.Operator):
    bl_idname = 'scene.dff_import_map'
    bl_label = 'Import IPL Map'

    filepath = bpy.props.StringProperty(name='IPL Path', subtype='FILE_PATH')

    def execute(self, context):
        print('DragonFF: SCENE_OT_dff_import_map called, filepath=', self.filepath)
        # Minimal demonstration: call gtaLib.parse_ipl and report
        try:
            from ..gtaLib import parse_ipl
        except Exception:
            try:
                import gtaLib
                parse_ipl = gtaLib.parse_ipl
            except Exception:
                parse_ipl = None

        if parse_ipl:
            entries = parse_ipl(self.filepath)
            print('Parsed IPL entries:', len(entries))
        else:
            print('gtaLib.parse_ipl not available')
        return {'FINISHED'}

class SCENE_OT_ipl_select(bpy.types.Operator):
    bl_idname = 'scene.ipl_select'
    bl_label = 'Select IPL Entry'

    def execute(self, context):
        print('DragonFF: SCENE_OT_ipl_select called')
        return {'FINISHED'}

# Some object operators referenced by gui hooks
class OBJECT_OT_dff_generate_bone_props(bpy.types.Operator):
    bl_idname = 'object.dff_generate_bone_props'
    bl_label = 'Generate Bone Props'
    def execute(self, context):
        print('DragonFF: OBJECT_OT_dff_generate_bone_props')
        return {'FINISHED'}

class OBJECT_OT_dff_set_parent_bone(bpy.types.Operator):
    bl_idname = 'object.dff_set_parent_bone'
    bl_label = 'Set Parent Bone'
    def execute(self, context):
        print('DragonFF: OBJECT_OT_dff_set_parent_bone')
        return {'FINISHED'}

class OBJECT_OT_dff_add_collision_box(bpy.types.Operator):
    bl_idname = 'object.dff_add_collision_box'
    bl_label = 'Add Collision Box'
    def execute(self, context):
        print('DragonFF: OBJECT_OT_dff_add_collision_box')
        return {'FINISHED'}

# Register/unregister helper
_classes = [IMPORT_OT_dff, EXPORT_OT_dff, EXPORT_OT_col, SCENE_OT_dff_import_map, SCENE_OT_ipl_select,
            OBJECT_OT_dff_generate_bone_props, OBJECT_OT_dff_set_parent_bone, OBJECT_OT_dff_add_collision_box]

def register():
    for cls in _classes:
        try:
            bpy.utils.register_class(cls)
        except Exception:
            pass


def unregister():
    for cls in reversed(_classes):
        try:
            bpy.utils.unregister_class(cls)
        except Exception:
            pass
