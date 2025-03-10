import qt_shared
import tgmlib
from mirror_map import P
import random
import math
from pathlib import Path
from configparser import ConfigParser
import struct
from io import BytesIO
import kd_map_tools

# All following calculations use the northern-most corner as (0,0)
# and treat the NW-SE edge as X, and the NE-SW edge as Y

# constraints
NUM_MINE = 12
NUM_LAIR = 16
NUM_CITY = 8
MIN_RUSH_DISTANCE = 96 #tiles
START_MIN_RADIUS = 0.35 #scaling factor
START_MAX_RADIUS = 0.75 #scaling factor
START_EXCLUDE_CITIES = 40
START_EXCLUDE_MINES = 15
START_EXCLUDE_LAIRS = 20
MEDIUM_VALUE_FACTOR = 0.1
HIGH_VALUE_FACTOR = 0.2

filename = Path('192x192.tgm')
data_path = Path('./Data/ObjectData')

tgm = tgmlib.tgmFile(filename)
tgm.load()
MAP_SIZE = tgm.chunks['EDTR'].size_se

player1 = kd_map_tools.Player(color='red', faction='nationalist', kingdom_name='_unnamed', starting_gold=400)
player2 = kd_map_tools.Player(color='blue', faction='council', kingdom_name='_unnamed', starting_gold=400)
kd_map_tools.getActiveKingdoms(tgm)
active_kingdoms = [0,1]
player_mapping = kd_map_tools.setPlayerData(tgm, (player1,player2,), active_kingdoms, 0)

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
    print(f'hyp: {hyp}')
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
                obj['gen_type'] = 'lair'
                exclude_city = 15
                exclude_lair = 10
                exclude_mine = 10
                contestable = 0
            case 0|3:
                obj['class'] = 'lair'
                obj['gen_type'] = 'lair'
                exclude_city = 15
                exclude_lair = 15
                exclude_mine = 10
                contestable = 0
            case 4:
                obj['class'] = 'mine'
                obj['gen_type'] = 'mine'
                exclude_city = 12
                exclude_lair = 10
                exclude_mine = 15
                contestable = 0
            case 1|5|6|7|8:
                obj['class'] = 'city'
                obj['gen_type'] = 'city'
                exclude_city = 40
                exclude_lair = 10
                exclude_mine = 10
                contestable = 0
            case _:
                obj['class'] = None
                obj['gen_type'] = None
        
        obj['exclude_city'] = building_ini.getint('GeneratorData', 'ExcludeCities', fallback=exclude_city)
        obj['exclude_lair'] = building_ini.getint('GeneratorData', 'ExcludeLairs', fallback=exclude_lair)
        obj['exclude_mine'] = building_ini.getint('GeneratorData', 'ExcludeMines', fallback=exclude_mine)
        obj['contestable'] = building_ini.getint('GeneratorData', 'Contestable', fallback=contestable)
        obj['value'] = building_ini.getint('GeneratorData', 'Value', fallback=1)
        
       
                
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
    new_obj.header.hotspot_se = new_obj.pos_se if buildings[name]['bounding_radius'] % 2 == 1 else new_obj.pos_se + 0.5
    new_obj.header.hotspot_sw = new_obj.pos_sw if buildings[name]['bounding_radius'] % 2 == 1 else new_obj.pos_sw + 0.5
    new_obj.booty_value = random.randint(buildings[name]['min_gold'], buildings[name]['max_gold'])
    building_ini = ConfigParser(inline_comment_prefixes=(';',))
    building_ini.read(tgmlib.resolve_path(f'./Data/ObjectData/Buildings/{name}.INI'))
    if (obj_cls := buildings[name]["class"]) == 'city':
        if (upgrade := building_ini.get('BaseData', 'NextLevel' ,fallback=None)):
            new_obj.upgrade_index = new_obj.TYPE_ref.by_name[upgrade.upper()]['index']
    if obj_cls in ('city', 'lair',):
        new_obj.militia.supply_zone = building_ini.getfloat('BaseData', 'SupplyRange')
        new_obj.militia.max = building_ini.getint('BaseData', 'MaxMilitia', fallback=10)
        new_obj.militia.current = new_obj.militia.max / 2
        new_obj.militia.regen_rate = building_ini.getfloat('BaseData', 'MilitiaGrowth', fallback=0.05)
        new_obj.militia.guard_zone = building_ini.getfloat('BaseData', 'ControlRange')
        new_obj.militia.front_index = new_obj.TYPE_ref.by_name[building_ini['BaseData']['MilitiaType'].upper()]['index']
        new_obj.militia.support_index = new_obj.militia.front_index
        new_obj.militia.company_size = building_ini.getint('BaseData', 'CompanySize')
        
    elif obj_cls == 'mine':
        new_obj.base_gold_production = building_ini.getfloat('ResourceData','GoldProduction', fallback=0)
        new_obj.base_stone_production = building_ini.getfloat('ResourceData','StoneProduction', fallback=0)
        new_obj.base_wood_production = building_ini.getfloat('ResourceData','WoodProduction', fallback=0)
        new_obj.base_iron_production = building_ini.getfloat('ResourceData','IronProduction', fallback=0)
        new_obj.base_mana_production = building_ini.getfloat('ResourceData','ManaProduction', fallback=0)
    print(f"obj_cls {obj_cls}")
    
    tgm.chunks['OBJS'].objs.append(new_obj)
    return new_obj

def generateObj(buildings, templates, gen_type, ):
    pop, weight = zip(*[[k, v['weight']] for k,v in buildings.items() if v['gen_type'] == gen_type])
    pick = random.choices(population=pop, weights=weight, k=1)[0]
    print(f'generating {pick}')
    for tries in range(0,100):
        br = math.ceil(buildings[pick]['bounding_radius'])
        match buildings[pick]['contestable']:
            case 0:                
                pos = P(random.randint(br, MAP_SIZE-br), random.randint(br, MAP_SIZE-br))
            case 1:
                #P(midpoint.se+1, center_line(midpoint.se+1))
                axis = (midpoint, P(midpoint.se+1, center_line(midpoint.se+1)))
                d = axis[1] - axis[0]
                det = d.se*d.se + d.sw*d.sw
                while True:
                    pos = P(random.randint(br, MAP_SIZE-br), random.randint(br, MAP_SIZE-br))
                    a = (d.sw*(pos.sw-axis[0].sw)+d.se*(pos.se-axis[0].se))/det
                    closest = P(axis[0].se+a*d.se, axis[0].sw+a*d.sw)
                    print(f' point: {pos} dist: {len(closest-pos)} target:{len(midpoint-start1)}')
                    #closest - (midpoint-start1)
                    if len(closest-pos) <= len(midpoint-start1) * (1-MEDIUM_VALUE_FACTOR):
                        break
            case 2:
                while True:
                    pos = P(random.randint(br, MAP_SIZE-br), random.randint(br, MAP_SIZE-br))
                    if len(pos - start1)*(1-HIGH_VALUE_FACTOR) <= len(pos - start2) <= len(pos - start1)*(1+HIGH_VALUE_FACTOR):
                        break
                
        for obj in tgm.chunks['OBJS'].objs:
            distance = len(P(obj.pos_se, obj.pos_sw) - pos)
            obj_data = buildings[obj.TYPE_ref.by_index[obj.header.index]['name']]
            #print(f'  distance to {obj.name}: {distance}')
            #print(f'  ')
            if distance <= obj_data[f'exclude_{gen_type}'] or distance <= buildings[pick][f'exclude_{obj_data["gen_type"]}']:
                break
        else:
            print(f'chose {pos} on try {tries}')
            newBuilding(pick, buildings, templates, pos)
            break
    else:
        print(f'failed to place {pick} after 100 tries')

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
    new_sp.header.hotspot_se = int(pos.se) + 0.5
    new_sp.header.hotspot_sw = int(pos.sw) + 0.5
    tgm.chunks['FTRS'].features.append(new_sp)
    return new_sp

def calcLine(p1: P, p2: P, perpendicular=False):
    slope = (p1.sw - p2.sw) / (p1.se - p2.se + 0.01)
    if perpendicular:
        slope = -1/slope
    return lambda x: slope * (x - p1.se) + p1.sw

def drawLine(line):
    #Takes a lambda containing the formula of a line
    for se in range(0,MAP_SIZE*8):
        sw = round(line(se/8))
        se = int(se/8)
        if 0 <= sw < MAP_SIZE:
            tgm.chunks['MGRD'].tiles[se][sw].terrain1 = 0xE
            tgm.chunks['MGRD'].tiles[se][sw].terrain2 = 0xE
            tgm.chunks['MGRD'].tiles[se][sw].layout = 0x0
                
templates = loadTemplates()
buildings = loadBuildings()   
buildings['ICE_DRAKE_LAIR']['weight'] = 10
buildings['STORM_DRAKE_LAIR']['weight'] = 10        
buildings['DRAGON_LAIR']['weight'] = 10    
buildings['NEW_AHRIMAN_CITADEL']['weight'] = 10    
    
start1, start2 = chooseStartPositions()
newStartPos(start1, player=0)
newStartPos(start2, player=1)
kd_map_tools.updateFeatures(tgm, player_mapping)
b1 = newBuilding('MONOLITH', buildings, templates, start1, player=0)
b2 = newBuilding('MONOLITH', buildings, templates, start2, player=1)
center = P(MAP_SIZE/2, MAP_SIZE/2)
midpoint = (start1 + start2) / 2
# =============================================================================
# mpm = newBuilding('MONOLITH', buildings, templates, midpoint)
# mpm.name = "Player Midpoint Marker"
# cm = newBuilding('FLAG', buildings, templates, center)
# cm.name = "Map Center"
# =============================================================================
#drawLine(calcLine(center, midpoint))
center_line = calcLine(midpoint, start1, perpendicular=True)
drawLine(center_line)
    
for _ in range(NUM_CITY):
    generateObj(buildings, templates, 'city')
for _ in range(NUM_LAIR):
    generateObj(buildings, templates, 'lair')
for _ in range(NUM_MINE):
    generateObj(buildings, templates, 'mine')



tgm.chunks['FIDX'].generate(tgm.chunks['FTRS'])
tgm.write(r"C:\Program Files (x86)\Steam\steamapps\common\Kohan Ahrimans Gift\Maps\_rmt.tgm")