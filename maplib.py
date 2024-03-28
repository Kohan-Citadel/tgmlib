#!/usr/bin/python

import typing
from enum import Enum
from configparser import ConfigParser
import re
#class UnitModifiers(Enum):
    

class KohanMap:
    def __init__(self, size: int):
        # Keeps track of what ID to assign to the next object
        self.next_id = 0
        self.size = size
        self.terrain = MapGrid(self.size)
        # Use editor ID as key for lookup
        self.objects = {}
        self.features = {}


class MapGrid:
    def __init__(self, size):
        self.size = size
        self.cells = [GridCell() for _ in range(self.size**2)]
        
class GridCell:
    '''A class representing a single grid cell in a Kohan map.
    It stores the terrain type(s) and layout,
    as well as references to the objects & features located there'''
    def __init__(self):
        self.terrain1 = 'grass'
        self.terrain2 = 'grass'
        self.layout = 0
        self.objects = [] # list of refs to objects occupying this tile
        self.features = [] # list of refs to features occupying this tile

class MapObject:
    '''A class representing an Object in a Kohan map.
    This can be either a Building or a Company.'''
    pass

class Building(MapObject):
    '''A class representing a Building Object in a Kohan map.
    This inherits from MapObject.'''
    pass

class Company(MapObject):
    '''A class representing a Company Object in a Kohan map.
    Contains a list of Unit objects.
    This inherits from MapObject.'''
    pass

class Unit:
    '''Class representing a single unit in a Company Object.
    Data is loaded from the cooresponding unit INI.'''
    def __init__(self, name):
        self.name = name
        unit_ini = ConfigParser(inline_comment_prefixes=(';',))
        unit_ini.read(f'./Data/ObjectData/Units/{name}.INI')
        self.display_name = unit_ini['ObjectData']['ProperName']
        self.unit_class = int(unit_ini['ObjectData']['Class'])
        self.sprite = f"./Art/Objects/{unit_ini['ObjectData']['Sprite']}"
        self.max_hp = float(unit_ini['ObjectData']['MaxHitPoints'])
        self.current_hp = self.max_hp
        
        self.upkeep = {
            'stone':    0,
            'wood':     0,
            'iron':     0,
            'mana':     0,
        }
        upkeep_re = re.compile(r"upkeep(stone|wood|iron|mana)")
        for k, v in unit_ini['ObjectData'].items():
            m = upkeep_re.match(k)
            if m:
                self.upkeep[m.group(1).lower()] = float(v)
                
        self.default_captain = unit_ini['UnitData']['Captain']
        self.banner_frame = unit_ini['UnitData']['BannerFrame']
        self.movement_speed = float(unit_ini['UnitData']['MovementRate'])
        
        # Use the names from BONUS.INI as keys
        self.modifiers_gained = {}
        self.modifiers_provided = {}
        for k, v in unit_ini['ElementBonus'].items():
            self.modifiers_gained[k] = v
        for k, v in unit_ini['SupportBonus'].items():
            self.modifiers_provided[k] = v
            
        self.morale = unit_ini['CompanyData']['Morale']
        self.visual_range = unit_ini['CompanyData']['VisualRange']
        self.control_zone = unit_ini['CompanyData']['ControlZone']
        self.entrenchment_rate = unit_ini['CompanyData']['EntrenchmentRate']
        
        if self.unit_class == 1:
            self.current_mana = unit_ini['SpellData']['MaxMana']

class MapFeature:
    '''A class representing a Feature in a Kohan Map.'''
    pass
        
        