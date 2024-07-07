#!/usr/bin/python

import ifflib
import struct
from pathlib import Path
from dataclasses import dataclass, field
from pprint import pprint
from copy import deepcopy
from bitarray import bitarray, util

comp_mods_lookup = {
	0x24: 'RESUPPLY_RATE_BONUS',
	0x25: 'ZONE_OF_CONTROL_BONUS',
	0x26: 'MORALE_BONUS',
	0x27: 'MORALE_LOSS_RATE_BONUS',
	0x28: 'MORALE_RECOVERY_RATE_BONUS',
	0x29: 'MORALE_CHECK_BONUS',
	0x2A: 'VISUAL_RANGE_BONUS',
	0x2B: 'ENTRENCHMENT_RATE_BONUS',
}

comp_mods_default = {
    'RESUPPLY_RATE_BONUS': [1, 'multiply'],
	'ZONE_OF_CONTROL_BONUS': [1, 'multiply'],
	'MORALE_BONUS': [0, 'add'],
	'MORALE_LOSS_RATE_BONUS': [1, 'multiply'],
	'MORALE_RECOVERY_RATE_BONUS': [1, 'multiply'],
	'MORALE_CHECK_BONUS': [0, 'add'],
	'VISUAL_RANGE_BONUS': [1, 'multiply'],
	'ENTRENCHMENT_RATE_BONUS': [1, 'multiply'],
    }

unit_mods_lookup = {
	0x01: 'ATTACK_BONUS_TO_ANY',
	0x02: 'ATTACK_BONUS_TO_MOUNTED',
	0x03: 'HIT_POINTS_BONUS',
	0x04: 'ATTACK_BONUS_TO_SHADOW',
	0x05: 'ATTACK_BONUS_TO_BUILDING',
	0x06: 'ATTACK_BONUS_TO_ARCHER',
	0x07: 'ATTACK_BONUS_TO_ROUTED',
	0x08: 'DEFENSE_BONUS_VS_ANY',
	0x09: 'DEFENSE_BONUS_VS_MOUNTED',
	0x0A: 'UNKNOWN',
	0x0B: 'DEFENSE_BONUS_VS_SHADOW',
	0x0C: 'DEFENSE_BONUS_VS_ARCHER',
	0x0D: 'WAS_DAMAGE_BONUS_TO_SHADOW',
	0x0E: 'DAMAGE_BONUS_TO_ANY',
	0x0F: 'WAS_DAMAGE_BONUS_TO_MOUNTED',
	0x10: 'IGNORE_TERRAIN_BONUS',
	0x11: 'ATTACK_BONUS_TO_NONSHADOW',
	0x12: 'RELOAD_TIME_BONUS',
	0x13: 'DAMAGE_TAKEN_FROM_MAGIC',
	0x14: 'DAMAGE_TAKEN_FROM_NON_MAGIC',
	0x15: 'DAMAGE_TAKEN_FROM_RANGED',
	0x16: 'DAMAGE_TAKEN_FROM_MELEE',
	0x17: 'DAMAGE_TAKEN_FROM_ANY',
	0x18: 'REVERSE_DAMAGE_WHEN_HIT',
	0x19: 'MOVEMENT_BONUS',
	0x1A: 'PARALYZE_BONUS',
	0x1B: 'ENTANGLE_BONUS',
	0x1C: 'DAMAGE_TAKEN_FROM_HOLY',
	0x1D: 'DAMAGE_TAKEN_FROM_UNHOLY',
	0x1E: 'DAMAGE_TAKEN_FROM_KHALDUNITE',
	0x1F: 'IMMUNITY_TO_ENCHANTMENT',
	0x20: 'MELEE_HOLY_DAMAGE',
	0x21: 'MELEE_UNHOLY_DAMAGE',
	0x22: 'CAUSE_KHALDUNITE_DAMAGE',
	0x23: 'CAUSE_MAGIC_DAMAGE',

}

unit_mods_default = {
	'ATTACK_BONUS_TO_ANY': [0, 'add'],
	'ATTACK_BONUS_TO_MOUNTED': [0, 'add'],
	'UK0': [0, 'add'],
	'ATTACK_BONUS_TO_SHADOW': [0, 'add'],
	'ATTACK_BONUS_TO_BUILDING': [0, 'add'],
	'ATTACK_BONUS_TO_ARCHER': [0, 'add'],
	'ATTACK_BONUS_TO_ROUTED': [0, 'add'],
	'DEFENSE_BONUS_VS_ANY': [0, 'add'],
	'DEFENSE_BONUS_VS_MOUNTED': [0, 'add'],
	'UK1': [0, 'add'],
	'DEFENSE_BONUS_VS_SHADOW': [0, 'add'],
	'DEFENSE_BONUS_VS_ARCHER': [0, 'add'],
	'WAS_DAMAGE_BONUS_TO_SHADOW': [1, 'multiply'],
	'DAMAGE_BONUS_TO_ANY': [1, 'multiply'],
	'WAS_DAMAGE_BONUS_TO_MOUNTED': [1, 'multiply'],
	'UK2': [0, 'add'],
	'ATTACK_BONUS_TO_NONSHADOW': [0, 'add'],
	'RELOAD_TIME_BONUS': [1, 'multiply'],
	'DAMAGE_TAKEN_FROM_MAGIC': [1, 'multiply'],
	'DAMAGE_TAKEN_FROM_NON_MAGIC': [1, 'multiply'],
	'DAMAGE_TAKEN_FROM_RANGED': [1, 'multiply'],
	'DAMAGE_TAKEN_FROM_MELEE': [1, 'multiply'],
	'DAMAGE_TAKEN_FROM_ANY': [1, 'multiply'],
	'REVERSE_DAMAGE_WHEN_HIT': [0, 'add'],
	'DAMAGE_TAKEN_FROM_HOLY': [1, 'multiply'],
	'DAMAGE_TAKEN_FROM_UNHOLY': [1, 'multiply'],
	'DAMAGE_TAKEN_FROM_KHALDUNITE': [1, 'multiply'],
	'IMMUNITY_TO_ENCHANTMENT': [0, 'add'],
	'MELEE_HOLY_DAMAGE': [0, 'add'],
	'MELEE_UNHOLY_DAMAGE': [0, 'add'],
	'CAUSE_KHALDUNITE_DAMAGE': [0, 'add'],
	'CAUSE_MAGIC_DAMAGE': [0, 'add'],
    }

def fix_encoding(text):
    return (text if type(text) is bytes else text.encode('ascii'))


class tgmFile:
    """
    A class representing a .TGM game asset file,
    which as a format is based on the IFF file structure
    """
    def __init__(self, filename: str):
        self.filename = Path(filename)
        self.read_from = self.filename.suffix.upper()
        match self.read_from:
            case '.TGM':
                self.iff = ifflib.iff_file(self.filename)
            case _:
                print(f"Error: invalid read type {self.read_from}")
        return
    
   
    class EdtrChunk:
        
        @dataclass
        class Kingdom:
            is_active: bool = False
            name_len: int = 0
            name: str = ''
            unknown: str = ''
            team: int = int.from_bytes(b'FFFF', 'little')
            sai: dict = field(default_factory=lambda: {
                'easy': {'name_len': 0, 'name': ''},
                'medium': {'name_len': 0, 'name': ''},
                'hard': {'name_len': 0, 'name': ''},
                })
            
            def pack(self):
                data = b''
                data += struct.pack(f'<IB{len(self.name)}s4sI',
                                    int(self.is_active),
                                    len(self.name),
                                    fix_encoding(self.name),
                                    self.unknown,
                                    self.team,)
                for sai in self.sai.values():
                    data += struct.pack(f'<B{len(sai["name"])}s',
                                        len(sai['name']),
                                        fix_encoding(sai['name']),)
                return data
                
        
        
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[2].data_offset)
                # Skips unknown bytes
                (self.unknown0,
                 self.name_len,) = struct.unpack('4sB', in_fh.read(5))
                (self.map_name,) = struct.unpack(f'{self.name_len}s', in_fh.read(self.name_len))
                (self.desc_len,) = struct.unpack('B', in_fh.read(1))
                (self.map_description,) = struct.unpack(f'{self.desc_len}s', in_fh.read(self.desc_len))
                (self.size_se,
                 self.size_sw,
                 self.deathmatch_teams,
                 self.deathmatch_kingdoms,) = struct.unpack('=4I', in_fh.read(16))
                self.deathmatch_players = bitarray(0, endian='little')
                self.deathmatch_players.frombytes(in_fh.read(4),)
                (self.custom_kingdoms,) = struct.unpack('=I', in_fh.read(4))
                self.custom_players = bitarray(0, endian='little')
                self.custom_players.frombytes(in_fh.read(4),)
                (self.scenario_kingdoms,) = struct.unpack('=I', in_fh.read(4))
                self.scenario_players = bitarray(0, endian='little')
                self.scenario_players.frombytes(in_fh.read(4),)
# =============================================================================
#                 
#                 self.deathmatch_players = util.int2ba(deathmatch_players, endian='little')
#                 self.custom_players = util.int2ba(custom_players, endian='little')
#                 self.scenario_players = util.int2ba(scenario_players, endian='little')
# =============================================================================
                
                self.kingdoms = []
                for i in range(0,8):
                    print(f'reading kingdom {i} at {in_fh.tell()}')
                    new_kingdom = self.Kingdom()
                    (new_kingdom.is_active,
                     new_kingdom.name_len,) = struct.unpack('BxxxB', in_fh.read(5))
                    (new_kingdom.name,) = struct.unpack(f'{new_kingdom.name_len}s', in_fh.read(new_kingdom.name_len))
                    (new_kingdom.unknown,
                     new_kingdom.team,) = struct.unpack('4sI', in_fh.read(8))
                    
                    for k in new_kingdom.sai.keys():
                        print(f'  reading sai {k} at {in_fh.tell()}')
                        (new_kingdom.sai[k]['name_len'],) = struct.unpack('B', in_fh.read(1))
                        (new_kingdom.sai[k]['name'],) = struct.unpack(f"{new_kingdom.sai[k]['name_len']}s", in_fh.read(new_kingdom.sai[k]['name_len']))
                    
                    self.kingdoms.append(new_kingdom)
                
                self.teams = []
                for i in range(0,4):
                    print(f'reading team {i} at {in_fh.tell()}')
                    new_team = {}
                    (new_team['unknown0'],
                     new_team['name_len'],) = struct.unpack('4sB', in_fh.read(5))
                    (new_team['name'],) = struct.unpack(f"{new_team['name_len']}s", in_fh.read(new_team['name_len']))
                    (new_team['unknown1'],) = struct.unpack('12s', in_fh.read(12))
                    self.teams.append(new_team)
                
                # Skips unknown bytes
                (self.unknown2,) = struct.unpack('84s', in_fh.read(84))
                print(f'Reading Players at {in_fh.tell()}')
                self.players = []
                for i in range(0,8):
                    new_player = {}
                    (new_player['name_len'],) = struct.unpack('B', in_fh.read(1))
                    (new_player['name'],) = struct.unpack(f"{new_player['name_len']}s", in_fh.read(new_player['name_len']))
                    (new_player['unknown1'],
                    new_player['faction'],
                    new_player['team'],
                    new_player['unknown2'],) = struct.unpack('4sII4s', in_fh.read(16))
                    self.players.append(new_player)
                
                (self.unknown3,
                 self.starting_gold,
                 self.unknown4,
                 use_politics,
                 self.unknown5,
                 allow_settlements,
                 allow_outposts,
                 self.max_companies,
                 self.max_settlements,
                 self.max_outposts,
                 self.unknown6,
                 self.allied_victory,
                 self.unknown7,) = struct.unpack('=12sfIIB5I28sI50s', in_fh.read(127))
                self.use_politics = bool(use_politics)
                self.allow_settlements = bool(allow_settlements)
                self.allow_outposts = bool(allow_outposts)
                
            
        def pack(self):
            data = b''
            data += struct.pack(f'<4sB{len(self.map_name)}sB{len(self.map_description)}s9I',
                                self.unknown0,
                                len(self.map_name),
                                fix_encoding(self.map_name),
                                len(self.map_description),
                                fix_encoding(self.map_description),
                                self.size_se,
                                self.size_sw,
                                self.deathmatch_teams,
                                self.deathmatch_kingdoms,
                                util.ba2int(self.deathmatch_players),
                                self.custom_kingdoms,
                                util.ba2int(self.custom_players),
                                self.scenario_kingdoms,
                                util.ba2int(self.scenario_players),)
            
            for k in self.kingdoms:
                data += k.pack()
            
            for t in self.teams:
                data += struct.pack(f'<4sB{len(t["name"])}s12s',
                                   t['unknown0'],
                                   len(t['name']),
                                   fix_encoding(t['name']),
                                   t['unknown1'],)
            
            data += struct.pack('<84s', self.unknown2,)
            
            for p in self.players:
                data += struct.pack(f'<B{len(p["name"])}s4sII4s',
                                    len(p['name']),
                                    fix_encoding(p['name']),
                                    p['unknown1'],
                                    p['faction'],
                                    p['team'],
                                    p['unknown2'],)
                
            data += struct.pack('<12sfIIB5I28sI50s',
                                self.unknown3,
                                self.starting_gold,
                                self.unknown4,
                                int(self.use_politics),
                                self.unknown5,
                                int(self.allow_settlements),
                                int(self.allow_outposts),
                                self.max_companies,
                                self.max_settlements,
                                self.max_outposts,
                                self.unknown6,
                                self.allied_victory,
                                self.unknown7,)   
            
            data = addChunkPadding(data)
            data = struct.pack('>4sI', b'EDTR', len(data)) + data
            return data  
            
            
    class MgrdChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file, EDTR):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[4].data_offset)
                (self.required,) = struct.unpack('=I', in_fh.read(4))
                self.EDTR_ref = EDTR
                print(f'Reading first tile @ {in_fh.tell()}')
                self.tiles = []
                for _ in range(self.EDTR_ref.size_se):
                    self.tiles.append([self.GridTile(*struct.unpack('>BB', in_fh.read(2))) for _ in range(self.EDTR_ref.size_sw)])
                
        class GridTile:
            def __init__(self, terrain, layout):
                self._terrain = terrain
                self._layout = layout
                self.terrain1 = terrain >> 4
                self.terrain2 = terrain & 15
                self.display = layout >> 4
                self.layout = layout & 15
            
            def copy(self):
                return type(self)(self._terrain, self._layout)
            
            def pack(self):
                terrain = (self.terrain1 << 4) | self.terrain2
                layout = (self.display << 4) | self.layout
                return struct.pack('>BB', terrain, layout)
        
        def pack(self):
            data = b''
            data += struct.pack('<I', self.required)
            
            for row in self.tiles:
                for tile in row:
                    data += tile.pack()
            
            data = addChunkPadding(data)
            data = struct.pack('>4sI', b'MGRD', len(data)) + data
            return data
                
    
    class FtrsChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file, TYPE):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[6].data_offset)
                start_pos = in_fh.tell()
                (self.load,) = struct.unpack('=i', in_fh.read(4))
                self.features = []
                while (in_fh.tell() < start_pos + iff.data.children[6].length - 12):
                    self.features.append(Feature(in_fh, TYPE))
                    if self.features[-1].header.index == 0xFFFF:
                        self.features.pop()
        
        def pack(self):
            data = b''
            data += struct.pack('<I', self.load)
            for feature in self.features:
                data += feature.pack()
            # Adds empty feature to signify chunk end
            data += b'\x10\x08\xFF\xFF' + b'\x00'*12
            data = addChunkPadding(data)
            data = struct.pack('>4sI', b'FTRS', len(data)) + data
            return data                
    
    
    class FidxChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[7].data_offset)
                start_pos = in_fh.tell()
                (self.count,) = struct.unpack('=I', in_fh.read(4))
                self.sizes = []
                self.sizes.extend(struct.unpack(f'={self.count}I', in_fh.read(4*self.count)))
        
        def generate(self, FTRS):
            self.sizes = [len(f.pack()) for f in FTRS.features if f.header.index != 0xFFFF]
            self.count = len(self.sizes)
        
        def pack(self):
            data = struct.pack(f'<{self.count+1}I', self.count, *self.sizes)
            data = addChunkPadding(data)
            data = struct.pack('>4sI', b'FIDX', len(data)) + data
            return data 
    
    class GameChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[10].data_offset)
                start_pos = in_fh.tell()
                (self.first_id, self.next_id,) = struct.unpack('=II', in_fh.read(8))
                self.ids = []
                for i in range(0x8000):
                    if (val := in_fh.read(2)) == b'\x00\x00':
                        self.ids.append(True)
                    elif val == b'\xFF\xFF':
                        self.ids.append(False)
                    else:
                        print(f'Invalid ID state {val} at id {i} in chunk GAME')
                        raise SystemExit(1)
                (self.ct_ids,) = struct.unpack('=I', in_fh.read(4))
                self.load_flags = []
                for _ in range(4096):
                    bitflag = struct.unpack('=B', in_fh.read(1))[0]
                    for _ in range(0,8):
                        self.load_flags.append(bitflag&1 == True)
                        bitflag >>= 1
                (self.data,) = struct.unpack('=68s', in_fh.read(68))
            
        def pack(self):
            data = struct.pack('<II', self.first_id, self.next_id,)
            
            for id in self.ids:
                if id is True:
                    data += struct.pack('<H', 0)
                else:
                    data += struct.pack('<H', 0xFFFF)
            data += struct.pack('<I', self.ct_ids,)
            bitflag = 0
            for i in range(len(self.load_flags)):
                if self.load_flags[i] is True:
                    bitflag |= 0b1 << (i % 8)
                if i > 0 and (i+1) % 8 == 0:
                    data += struct.pack('<B', bitflag)
                    bitflag = 0
            data += struct.pack('<68s', self.data,)
            data = struct.pack('>4sI', b'GAME', len(data)) + data
            return data 
    
    
    class TypeChunk:
        
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[13].data_offset)
                
                (self.unknown0,
                 self.num_objs,) = struct.unpack('HH', in_fh.read(4))
                
                self.by_name = {}
                self.by_index = {}
                for i in range(0, self.num_objs):
                    new_obj = {}
                    name = struct.unpack('32s', in_fh.read(32))[0].rstrip(b'\x00').decode('ascii')
                    new_obj['name'] = name
                    new_obj['index'] = i
                    
                    (new_obj['subtype'],
                     new_obj['type'],) = struct.unpack('BB', in_fh.read(2))
                    
                    # This allows for lookup by either name or index, and both will point to the same mutable object
                    self.by_name[name] = new_obj
                    self.by_index[i] = new_obj
        
        def pack(self):
            data = b''
            data += struct.pack('HH',
                                self.unknown0,
                                self.num_objs,)
            for k, v in self.by_index.items():
                data += struct.pack('<32sBB',
                                    v['name'].encode('ascii'),
                                    v['subtype'],
                                    v['type'],)
           
            data = addChunkPadding(data)
            data = struct.pack('>4sI', b'TYPE', len(data)) + data
            return data
    
    
    class HrosChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[14].data_offset)
                start_pos = in_fh.tell()
                
                (self.uk0,) = struct.unpack('=I', in_fh.read(4))
                
                self.heroes = {}
                while in_fh.tell() + 22 < iff.data.children[14].length + start_pos:
                    hero = {}
                    (name_len,) = struct.unpack('=B', in_fh.read(1))
                    (name,
                     hero['status'],
                     hero['i1'],
                     hero['experience'],
                     hero['awakened'],
                     hero['s1'],
                     hero['player_id'],
                     hero['editor_id'],) = struct.unpack(f'={name_len}siifihii', in_fh.read(26+name_len))
                    self.heroes[name.decode('ascii')] = hero
            
        def pack(self):
            data = b''
            data += struct.pack('<I', self.uk0)
            for name, hero in self.heroes.items():
                data += struct.pack(f'<B{len(name)}siifihii',
                                    len(name),
                                    name.encode('ascii'),
                                    hero['status'],
                                    hero['i1'],
                                    hero['experience'],
                                    hero['awakened'],
                                    hero['s1'],
                                    hero['player_id'],
                                    hero['editor_id'],)
            
            data = addChunkPadding(data, force=True)
            data = struct.pack('>4sI', b'HROS', len(data)) + data
            return data
    
    class PlrsChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[15].data_offset)
                (self.unknown0,) = struct.unpack('I', in_fh.read(4))
                
                self.players = []
                for i in range(0, 9):
                    self.players.append(Player(in_fh))
        
        def pack(self):
            data = b''
            data += struct.pack('<I', self.unknown0,)
            for p in self.players:
                data += p.pack()
            data = addChunkPadding(data)
            data = struct.pack('>4sI', b'PLRS', len(data)) + data
            return data

    
    class ObjsChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file, TYPE):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[16].data_offset)
                (self.unknown0,) = struct.unpack('=4s', in_fh.read(4))
                self.objs = []
                
                while in_fh.tell() < (iff.data.children[16].data_offset + iff.data.children[16].length - 4):
                #for _ in range(6):
                    self.objs.append(getMapObjClass(in_fh)(in_fh, TYPE))
                    if self.objs[-1].header.index == 0xFFFF:
                        self.objs.pop()
                    #pprint(vars(self.objs[-1]))   
                    #print('')
        
        def pack(self):
            data = b''
            data += struct.pack('<4s', self.unknown0)
            for obj in self.objs:
                data += obj.pack()
            # Adds empty obj to signify chunk end
            data += b'\x10\x08\xFF\xFF' + b'\x00'*12
            data = addChunkPadding(data)
            data = struct.pack('>4sI', b'OBJS', len(data)) + data
            return data
                
    
    def load(self):
        match self.read_from:
            case '.TGM':
                self.iff.load()
                if self.iff.data.formtype != "TGSV":
                    print(f"Error: invalid file type: {self.iff.data.formtype}")
                self.chunks = {}
                self.chunks['EDTR'] = self.EdtrChunk(self.filename, self.iff)
                self.chunks['MGRD'] = self.MgrdChunk(self.filename, self.iff, self.chunks['EDTR'])
                self.chunks['FIDX'] = self.FidxChunk(self.filename, self.iff)
                self.chunks['GAME'] = self.GameChunk(self.filename, self.iff)
                self.chunks['TYPE'] = self.TypeChunk(self.filename, self.iff)
                self.chunks['FTRS'] = self.FtrsChunk(self.filename, self.iff, self.chunks['TYPE'])
                self.chunks['HROS'] = self.HrosChunk(self.filename, self.iff)
                self.chunks['PLRS'] = self.PlrsChunk(self.filename, self.iff)
                self.chunks['OBJS'] = self.ObjsChunk(self.filename, self.iff, self.chunks['TYPE'])
    
    def write(self, dest_path):
        with open(self.filename, 'rb') as in_fp, open(dest_path, 'wb+') as out_fp:
            #write placeholder FORM
            out_fp.write(b'FORM\xFF\xFF\xFF\xFFTGSV')
            for iff_chunk in self.iff.data.children:
                if iff_chunk.type in self.chunks and hasattr(self.chunks[iff_chunk.type], 'pack'):
                    out_fp.write(self.chunks[iff_chunk.type].pack())
                else:
                    out_fp.write(struct.pack('>4sI', iff_chunk.type.encode('ascii'), iff_chunk.length))
                    in_fp.seek(iff_chunk.data_offset)
                    out_fp.write(in_fp.read(iff_chunk.length))
                    if last_bytes := (out_fp.tell() % 4):
                        out_fp.write(b'\x00'*(4-last_bytes))
            
            file_size = out_fp.seek(0,2)
            out_fp.seek(4)
            out_fp.write(struct.pack('>I', file_size - 12))

class Player:
    def __init__(self, in_fh,):
        self.fh = in_fh
        start_pos = self.fh.tell()
        self.start = self.fh.tell()
        #print(f'reading player {i} @ {self.fh.tell()}')
        (self.unknown0,
         self.size0,
         self.size1,) = struct.unpack('3I', self.fh.read(12))
        #print(f'pos: {in_fh.tell()}')
        self.name = struct.unpack('=15s', self.fh.read(15))[0].split(b'\x00')[0].decode('ascii')
        print(f"   name {self.name}")
        (self.faction,
         self.unknown1,
         self.starting_gold,
         is_active,
         self.sai_len,) = struct.unpack('=IffIB', self.fh.read(17))
        self.is_active = bool(is_active)
        
        (self.sai_name,) = struct.unpack(f'={self.sai_len}s', self.fh.read(self.sai_len))
        
        size_factor = -20 if self.size0 == 0x12 else 0
        if self.name == "Independent":
            data_len = start_pos + 4592 - in_fh.tell() + size_factor
            (self.data0,) = struct.unpack(f'={data_len}s',self.fh.read(data_len))
        else:
            self.economy = {}
            (self.economy['gold'],
             self.economy['unknown1'],
             self.economy['stone'],
             self.economy['unknown2'],
             self.economy['wood'],
             self.economy['unknown3'],
             self.economy['iron'],
             self.economy['unknown4'],
             self.economy['mana'],
             self.economy['unknown5'],) = struct.unpack('=10f', self.fh.read(40))
            
            (self.unknown2,) = struct.unpack('=4s', self.fh.read(4))
            
            self.political_relations = {}
            (self.political_relations['player1'],
             self.political_relations['player2'],
             self.political_relations['player3'],
             self.political_relations['player4'],
             self.political_relations['player5'],
             self.political_relations['player6'],
             self.political_relations['player7'],
             self.political_relations['player8'],) = struct.unpack('=8f', self.fh.read(32))
            
            (self.data1,
             self.start_pos_se,
             self.start_pos_sw,
             self.unknown3,
             self.allies,
             self.lock_politics,
             self.data2,) = struct.unpack(f'=4192sff12sBxxxBxxx{250 + size_factor}s', self.fh.read(4470 + size_factor))
        
    def pack(self):
        data = b''
        data += struct.pack(f'<3I15sIffIB{len(self.sai_name)}s',
                            self.unknown0,
                            self.size0,
                            self.size1,
                            self.name.encode('ascii'),
                            self.faction,
                            self.unknown1,
                            self.starting_gold,
                            int(self.is_active),
                            len(self.sai_name),
                            self.sai_name,)
        
        if self.name == "Independent":
            data += struct.pack(f'<{len(self.data0)}s', self.data0)
        else:
            print(f'start_pos : ({self.start_pos_se}, {self.start_pos_sw})')
            data += struct.pack(f'<10f4s8f4192sff12sBxxxBxxx{len(self.data2)}s',
                                self.economy['gold'],
                                self.economy['unknown1'],
                                self.economy['stone'],
                                self.economy['unknown2'],
                                self.economy['wood'],
                                self.economy['unknown3'],
                                self.economy['iron'],
                                self.economy['unknown4'],
                                self.economy['mana'],
                                self.economy['unknown5'],
                                self.unknown2,
                                self.political_relations['player1'],
                                self.political_relations['player2'],
                                self.political_relations['player3'],
                                self.political_relations['player4'],
                                self.political_relations['player5'],
                                self.political_relations['player6'],
                                self.political_relations['player7'],
                                self.political_relations['player8'],
                                self.data1,
                                self.start_pos_se,
                                self.start_pos_sw,
                                self.unknown3,
                                self.allies,
                                self.lock_politics,
                                self.data2,)
        return data

class MapObj:
    def __init__(self, in_fh, TYPE):
        self.fh = in_fh
        self.TYPE_ref = TYPE
        print(f'reading header @ {self.fh.tell()}')
        self.header = self.ObjectHeader(self.fh)
                
    class ObjectHeader:
        def __init__(self, fh):
            (self.obj_class,
             self.player,
             self.index,
             self.editor_id,
             self.hotspot_se,
             self.hotspot_sw,) = struct.unpack('=BBHIff', fh.read(16))
    
        def pack(self):
            return struct.pack('BBHIff',
                               self.obj_class,
                               self.player,
                               self.index,
                               self.editor_id,
                               self.hotspot_se,
                               self.hotspot_sw,)
    
    def pack(self):
        return self.header.pack()
    
    def __repr__(self):
        return f'{self.TYPE_ref.by_index[self.header.index]["name"]} @ ({self.header.hotspot_se}),({self.header.hotspot_sw},) player {self.header.player}\n'


class Building(MapObj):
    
    class MilitiaData:
        def __init__(self, fh):
            (self.padding,
             self.supply_zone,
             self.unknown1,
             self.current,
             self.regen_rate,
             self.unknown2,
             self.guard_zone,
             self.unknown3,
             self.front_index,
             self.support_index,
             self.company_size,
             self.comp_name_len,) = struct.unpack('=5sf8sff9sf5sHHBB', fh.read(49))
            (self.company_name,) = struct.unpack(f'={self.comp_name_len}s', fh.read(self.comp_name_len))
            (self.max,) = struct.unpack('=f', fh.read(4))
            
        def pack(self):
            data = struct.pack('<5sf8sff9sf5sHHBB',
                               self.padding,
                               self.supply_zone,
                               self.unknown1,
                               self.current,
                               self.regen_rate,
                               self.unknown2,
                               self.guard_zone,
                               self.unknown3,
                               self.front_index,
                               self.support_index,
                               self.company_size,
                               len(self.company_name),)
            data += struct.pack(f'<{len(self.company_name)}s', self.company_name,)
            data += struct.pack('<f', self.max,)
            return data
    
    class Modifiers:
        def __init__(self, fh):
            (self.start,
             self.size,
             self.group_1_commission_cost,
             self.group_1_commission_cost,
             self.group_1_commission_cost,
             self.group_1_commission_cost,
             self.militia_av,
             self.militia_dv,
             self.magic_resistance,
             self.non_magic_resistance,
             self.construction_cost,) = struct.unpack('=2I9f', fh.read(44))
            print(f'    Modifiers: size: {self.size}')
            if self.size > 36:
                (self.khaldunite_resistance,
                 self.padding,) = struct.unpack(f'=f{self.size-40}s', fh.read(4+self.size-40))
        
        def pack(self):
            data = struct.pack('<9f',
                               self.group_1_commission_cost,
                               self.group_1_commission_cost,
                               self.group_1_commission_cost,
                               self.group_1_commission_cost,
                               self.militia_av,
                               self.militia_dv,
                               self.magic_resistance,
                               self.non_magic_resistance,
                               self.construction_cost,)
            if hasattr(self, 'khaldunite_resistance'):
                data += struct.pack(f'<f{len(self.padding)}s',
                                    self.khaldunite_resistance,
                                    self.padding,)
            return struct.pack('<2I', self.start, len(data)) + data
    
    def __init__(self, in_fh, TYPE):
        MapObj.__init__(self, in_fh, TYPE)
        (self.name,
         self.flag1,
         self.flag2,) = struct.unpack('=20sBB', self.fh.read(22))
        if self.flag2 == 13:
            (self.current_hp,) = struct.unpack('=f', self.fh.read(4))
        elif self.flag2 == 7:
            (self.unknown_flag_data,) = struct.unpack('=B', self.fh.read(1))
        
        (self.unknown1,
         self.status,
         self.unknown2,
         self.pos_se,
         self.pos_sw,
         self.current_gold_production,
         self.current_stone_production,
         self.current_wood_production,
         self.current_iron_production,
         self.current_mana_production,
         self.unknown3,
         self.max_hp,
         self.unknown4,
         self.booty_value,) = struct.unpack('=12sBfHHfffffcf4sf', self.fh.read(54))
        
        #print(f'uk0name: {self.name}, player: {self.player}, index: {self.index}, id: {self.editor_id}, hs_sw: {self.hotspot_sw}, hs_se: {self.hotspot_se}')
        match self.TYPE_ref.by_index[self.header.index]['subtype']:
            # Ruins
            case 0:
                (self.ruin_data,) = struct.unpack('=13s', self.fh.read(13))
            
            # Settlements
            case 1|5|6|7|8:
                self.militia = self.MilitiaData(self.fh)
                if self.fh.read(1) == b'\x00':
                    uk5_size = 10
                else:
                    uk5_size = 9
                self.fh.seek(-1, 1)
                (self.unknown5,
                 self.component_bitflag,
                 self.unknown6,
                 self.inportant0) = struct.unpack(f'={uk5_size}sB4sI', self.fh.read(uk5_size+9))
                
                # this padding is different sizes with no apparent flags, so scan ahead to find 0xA040
                pad_len = findBytes(b'\xA0\x40', self.fh) - self.fh.tell() + 6
                (self.padding0,
                 self.upgrade_index,) = struct.unpack(f'={pad_len}sHxxxx', self.fh.read(pad_len+6))
                
                print(f'  reading building mods @ {self.fh.tell()}')
                self.building_modifiers = self.Modifiers(self.fh)
                
                (self.important1,
                 self.num_modifiers) = struct.unpack('=2I', self.fh.read(8))
                self.modifiers_gained = []
                if self.num_modifiers == 0:
                    (self.block_2,) = struct.unpack('=5s', self.fh.read(5))
                else:
                    print(f'nm:{self.num_modifiers}')
                    for _ in range (self.num_modifiers):
                        new_mod = {}
                        (new_mod['id'],
                         new_mod['value'],
                         new_mod['null'],) = struct.unpack('=HfB', self.fh.read(7))
                        self.modifiers_gained.append(new_mod)
                        
                    (self.unknown,
                     self.upgrade_cost) = struct.unpack('=Bf', self.fh.read(5))
                    
                self.components = []
                self.ct_components = 0
                # Counts the number of high bits in the bitflag
                x = self.component_bitflag
                for _ in range(0,8):
                    self.ct_components += x&1
                    x >>= 1
                print(f' comp_flag {self.component_bitflag} yielded {self.ct_components} componenets')
                # +1 for adtl blank comp
                print(f'  reading comps @ {self.fh.tell()}')
                for i in range(self.ct_components + 1):
                    new_comp = {}
                    print(f'    reading comp @ {self.fh.tell()}')
                    if (check_cost := struct.unpack('=f', self.fh.read(4))[0]) > 1:
                        new_comp['component_cost'] = check_cost
                    else:
                        self.fh.seek(-4, 1)
                    
                    (new_comp['size'],) = struct.unpack('=I', self.fh.read(4))
                    upgrade_name = struct.unpack('=20s', self.fh.read(20))[0].split(sep=b'\00', maxsplit=1)[0]
                    print(f'    un:{upgrade_name} {len(upgrade_name)}')
                    self.fh.seek(-20 + len(upgrade_name), 1)
                    if len(upgrade_name) > 1:
                        new_comp['upgrade_name'] = upgrade_name
                    #TODO adjust size of 'data' to account for name length
                    (new_comp['data'],) = struct.unpack(f"={new_comp['size']}s", self.fh.read(new_comp['size']))
                    self.components.append(new_comp)
            case 2:
                self.militia = self.MilitiaData(self.fh)
                # Skips null bytes
                self.padding0 = b''
                while self.fh.read(1) == b'\x00':
                    self.padding0 += b'\x00'
                self.fh.seek(-1,1)
                
            case 3:
                self.militia = self.MilitiaData(self.fh)
                (self.unknown5,) = struct.unpack('=17s', self.fh.read(17))
                
            case 4:
                (self.unknown5,
                 self.base_gold_production,
                 self.base_stone_production,
                 self.base_wood_production,
                 self.base_iron_production,
                 self.base_mana_production,) = struct.unpack('=26sfffff', self.fh.read(46))
    
    def pack(self):
        #print(f'edtr_id:{self.header.editor_id} type:{self.TYPE_ref.by_index[self.header.index]} se:{self.header.hotspot_se} sw:{self.header.hotspot_sw}')
        data = self.header.pack()
        
        data += struct.pack('<20sBB',
                            self.name,
                            self.flag1,
                            self.flag2,)
        if self.flag2 == 13:
            data += struct.pack('<f', self.current_hp,)
        elif self.flag2 == 7:
            data += struct.pack('<B', self.unknown_flag_data,)
        
        data += struct.pack('<12sBfHHfffffcf4sf',
                            self.unknown1,
                            self.status,
                            self.unknown2,
                            self.pos_se,
                            self.pos_sw,
                            self.current_gold_production,
                            self.current_stone_production,
                            self.current_wood_production,
                            self.current_iron_production,
                            self.current_mana_production,
                            self.unknown3,
                            self.max_hp,
                            self.unknown4,
                            self.booty_value,)
        
        match self.TYPE_ref.by_index[self.header.index]['subtype']:
            # Ruins
            case 0:
                data += struct.pack('<13s', self.ruin_data,)
            
            # Settlements
            case 1|5|6|7|8:
                data += self.militia.pack()
                
                data += struct.pack(f'<10sB4sI{len(self.padding0)}sHxxxx',
                                    self.unknown5,
                                    self.component_bitflag,# TODO Calculate correct flag in case components have changed
                                    self.unknown6,
                                    self.inportant0,
                                    self.padding0,
                                    self.upgrade_index,)
                
                data += self.building_modifiers.pack()
                
                data += struct.pack('<2I',
                                    self.important1,
                                    len(self.modifiers_gained),)
                if len(self.modifiers_gained) == 0:
                    data += struct.pack('<5s', self.block_2,)
                else:
                    for mod in self.modifiers_gained:
                        data += struct.pack('<HfB',
                                            mod['id'],
                                            mod['value'],
                                            mod['null'],)
                    data += struct.pack('<Bf',
                                        self.unknown,
                                        self.upgrade_cost,)
                
                for comp in self.components:
                    if 'component_cost' in comp:
                        data += struct.pack('<f', comp['component_cost'])
                    data += struct.pack('<I',comp['size'],)
                    if 'upgrade_name' in comp:
                        data += struct.pack('<20s', comp['upgrade_name'])
                    data += struct.pack(f"<{len(comp['data'])}s", comp['data'],)
            case 2:
                data += self.militia.pack()
                data += struct.pack(f'<{len(self.padding0)}s', self.padding0,)
            case 3:
                data += self.militia.pack()
                data += struct.pack('<17s', self.unknown5,)
            case 4:
                data += struct.pack('<26sfffff',
                                    self.unknown5,
                                    self.base_gold_production,
                                    self.base_stone_production,
                                    self.base_wood_production,
                                    self.base_iron_production,
                                    self.base_mana_production,)
        return data        


class Company(MapObj):  
    def __init__(self, in_fh, TYPE):
        MapObj.__init__(self, in_fh, TYPE)
        
        (self.captain_index,
         self.front_index,
         self.support1_index,
         self.support2_index,
         self.b1,
         self.b2,
         self.b3,
         self.b4,
         self.name,) = struct.unpack('=4H4B22s', self.fh.read(34))
        
        (self.uk0,
         self.captain_id,
         self.occupy_flag0,
         self.control_zone,
         self.occupy_flag1,
         self.required,
         self.uk2,
         stone,
         wood,
         iron,
         mana,
         self.speed,
         self.f0,
         self.f1,
         self.attack_efficiency,
         self.formation_atk_mod,
         self.f4,
         self.experience,
         self.uk3,
         self.current_morale,
         self.max_morale,
         self.uk4,
         self.zone_of_control,
         self.uk4_5,
         self.slowest_unit,) = struct.unpack('=6sHIfII4s11f13s2f16sf12sB', self.fh.read(126))
        
        self.upkeep = {
            'stone': stone,
            'wood': wood,
            'iron': iron,
            'mana': mana,
            }
        
        # Find padding bytes & beginning of company mods, subtract back to start of unit positions
        zoc_to_pos_size = findBytes(b'\x00\x00\x00\x00\x04\x00\x00\x00', self.fh, search_start=100) - self.fh.tell() - 48
        
        print(f'ztps:{zoc_to_pos_size}')
        (self.zoc_to_pos,
         u0_pos_se,
         u0_pos_sw,
         u1_pos_se,
         u1_pos_sw,
         u2_pos_se,
         u2_pos_sw,
         u3_pos_se,
         u3_pos_sw,
         u4_pos_se,
         u4_pos_sw,
         u5_pos_se,
         u5_pos_sw,) = struct.unpack(f'={zoc_to_pos_size}s12f4x', self.fh.read(zoc_to_pos_size + 52))
        
        self.unit_positions = [
            {'se': u0_pos_se,
             'sw': u0_pos_sw,},
            {'se': u1_pos_se,
             'sw': u1_pos_sw,},
            {'se': u2_pos_se,
             'sw': u2_pos_sw,},
            {'se': u3_pos_se,
             'sw': u3_pos_sw,},
            {'se': u4_pos_se,
             'sw': u4_pos_sw,},
            {'se': u5_pos_se,
             'sw': u5_pos_sw,},
            ]
        
        (start, num_modifiers,) = struct.unpack('=II', self.fh.read(8))
        self.company_modifiers_provided = [('start', start)]
        print(f'  start: {start}, num: {num_modifiers} @ {self.fh.tell()}')
        for _ in range(num_modifiers):
            (key, value,) = struct.unpack('=Hfx', self.fh.read(7))
            self.company_modifiers_provided.append((comp_mods_lookup[key], value,))
        
        (start, num_modifiers,) = struct.unpack('=II', self.fh.read(8))
        self.unit_modifiers_provided = [('start', start),]
        for _ in range(num_modifiers):
            (key, value,) = struct.unpack('=Hfx', self.fh.read(7))
            self.unit_modifiers_provided.append((unit_mods_lookup[key], value,))
        self.fh.seek(4, 1) # skips 4byte padding
        
        (start,)  = struct.unpack('=8s', self.fh.read(8))
        self.modifiers_gained = deepcopy(comp_mods_default)
        self.modifiers_gained['start'] = start
        for m in comp_mods_lookup.values():
            (self.modifiers_gained[m][0],) = struct.unpack('=f', self.fh.read(4))
        
        (self.unknown_mod,
         self.uk6,
         self.num_units,) = struct.unpack('=f13sI', self.fh.read(21))
        
        self.units = [Unit(self.fh, self.TYPE_ref) for _ in range(self.num_units)]
        
        (self.f11,
         self.f12,
         self.detection_zone,
         self.uk7,
         self.f13,) = struct.unpack('=ff9sff', self.fh.read(25))
        
    def pack(self):
        data = self.header.pack()
        data += struct.pack('<4H4B22s',
                            self.captain_index,
                            self.front_index,
                            self.support1_index,
                            self.support2_index,
                            self.b1,
                            self.b2,
                            self.b3,
                            self.b4,
                            self.name,)
        data += struct.pack('<6sHIfII4s11f13s2f16sf12sB',
                            self.uk0,
                            self.captain_id,
                            self.occupy_flag0,
                            self.control_zone,
                            self.occupy_flag1,
                            self.required,
                            self.uk2,
                            self.upkeep['stone'],
                            self.upkeep['wood'],
                            self.upkeep['iron'],
                            self.upkeep['mana'],
                            self.speed,
                            self.f0,
                            self.f1,
                            self.attack_efficiency,
                            self.formation_atk_mod,
                            self.f4,
                            self.experience,
                            self.uk3,
                            self.current_morale,
                            self.max_morale,
                            self.uk4,
                            self.zone_of_control,
                            self.uk4_5,
                            self.slowest_unit,)
        data += struct.pack(f'={len(self.zoc_to_pos)}s12f4x',
                            self.zoc_to_pos,
                            self.unit_positions[0]['se'],
                            self.unit_positions[0]['sw'],
                            self.unit_positions[1]['se'],
                            self.unit_positions[1]['sw'],
                            self.unit_positions[2]['se'],
                            self.unit_positions[2]['sw'],
                            self.unit_positions[3]['se'],
                            self.unit_positions[3]['sw'],
                            self.unit_positions[4]['se'],
                            self.unit_positions[4]['sw'],
                            self.unit_positions[5]['se'],
                            self.unit_positions[5]['sw'],)
        
        data += struct.pack('=II',
                            self.company_modifiers_provided[0][1],
                            len(self.company_modifiers_provided[1:]),)
        for name, value in self.company_modifiers_provided[1:]:
            code = next(k for k, v in comp_mods_lookup.items() if v == name)
            data += struct.pack('<Hfx',
                                code,
                                value)
            
        data += struct.pack('=II',
                            self.unit_modifiers_provided[0][1],
                            len(self.unit_modifiers_provided[1:]),)
        for (name, value,) in self.unit_modifiers_provided[1:]:
            code = next(k for k, v in unit_mods_lookup.items() if v == name)
            data += struct.pack('<Hfx',
                                code,
                                value)
        data += struct.pack('<4x')
        
        data += struct.pack('<8s', self.modifiers_gained['start'])
        for name, value in self.modifiers_gained.items():
            if name != 'start':
                data += struct.pack('<f', value[0])
        
        data += struct.pack('<f13sI',
                            self.unknown_mod,
                            self.uk6,
                            self.num_units,)
        
        for unit in self.units:
            data += unit.pack()
        
        data += struct.pack('<ff9sff',
                            self.f11,
                            self.f12,
                            self.detection_zone,
                            self.uk7,
                            self.f13,)
        return data
            
        
class Unit(MapObj):
    def __init__(self, in_fh, TYPE):
        (self.unit_index,) = struct.unpack('=B', in_fh.read(1))
              
        MapObj.__init__(self, in_fh, TYPE)
        
        (self.flag1, self.flag2,) = struct.unpack('=BB', self.fh.read(2))
        self.current_hp = None
        match self.flag2:
            case 0x09:
                (self.current_hp,
                 self.uk0,) = struct.unpack('=fH', self.fh.read(6))
            case 0x0B:
                (self.uk0,) = struct.unpack('=H', self.fh.read(2))
            case 0x0D:
                (self.current_hp,) = struct.unpack('=f', self.fh.read(4))
        
        (self.uk1,
         self.pos_se,
         self.pos_sw,
         self.f0,
         self.f1,
         self.f2,
         self.f3,
         self.f4,
         self.current_speed0,
         self.uk2,
         self.current_speed1,
         self.uk2_5,
         start,
         modifiers_size,) = struct.unpack('=24sHH6f22sf16sII', self.fh.read(102))
        
        self.modifiers_gained = deepcopy(unit_mods_default)
        self.modifiers_gained['start'] = start
        for m in unit_mods_default.keys():
            (self.modifiers_gained[m][0],) = struct.unpack('=f', self.fh.read(4))
        
        (self.f5,
         self.uk3,
         self.hotspot_se,
         self.hotspot_sw,
         self.f6,
         self.f7,
         self.base_speed,) = struct.unpack('=4xf32s5f', self.fh.read(60))
        
        start_search = in_fh.tell();
        hp_pos = findBytes(b'\x00\x40\x40\x00\x00\x00\x00\x01', self.fh, search_length=100) + 8
        (self.uk4,
         self.max_hp,) = struct.unpack(f'={hp_pos-start_search}sf', self.fh.read(4+hp_pos-start_search))
        
        match self.TYPE_ref.by_index[self.header.index]['subtype']:
            case 1:
                (self.f8,
                 self.mana,
                 self.uk5,) = struct.unpack('=ff5s', self.fh.read(13))
            case 2:
                (self.f8,
                 self.mana,
                 self.uk5,) = struct.unpack('=ff9s', self.fh.read(17))
    
    def pack(self):
        data = b''
        data += struct.pack('<B', self.unit_index,)
        data += self.header.pack()
        data += struct.pack('<BB', self.flag1, self.flag2,)
        
        match self.flag2:
            case 0x09:
                 data += struct.pack('<fH', self.current_hp, self.uk0,)
            case 0x0B:
                data += struct.pack('<H', self.uk0,)
            case 0x0D:
                data += struct.pack('<f', self.current_hp,)
        data += struct.pack('<24sHH6f22sf16sII',
                            self.uk1,
                            self.pos_se,
                            self.pos_sw,
                            self.f0,
                            self.f1,
                            self.f2,
                            self.f3,
                            self.f4,
                            self.current_speed0,
                            self.uk2,
                            self.current_speed1,
                            self.uk2_5,
                            self.modifiers_gained['start'],
                            (len(self.modifiers_gained) - 1) * 4,)
        for k, v in self.modifiers_gained.items():
            if k != 'start':
                data += struct.pack('f', v[0])
        data += struct.pack(f'<if32s5f{len(self.uk4)}sf',
                            0,
                            self.f5,
                            self.uk3,
                            self.hotspot_se,
                            self.hotspot_sw,
                            self.f6,
                            self.f7,
                            self.base_speed,
                            self.uk4,
                            self.max_hp,)
        #print(f'unit index: {self.unit_index}, index: {self.header.index}, type: {self.TYPE_ref.by_index[self.header.index]["type"]}, subtype: {self.TYPE_ref.by_index[self.header.index]["subtype"]}')
        match self.TYPE_ref.by_index[self.header.index]['subtype']:
            case 1:
                data += struct.pack('<ff5s',
                                    self.f8,
                                    self.mana,
                                    self.uk5,)
            case 2:
                data += struct.pack('<ff9s',
                                    self.f8,
                                    self.mana,
                                    self.uk5,)
        return data
    

class Misc(MapObj):
    def __init__(self, in_fh, TYPE):
        MapObj.__init__(self, in_fh, TYPE)
        if self.header.index != 0xFFFF:
            (self.flag1, self.flag2,) = struct.unpack('=BB', self.fh.read(2))
            if self.flag2 == 0x0B:
                (self.s0,) = struct.unpack('=H', self.fh.read(2))
            match self.TYPE_ref.by_index[self.header.index]['subtype']:
                    case 0:
                        (self.data,) = struct.unpack('4s', self.fh.read(4))
                    case 1:
                        (self.data,) = struct.unpack('4s', self.fh.read(25))
                    case 2:
                        (self.data,) = struct.unpack('4s', self.fh.read(25))
    
    def pack(self):
        data = self.header.pack()
        if self.header.index != 0xFFFF:
            data += struct.pack('<BB', self.flag1, self.flag2,)
            if self.flag2 == 0x0B:
                data += struct.pack('<H', self.s0,)
            data += struct.pack(f'<{len(self.data)}s', self.data)
        
        return data

class Feature(MapObj):
    def __init__(self, in_fh, TYPE):
        MapObj.__init__(self, in_fh, TYPE)
        if self.header.index != 0xFFFF:
            (self.flag1, self.flag2,) = struct.unpack('=BB', self.fh.read(2))
            if self.flag1 == 0x09 and self.flag2 == 0x0F:
                (self.data,) = struct.unpack('4s', self.fh.read(4))
    
    def pack(self):
        data = self.header.pack()
        if self.header.index != 0xFFFF:
            data += struct.pack('<BB', self.flag1, self.flag2,)
            if self.flag1 == 0x09 and self.flag2 == 0x0F:
                data += struct.pack('<4s', self.data,)
        return data
        
def findBytes(query, fh, search_start=None ,search_length=None):
    start_pos = fh.tell()
    if search_start:
        fh.seek(search_start, 1)
    cur_val = fh.read(len(query))
    while cur_val != query:
        if search_length and fh.tell() - start_pos > search_length:
            return None
        cur_val = cur_val[1:] + fh.read(1)
    
    find_pos = fh.tell() - len(query)
    fh.seek(start_pos)
    return find_pos

def getMapObjClass(in_fh):
    (obj_class,) = struct.unpack('=B', in_fh.read(1))
    in_fh.seek(-1, 1)
    print(type(obj_class))
    print(f'obj_class: {obj_class:#x} @ {in_fh.tell()}')
    match obj_class:
        case 0x10:
            return Misc
        case 0x24:
            return Building
        case 0x3C:
            return Company
        case _:
            return MapObj
         
def addChunkPadding(data, force=False):
    final_modulo = 5 if force == True else 4
    padding = b'\x00' * ((4 - len(data) % 4) % final_modulo)
    print(f'Padding Length: {len(padding)}')
    return data + padding
                
                
#testTGM = tgmFile('ECM1-CLEANED.TGM')
#testTGM.load()
#testTGM.write('write-test.tgm')
#for obj in testTGM.TYPE.objs.values():
#    print(obj)

#for obj in testTGM.OBJS.objs:
#    print(obj)

#print(testTGM.OBJS.objs[30].base_iron_production)
#for child in testTGM.iff.data.children: print(f'{child.type}')


