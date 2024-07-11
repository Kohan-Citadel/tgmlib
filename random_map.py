import qt_shared
import tgmlib
from mirror_map import P
import random
import math
from pathlib import Path

# All following calculations use the northern-most corner as (0,0)
# and treat the NW-SE edge as Y, and the NE-SW edge as X

# constraints
NUM_MINE = 10
NUM_LAIR = 12
NUM_CITY = 6
MIN_RUSH_DISTANCE = 64 #tiles
START_MIN_RADIUS = 0.3 #scaling factor
START_MAX_RADIUS = 0.8 #scaling factor



filename = Path('192x192.tgm')

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
    
chooseStartPositions()