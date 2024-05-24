import tgmlib
from maplib import Position
from copy import deepcopy
P = Position

tile_symmetries = {
    0x0: {'n/s': {'rotation': 0x0, 'reflection': 0x0,},
          'e/w': {'rotation': 0x0, 'reflection': 0x0,},
          'ne/sw': {'rotation': 0x0, 'reflection': 0x0,},
          'nw/se': {'rotation': 0x0, 'reflection': 0x0,},},
    0x1: {'n/s': {'rotation': 0x5, 'reflection': 0x1,},
          'e/w': {'rotation': 0x5, 'reflection': 0x5,},
          'ne/sw': {'rotation': 0x5, 'reflection': 0x3,},
          'nw/se': {'rotation': 0x5, 'reflection': 0x7,},},
    0x2: {'n/s': {'rotation': 0x6, 'reflection': 0x8,},
          'e/w': {'rotation': 0x6, 'reflection': 0x4,},
          'ne/sw': {'rotation': 0x6, 'reflection': 0x2,},
          'nw/se': {'rotation': 0x6, 'reflection': 0x6,},},
    0x3: {'n/s': {'rotation': 0x7, 'reflection': 0x7,},
          'e/w': {'rotation': 0x7, 'reflection': 0x3,},
          'ne/sw': {'rotation': 0x7, 'reflection': 0x1,},
          'nw/se': {'rotation': 0x7, 'reflection': 0x5,},},
    0x4: {'n/s': {'rotation': 0x8, 'reflection': 0x6,},
          'e/w': {'rotation': 0x8, 'reflection': 0x2,},
          'ne/sw': {'rotation': 0x8, 'reflection': 0x8,},
          'nw/se': {'rotation': 0x8, 'reflection': 0x4,},},
    0x5: {'n/s': {'rotation': 0x1, 'reflection': 0x5,},
          'e/w': {'rotation': 0x1, 'reflection': 0x1,},
          'ne/sw': {'rotation': 0x1, 'reflection': 0x7,},
          'nw/se': {'rotation': 0x1, 'reflection': 0x3,},},
    0x6: {'n/s': {'rotation': 0x2, 'reflection': 0x4,},
          'e/w': {'rotation': 0x2, 'reflection': 0x8,},
          'ne/sw': {'rotation': 0x2, 'reflection': 0x6,},
          'nw/se': {'rotation': 0x2, 'reflection': 0x2,},},
    0x7: {'n/s': {'rotation': 0x3, 'reflection': 0x3,},
          'e/w': {'rotation': 0x3, 'reflection': 0x7,},
          'ne/sw': {'rotation': 0x3, 'reflection': 0x5,},
          'nw/se': {'rotation': 0x3, 'reflection': 0x1,},},
    0x8: {'n/s': {'rotation': 0x4, 'reflection': 0x2,},
          'e/w': {'rotation': 0x4, 'reflection': 0x6,},
          'ne/sw': {'rotation': 0x4, 'reflection': 0x4,},
          'nw/se': {'rotation': 0x4, 'reflection': 0x8,},},
    0x9: {'n/s': {'rotation': 0x9, 'reflection': 0x9,},
          'e/w': {'rotation': 0x9, 'reflection': 0x9,},
          'ne/sw': {'rotation': 0x9, 'reflection': 0xA,},
          'nw/se': {'rotation': 0x9, 'reflection': 0xA,},},
    0xA: {'n/s': {'rotation': 0xA, 'reflection': 0xA,},
          'e/w': {'rotation': 0xA, 'reflection': 0xA,},
          'ne/sw': {'rotation': 0xA, 'reflection': 0x9,},
          'nw/se': {'rotation': 0xA, 'reflection': 0x9,},},
    0xB: {'n/s': {'rotation': 0xC, 'reflection': 0xB,},
          'e/w': {'rotation': 0xC, 'reflection': 0xC,},
          'ne/sw': {'rotation': 0xC, 'reflection': 0xE,},
          'nw/se': {'rotation': 0xC, 'reflection': 0xD,},},
    0xC: {'n/s': {'rotation': 0xB, 'reflection': 0xC,},
          'e/w': {'rotation': 0xB, 'reflection': 0xB,},
          'ne/sw': {'rotation': 0xB, 'reflection': 0xD,},
          'nw/se': {'rotation': 0xB, 'reflection': 0xE,},},
    0xD: {'n/s': {'rotation': 0xE, 'reflection': 0xE,},
          'e/w': {'rotation': 0xE, 'reflection': 0xD,},
          'ne/sw': {'rotation': 0xE, 'reflection': 0xC,},
          'nw/se': {'rotation': 0xE, 'reflection': 0xB,},},
    0xE: {'n/s': {'rotation': 0xD, 'reflection': 0xD,},
          'e/w': {'rotation': 0xD, 'reflection': 0xE,},
          'ne/sw': {'rotation': 0xD, 'reflection': 0xB,},
          'nw/se': {'rotation': 0xD, 'reflection': 0xC,},},
    0xF: {'n/s': {'rotation': 0xF, 'reflection': 0xF,},
          'e/w': {'rotation': 0xF, 'reflection': 0xF,},
          'ne/sw': {'rotation': 0xF, 'reflection': 0xA,},
          'nw/se': {'rotation': 0xF, 'reflection': 0xA,},},
    
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
        #TODO handle objs on axis properly
        return False

# from https://stackoverflow.com/a/47198877
def flipCoords(center, axis, point, symmetry_type):
    if symmetry_type == 'rotation':
        return center + (center - point)
    if symmetry_type == 'reflection':
        print(f'   point: {point}')
        d = axis[1] - axis[0]
        det = d.se*d.se + d.sw*d.sw
        a = (d.sw*(point.sw-axis[0].sw)+d.se*(point.se-axis[0].se))/det
        closest = P(axis[0].se+a*d.se, axis[0].sw+a*d.sw)
        return closest + (closest - point)


def mirror(tgm: tgmlib.tgmFile, symmetry_axis='north/south', side='positive', symmetry_type='rotation'):
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
            axis = [P(0,0), P(size_se, size_sw)]
            symmetry_axis = 'n/s'
        case 'east/west'|'e/w':
            axis = [P(0, size_sw), P(size_se, 0)]
            symmetry_axis = 'e/w'
        case 'north-east/south-west'|'ne/sw':
            axis = [P((size_se)/2, 0), P((size_se)/2, size_sw)]
            symmetry_axis = 'ne/sw'
        case 'north-west/south-east'|'nw/se':
            axis = [P(0, (size_sw)/2), P(size_se, (size_sw)/2)]
            symmetry_axis = 'nw/se'
        case _:
            print(f"invalid axis '{axis}'")
    
    center = P((size_se)/2, (size_sw)/2)
    
    for se in range(size_se):
        for sw in range(size_sw):
            if cross(axis, P(se,sw), side):
                new_pos = flipCoords(center, axis, P(se+0.5, sw+0.5), symmetry_type)
                print(new_pos)
                tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)] = tgm.chunks['MGRD'].tiles[se][sw].copy()
                new_tile = tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)]
                if new_tile.layout in tile_symmetries:
                    print(f'flipping tile')
                    new_tile.layout = tile_symmetries[new_tile.layout][symmetry_axis][symmetry_type]
                else:
                    new_tile.terrain1 = 0xB
                    new_tile.terrain2 = 0xB
    
    ftrs_iter = tgm.chunks['FTRS'].features.copy()
    for f in ftrs_iter:
        if cross(axis, P(f.header.hotspot_se, f.header.hotspot_sw), side):
            f.fh = None
            new_f = deepcopy(f)
            new_pos = flipCoords(center, axis, P(f.header.hotspot_se, f.header.hotspot_sw), symmetry_type)
            new_f.header.hotspot_se, new_f.header.hotspot_sw = new_pos.se, new_pos.sw
            new_f.header.editor_id = tgm.chunks['GAME'].next_id
            tgm.chunks['GAME'].next_id += 1
            tgm.chunks['GAME'].ids[new_f.header.editor_id] = True
            tgm.chunks['GAME'].load_flags[new_f.header.editor_id] = True
            tgm.chunks['FTRS'].features.append(new_f)
            tgm.chunks['FIDX'].count += 1
            tgm.chunks['FIDX'].sizes.append(len(new_f.pack()))
        else:
            tgm.chunks['GAME'].ids[f.header.editor_id] = False
            tgm.chunks['GAME'].load_flags[f.header.editor_id] = False
            pop_index = tgm.chunks['FTRS'].features.index(f)
            tgm.chunks['FTRS'].features.pop(pop_index)
            tgm.chunks['FIDX'].count -= 1
            tgm.chunks['FIDX'].sizes.pop(pop_index)
    
    objs_iter = tgm.chunks['OBJS'].objs.copy()
    for o in objs_iter:
        if cross(axis, P(o.header.hotspot_se, o.header.hotspot_sw), side):
            # TODO Enable company mirroring
            if type(o) != tgmlib.Company:
                o.fh = None
                new_o = deepcopy(o)
                new_pos = flipCoords(center, axis, P(o.header.hotspot_se, o.header.hotspot_sw), symmetry_type)
                new_o.header.hotspot_se, new_o.header.hotspot_sw = new_pos.se, new_pos.sw
                new_o.header.editor_id = tgm.chunks['GAME'].next_id
                new_o.pos_se, new_o.pos_sw = int(new_pos.se), int(new_pos.sw)
                tgm.chunks['GAME'].next_id += 1
                tgm.chunks['GAME'].ids[new_o.header.editor_id] = True
                tgm.chunks['GAME'].load_flags[new_o.header.editor_id] = True
                tgm.chunks['OBJS'].objs.append(new_o)
        else:
            tgm.chunks['GAME'].ids[o.header.editor_id] = False
            tgm.chunks['GAME'].load_flags[o.header.editor_id] = False
            tgm.chunks['OBJS'].objs.pop(tgm.chunks['OBJS'].objs.index(o))
    
