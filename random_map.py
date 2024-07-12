import qt_shared
import tgmlib
from mirror_map import P
import random
import math
from pathlib import Path
from configparser import ConfigParser
import struct
from io import BytesIO

# All following calculations use the northern-most corner as (0,0)
# and treat the NW-SE edge as X, and the NE-SW edge as Y

# constraints
NUM_MINE = 10
NUM_LAIR = 12
NUM_CITY = 6
MIN_RUSH_DISTANCE = 96 #tiles
START_MIN_RADIUS = 0.3 #scaling factor
START_MAX_RADIUS = 0.8 #scaling factor



filename = Path('192x192.tgm')
data_path = Path('./Data/ObjectData')

tgm = tgmlib.tgmFile(filename)
tgm.load()
MAP_SIZE = tgm.chunks['EDTR'].size_se

def generateStartPosition():
    center = P(MAP_SIZE/2, MAP_SIZE/2)
    angle = random.random() * 2 * math.pi
    if 0 <= angle < math.pi/4 or math.pi*3/4 <= angle < math.pi*5/4 or math.pi*7/4 <= angle <= math.pi*2:
        # constrain y-leg because x will be maximum size
        leg = (MAP_SIZE/2) * math.tan(angle)
    else:
        # constrain x-leg because y will be maximum size
        leg = (MAP_SIZE/2) / math.tan(angle)
    hyp = math.sqrt((MAP_SIZE/2)**2 + leg**2)
    distance = hyp * random.uniform(START_MIN_RADIUS, START_MAX_RADIUS)
    x = distance * math.cos(angle)
    y = distance * math.sin(angle)
    pos = P(x,y) + center
    print(f'angle: {angle/math.pi:.3f}pi rad')
    print(f'distance: {distance}')
    print(pos)
    return pos

def chooseStartPositions():
    pos1 = generateStartPosition()
    attempts = 0
    while pos1.distance(pos2 := generateStartPosition()) < MIN_RUSH_DISTANCE:
        attempts += 1
        if attempts > 100:
            raise SystemExit('Failed to place 2nd start position after 100 attempts')
    
    print(pos2)
    return (pos1, pos2)

def loadBuildings():
    buildings = {}
    
    for child in (data_path/'Buildings').iterdir():
        building_ini = ConfigParser(inline_comment_prefixes=(';',))
        obj = {}
        building_ini.read(child)
        print(f'reading {child}')
        obj['weight'] = building_ini.getint('ObjectData', 'Weight', fallback=0)
        obj['bounding_radius'] = float(building_ini['ObjectData']['BoundingRadius'])
        obj['type'] = tgm.chunks['TYPE'].by_name[child.stem]['index']
        obj['min_gold'] = int(building_ini['BuildingData']['booty_min'])
        obj['max_gold'] = int(building_ini['BuildingData']['booty_max'])
        match int(building_ini['ObjectData']['Class']):
            case 0:
                obj['class'] = 'ruin'
            case 3:
                obj['class'] = 'lair'
            case 4:
                obj['class'] = 'mine'
            case 1|5|6|7|8:
                obj['class'] = 'city'
        buildings[child.stem] = obj
# =============================================================================
#         match int(building_ini['ObjectData']['Class']):
#             case 0|3:
#                 buildings['lairs'][child.stem] = obj
#             case 4:
#                 buildings['mines'][child.stem] = obj
#             case 1|5|6|7|8:
#                 buildings['cities'][child.stem] = obj
# =============================================================================
    return buildings

def loadTemplates():
    templates = {}
    for obj_cls in ('city', 'lair', 'ruin', 'start_pos', 'mine'):
        with open(tgmlib.resolve_path(f'./Data/BuildingTemplates/{obj_cls}'), 'rb') as template_fh:
            templates[obj_cls] = template_fh.read()
    return templates
        
def newBuilding(name, buildings, templates, pos: P, player=8):
    # first set the correct index in the template to guarantee proper parsing
    template = templates[buildings[name]['class']]
    index = tgm.chunks['TYPE'].by_name[name]['index']
    print(f'creating new {name} with class {buildings[name]["class"]} and index {index}')
    template = template[:2] + struct.pack('<H', index) + template[4:]
    template_buf = BytesIO(template)
    new_obj = tgmlib.Building(template_buf, tgm.chunks['TYPE'])
    new_obj.header.index = new_obj.TYPE_ref.by_name[name]['index']
    new_obj.header.player = player
    new_obj.header.editor_id = tgm.chunks['GAME'].next_id
    tgm.chunks['GAME'].next_id += 1
    tgm.chunks['GAME'].ids[new_obj.header.editor_id] = True
    tgm.chunks['GAME'].load_flags[new_obj.header.editor_id] = True
    new_obj.pos_se = int(pos.se)
    new_obj.pos_sw = int(pos.sw)
    new_obj.header.hotspot_se = pos.se if buildings[name]['bounding_radius'] % 2 == 1 else pos.se + 0.5
    new_obj.header.hotspot_sw = pos.sw if buildings[name]['bounding_radius'] % 2 == 1 else pos.sw + 0.5
    new_obj.booty_value = random.randint(buildings[name]['min_gold'], buildings[name]['max_gold'])
    building_ini = ConfigParser(inline_comment_prefixes=(';',))
    building_ini.read(tgmlib.resolve_path(f'./Data/ObjectData/Buildings/{name}.INI'))
    if (obj_cls := buildings[name]["class"]) in ('city', 'lair',):
        new_obj.militia.supply_zone = building_ini.getfloat('BaseData', 'SupplyRange')
        new_obj.militia.max = building_ini.getint('BaseData', 'MaxMilitia', fallback=10)
        new_obj.militia.current = new_obj.militia.max / 2
        new_obj.militia.regen_rate = building_ini.getfloat('BaseData', 'MilitiaGrowth', fallback=0.05)
        new_obj.militia.guard_zone = building_ini.getfloat('BaseData', 'ControlRange')
        new_obj.militia.front_index = new_obj.TYPE_ref.by_name[building_ini['BaseData']['MilitiaType'].upper()]['index']
        new_obj.militia.support_index = new_obj.militia.front_index
        new_obj.militia.company_size = building_ini.getint('BaseData', 'CompanySize')
        new_obj.upgrade_index = new_obj.TYPE_ref.by_name[building_ini['BaseData']['NextLevel'].upper()]['index']
    elif obj_cls == 'mine':
        new_obj.base_gold_production = building_ini.getfloat('ResourceData','GoldProduction', fallback=0)
        new_obj.base_stone_production = building_ini.getfloat('ResourceData','StoneProduction', fallback=0)
        new_obj.base_wood_production = building_ini.getfloat('ResourceData','WoodProduction', fallback=0)
        new_obj.base_iron_production = building_ini.getfloat('ResourceData','IronProduction', fallback=0)
        new_obj.base_mana_production = building_ini.getfloat('ResourceData','ManaProduction', fallback=0)
    print(f"obj_cls {obj_cls}")
    
    tgm.chunks['OBJS'].objs.append(new_obj)
    return new_obj

def newStartPos(pos: P, player):
    with open(tgmlib.resolve_path('./Data/BuildingTemplates/start_pos'), 'rb') as template_fh:
        new_sp = tgmlib.Feature(template_fh, tgm.chunks['TYPE'])
    new_sp.header.index = new_sp.TYPE_ref.by_name['START_POSITION']['index']
    new_sp.header.player = player
    new_sp.header.editor_id = tgm.chunks['GAME'].next_id
    tgm.chunks['GAME'].next_id += 1
    tgm.chunks['GAME'].ids[new_sp.header.editor_id] = True
    tgm.chunks['GAME'].load_flags[new_sp.header.editor_id] = True
    new_sp.pos_se = int(pos.se)
    new_sp.pos_sw = int(pos.sw)
    new_sp.header.hotspot_se = pos.se + 0.5
    new_sp.header.hotspot_sw = pos.sw + 0.5
    tgm.chunks['FTRS'].features.append(new_sp)
    return new_sp



                
                
templates = loadTemplates()
buildings = loadBuildings()           
        
    
pos1, pos2 = chooseStartPositions()
newStartPos(pos1, player=0)
newStartPos(pos2, player=4)
b1 = newBuilding('COUNCIL_VILLAGE', buildings, templates, pos1, player=0)
b2 = newBuilding('COUNCIL_VILLAGE', buildings, templates, pos2, player=4)

tgm.chunks['FIDX'].generate(tgm.chunks['FTRS'])
tgm.write(r"C:\Program Files (x86)\Steam\steamapps\common\Kohan Ahrimans Gift\Maps\_rmt.tgm")