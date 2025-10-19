from . import ops as ops_mod
def get_classes():
    return getattr(ops_mod, 'classes', [])
