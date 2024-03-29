#!/usr/bin/python

import typing
from enum import Enum
from configparser import ConfigParser
import re
from pathlib import Path
import math
from PIL import Image
import tgrtool
#class UnitModifiers(Enum):
class CompanyFormations(Enum):
    COMBAT = 0
    SKIRMISH = 1
    COLUMN = 2
    PRESSED = 3

X = 0
Y = 1

class Position:
    def __init__(self, se: float=0, sw: float=0):
        self.se = se
        self.sw = sw
    
    def set(self, se: float=0, sw: float=0):
        self.se = se
        self.sw = sw
    
    def copy(self):
        return Position(se=self.se, sw=self.sw)
    
    def to_pixels(self, size: int):
        self.x = int(35.77709 * (self.se * math.cos(-26.57*math.pi/180) + self.sw * math.cos(206.57*math.pi/180)) + (size/2 - 0.5) * 64)
        self.y = int(35.77709 * (self.se * math.sin(26.57*math.pi/180) + self.sw * math.sin(-206.57*math.pi/180)))
    
    def __str__(self):
        out = f'map coordinates: ({self.se}, {self.sw})'
        if hasattr(self, 'x'):
            out += f' pixel coordinate: ({self.x}, {self.y})'
        return out
        

class KohanMap:
    def __init__(self, size: int):
        # Keeps track of what ID to assign to the next object
        self.last_id = -1
        self.size = size
        self.terrain = MapGrid(self.size)
        # Use editor ID as key for lookup
        self.objects = {}
        self.features = {}
    
    def get_next_id(self):
        self.last_id += 1
        return self.last_id
    
    def render(self):
        self.size_x = self.size * 64
        self.size_y = self.size * 32
        rendered_map = Image.new('RGBA', (self.size_x, self.size_y), color=(0,0,0,0))
        ct = 0
        for cell in self.terrain.cells:
            cell.position.to_pixels(self.size)
            #print(cell.position.x, cell.position.y)
            if (ct // self.size) % 2 == 0:
                if ct % 2:
                    cell_img = Image.open(Path('../tile-imgs/0x2_border.png'))
                else:
                    cell_img = Image.open(Path('../tile-imgs/0x2_border2.png'))
            else:
                if ct % 2:
                    cell_img = Image.open(Path('../tile-imgs/0x2_border2.png'))
                else:
                    cell_img = Image.open(Path('../tile-imgs/0x2_border.png'))
                    
            rendered_map.paste(cell_img, (cell.position.x, cell.position.y, cell.position.x+64, cell.position.y+32), cell_img)
            ct+=1
        for obj in self.objects.values():
            sprite, box = obj.fetch_sprite()
            rendered_map.paste(sprite,box=box,mask=sprite)
            
        rendered_map.show()
    

class MapGrid:
    def __init__(self, size):
        self.size = size
        self.cells = [GridCell(Position(math.floor(i / self.size), i % self.size)) for i in range(self.size**2)]
        
class GridCell:
    '''A class representing a single grid cell in a Kohan map.
    It stores the terrain type(s) and layout,
    as well as references to the objects & features located there'''
    def __init__(self, position: Position):
        self.position = position.copy()
        self.terrain1 = 'grass'
        self.terrain2 = 'grass'
        self.layout = 0
        self.objects = [] # list of refs to objects occupying this tile
        self.features = [] # list of refs to features occupying this tile

class MapObject:
    '''A class representing an Object in a Kohan map.
    This can be either a Building or a Company.'''
    def __init__(self, Map: KohanMap, position: Position=Position(0,0), player: int=0):
        self.Map = Map
        self.id = self.Map.get_next_id()
        Map.objects[self.id] = self
        self.position = position.copy()
        self.player = player
        

class Building(MapObject):
    '''A class representing a Building Object in a Kohan map.
    This inherits from MapObject.'''
    pass

class Company(MapObject):
    '''A class representing a Company Object in a Kohan map.
    Contains a list of Unit objects.
    This inherits from MapObject.'''
    def __init__(self, Map: KohanMap, position, captain: str='CAPTAIN', front: str='FOOTMAN', support1=None, support2=None, player: int=0, formation: CompanyFormations=CompanyFormations.SKIRMISH):
        MapObject.__init__(self, Map, position=position, player=player)
        self.units = []
        self.units.append(Unit(captain, Map, self, self.player))
        self.units.extend([Unit(front, Map, self, self.player) for _ in range(0,4)])
        if support1:
            self.units.append(Unit(support1, Map, self, self.player))
        if support2:
            self.units.append(Unit(support2, Map, self, self.player))
        
        self.max_morale = self.units[1].morale
        self.current_morale = self.max_morale
        self.banner_icon = self.units[1].banner_frame
        self.formation = formation
    
    def place_units(self, heading=0):
        '''Sets unit positions relative to company position, using a layout based on formation.
        heading is counterclockwise rotation from east in degrees.'''
        formations = {
            CompanyFormations.COMBAT.value: [(0.5,-1.5), (1.5,-0.5), (-0.5,-2.5), (2.5,-0.5), (-1,-1.5), (1.5,1)],
            CompanyFormations.SKIRMISH.value: [(0.5,-1.5), (1.5,-0.5), (-1.5,0.5), (-0.5,1.5), (-1.5,-1.5), (1.5,1.5)],
            CompanyFormations.COLUMN.value: [(1.2,-1.2), (1.8,-1.8), (-1.2,1.2), (-1.8,1.8), (0.6,-0.6), (-0.6,0.6)],
            CompanyFormations.PRESSED.value: [(1.2,-1.2), (1.8,-1.8), (-1.2,1.2), (-1.8,1.8), (0.6,-0.6), (-0.6,0.6)],
        }
        
        heading = heading * math.pi / 180
        
        self.units[0].position = self.position.copy()
        
        for i, unit in enumerate(self.units[1:]):
            f = formations[self.formation.value][i]
            h = math.sqrt(math.pow(f[X],2) + math.pow(f[Y],2))
            theta = math.atan2(f[Y], f[X]) + heading
            x1 = math.cos(theta)*h + self.position.se
            y1 = math.sin(theta)*h + self.position.sw
            unit.position.set(x1, y1)
            #print(f'index {i}')
            #print(f'   company: {self.position}')
            #for u in self.units:
            #    print(f'   {u.position}')
            #print('---------\n')
            
    
    def fetch_sprite(self):
        self.position.to_pixels(self.Map.size)
        img_path = Path('./Art/Interface/Banners/')
        banner = Image.open(img_path/'council-recruit.png')
        icon = Image.open(img_path/f'icon-{self.banner_icon}.png')
        banner.paste(icon,mask=icon)
        sprite_ini = ConfigParser()
        sprite_ini.read(img_path/'sprite.ini')
        hsx = int(sprite_ini['HotSpot']['X'])
        hsy = int(sprite_ini['HotSpot']['Y'])
        box = (self.position.x -hsx, self.position.y - hsy, self.position.x + banner.size[0] - hsx, self.position.y + banner.size[1] - hsy)
        return (banner, box)
        
            
class Unit(MapObject):
    '''Class representing a single unit in a Company Object.
    Data is loaded from the cooresponding unit INI.'''
    def __init__(self, name: str, Map: KohanMap, parent: Company, player: int=0):
        MapObject.__init__(self, Map, player=player)
        self.parent = parent
        self.name = name
        unit_ini = ConfigParser(inline_comment_prefixes=(';',))
        filepath = Path(f'./Data/ObjectData/Units/{name}.INI').resolve()
        try:
            unit_ini.read(filepath)
            self.display_name = unit_ini['ObjectData']['ProperName']
            self.unit_class = int(unit_ini['ObjectData']['Class'])
            self.sprite_path = f"./Art/Objects/{unit_ini['ObjectData']['Sprite']}"
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
                    
            self.unit_type = unit_ini['UnitData']['Type']
            self.movement_speed = float(unit_ini['UnitData']['MovementRate'])
            
            if self.unit_type == 'FRONT':
                self.default_captain = unit_ini['UnitData']['Captain']
                self.banner_frame = unit_ini['UnitData']['BannerFrame']
                self.morale = unit_ini['CompanyData']['Morale']
                self.visual_range = unit_ini['CompanyData']['VisualRange']
                self.control_zone = unit_ini['CompanyData']['ControlZone']
                self.entrenchment_rate = unit_ini['CompanyData']['EntrenchmentRate']

            # Use the names from BONUS.INI as keys
            self.modifiers_gained = {}
            self.modifiers_provided = {}
            for k, v in unit_ini['ElementBonus'].items():
                self.modifiers_gained[k] = v
            for k, v in unit_ini['SupportBonus'].items():
                self.modifiers_provided[k] = v
                
            if self.unit_class == 1:
                self.current_mana = unit_ini['SpellData']['MaxMana']
                
        except Exception as e:
            print(repr(e))
            print(f'Unable to create unit with name {name}: file {filepath} does not exist')
    
    def fetch_sprite(self):
        self.position.to_pixels(self.Map.size)
        dest = Path(f'./Art/Objects/Units/Extracted/{self.name}')
        args = tgrtool.main_parse.parse_args(['unpack', f'{self.sprite_path}', '--single-frame', '0', '-c', '1', '-o', f'{dest}'])
        args.func(args)
        sprite_ini = ConfigParser()
        sprite_ini.read(dest/'sprite.ini')
        hsx = int(sprite_ini['HotSpot']['X'])
        hsy = int(sprite_ini['HotSpot']['Y'])
        sprite = Image.open(dest / 'fram_0000.png')
        box = (self.position.x - hsx, self.position.y - hsy, self.position.x + sprite.size[0] - hsx, self.position.y + sprite.size[1] - hsy)
        return (sprite, box)

class MapFeature:
    '''A class representing a Feature in a Kohan Map.'''
    pass
        
        