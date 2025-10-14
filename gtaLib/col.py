# col.py — DragonFF COL (collision) format handler, Blender 2.79 port
# GPLv3 © Parik 2019, modified for 2.79 compatibility

from struct import unpack_from, calcsize, pack
from struct import error as StructError
from collections import namedtuple

try:
    from .dff import strlen
except ImportError:
    # fallback for loose execution
    from dff import strlen


class ColModel:
    """Single COL model container"""
    def __init__(self):
        self.version = None
        self.model_name = None
        self.model_id = 0
        self.bounds = None
        self.spheres = []
        self.boxes = []
        self.mesh_verts = []
        self.mesh_faces = []
        self.face_groups = []
        self.lines = []
        self.flags = 0
        self.shadow_verts = []
        self.shadow_faces = []
        self.col_mesh = None


# type aliases initialised by Sections.init_sections()
TBounds = None
TSurface = None
TSphere = None
TBox = None
TFaceGroup = None
TVertex = None
TFace = None
TVector = namedtuple("TVector", "x y z")


class Sections:
    """Helper for reading/writing structured binary blocks"""
    version = 1
    __formats = {}

    @staticmethod
    def init_sections(version):
        global TSurface, TVertex, TBox, TBounds, TSphere, TFace, TFaceGroup

        TSurface = namedtuple("TSurface", "material flags brightness light")
        TVertex = namedtuple("TVertex", "x y z")
        TBox = namedtuple("TBox", "min max surface")

        if version == 1:
            TBounds = namedtuple("TBounds", "radius center min max")
            TSphere = namedtuple("TSphere", "radius center surface")
            TFace = namedtuple("TFace", "a b c surface")
        else:
            TFaceGroup = namedtuple("TFaceGroup", "min max start end")
            TFace = namedtuple("TFace", "a b c material light")
            TBounds = namedtuple("TBounds", "min max center radius")
            TSphere = namedtuple("TSphere", "center radius surface")

        Sections.version = version
        Sections.__formats = {
            TBounds: ["fVVV", "VVVf"],
            TSurface: ["BBBB", "BBBB"],
            TSphere: ["fVS", "VfS"],
            TBox: ["VVS", "VVS"],
            TFaceGroup: ["VVHH", "VVHH"],
            TVertex: ["fff", "hhh"],
            TFace: ["IIIS", "HHHBB"],
        }

    # ---------------------------------------------------------------------

    @staticmethod
    def compress_vertices(vertices):
        return [TVertex._make(int(i * 128) for i in vertex) for vertex in vertices]

    @staticmethod
    def __read_format(fmt, data, offset):
        output = []
        for char in fmt:
            if char == "V":
                output.append(unpack_from("<fff", data, offset))
                offset += 12
            elif char == "S":
                output.append(Sections.read_section(TSurface, data, offset))
                offset += Sections.size(TSurface)
            else:
                output.append(unpack_from(char, data, offset)[0])
                offset += calcsize(char)
        return output

    @staticmethod
    def __write_format(fmt, data):
        _data = b""
        for i, char in enumerate(fmt):
            if char == "V":
                _data += pack("<fff", *data[i])
            elif char == "S":
                _data += Sections.write_section(TSurface, data[i])
            else:
                _data += pack(char, data[i])
        return _data

    @staticmethod
    def write_section(type_, data):
        ver = 0 if Sections.version == 1 else 1
        return Sections.__write_format(Sections.__formats[type_][ver], data)

    @staticmethod
    def read_section(type_, data, offset):
        ver = 0 if Sections.version == 1 else 1
        return type_._make(Sections.__read_format(Sections.__formats[type_][ver], data, offset))

    @staticmethod
    def size(type_):
        ver = 0 if Sections.version == 1 else 1
        fmt = Sections.__formats[type_][ver]
        fmt = fmt.replace("V", "fff").replace("S", "BBBB")
        return calcsize(fmt)


# -------------------------------------------------------------------------
class coll:
    """COL file reader/writer"""

    __slots__ = ["models", "_data", "_pos"]

    def __init__(self, model=None):
        self.models = []
        self._data = b""
        self._pos = 0
        if model is not None:
            self.models.append(model)

    # utility --------------------------------------------------------------

    def __read_struct(self, fmt):
        val = unpack_from(fmt, self._data, self._pos)
        self._pos += calcsize(fmt)
        return val

    def __incr(self, n):
        pos = self._pos
        self._pos += n
        return pos

    def __read_block(self, block_type, count=-1):
        block_size = Sections.size(block_type)
        objs = []
        if count == -1:
            count = unpack_from("<I", self._data, self.__incr(4))[0]
        for _ in range(count):
            objs.append(Sections.read_section(block_type, self._data, self.__incr(block_size)))
        return objs

    # core read ------------------------------------------------------------

    def __read_legacy_col(self, model):
        model.spheres += self.__read_block(TSphere)
        self.__incr(4)
        model.boxes += self.__read_block(TBox)
        model.mesh_verts += self.__read_block(TVertex)
        model.mesh_faces += self.__read_block(TFace)

    def __read_new_col(self, model, pos):
        (
            sphere_count,
            box_count,
            face_count,
            line_count,
            flags,
            spheres_offset,
            box_offset,
            lines_offset,
            verts_offset,
            faces_offset,
            triangles_offset,
        ) = unpack_from("<HHHBxIIIIIII", self._data, self.__incr(36))

        model.flags = flags
        if model.version >= 3:
            (
                shadow_mesh_face_count,
                shadow_verts_offset,
                shadow_faces_offset,
            ) = unpack_from("<III", self._data, self.__incr(12))
        if model.version == 4:
            self.__incr(4)

        # Spheres
        self._pos = pos + spheres_offset + 4
        model.spheres += self.__read_block(TSphere, sphere_count)

        # Boxes
        self._pos = pos + box_offset + 4
        model.boxes += self.__read_block(TBox, box_count)

        # Faces
        self._pos = pos + faces_offset + 4
        model.mesh_faces += self.__read_block(TFace, face_count)

        # Vertices
        verts_count = 0
        for f in model.mesh_faces:
            verts_count = max(verts_count, f.a + 1, f.b + 1, f.c + 1)
        self._pos = pos + verts_offset + 4
        model.mesh_verts += self.__read_block(TVertex, verts_count)
        model.mesh_verts = [(v.x / 128, v.y / 128, v.z / 128) for v in model.mesh_verts]

        # Shadow mesh
        if model.version >= 3 and flags & 16:
            self._pos = pos + shadow_verts_offset + 4
            verts_count = (shadow_faces_offset - shadow_verts_offset) // 6
            model.shadow_verts += self.__read_block(TVertex, verts_count)
            model.shadow_verts = [(v.x / 128, v.y / 128, v.z / 128) for v in model.shadow_verts]
            self._pos = pos + shadow_faces_offset + 4
            model.shadow_faces += self.__read_block(TFace, shadow_mesh_face_count)

    def __read_col(self):
        model = ColModel()
        pos = self._pos

        try:
            if self._data[:3] == b"COL":
                magic, size, name, mid = self.__read_struct("4sI22sH")
            else:
                magic, size, name, mid = (b"COLL", len(self._data) - 8, b"col", 0)
        except StructError:
            raise RuntimeError("Unexpected EOF")

        magic = magic.decode("ascii", errors="ignore")
        model.model_name = name.split(b"\x00", 1)[0].decode("ascii", errors="ignore")
        model.model_id = mid

        vermap = {"COLL": 1, "COL2": 2, "COL3": 3, "COL4": 4}
        model.version = vermap.get(magic, None)
        if not model.version:
            raise RuntimeError("Invalid COL header: {}".format(magic))

        Sections.init_sections(model.version)

        model.bounds = Sections.read_section(TBounds, self._data, self._pos)
        self._pos += Sections.size(TBounds)

        if model.version == 1:
            self.__read_legacy_col(model)
        else:
            self.__read_new_col(model, pos)

        self._pos = pos + size + 8
        return model

    # ---------------------------------------------------------------------

    def load_memory(self, mem):
        self._data = mem
        self._pos = 0
        while self._pos < len(self._data):
            try:
                self.models.append(self.__read_col())
            except RuntimeError:
                break

    def load_file(self, fname):
        with open(fname, "rb") as f:
            self.load_memory(f.read())

    # write ---------------------------------------------------------------

    def __write_block(self, block_type, blocks, write_count=True):
        data = b""
        if write_count:
            data += pack("<I", len(blocks))
        for b in blocks:
            data += Sections.write_section(block_type, b)
        return data

    def __write_col_legacy(self, model):
        d = b""
        d += self.__write_block(TSphere, model.spheres)
        d += pack("<I", 0)
        d += self.__write_block(TBox, model.boxes)
        d += self.__write_block(TVertex, model.mesh_verts)
        d += self.__write_block(TFace, model.mesh_faces)
        return d

    def __write_col(self, model):
        Sections.init_sections(model.version)
        data = (
            self.__write_col_legacy(model)
            if model.version == 1
            else self.__write_col_new(model)
        )
        data = Sections.write_section(TBounds, model.bounds) + data
        header_size = 24
        header = [
            ("COL" + ("L" if model.version == 1 else str(model.version))).encode("ascii"),
            len(data) + header_size,
            model.model_name.encode("ascii"),
            model.model_id,
        ]
        return pack("4sI22sH", *header) + data

    def write_memory(self):
        return b"".join(self.__write_col(m) for m in self.models)

    def write_file(self, fname):
        with open(fname, "wb") as f:
            f.write(self.write_memory())

