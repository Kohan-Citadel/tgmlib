import tgmlib
from configparser import ConfigParser
from pathlib import Path
import re
import json
from copy import deepcopy
from PyQt5 import QtCore, QtWidgets, QtGui
import qt_shared

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        self.role = QtCore.Qt.UserRole + 1
        
        self.tgm_loaded = False
        self.tgms = []
        self.files = []
        layout = QtWidgets.QVBoxLayout()
        #self.setWindowTitle("Kohan Duels Map Randomizer")
        self.select_map = QtWidgets.QPushButton('Select TGM(s)')
        self.select_map.clicked.connect(self.loadMaps)
        layout.addWidget(self.select_map)
        
        self.ref_map_menu = QtWidgets.QComboBox()
        for child in tgmlib.resolve_path('./Data/RefMaps').iterdir():
            self.ref_map_menu.addItem(child.name)
            self.ref_map_menu.setItemData(self.ref_map_menu.count()-1, child, role=self.role)
        self.ref_map_browse = QtWidgets.QPushButton('Browse')
        self.ref_map_browse.setFixedSize(70,22)
        self.ref_map_browse.clicked.connect(lambda: self.Browse(self.ref_map_menu, "Kohan Maps (*.tgm)"))
        self.ref_map_menu.currentIndexChanged.connect(lambda i: print(self.ref_map_menu.itemData(i, self.role)))
        l1 = QtWidgets.QHBoxLayout()
        l1.addWidget(QtWidgets.QLabel('Reference TGM'), stretch=3)
        l1.addWidget(self.ref_map_menu, stretch=5)
        l1.addWidget(self.ref_map_browse)
        layout.addLayout(l1)
        
        self.name_mapping_menu = QtWidgets.QComboBox()
        for child in tgmlib.resolve_path('./Data/NameMappings').iterdir():
            self.name_mapping_menu.addItem(child.name)
            self.name_mapping_menu.setItemData(self.name_mapping_menu.count()-1, child, role=self.role)
        self.name_mapping_browse = QtWidgets.QPushButton('Browse')
        self.name_mapping_browse.setFixedSize(70,22)
        self.name_mapping_browse.clicked.connect(lambda: self.Browse(self.name_mapping_menu, "Type Name Mappings (*.json)"))
        self.name_mapping_menu.currentIndexChanged.connect(lambda i: print(self.name_mapping_menu.currentData(self.role)))
        l2 = QtWidgets.QHBoxLayout()
        l2.addWidget(QtWidgets.QLabel('Type Name Mapping'), stretch=3)
        l2.addWidget(self.name_mapping_menu, stretch=5)
        l2.addWidget(self.name_mapping_browse)
        layout.addLayout(l2)
        
        self.update = QtWidgets.QPushButton('Update')
        self.update.setEnabled(False)
        self.update.clicked.connect(self.updateMaps)
        layout.addWidget(self.update)

        back_button = QtWidgets.QPushButton('Back to Menu')
        back_button.clicked.connect(lambda: self.parent().parent().switchWidget('homepage'))
        layout.addWidget(back_button)
        self.setLayout(layout)
        self.setMaximumSize(400,230)

    def loadMaps(self):
        files = qt_shared.FileDialog(multiple=True,
                                     forOpen=True,
                                     filters=("Kohan Maps (*.tgm)", "All Files (*)",),
                                     isFolder=False)
        
        print(f'length of files: {len(files)}')
        print(f'type of files: {type(files)}')
        if files:
            # Clears out old data
            self.files = []
            for filename in files:
                filename = Path(filename)
                print(filename)
                self.files.append(filename)
            
            self.loadTGMs()
           
            self.update.setEnabled(True)
    
    def Browse(self, menu, filters):
        file = qt_shared.FileDialog(filters=filters)
        if file:
            file = Path(file[0])
            menu.addItem(file.name)
            menu.setItemData(menu.count()-1, file, role=self.role)
            menu.setCurrentIndex(menu.count()-1)
    
    def loadTGMs(self):
        self.tgms = []
        for filename in self.files:
            self.tgms.append(tgmlib.tgmFile(filename))
            self.tgms[-1].load()
        self.tgm_loaded = True
    
    def updateMaps(self):
        if not self.tgm_loaded:
            self.loadTGMs()
        save_dir = qt_shared.FileDialog(directory=self.files[0].parent, forOpen=True, isFolder=True)
        if save_dir:
            save_dir = Path(save_dir[0])
            self.tgm_loaded = False
            ref_map = tgmlib.tgmFile(self.ref_map_menu.currentData(self.role))
            ref_map.load()
            with open(self.name_mapping_menu.currentData(self.role), 'r') as fp:
                name_mapping = json.load(fp)
            
            for tgm in self.tgms:
                print(f'Updating {tgm.filename} ... ', end='')
                update(tgm,
                       ref_map,
                       name_mapping,
                       save_dir/tgm.filename.name)
                print('finished!')
        



def update(old_map, ref_map, name_mapping, dest_path):
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
            print(f'merging {k} and {name_mapping[k]}')
            # Use HROS entry with higher state value
            src = old_map.chunks['HROS'].heroes.pop(k)
            if name_mapping[k] not in old_map.chunks['HROS'].heroes:
                old_map.chunks['HROS'].heroes[name_mapping[k]] = hero_template.copy()
            if src['player_id'] != -1:
                if src['status'] > old_map.chunks['HROS'].heroes[name_mapping[k]]['status']:
                    print(f'  overwriting {name_mapping[k]} with {k}')
                    old_map.chunks['HROS'].heroes[name_mapping[k]] = src.copy()
                else:
                    print(f'Duplicate hero {k} with ID {src["editor_id"]} marked for removal')
                    heroes_to_remove.append(src['editor_id'])
            else:
                print(f'  discarding {k}')

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
        try:
            new_index = ref_map.chunks['TYPE'].by_name[name]['index']
            old_index = v['index']
            index_mapping[old_index] = new_index
        except KeyError:
            print(f'{name} is not present in type_ref, setting index to 0\nconsider adding {name} to the name mapping')
    
    for f in old_map.chunks['FTRS'].features:
        f.header.index = index_mapping[f.header.index] 
        
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
        #print(f'obj id:{i} edtr_id:{obj.header.editor_id} ix:{obj.header.index}')
        i += 1
        obj.header.index = index_mapping[obj.header.index]
        match obj.header.obj_class:
            case 0x24:
                if hasattr(obj, 'militia'):
                    obj.militia.front_index = index_mapping[obj.militia.front_index]
                    obj.militia.support_index = index_mapping[obj.militia.support_index]
                if hasattr(obj, 'upgrade_index'):
                    obj.upgrade_index = index_mapping[obj.upgrade_index]
                if hasattr(obj, 'current_hp'):
                    building_ini = ConfigParser(inline_comment_prefixes=(';',))
                    name = ref_map.chunks['TYPE'].by_index[obj.header.index]['name']
                    filepath = tgmlib.resolve_path(f'./Data/ObjectData/Buildings/{name}.INI')
                    if not filepath.exists():
                        print(f'{filepath} does not exist!')
                        raise SystemExit()
                    building_ini.read(filepath)
                    print(f'reading {filepath}')
                    obj.current_hp, obj.max_hp = (float(building_ini['ObjectData']['MaxHitPoints']),)*2
    
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
                        filepath = tgmlib.resolve_path(f'./Data/ObjectData/Heroes/{name}.INI')
                        if not filepath.exists():
                            print(f'{filepath} does not exist!')
                            raise SystemExit()
                        unit_ini.read(filepath)
                        unitUpdateModifiers(unit_ini, unit.unit_index, hero_level=level)
                        old_map.chunks['HROS'].heroes[name]['editor_id'] = unit.header.editor_id
                        if level == 0:
                            unit.max_hp = unit.current_hp = float(unit_ini['ObjectData']['MaxHitPoints']) 
                        else:
                            unit.max_hp = unit.current_hp = float(unit_ini[f'Level{level}']['MaxHitPoints'])
                     
                    else:
                        name = ref_type['name']
                        filepath = tgmlib.resolve_path(f'./Data/ObjectData/Units/{name}.INI')
                        if not filepath.exists():
                            print(f'{filepath} does not exist!')
                            raise SystemExit()
                        unit_ini.read(filepath)
                        unit.max_hp = unit.current_hp = float(unit_ini['ObjectData']['MaxHitPoints'])
                        unitUpdateModifiers(unit_ini, unit.unit_index)
                    
                    # divide by 14 to convert from display speed to internal speed
                    unit.current_speed0, unit.current_speed1, unit.base_speed = (float(unit_ini['UnitData']['MovementRate'])/14,)*3
                    if unit.base_speed < obj.speed:
                        #print(f'obj[{i}]: unit[{unit.unit_index}]: base speed {unit.base_speed} less than company speed {obj.speed}')
                        obj.speed = unit.base_speed
                        obj.slowest_unit = unit.unit_index
                        #print(f'  set slowest_unit to {obj.slowest_unit}')
                
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