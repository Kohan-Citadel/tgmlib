import tgmlib
from configparser import ConfigParser
from pathlib import Path
import re
from copy import deepcopy
import struct

old_map_path = 'throneoftheancientsdex29.tgm'
new_map_path = 'KG-0.9.6.TGM'
dest_path = 'THRONE-UPDATE.TGM'
name_mapping_path = ''
old_map = tgmlib.tgmFile(old_map_path)
ref_map = tgmlib.tgmFile(new_map_path)
old_map.load()
print('---------------------------------------------------------------------')
ref_map.load()

# Use this mapping to go from pre KG-0.9.5 (includes AG-1.3.7 and 1.3.10) to KG-0.9.6
name_mapping = {
    'AETHAN_FARHYD2': 'AETHAN_FARHYD',
    'AETHAN_FARHYD2 corpse': 'AETHAN_FARHYD corpse',
    'AHIKAR_IRAJ2': 'AHIKAR_IRAJ',
    'AHIKAR_IRAJ2 corpse': 'AHIKAR_IRAJ corpse',
    'CREATURE': 'RHAKSHA',
    'DHAVRUM_BELRAAG': 'DHAVRUM_BELRAAG_CAPTAIN',
    'Dhavrum BelraagAscended': 'DHAVRUM_BELRAAG_CAPTAIN',
    'Dhavrum BelraagEnlightened': 'DHAVRUM_BELRAAG_CAPTAIN',
    'Dhavrum BelraagRestored': 'DHAVRUM_BELRAAG_CAPTAIN',
    'DHAVRUM_BELRAAG corpse': 'DHAVRUM_BELRAAG_CAPTAIN corpse',
    'DALI_AZADE': 'DHAVRUM_BELRAAG',
    'DALI_AZADE corpse': 'DHAVRUM_BELRAAG corpse',
    'DALI_AZADE2': 'DHAVRUM_BELRAAG',
    'DALI_AZADE2 corpse': 'DHAVRUM_BELRAAG corpse',
    "GAROJ'MOK": "GAROJ'MOK_CAPTAIN",
    "GAROJ'MOK corpse": "GAROJ'MOK_CAPTAIN corpse",
    "Garoj'mokAscended": "GAROJ'MOK_CAPTAIN",
    "Garoj'mokEnlightened": "GAROJ'MOK_CAPTAIN",
    "Garoj'mokRestored": "GAROJ'MOK_CAPTAIN",
    'DARYA_AZAR': "GAROJ'MOK",
    'DARYA_AZAR corpse': "GAROJ'MOK corpse",
    'DARYA_AZAR2': "GAROJ'MOK",
    'DARYA_AZAR2 corpse': "GAROJ'MOK corpse",
    'GideonAscended': 'Gideon XarrAscended',
    'GideonEnlightened': 'Gideon XarrEnlightened',
    'GideonRestored': 'Gideon XarrRestored',
    'KARG': 'KARG_CAPTAIN',
    'KARG corpse': 'KARG_CAPTAIN corpse',
    'KargAscended': 'KARG_CAPTAIN',
    'KargEnlightened': 'KARG_CAPTAIN',
    'KargRestored': 'KARG_CAPTAIN',
    'KING_ULRIC': 'KING_ULRIC_CAPTAIN',
    'KING_ULRIC corpse': 'KING_ULRIC_CAPTAIN corpse',
    'King UlricAscended': 'KING_ULRIC_CAPTAIN',
    'King UlricEnlightened': 'KING_ULRIC_CAPTAIN',
    'King UlricRestored': 'KING_ULRIC_CAPTAIN',
    'SLAAN_CHAMPION': 'SLAANRI_CHAMPION',
    'SLAAN_MILITIA': 'SLAANRI_MILITIA',
    'JHAENGUS': 'KARG',
    'JHAENGUS corpse': 'KARG corpse',
    'JHAENGUS2': 'KARG',
    'JHAENGUS2 corpse': 'KARG corpse',
    'JILLA_JANNAT': 'KING_ULRIC',
    'JILLA_JANNAT corpse': 'KING_ULRIC corpse',
    'JILLA_JANNAT2': 'KING_ULRIC',
    'JILLA_JANNAT2 corpse': 'KING_ULRIC corpse',
    'LORD_JAVIDAN': 'DARIUS_JAVIDAN',
    'LORD_JAVIDAN corpse': 'DARIUS_JAVIDAN corpse',
    'LUCIUS_AJAM': 'LORD_JAVIDAN',
    'LUCIUS_AJAM corpse': 'LORD_JAVIDAN corpse',
    'LUCIUS_AJAM2': 'LORD_JAVIDAN',
    'LUCIUS_AJAM2 corpse': 'LORD_JAVIDAN corpse',
    'Lord JavidanAscended': 'Darius JavidanAscended',
    'Lord JavidanEnlightened': 'Darius JavidanEnlightened',
    'Lord JavidanRestored': 'Darius JavidanRestored',
    'Lord Amon KothAscended': 'Amon KothAscended',
    'Lord Amon KothEnlightened': 'Amon KothEnlightened',
    'Lord Amon KothRestored': 'Amon KothRestored',
    'MEGALITH': 'MONOLITH',
    'MISTRESS_ROXANNA': 'VASHTI',
    'MISTRESS_ROXANNA corpse': 'VASHTI corpse',
    'Mistress JavidanAscended': 'VashtiAscended',
    'Mistress JavidanEnlightened': 'VashtiEnlightened',
    'Mistress JavidanRestored': 'VashtiRestored',
    'MISTRESS_VASHTI': 'VASHTI',
    'MISTRESS_VASHTI corpse': 'VASHTI corpse',
    'Mistress VashtiAscended': 'VashtiAscended',
    'Mistress VashtiEnlightened': 'VashtiEnlightened',
    'Mistress VashtiRestored': 'VashtiRestored',
    'MAUSALLAS_BAHRAM': 'MISTRESS_ROXANNA',
    'MAUSALLAS_BAHRAM corpse': 'MISTRESS_ROXANNA corpse',
    'MAUSALLAS_BAHRAM2': 'MISTRESS_ROXANNA',
    'MAUSALLAS_BAHRAM2 corpse': 'MISTRESS_ROXANNA corpse',
    'MP_AMON_KOTH2': 'AMON_KOTH',
    'MP_AMON_KOTH2 corpse': 'AMON_KOTH corpse',
    'Samman RavidAscended': 'Samman OsahyrAscended',
    'Samman RavidEnlightened': 'Samman OsahyrEnlightened',
    'Samman RavidRestored': 'Samman OsahyrRestored',
    'SAR_LASHKAR2': 'SAR_LASHKAR',
    'SAR_LASHKAR2 corpse': 'SAR_LASHKAR corpse',
    'Lord Sar LashkarAscended': 'Sar LashkarAscended',
    'Lord Sar LashkarEnlightened': 'Sar LashkarEnlightened',
    'Lord Sar LashkarRestored': 'Sar LashkarRestored',
    'SEBASTIAN_ATAFEH': 'SAR_LASHKAR2',
    'SEBASTIAN_ATAFEH corpse': 'SAR_LASHKAR2 corpse',
    'SEBASTIAN_ATAFEH2': 'SAR_LASHKAR2',
    'SEBASTIAN_ATAFEH2 corpse': 'SAR_LASHKAR2 corpse',
    'SHOHN_MAHT2': 'SHOHN_MAHT',
    'SHOHN_MAHT2 corpse': 'SHOHN_MAHT corpse',
    'MP_SHOHN_MAHT2': 'SHOHN_MAHT',
    'MP_SHOHN_MAHT2 corpse': 'SHOHN_MAHT corpse',
    'Lord Shohn MahtAscended': 'Shohn MahtAscended',
    'Lord Shohn MahtEnlightened': 'Shohn MahtEnlightened',
    'Lord Shohn MahtRestored': 'Shohn MahtRestored',
    'Lord Shohn Maht 2Ascended': 'Shohn MahtAscended',
    'Lord Shohn Maht 2Enlightened': 'Shohn MahtEnlightened',
    'Lord Shohn Maht 2Restored': 'Shohn MahtRestored',
    'SOLOMON_GHAFFAR': 'SHOHN_MAHT2',
    'SOLOMON_GHAFFAR corpse': 'SHOHN_MAHT2 corpse',
    'SOLOMON_GHAFFAR2': 'SHOHN_MAHT2',
    'SOLOMON_GHAFFAR2 corpse': 'SHOHN_MAHT2 corpse',
    'BANDIT_CAMP': 'BRIGAND_CAMP',
    'BANDIT_CAMP ruin': 'BRIGAND_CAMP ruin',
    'NEST': 'RHAKSHA_NEST',
    'NEST ruin': 'RHAKSHA_NEST ruin',
    'NEW_AHRIMAN_CITADEL': 'AHRIMAN_CITADEL',
    'NEW_AHRIMAN_CITADEL ruin': 'AHRIMAN_CITADEL ruin',
    'NOVITIATE': 'DISCIPLE',
    'NOVITIATE corpse': 'DISCIPLE corpse',
    }

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
        #TODO implement a way to control read order (to better control collisions)
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
    if f['index'] != 0xFFFF:
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
        for k, v in unit_ini[sb_name].items():
            K = k.upper()
            if K in tgmlib.comp_mods_default:
                obj.company_modifiers_provided.append((K, float(v),))
            elif K in tgmlib.unit_mods_lookup.values():
                obj.unit_modifiers_provided.append((K, float(v),))


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

#copy each chunk from old_map verbatim, unless it's been updated
with open(old_map_path, 'rb') as in_fp, open(dest_path, 'wb+') as out_fp:
    #write placeholder FORM
    out_fp.write(b'FORM\xFF\xFF\xFF\xFFTGSV')
    for iff_chunk in old_map.iff.data.children:
        if iff_chunk.type in old_map.chunks and hasattr(old_map.chunks[iff_chunk.type], 'pack'):
            out_fp.write(old_map.chunks[iff_chunk.type].pack())
        else:
            out_fp.write(struct.pack('>4sI', iff_chunk.type.encode('ascii'), iff_chunk.length))
            in_fp.seek(iff_chunk.data_offset)
            out_fp.write(in_fp.read(iff_chunk.length))
            if last_bytes := (out_fp.tell() % 4):
                out_fp.write(b'\x00'*(4-last_bytes))
    
    file_size = out_fp.seek(0,2)
    out_fp.seek(4)
    out_fp.write(struct.pack('>I', file_size - 12))
            


# Items to update:
    #main index and all references
        #copy correct index (TYPE) from correct blank map


    

#Adtl TODO

    #Add repacking to .TGM