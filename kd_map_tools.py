# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:19:01 2024

@author: Sceadu
"""
import tgmlib
import random
from configparser import ConfigParser
from pathlib import Path
from PyQt5 import QtWidgets
import qt_shared

# things that need to be adjusted for each kingdom:
#  - Whether or not it is being used
#  - Kingdom Name
#  - Player
#  - Faction
#  - Heroes
#  - Owned objects
#  - Starting Gold
#  - Starting outpost

num_players = 2
starting_outpost = False

color_mapping = {
    'red': 0,
    'blue': 1,
    'green': 2,
    'black': 3,
    'orange': 4,
    'purple': 5,
    'cyan': 6,
    'brown': 7,
    }

faction_mapping = {
    'nationalist': 1,
    'royalist': 2,
    'council': 3,
    'ceyah': 4,
    }

class Player:
    def __init__(self, color=None, faction=None, player_name=None, kingdom_name=None, starting_gold=None):
        self.color = color
        self.faction = faction
        self.player_name = player_name
        self.kingdom_name = kingdom_name
        self.starting_gold = starting_gold
    
    def playerNum(self):
        return color_mapping[self.color]

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        
        self.tgm_loaded = False
        
        #self.setWindowTitle("Kohan Duels Map Randomizer")
        
        self.player1 = PlayerSettings()
        self.player2 = PlayerSettings()
        self.map_settings = MapSettings()
        self.map_settings.select_map.clicked.connect(self.selectMap)
        self.map_settings.generate_map.clicked.connect(self.generateMap)
        
        settings = QtWidgets.QHBoxLayout()
        settings.addLayout(self.player1)
        settings.addLayout(self.player2)
        settings.addLayout(self.map_settings)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(settings)
        back_button = QtWidgets.QPushButton('Back to Menu')
        back_button.clicked.connect(lambda: self.parent().parent().switchWidget('homepage'))
        layout.addWidget(back_button)
        self.setLayout(layout)

    def selectMap(self):
        filename = qt_shared.FileDialog()
        print(f'filename: {filename}')
        if filename:
            print('valid file')
            self.filename = Path(filename[0])
            print(self.filename)
            self.loadTGM()
    
    def loadTGM(self):
        self.tgm = tgmlib.tgmFile(self.filename)
        self.tgm.load()
        self.map_settings.select_map.setText(self.filename.stem)
        self.tgm_loaded = True
    
    def generateMap(self):
        if not self.tgm_loaded:
            self.loadTGM()
        self.tgm_loaded = False
        players = [self.player1.getSettings(), self.player2.getSettings()]
        for p in players:
            p.starting_gold = self.map_settings.starting_gold.value()
        kingdoms = getActiveKingdoms(self.tgm)
        player_mapping = setPlayerData(self.tgm, players, kingdoms, self.map_settings.heroes.value())
        updateObjects(self.tgm, player_mapping)
        updateFeatures(self.tgm, player_mapping)
        outfile = self.filename.parent/'RandomizedKDMaps'/(self.filename.stem+f'-{players[0].player_name}vs{players[1].player_name}.tgm')
        print(f'saving map to {outfile}')
        outfile.parent.mkdir(exist_ok=True, parents=True)
        self.tgm.write(outfile)

class PlayerSettings(QtWidgets.QVBoxLayout):
    def __init__(self, ):
        super().__init__()
        #self.tgm = tgm
        
        self.addWidget(QtWidgets.QLabel('Player Settings'))
        
        self.name = QtWidgets.QLineEdit()
        self.name.setPlaceholderText('Player Name')
        l1 = QtWidgets.QHBoxLayout()
        l1.addWidget(QtWidgets.QLabel('Player Name:'))
        l1.addWidget(self.name)
        self.addLayout(l1)
        
        self.kingdom = QtWidgets.QLineEdit()
        self.kingdom.setPlaceholderText('Kingdom Name')
        l2 = QtWidgets.QHBoxLayout()
        l2.addWidget(QtWidgets.QLabel('Kingdom Name:'))
        l2.addWidget(self.kingdom)
        self.addLayout(l2)
        
        self.color = QtWidgets.QComboBox()
        self.color.addItems(['Red', 'Blue', 'Green', 'Black', 'Orange', 'Purple', 'Cyan', 'Brown',])
        l3 = QtWidgets.QHBoxLayout()
        l3.addWidget(QtWidgets.QLabel('Player Color:'))
        l3.addWidget(self.color)
        self.addLayout(l3)
        
        self.faction = QtWidgets.QComboBox()
        self.faction.addItems(['Nationalist', 'Royalist', 'Council', 'Ceyah',])
        l4 = QtWidgets.QHBoxLayout()
        l4.addWidget(QtWidgets.QLabel('Faction:'))
        l4.addWidget(self.faction)
        self.addLayout(l4)
        
    def getSettings(self):
        player = Player(player_name=self.name.text(),
                        kingdom_name=self.kingdom.text(),
                        faction=self.faction.currentText().lower(),
                        color=self.color.currentText().lower(),)
        return player
        
class MapSettings(QtWidgets.QVBoxLayout):
    def __init__(self,):
        super().__init__()
        
        self.addWidget(QtWidgets.QLabel('Map Settings'))
        
        self.select_map = QtWidgets.QPushButton('Select Map')
        self.addWidget(self.select_map)
    
        self.starting_gold = QtWidgets.QSpinBox()
        self.starting_gold.setRange(0, 9999)
        self.starting_gold.setValue(789)
        l1 = QtWidgets.QHBoxLayout()
        l1.addWidget(QtWidgets.QLabel('Starting Gold:'))
        l1.addWidget(self.starting_gold)
        self.addLayout(l1)
        
        self.heroes = QtWidgets.QSpinBox()
        self.heroes.setRange(0, 8)
        self.heroes.setValue(5)
        l2 = QtWidgets.QHBoxLayout()
        l2.addWidget(QtWidgets.QLabel('Heroes:'))
        l2.addWidget(self.heroes)
        self.addLayout(l2)
        
        self.generate_map = QtWidgets.QPushButton('Generate Map')
        self.addWidget(self.generate_map)
        
    

def load_heroes():
    heroes = {
        'CEYAH':        [],
        'COUNCIL':      [],
        'NATIONALIST':  [],
        'ROYALIST':     [],
    }
    
    with open(tgmlib.resolve_path('./data/heroes.csv'), 'r') as hero_list:
        while True:
            line = hero_list.readline()
            if line == '':
                break
            hero, faction = line.strip('\n').split(',')
            heroes[faction].append(hero)
    
    return heroes

def choose_heroes(hero_list, faction, number=1):
    picks = []
    for i in range(0, number):
        pick = random.randint(0, len(hero_list[faction])-1)
        picks.append(hero_list[faction].pop(pick))
    return picks

def getActiveKingdoms(tgm):
# check which kingdoms are currently in use
# for later object replacement
    active_kingdoms = []
    for i, k in enumerate(tgm.chunks['EDTR'].kingdoms):
        if k.is_active:
            active_kingdoms.append(i)
        k.is_active = False
        tgm.chunks['PLRS'].players[i].is_active = False
    
    tgm.chunks['EDTR'].deathmatch_kingdoms = num_players
    tgm.chunks['EDTR'].custom_kingdoms = num_players
    tgm.chunks['EDTR'].scenario_kingdoms = num_players
    tgm.chunks['EDTR'].deathmatch_players.setall(False)
    tgm.chunks['EDTR'].custom_players.setall(False)
    tgm.chunks['EDTR'].scenario_players.setall(False)    
    return active_kingdoms

def setPlayerData(tgm, players, active_kingdoms, num_heroes):
    # holds a mapping between existing player numbers and new ones
    player_mapping = {}
    for p in players:
        tgm.chunks['EDTR'].kingdoms[p.playerNum()].is_active = True
        tgm.chunks['EDTR'].kingdoms[p.playerNum()].name = p.kingdom_name
        #tgm.chunks['EDTR'].players[color_mapping[p.color]]['name'] = p.player_name
        tgm.chunks['EDTR'].players[p.playerNum()]['faction'] = faction_mapping[p.faction]
        try:
            tgm.chunks['EDTR'].deathmatch_players[p.playerNum()] = True
            tgm.chunks['EDTR'].custom_players[p.playerNum()] = True
            tgm.chunks['EDTR'].scenario_players[p.playerNum()] = True
        except IndexError:
            print(f'Player "{p.player_name}" with player number "{p.playerNum()}" out-of-bounds for EDTR data\nSizes are {len(tgm.chunks["EDTR"].deathmatch_players)}, {len(tgm.chunks["EDTR"].custom_players)}, and {len(tgm.chunks["EDTR"].scenario_players)} bits')
        tgm.chunks['PLRS'].players[p.playerNum()].faction = faction_mapping[p.faction]
        tgm.chunks['PLRS'].players[p.playerNum()].starting_gold = p.starting_gold
        tgm.chunks['PLRS'].players[p.playerNum()].is_active = True
        
        heroes = choose_heroes(load_heroes(), p.faction.upper(), number=num_heroes)
        for name in heroes:
            tgm.chunks['HROS'].heroes[name]['status'] = 1
            tgm.chunks['HROS'].heroes[name]['experience'] = 0
            tgm.chunks['HROS'].heroes[name]['awakened'] = 0
            tgm.chunks['HROS'].heroes[name]['player_id'] = color_mapping[p.color]
        
        pick = random.randint(0, len(active_kingdoms)-1)
        player_mapping[active_kingdoms.pop(pick)] = p
    return player_mapping

def updateObjects(tgm, player_mapping):
    for i, o in enumerate(tgm.chunks['OBJS'].objs):
        if o.header.player != 8:
            try:
                new_player = player_mapping[o.header.player]
                o.header.player = new_player.playerNum()
                #if the name starts with a faction, take correct faction, append to building type, lookup index
                name = o.TYPE_ref.by_index[o.header.index]['name'].split('_')
                # If obj type-name starts with a faction name
                if name[0].lower() in faction_mapping.keys():
                    new_name = '_'.join([new_player.faction.upper()] + name[1:])
                    o.header.index = o.TYPE_ref.by_name[new_name]['index']
                    # Fix upgrade index if present
                    if o.upgrade_index != 0xFFFF:
                        new_upgrade_name = '_'.join([new_player.faction.upper()] + o.TYPE_ref.by_index[o.upgrade_index]['name'].split('_')[1:])
                        o.upgrade_index = o.TYPE_ref.by_name[new_upgrade_name]['index']
                    # Set HP
                    building_ini = ConfigParser(inline_comment_prefixes=(';',))
                    filepath = tgmlib.resolve_path(f'./Data/ObjectData/Buildings/{new_name}.INI')
                    if not filepath.exists():
                        print(f'{filepath} does not exist!')
                        raise SystemExit()
                    building_ini.read(filepath)
                    print(f'reading {filepath}')
                    o.current_hp, o.max_hp = (float(building_ini['ObjectData']['MaxHitPoints']),)*2
                    o.militia.supply_zone = float(building_ini['BaseData']['SupplyRange'])
                    o.militia.guard_zone = float(building_ini['BaseData']['ControlRange'])
                    o.militia.max = float(building_ini['BaseData']['MaxMilitia'])
                    o.militia.current = o.militia.max/2
                    o.militia.regen_rate = float(building_ini['BaseData']['MilitiaGrowth'])
                    o.militia.company_size = int(building_ini['BaseData']['CompanySize'])
                    o.militia.front_index = o.TYPE_ref.by_name[building_ini['BaseData']['MilitiaType'].upper()]['index']
                    o.militia.support_index = o.militia.front_index
            except KeyError:
                tgm.chunks['OBJS'].objs[i] = None
    
    tgm.chunks['OBJS'].objs[:] = (o for o in tgm.chunks['OBJS'].objs if o is not None)
    return

def updateFeatures(tgm, player_mapping):
    for i, f in enumerate(tgm.chunks['FTRS'].features):
        if tgm.chunks['TYPE'].by_index[f.header.index]['name'] == 'START_POSITION':
            try:
                new_player = player_mapping[f.header.player]
                f.header.player = new_player.playerNum()
                print(f'initial pos ({tgm.chunks["PLRS"].players[new_player.playerNum()].start_pos_se}, {tgm.chunks["PLRS"].players[new_player.playerNum()].start_pos_sw})')
                tgm.chunks['PLRS'].players[new_player.playerNum()].start_pos_se = f.header.hotspot_se
                tgm.chunks['PLRS'].players[new_player.playerNum()].start_pos_sw = f.header.hotspot_sw            
            except KeyError:
                print(f'setting {f} ({i}) to none')
                tgm.chunks['FTRS'].features[i] = None
    
    tgm.chunks['FTRS'].features[:] = (f for f in tgm.chunks['FTRS'].features if f is not None)
    # creates new FIDX after editing FTRS
    tgm.chunks['FIDX'].generate(tgm.chunks['FTRS'])
    return