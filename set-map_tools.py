# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:19:01 2024

@author: Sceadu
"""
import tgmlib
import random
from configparser import ConfigParser
from pathlib import Path

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
num_heroes = 4
starting_outpost = False

tgm = tgmlib.tgmFile('qtm.tgm')
tgm.load()

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

def load_heroes():
    heroes = {
        'CEYAH':        [],
        'COUNCIL':      [],
        'NATIONALIST':  [],
        'ROYALIST':     [],
    }
    
    with open('data/heroes.csv', 'r') as hero_list:
        while True:
            line = hero_list.readline()
            if line == '':
                break
            hero, faction = line.strip('\n').split(',')
            heroes[faction].append(hero)
    
    return heroes

def choose_heroes(faction, number=1):
    picks = []
    for i in range(0, number):
        pick = random.randint(0, len(hero_list[faction])-1)
        picks.append(hero_list[faction].pop(pick))
    return picks

hero_list = load_heroes()

players = [
    Player(color='green',player_name='Joe',kingdom_name='Joeland',starting_gold=767,faction='royalist'),
    Player(color='red',player_name='Albert',kingdom_name='Albion',starting_gold=676,faction='council'),
    ]

# check which kingdoms are currently in use
# for later object replacement
index = 0
active_kingdoms = []
for k in tgm.chunks['EDTR'].kingdoms:
    if k.is_active:
        active_kingdoms.append(index)
    k.is_active = False
    index += 1

# holds a mapping between existing player numbers and new ones
player_mapping = {}

for p in players:
    tgm.chunks['EDTR'].kingdoms[color_mapping[p.color]].is_active = True
    tgm.chunks['EDTR'].kingdoms[color_mapping[p.color]].name = p.kingdom_name
    #tgm.chunks['EDTR'].players[color_mapping[p.color]]['name'] = p.player_name
    tgm.chunks['EDTR'].players[color_mapping[p.color]]['faction'] = faction_mapping[p.faction]
    
    heroes = choose_heroes(p.faction.upper(), number=num_heroes)
    for name in heroes:
        tgm.chunks['HROS'].heroes[name]['status'] = 1
        tgm.chunks['HROS'].heroes[name]['experience'] = 0
        tgm.chunks['HROS'].heroes[name]['awakened'] = 0
        tgm.chunks['HROS'].heroes[name]['player_id'] = color_mapping[p.color]
    
    pick = random.randint(0, len(active_kingdoms)-1)
    player_mapping[active_kingdoms.pop(pick)] = p
    

        
for i, o in enumerate(tgm.chunks['OBJS'].objs):
    try:
        if o.header.player != 8:
            new_player = player_mapping[o.header.player]
            o.header.player = color_mapping[new_player.color]
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
                filepath = Path(f'./Data/ObjectData/Buildings/{new_name}.INI').resolve()
                if not filepath.exists():
                    print(f'{filepath} does not exist!')
                    raise SystemExit()
                building_ini.read(filepath)
                print(f'reading {filepath}')
                o.current_hp, o.max_hp = (float(building_ini['ObjectData']['MaxHitPoints']),)*2
    except KeyError:
        tgm.chunks['OBJS'].objs[i] = None

tgm.chunks['OBJS'].objs[:] = (o for o in tgm.chunks['OBJS'].objs if o is not None)

print(tgm.chunks['OBJS'].objs)   

tgm.write('C:/Program Files (x86)/Steam/steamapps/common/Kohan Ahrimans Gift/Maps/set-map_test.tgm')     
