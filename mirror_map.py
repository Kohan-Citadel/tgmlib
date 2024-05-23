import tgmlib
from maplib import Position
P = Position

tile_symmetries = {
    0x0: {'n/s': {
            'rotational': 0x0,
            'reflectional': 0x0,},
        'e/w': {
            'rotational': 0x0,
            'reflectional': 0x0,},
        'ne/sw': {
            'rotational': 0x0,
            'reflectional': 0x0,},
        'nw/se': {
            'rotational': 0x0,
            'reflectional': 0x0,},},
    0x1: {'n/s': {
            'rotational': 0x5,
            'reflectional': 0x1,},
        'e/w': {
            'rotational': 0x5,
            'reflectional': 0x5,},
        'ne/sw': {
            'rotational': 0x5,
            'reflectional': 0x3,},
        'nw/se': {
            'rotational': 0x5,
            'reflectional': 0x7,},},
    0x20: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0x30: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0x40: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0x50: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0x60: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0x70: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0x80: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0x90: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0xA0: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0xB0: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0xC0: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0xD0: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0xE0: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    0xF0: {'n/s': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'e/w': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'ne/sw': {
            'rotational': 0xF,
            'reflectional': 0xF,},
        'nw/se': {
            'rotational': 0xF,
            'reflectional': 0xF,},},
    
    }

# from https://stackoverflow.com/a/3838398
def cross(axis, point, side):
    v1 = axis[1] - axis[0]   # Vector 1
    v2 = axis[1] - point   # Vector 2
    xp = v1.se*v2.sw - v1.sw*v2.se  # Cross product (magnitude)
    if xp > 0 and side == 'positive':
        #print(f'({point.se},{point.sw}) > 0')
        return True
    elif xp < 0 and side =='negative':
        #print(f'({point.se},{point.sw}) < 0')
        return True
    else:
        return False

# from https://stackoverflow.com/a/47198877
def flipCoords(center, axis, point, symmetry_type):
    if symmetry_type == 'rotational':
        return center + (center - point)
    if symmetry_type == 'reflectional':
        d = axis[1] - axis[0]
        det = d.se*d.se + d.sw*d.sw
        a = (d.sw*(point.sw-axis[0].sw)+d.sw*(point.se-axis[0].se))/det
        closest = P(axis[0].se+a*d.se, axis[0].sw+a*d.sw)
        return closest + (closest - point)


def mirror(tgm: tgmlib.tgmFile, symmetry_axis='north/south', side='positive', symmetry_type='rotational'):
    #choose axis
    #mirror terrain across axis
    #mirror features across axis
    #mirror objects across axis
    #keep track of editor ids
    #make mirrored objects a different player
    #update GAME chunk if necessary
    size_se = tgm.chunks['EDTR'].size_se
    size_sw = tgm.chunks['EDTR'].size_sw
    match symmetry_axis:
        case 'north/south'|'n/s':
            axis = [P(0,0), P(size_se-1, size_sw-1)]
            symmetry_axis = 'n/s'
        case 'east/west'|'e/w':
            axis = [P(0, size_sw-1), P(size_se-1, 0)]
            symmetry_axis = 'e/w'
        case 'north-east/south-west'|'ne/sw':
            axis = [P((size_se-1)/2, 0), P((size_se-1)/2, size_sw)]
            symmetry_axis = 'ne/sw'
        case 'north-west/south-east'|'nw/se':
            axis = [P(0, (size_sw-1)/2), P(size_se, (size_sw-1)/2)]
            symmetry_axis = 'nw/se'
        case _:
            print(f"invalid axis '{axis}'")
    
    center = P((size_se-1)/2, (size_sw-1)/2)
    
    for se in range(size_se):
        for sw in range(size_sw):
            if cross(axis, P(se,sw), side):
                new_pos = flipCoords(center, axis, P(se, sw), symmetry_type)
                tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)] = tgm.chunks['MGRD'].tiles[se][sw].copy()
                new_tile = tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)]
                if new_tile.layout in tile_symmetries:
                    print(f'flipping tile')
                    new_tile.layout = tile_symmetries[new_tile.layout][symmetry_axis][symmetry_type]
                else:
                    new_tile.terrain1 = 0xB
                    new_tile.terrain2 = 0xB

tgm = tgmlib.tgmFile('ECM1-CLEARED.TGM')
tgm.load()
mirror(tgm, symmetry_axis='n/s', symmetry_type='rotational')
tgm.write('../../../Mod-Test-Only/Maps/_MIRROR.TGM')
    
