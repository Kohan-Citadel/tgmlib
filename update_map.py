import tgmlib
from configparser import ConfigParser
from pathlib import Path
import re
from copy import deepcopy
import json

old_map_path = 'ECM1-CLEANED.TGM'
new_map_path = 'KG-0.9.6.TGM'
dest_path = '../../../Mod-Test-Only/Maps/ECM1-UPDATE-FIX.TGM'
name_mapping_path = 'name-mapping-KG0.9.6.json'
old_map = tgmlib.tgmFile(old_map_path)
ref_map = tgmlib.tgmFile(new_map_path)
old_map.load()
print('---------------------------------------------------------------------')
ref_map.load()

# Use this mapping to go from pre KG-0.9.5 (includes AG-1.3.7 and 1.3.10) to KG-0.9.6
with open(name_mapping_path, 'r') as fp:
    name_mapping = json.load(fp)

# stores editor ids of duplicate heroes to be replaced with captain
heroes_to_remove = []
hero_template = {
        'status': 0,
        'i1': 0,
        'experience': 0.0,
        'awakened': 0,
        's1': 0,
        'player_id': -1,
        'editor_id': 0,
        }

old_heroes = list(old_map.chunks['HROS'].heroes.keys())
name_map_list = list(name_mapping.keys())
def sortHeroes(hero_name):
    if hero_name in name_map_list:
        return name_map_list.index(hero_name)
    else:
        return 999
old_heroes.sort(key=sortHeroes)
for k in old_heroes:
    if k in name_mapping:
        print(f'merging {k} into {name_mapping[k]}')
        # Use HROS entry with higher state value
        src = old_map.chunks['HROS'].heroes.pop(k)
        if name_mapping[k] not in old_map.chunks['HROS'].heroes:
            old_map.chunks['HROS'].heroes[name_mapping[k]] = hero_template.copy()
        if src['status'] > old_map.chunks['HROS'].heroes[name_mapping[k]]['status']:
            old_map.chunks['HROS'].heroes[name_mapping[k]] = src.copy()
        elif src['player_id'] != -1:
            print(f'Duplicate hero {k} with ID {src["editor_id"]} marked for removal')
            heroes_to_remove.append(src['editor_id'])

sym_dif = old_map.chunks['HROS'].heroes.keys() ^ ref_map.chunks['HROS'].heroes.keys()
only_old = sym_dif & old_map.chunks['HROS'].heroes.keys()
only_ref = sym_dif & ref_map.chunks['HROS'].heroes.keys()
for k in only_old:
    old_map.chunks['HROS'].heroes.pop(k)
for k in only_ref:
    old_map.chunks['HROS'].heroes[k] = hero_template.copy()
#Put heroes back in alphabetical order
old_map.chunks['HROS'].heroes = dict(sorted(old_map.chunks['HROS'].heroes.items()))

# Added to prevent crashes from empty type indicies
index_mapping = {0xFFFF: 0xFFFF}

for k, v in old_map.chunks['TYPE'].by_name.items():
    if k in name_mapping:
        name = name_mapping[k]
    else:
        name = k
        
    new_index = ref_map.chunks['TYPE'].by_name[name]['index']
    old_index = v['index']
    index_mapping[old_index] = new_index

for f in old_map.chunks['FTRS'].features:
    f['index'] = index_mapping[f['index']] 

def unitUpdateModifiers(unit_ini, unit_index, hero_level=0):
    eb_name = 'ElementBonus'
    sb_name = 'SupportBonus'
    if hero_level > 0:
        eb_name += str(hero_level)
        sb_name += str(hero_level)
    
    for k, v in unit_ini[eb_name].items():
        K = k.upper()
        if K in tgmlib.unit_mods_default:
            op = unit.modifiers_gained[K][1]
            #print(f'  op: {op}')
            if op == 'add':
                unit.modifiers_gained[K][0] += int(v)
                #print(f'  new val: {unit.modifiers_gained[K][0]}')
            elif op == 'multiply':
                unit.modifiers_gained[K][0] *= float(v)
            
    if unit_index in (0,5,6):
        # reversed to match the order kohan writes modifiers
        for k, v in reversed(dict(unit_ini[sb_name]).items()):
            K = k.upper()
            if K in tgmlib.comp_mods_default:
                obj.company_modifiers_provided.insert(1, (K, float(v),))
            elif K in tgmlib.unit_mods_lookup.values():
                obj.unit_modifiers_provided.insert(1,(K, float(v),))


hero_name_re = re.compile(r"([a-zA-Z012_ ']+?)(Enlightened|Restored|Ascended){0,1}$")
i = 0
for obj in old_map.chunks['OBJS'].objs:
    #print(f'obj id:{i} edtr_id:{obj.header.editor_id} ix:{obj.header.index} -> {index_mapping[obj.header.index]}')
    i += 1
    obj.header.index = index_mapping[obj.header.index]
    match obj.header.obj_class:
        case 0x24:
            if hasattr(obj, 'militia'):
                obj.militia.front_index = index_mapping[obj.militia.front_index]
                obj.militia.support_index = index_mapping[obj.militia.support_index]

        case 0x3C:
            obj.captain_index = index_mapping[obj.captain_index]
            obj.front_index = index_mapping[obj.front_index]
            obj.support1_index = index_mapping[obj.support1_index]
            obj.support2_index = index_mapping[obj.support2_index]
            
            #set modifiers to default
            start = obj.modifiers_gained['start']
            obj.modifiers_gained = deepcopy(tgmlib.comp_mods_default)
            obj.modifiers_gained['start'] = start
            obj.unit_modifiers_provided = obj.unit_modifiers_provided[:1]
            obj.company_modifiers_provided = obj.company_modifiers_provided[:1]
            
            # Higher value than any real unit
            # This will be reduced to slowest unit in comp
            obj.speed = 5
            
            for unit in obj.units:
                if unit.header.editor_id in heroes_to_remove:
                    print(f'Removing Hero {old_map.chunks["TYPE"].by_index[unit.header.index]["name"]} with ID {unit.header.editor_id}')
                    unit.header.index = obj.captain_index = ref_map.chunks['TYPE'].by_name['CAPTAIN']['index']
                else:
                    unit.header.index = index_mapping[unit.header.index]
                unit_ini = ConfigParser(inline_comment_prefixes=(';',))
                ref_type = ref_map.chunks['TYPE'].by_index[unit.header.index]
                #set modifiers to default
                start = unit.modifiers_gained['start']
                unit.modifiers_gained = deepcopy(tgmlib.unit_mods_default)
                unit.modifiers_gained['start'] = start
                # if hero
                if ref_type['subtype'] == 2:
                    #print(f'  rexeging Hero Name {ref_type["name"]}')
                    m = hero_name_re.match(ref_type['name'])
                    name = m.group(1).upper().replace(' ', '_')
                    if name == 'SAMMAN_OSAHYR':
                        name = 'SAMMAN OSAHYR'
                    if name == "ISHAN_'GHUL":
                        name = "ISHAN'GHUL"
                    match m.group(2):
                        case 'Enlightened':
                            level = 1
                        case 'Restored':
                            level = 2
                        case 'Ascended':
                            level = 3
                        case _:
                            level = 0
                    
                    #print(f'  {ref_type["name"]} {name} {level}')
                    filepath = Path(f'./Data/ObjectData/Heroes/{name}.INI').resolve()
                    unit_ini.read(filepath)
                    unitUpdateModifiers(unit_ini, unit.unit_index, hero_level=level)
                    if level == 0:
                        unit.max_hp = unit.current_hp = float(unit_ini['ObjectData']['MaxHitPoints']) 
                    else:
                        unit.max_hp = unit.current_hp = float(unit_ini[f'Level{level}']['MaxHitPoints'])
                 
                else:
                    name = ref_type['name']
                    filepath = Path(f'./Data/ObjectData/Units/{name}.INI').resolve()
                    unit_ini.read(filepath)
                    unit.max_hp = unit.current_hp = float(unit_ini['ObjectData']['MaxHitPoints'])
                    unitUpdateModifiers(unit_ini, unit.unit_index)
                
                # divide by 14 to convert from display speed to internal speed
                unit.current_speed = unit.base_speed = float(unit_ini['UnitData']['MovementRate'])/14
                if unit.base_speed < obj.speed:
                    obj.speed = unit.base_speed
    
            
            for unit in obj.units:
                for (k, v,) in obj.unit_modifiers_provided[1:]:
                    if k in unit.modifiers_gained:
                        op = unit.modifiers_gained[k][1]
                        if op == 'add':
                            unit.modifiers_gained[k][0] += int(v)
                        elif op == 'multiply':
                            unit.modifiers_gained[k][0] *= float(v)
                    if k == 'HIT_POINTS_BONUS':
                        unit.current_hp *= float(v)
                        unit.max_hp = unit.current_hp
                        if unit.flag2 not in (0x09, 0x0D):
                            unit.flag2 = 0x0D
            
            #print(obj.modifiers_gained)
            for (k, v,) in obj.company_modifiers_provided[1:]:
                op = obj.modifiers_gained[k][1]
                if op == 'add':
                    obj.modifiers_gained[k][0] += int(v)
                elif op == 'multiply':
                    obj.modifiers_gained[k][0] *= float(v)

old_map.chunks['TYPE'].unknown0 = ref_map.chunks['TYPE'].unknown0
old_map.chunks['TYPE'].num_objs = ref_map.chunks['TYPE'].num_objs
old_map.chunks['TYPE'].by_name = ref_map.chunks['TYPE'].by_name
old_map.chunks['TYPE'].by_index = ref_map.chunks['TYPE'].by_index

old_map.write(dest_path)