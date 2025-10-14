# GTA DragonFF map utility (2.79 compatible)
# Python 3.5 safe: no dataclasses, no f-strings
from __future__ import absolute_import, print_function

import os
import struct
from io import BytesIO, BufferedReader, StringIO

from .data import map_data
from .img import img

#######################################################
class MapData(object):
    def __init__(self, object_instances, object_data, cull_instances):
        self.object_instances = object_instances
        self.object_data = object_data
        self.cull_instances = cull_instances

#######################################################
class TextIPLData(object):
    def __init__(self, object_instances, cull_instances):
        self.object_instances = object_instances
        self.cull_instances = cull_instances

# Base for all IPL / IDE section reader / writer classes
#######################################################
class SectionUtility(object):

    def __init__(self, section_name, data_structures=None):
        if data_structures is None:
            data_structures = []
        self.section_name = section_name
        self.data_structures_dict = {len(ds._fields): ds for ds in data_structures}

    #######################################################
    def read(self, file_stream):
        entries = []
        line = file_stream.readline().strip()

        while line != "end" and line != "":
            line_params = [e.strip() for e in line.split(",")]

            # Append file name for IDEs (needed for collision lookups)
            filename = os.path.basename(getattr(file_stream, "name", ""))
            if filename.lower().endswith(".ide"):
                line_params.append(filename)

            data_structure = self.get_data_structure(line_params)

            if data_structure is None:
                print(type(self).__name__, "Error: No appropriate data structure found")
                print("    Section name:", self.section_name)
                print("    Line parameters:", str(line_params))
            elif len(data_structure._fields) != len(line_params):
                print(type(self).__name__, "Error: Line parameters mismatch.")
                print("    Section name:", self.section_name)
                print("    Data structure name:", data_structure.__name__)
                print("    Data structure:", str(data_structure._fields))
                print("    Line parameters:", str(line_params))
            else:
                entries.append(data_structure(*line_params))

            line = file_stream.readline().strip()

        return entries

    #######################################################
    def get_data_structure(self, line_params):
        return self.data_structures_dict.get(len(line_params))

    #######################################################
    def write(self, file_stream, lines):
        file_stream.write(self.section_name + "\n")
        for line in lines:
            file_stream.write(str(line) + "\n")
        file_stream.write("end\n")

# Utility for reading / writing to map data files (.IPL, .IDE)
#######################################################
class MapDataUtility(object):

    @staticmethod
    def find_path_case_insensitive(base_path, filename):
        current_path = os.path.join(base_path, filename)
        if os.path.isfile(current_path):
            return current_path

        current_path = base_path
        parts = os.path.normpath(filename).split(os.sep)
        for part in parts:
            try:
                entries = os.listdir(current_path)
            except Exception:
                return None
            match = None
            for entry in entries:
                if entry.lower() == part.lower():
                    match = entry
                    break
            if match is None:
                return None
            current_path = os.path.join(current_path, match)
        return current_path

    @staticmethod
    def is_binary_ipl_stream(file_stream):
        current_pos = file_stream.tell()
        try:
            header = file_stream.read(4)
            file_stream.seek(current_pos)
            return header == b"bnry"
        except Exception:
            file_stream.seek(current_pos)
            return False

    @staticmethod
    def get_full_path(game_root, filename):
        if os.path.isabs(filename):
            return filename
        fullpath = MapDataUtility.find_path_case_insensitive(game_root, filename)
        if fullpath:
            return fullpath
        return os.path.join(game_root, filename)

    @staticmethod
    def merge_dols(dol1, dol2):
        result = dict(dol1)
        result.update(dol2)
        for k in set(dol1).intersection(dol2):
            result[k] = dol1[k] + dol2[k]
        return result

    @staticmethod
    def read_binary_ipl_from_stream(file_stream, data_structures):
        sections = {}
        start_pos = file_stream.tell()
        header = file_stream.read(32)
        if len(header) < 32:
            print("Error: Invalid binary IPL file - header too short")
            return sections

        _, num_of_instances, _, _, _, _, _, instances_offset = struct.unpack("4siiiiiii", header)

        item_size = 40
        insts = []
        file_stream.seek(start_pos + instances_offset)
        for i in range(num_of_instances):
            instances = file_stream.read(item_size)
            if len(instances) < item_size:
                print("Warning: Could not read instance %d, reached EOF" % i)
                break
            vals_unpacked = struct.unpack("fffffffiii", instances)
            x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, w_rot, obj_id, interior, lod = vals_unpacked
            vals = [obj_id, "", interior, x_pos, y_pos, z_pos, x_rot, y_rot, z_rot, w_rot, lod]
            insts.append(data_structures["inst"](*[str(v) for v in vals]))

        sections["inst"] = insts
        print("inst: %d entries" % len(insts))
        return sections

    @staticmethod
    def read_text_file_from_stream(file_stream, data_structures, aliases):
        sections = {}
        line = file_stream.readline().strip()
        while line:
            section_name = line
            section_utility = None
            if section_name in aliases:
                available_data_structures = [data_structures[s] for s in aliases[line]]
                section_utility = SectionUtility(section_name, available_data_structures)
            elif section_name in data_structures:
                section_utility = SectionUtility(section_name, [data_structures[section_name]])
            if section_utility is not None:
                sections[section_name] = section_utility.read(file_stream)
                print("%s: %d entries" % (section_name, len(sections[section_name])))
            line = file_stream.readline().strip()
        return sections

    @staticmethod
    def read_file(filepath, data_structures, aliases):
        self = MapDataUtility
        sections = {}
        try:
            with open(filepath, "rb") as file_stream:
                if self.is_binary_ipl_stream(file_stream):
                    sections = self.read_binary_ipl_from_stream(file_stream, data_structures)
                else:
                    binary_data = file_stream.read()
                    text_data = binary_data.decode("latin-1")
                    text_stream = StringIO(text_data)
                    text_stream.name = filepath
                    sections = self.read_text_file_from_stream(text_stream, data_structures, aliases)
        except Exception as e:
            print("Error reading file:", filepath, e)
        return sections

    @staticmethod
    def load_ide_data(game_root, ide_paths, data_structures, aliases):
        self = MapDataUtility
        ide = {}
        for file in ide_paths:
            fullpath = self.get_full_path(game_root, file)
            print("\nMapDataUtility reading:", fullpath)
            sections = self.read_file(fullpath, data_structures, aliases)
            ide = self.merge_dols(ide, sections)
        return ide

    @staticmethod
    def load_ipl_data(game_root, ipl_section, data_structures, aliases):
        self = MapDataUtility
        ipl = {}
        fullpath = self.get_full_path(game_root, ipl_section)
        print("\nMapDataUtility reading:", fullpath)

        if not os.path.isfile(fullpath):
            imgpath = os.path.join(game_root, "models/gta3.img")
            try:
                with img.open(imgpath) as img_file:
                    basename = os.path.basename(ipl_section)
                    entry_idx = img_file.find_entry_idx(basename)
                    if entry_idx > -1:
                        print("Read binary IPL from gta3.img:", basename)
                        _, data = img_file.read_entry(entry_idx)
                        file_stream = BufferedReader(BytesIO(data))
                        sections = MapDataUtility.read_binary_ipl_from_stream(file_stream, data_structures)
                        ipl = self.merge_dols(ipl, sections)
                        return ipl
            except Exception as e:
                print("Warning: gta3.img not found or unreadable:", e)

        sections = self.read_file(fullpath, data_structures, aliases)
        return self.merge_dols(ipl, sections)

    @staticmethod
    def load_map_data(game_id, game_root, ipl_section, is_custom_ipl):
        self = MapDataUtility
        data = map_data.data[game_id].copy()

        if is_custom_ipl:
            ide_paths = []
            for root_path, _, files in os.walk(os.path.join(game_root, "data/maps")):
                for file in files:
                    if file.lower().endswith(".ide"):
                        fullpath = os.path.join(root_path, file)
                        ide_paths.append(os.path.relpath(fullpath, game_root))
            data["IDE_paths"] = ide_paths
        else:
            if game_id == map_data.game_version.SA:
                data["IDE_paths"] = list(data["IDE_paths"])
                for p in list(data["IDE_paths"]):
                    if p.startswith("DATA/MAPS/generic/") or p.startswith("DATA/MAPS/leveldes/") or "xref" in p:
                        continue
                    ide_prefix = p.split("/")[-1].lower()
                    ipl_prefix = ipl_section.split("/")[-1].lower()[:3]
                    if not ide_prefix.startswith(ipl_prefix):
                        data["IDE_paths"].remove(p)

        ide = self.load_ide_data(game_root, data["IDE_paths"], data["structures"], data["IDE_aliases"])
        ipl = self.load_ipl_data(game_root, ipl_section, data["structures"], data["IPL_aliases"])

        object_instances = []
        cull_instances = []
        object_data = {}

        if "inst" in ipl:
            object_instances.extend(ipl["inst"])
        if "cull" in ipl:
            cull_instances.extend(ipl["cull"])
        if "objs" in ide:
            for entry in ide["objs"]:
                if entry.id in object_data:
                    print("OBJ ERROR! duplicate ID:", entry.id)
                object_data[entry.id] = entry
        if "tobj" in ide:
            for entry in ide["tobj"]:
                if entry.id in object_data:
                    print("TOBJ ERROR! duplicate ID:", entry.id)
                object_data[entry.id] = entry

        return MapData(object_instances, object_data, cull_instances)

    @staticmethod
    def write_text_ipl_to_stream(file_stream, game_id, ipl_data):
        file_stream.write("# IPL generated with DragonFF\n")
        section_utility = SectionUtility("inst")
        section_utility.write(file_stream, ipl_data.object_instances)

        section_utility = SectionUtility("cull")
        section_utility.write(file_stream, ipl_data.cull_instances)

        if game_id == map_data.game_version.VC:
            for name in ["pick", "path"]:
                section_utility = SectionUtility(name)
                section_utility.write(file_stream, [])
        elif game_id == map_data.game_version.SA:
            for name in ["path", "grge", "enex", "pick", "cars", "jump", "tcyc", "auzo", "mult"]:
                section_utility = SectionUtility(name)
                section_utility.write(file_stream, [])

    @staticmethod
    def write_ipl_data(filename, game_id, ipl_data):
        with open(filename, "w") as file_stream:
            MapDataUtility.write_text_ipl_to_stream(file_stream, game_id, ipl_data)

