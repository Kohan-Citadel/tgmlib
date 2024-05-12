#!/usr/bin/python

import ifflib
import struct
from pathlib import Path
from dataclasses import dataclass, field
from pprint import pprint

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
        
        
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[2].data_offset)
                # Skips unknown bytes
                (self.unknown1,) = struct.unpack('4s', in_fh.read(4))
                (self.name_len,) = struct.unpack('B', in_fh.read(1))
                (self.map_name,) = struct.unpack(f'{self.name_len}s', in_fh.read(self.name_len))
                (self.desc_len,) = struct.unpack('B', in_fh.read(1))
                (self.map_description,) = struct.unpack(f'{self.desc_len}s', in_fh.read(self.desc_len))
                # Skips unknown bytes
                (self.size_se,
                 self.size_sw,
                 self.deathmatch_teams,
                 self.custom_play_kingdoms,
                 self.scenario_deathmatch_kingdoms,) = struct.unpack('III8xI4xI4x', in_fh.read(36))
                
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
            return
    class MgrdChunk:
        def __init__(self, filename: str, iff: ifflib.iff_file, EDTR):
            with open(filename, "rb") as in_fh:
                # Skip required, fixed int at begining of chunk
                in_fh.seek(iff.data.children[4].data_offset + 4)
                print(f'Reading first tile @ {in_fh.tell()}')
                self.tiles = [self.GridTile(*struct.unpack('>BB', in_fh.read(2))) for _ in range(EDTR.size_se*EDTR.size_sw)]
                
        class GridTile:
            def __init__(self, terrain, layout):
                self._terrain = terrain
                self._layout = layout
                self.terrain1 = terrain >> 4
                self.terrain2 = terrain & 15
                self.display = layout >> 4
                self.layout = layout & 15
                
    
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
            return
    
    class PlrsChunk:
        
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[15].data_offset)
                (unknown0,) = struct.unpack('I', in_fh.read(4))
                
                self.players = []
                for i in range(0, 8):
                    start_pos = in_fh.tell()
                    new_player = {}
                    (new_player['unknown'],
                     new_player['unknown0'],) = struct.unpack('I8s', in_fh.read(12))
                    print(f'pos: {in_fh.tell()}')
                    new_player['name'] = struct.unpack('=15s', in_fh.read(15))[0].rstrip(b'\x00').decode('utf-8')
                    print(new_player['name'])
                    (new_player['faction'],
                     new_player['unknown1'],
                     new_player['sai_len'],) = struct.unpack('=B12sxxxB', in_fh.read(17))
                    print(new_player['sai_len'])
                    (new_player['sai_name'],) = struct.unpack(f'={new_player["sai_len"]}s', in_fh.read(new_player['sai_len']))
                    in_fh.seek(start_pos+4597)
                    self.players.append(new_player)
            return
        
    class ObjsChunk:
        
        class MapObj:
            
            class ObjectHeader:
                def __init__(self, in_fh):
                    (self.obj_class,
                     self.player,
                     self.index,
                     self.editor_id,
                     self.hotspot_se,
                     self.hotspot_sw,) = struct.unpack('=BBHIff', in_fh.read(16))
            
            
            
            class Building:
                
                class MilitiaData:
                    def __init__(self, in_fh):
                        (self.padding,
                         self.supply_zone,
                         self.unknown1,
                         self.current_militia,
                         self.militia_regen,
                         self.unknown2,
                         self.guard_zone,
                         self.unknown3,
                         self.militia_front,
                         self.militia_support,
                         self.company_size,
                         self.comp_name_len,) = struct.unpack('=5sf8sff9sf5sHHBB', in_fh.read(49))
                        (self.company_name,) = struct.unpack(f'={self.comp_name_len}s', in_fh.read(self.comp_name_len))
                        (self.max_militia,) = struct.unpack('=f', in_fh.read(4))
                
                class Modifiers:
                    def __init__(self, in_fh):
                        (self.size,
                         self.group_1_commission_cost,
                         self.group_1_commission_cost,
                         self.group_1_commission_cost,
                         self.group_1_commission_cost,
                         self.militia_av,
                         self.militia_dv,
                         self.magic_resistance,
                         self.non_magic_resistance,
                         self.construction_cost,) = struct.unpack('=I9f', in_fh.read(40))
                        if self.size > 36:
                            (self.kaldunite_resistance,
                             self.padding,) = struct.unpack(f'=f{self.size-40}s', in_fh.read(4+self.size-40))
                
                
                        
                
                def __init__(self, in_fh, TYPE, header):
                    (self.name,
                     self.flag1,
                     self.flag2,) = struct.unpack('=20sBB', in_fh.read(22))
                    if self.flag2 == 13:
                        (self.current_hp,) = struct.unpack('=f', in_fh.read(4))
                    elif self.flag2 == 7:
                        (self.unknown_flag_data,) = struct.unpack('=B', in_fh.read(1))
                    
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
                     self.booty_value,) = struct.unpack('=12sBfHHfffffcf4sf', in_fh.read(54))
                    
                    #print(f'uk0name: {self.name}, player: {self.player}, index: {self.index}, id: {self.editor_id}, hs_sw: {self.hotspot_sw}, hs_se: {self.hotspot_se}')
                    match TYPE.by_index[header.index]['subtype']:
                        # Ruins
                        case 0:
                            (self.ruin_data,) = struct.unpack('=13s', in_fh.read(13))
                        
                        # Settlements
                        case 1|5|6|7|8:
                            self.militia_data = self.MilitiaData(in_fh)
                            
                            (self.unknown5,
                             self.component_bitflag,
                             self.unknown6,
                             self.inportant0) = struct.unpack('=10sB4sI', in_fh.read(19))
                            
                            # this padding is different sizes with no apparent flags, so scan ahead to find 0xA040
                            start_pos = in_fh.tell()
                            while in_fh.read(2) != b'\xA0\x40':
                                in_fh.seek(-1, 1)
                            pad_len = in_fh.tell() - start_pos
                            in_fh.seek(start_pos)
                            (padding,) = struct.unpack(f'={pad_len+14}s', in_fh.read(pad_len+14))
                            print(f'  reading building mods @ {in_fh.tell()}')
                            self.building_modifiers = self.Modifiers(in_fh)
                            
                            (self.important1,
                             self.num_modifiers) = struct.unpack('=2I', in_fh.read(8))
                            if self.num_modifiers == 0:
                                (self.block_2,) = struct.unpack('=5s', in_fh.read(5))
                            else:
                                self.gained_modifiers = []
                                print(f'nm:{self.num_modifiers}')
                                for _ in range (self.num_modifiers):
                                    new_mod = {}
                                    (new_mod['id'],
                                     new_mod['value'],
                                     new_mod['null'],) = struct.unpack('=HfB', in_fh.read(7))
                                    
                                (self.unknown,
                                 self.upgrade_cost) = struct.unpack('=Bf', in_fh.read(5))
                                
                            self.components = []
                            self.ct_components = 0
                            # Counts the number of high bits in the bitflag
                            x = self.component_bitflag
                            for _ in range(0,8):
                                self.ct_components += x&1
                                x >>= 1
                            # +1 for adtl blank comp
                            print(f'  reading comps @ {in_fh.tell()}')
                            for i in range(self.ct_components + 1):
                                new_comp = {}
                                print(f'    reading comp @ {in_fh.tell()}')
                                if (check_cost := struct.unpack('=f', in_fh.read(4))[0]) > 1:
                                    new_comp['component_cost'] = check_cost
                                else:
                                    in_fh.seek(-4, 1)
                                
                                (new_comp['size'],) = struct.unpack('=I', in_fh.read(4))
                                upgrade_name = struct.unpack('=20s', in_fh.read(20))[0].split(sep=b'\00', maxsplit=1)[0]
                                print(f'    un:{upgrade_name} {len(upgrade_name)}')
                                in_fh.seek(-20 + len(upgrade_name), 1)
                                if len(upgrade_name) > 1:
                                    new_comp['upgrade_name'] = upgrade_name
                                (new_comp['data'],) = struct.unpack(f"={new_comp['size']}s", in_fh.read(new_comp['size']))
                                self.components.append(new_comp)
                        case 2:
                            self.militia_data = self.MilitiaData(in_fh)
                            # Skips null bytes
                            pad_size = 0
                            while in_fh.read(1) == b'\00':
                                pad_size += 1
                            in_fh.seek(-1,1)
                            
                        case 3:
                            self.militia_data = self.MilitiaData(in_fh)
                            (self.unknown5,) = struct.unpack('=17s', in_fh.read(17))
                            
                        case 4:
                            (self.unknown5,
                             self.base_gold_production,
                             self.base_stone_production,
                             self.base_wood_production,
                             self.base_iron_production,
                             self.base_mana_production,) = struct.unpack('=26sfffff', in_fh.read(46))
            
            class Company:
                
                class Unit:
                    def __init__(self, in_fh):
                        (self.unit_index,) = struct.unpack('=B', in_fh.read(1))
                        self.header = ObjsChunk.MapObj.ObjectHeader(in_fh)
                        (self.flag1, self.flag2,) = struct.unpack('=', buffer)
                        
                def __init__(self, in_fh):
                    (self.captain_index,
                     self.front_index,
                     self.support1_index,
                     self.support2_index,
                     self.b1,
                     self.b2,
                     self.b3,
                     self.b4,
                     self.name,) = struct.unpack('=4H4B22s', in_fh.read(34))
                    
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
                     self.uk5,
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
                     u5_pos_sw,
                     ) = struct.unpack('=6sHIfII4s11f13s2f16sf167s12fxxxx', in_fh.read(332))
                    
                    self.upkeep = {
                        'stone': stone,
                        'wood': wood,
                        'iron': iron,
                        'mana': mana,
                        }
                    
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
                    
                    (start, num_modifiers,) = struct.unpack('=II', in_fh.read(8))
                    self.company_modifiers_provided = {}
                    for _ in range(num_modifiers):
                        (key, value,) = struct.unpack('=Hfx', in_fh.read(7))
                        self.company_modifiers_provided[comp_mods_lookup[key]] = value
                    
                    (start, num_modifiers,) = struct.unpack('=II', in_fh.read(8))
                    self.unit_modifiers_provided = {}
                    for _ in range(num_modifiers):
                        (key, value,) = struct.unpack('=Hfx', in_fh.read(7))
                        self.unit_modifiers_provided[unit_mods_lookup[key]] = value
                    in_fh.seek(4, 1) # skips 4byte padding
                    
                    self.all_company_modifiers = {}
                    in_fh.seek(8, 1) # skips 8 'start' bytes
                    for m in comp_mods_lookup.values():
                        (self.all_company_modifiers[m],) = struct.unpack('=f', in_fh.read(4))
                    
                    (self.uk6,
                     self.num_units,) = struct.unpack('=13sI', in_fh.read(17))
                    
                    
                    
                    
                    
            
            # MapObj init
            def __init__(self, in_fh, TYPE):
                print(f'reading header @ {in_fh.tell()}')
                self.header = self.ObjectHeader(in_fh)
                
                
                match self.header.obj_class:
                    case 0x24:
                        self.data = self.Building(in_fh, TYPE, self.header)
                    case 0x3C:
                        self.data = self.Company(in_fh)
                        
                
                
                
                
        
        
        def __init__(self, filename: str, iff: ifflib.iff_file, TYPE):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[16].data_offset)
                self.unknown0 = struct.unpack('=4s', in_fh.read(4))
                self.objs = []
                
                #while in_fh.tell() < (iff.data.children[16].data_offset + iff.data.children[16].length - 18):
                for _ in range(6):
                    self.objs.append(self.MapObj(in_fh, TYPE))
                    #pprint(vars(self.objs[-1]))   
                    #print('')
                
                
    
    def load(self):
        match self.read_from:
            case '.TGM':
                self.iff.load()
                if self.iff.data.formtype != "TGSV":
                    print(f"Error: invalid file type: {self.iff.data.formtype}")
                self.EDTR = self.EdtrChunk(self.filename, self.iff)
                self.MGRD = self.MgrdChunk(self.filename, self.iff, self.EDTR)
                self.TYPE = self.TypeChunk(self.filename, self.iff)
                #self.PLRS = self.PlrsChunk(self.filename, self.iff)
                self.OBJS = self.ObjsChunk(self.filename, self.iff, self.TYPE)
        return

        
                
                
                
                
testTGM = tgmFile("../../hero-randomizer/bonehenge-KG.tgm")
testTGM.load()
#for obj in testTGM.TYPE.objs.values():
#    print(obj)

#for obj in testTGM.OBJS.objs:
#    print(obj)

#print(testTGM.OBJS.objs[30].base_iron_production)
#for child in testTGM.iff.data.children: print(f'{child.type}')


