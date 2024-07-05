# -*- coding: utf-8 -*-
"""
Created on Fri Jul  5 13:19:01 2024

@author: Sceadu
"""
import tgmlib
import random

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
    Player(color='cyan',player_name='Albert',kingdom_name='Albion',starting_gold=676,faction='nationalist'),
    ]



for p in players:
    tgm.chunks['EDTR'].kingdoms[color_mapping[p.color]].is_active = True
    tgm.chunks['EDTR'].kingdoms[color_mapping[p.color]].name = p.kingdom_name
    tgm.chunks['EDTR'].players[color_mapping[p.color]]['name'] = p.player_name
    tgm.chunks['EDTR'].players[color_mapping[p.color]]['faction'] = faction_mapping[p.faction]
    
    heroes = choose_heroes(p.faction.upper(), number=num_heroes)
    for name in heroes:
        tgm.chunks['HROS'].heroes[name]['status'] = 1
        tgm.chunks['HROS'].heroes[name]['experience'] = 0
        tgm.chunks['HROS'].heroes[name]['awakened'] = 0
        tgm.chunks['HROS'].heroes[name]['player_id'] = color_mapping[p.color]

        
        
