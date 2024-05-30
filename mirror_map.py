import tgmlib
from maplib import Position as P
from copy import deepcopy
import math

tile_symmetries = {
    0x0: {'rotation': (0x0, 0x0, 0x0, 0x0,),
          'reflection': {'n/s': 0x0, 'e/w': 0x0, 'ne/sw': 0x0, 'nw/se': 0x0,},},
    0x1: {'rotation': (0x1, 0x3, 0x5, 0x7,),
          'reflection': {'n/s': 0x1, 'e/w': 0x5, 'ne/sw': 0x3, 'nw/se': 0x7,},},
    0x2: {'rotation': (0x2, 0x4, 0x6, 0x8,),
          'reflection': {'n/s': 0x8, 'e/w': 0x4, 'ne/sw': 0x2, 'nw/se': 0x6,},},
    0x3: {'rotation': (0x3, 0x5, 0x7, 0x1,),
          'reflection': {'n/s': 0x7, 'e/w': 0x3, 'ne/sw': 0x1, 'nw/se': 0x5,},},
    0x4: {'rotation': (0x4, 0x6, 0x8, 0x2,),
          'reflection': {'n/s': 0x6, 'e/w': 0x2, 'ne/sw': 0x8, 'nw/se': 0x4,},},
    0x5: {'rotation': (0x5, 0x7, 0x1, 0x3,),
          'reflection': {'n/s': 0x5, 'e/w': 0x1, 'ne/sw': 0x7, 'nw/se': 0x3,},},
    0x6: {'rotation': (0x6, 0x8, 0x2, 0x4,),
          'reflection': {'n/s': 0x4, 'e/w': 0x8, 'ne/sw': 0x6, 'nw/se': 0x2,},},
    0x7: {'rotation': (0x7, 0x1, 0x3, 0x5,),
          'reflection': {'n/s': 0x3, 'e/w': 0x7, 'ne/sw': 0x5, 'nw/se': 0x1,},},
    0x8: {'rotation': (0x8, 0x2, 0x4, 0x6,),
          'reflection': {'n/s': 0x2, 'e/w': 0x6, 'ne/sw': 0x4, 'nw/se': 0x8,},},
    0x9: {'rotation': (0x9, 0xA, 0x9, 0xA,),
          'reflection': {'n/s': 0x9, 'e/w': 0xA, 'ne/sw': 0x9, 'nw/se': 0xA,},},
    0xA: {'rotation': (0xA, 0x9, 0xA, 0x9,),
          'reflection': {'n/s': 0xA, 'e/w': 0xA, 'ne/sw': 0x9, 'nw/se': 0x9,},},
    0xB: {'rotation': (0xB, 0xE, 0xC, 0xD,),
          'reflection': {'n/s': 0xB, 'e/w': 0xC, 'ne/sw': 0xE, 'nw/se': 0xD,},},
    0xC: {'rotation': (0xC, 0xD, 0xB, 0xE,),
          'reflection': {'n/s': 0xC, 'e/w': 0xB, 'ne/sw': 0xD, 'nw/se': 0xE,},},
    0xD: {'rotation': (0xD, 0xB, 0xE, 0xC,),
          'reflection': {'n/s': 0xE, 'e/w': 0xD, 'ne/sw': 0xB, 'nw/se': 0xC,},},
    0xE: {'rotation': (0xE, 0xC, 0xD, 0xB,),
          'reflection': {'n/s': 0xD, 'e/w': 0xE, 'ne/sw': 0xB, 'nw/se': 0xC,},},
    0xF: {'rotation': (0xF, 0xA, 0xF, 0xA,),
          'reflection': {'n/s': 0xF, 'e/w': 0xF, 'ne/sw': 0xA, 'nw/se': 0xA,},},
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
def flipCoords(center, point, symmetry_type, angle=None, axis=None, debug=False):
    if symmetry_type == 'rotation':
        # creates vector from map center to point, transpose to origin
        v1 = center - point
        se2 = v1.se * math.cos(angle) - v1.sw * math.sin(angle)
        sw2 = v1.se * math.sin(angle) + v1.sw * math.cos(angle)
        if debug:
            print(f"start pos: {point}")
            print(f"  v1 {v1}\n  se2 = {v1.se * math.cos(angle)} - {v1.sw * math.sin(angle)}\n  sw2 = {v1.se * math.sin(angle)} + {v1.sw * math.cos(angle)}")
            print(f"  v2: {P(se2, sw2)}")
            print(f"  final pos: {P(se2, sw2) + center}")
        return center - P(se2, sw2)
    if symmetry_type == 'reflection':
        #print(f'   point: {point}')
        d = axis[1] - axis[0]
        det = d.se*d.se + d.sw*d.sw
        a = (d.sw*(point.sw-axis[0].sw)+d.se*(point.se-axis[0].se))/det
        closest = P(axis[0].se+a*d.se, axis[0].sw+a*d.sw)
        return closest + (closest - point)

def mirror(tgm: tgmlib.tgmFile, sections, source_region, **kwargs):
    #choose axis
    #mirror terrain across axis
    #mirror features across axis
    #mirror objects across axis
    #keep track of editor ids
    #make mirrored objects a different player
    #update GAME chunk if necessary
    size_se = tgm.chunks['EDTR'].size_se
    size_sw = tgm.chunks['EDTR'].size_sw
    center = P((size_se)/2, (size_sw)/2)
    
    # radians between mirroring regions
    rotational_offset = 2 * math.pi / sections
    
    match sections:
        case 2:
            #half map
            symmetry_type = kwargs['symmetry_type']
            match source_region:
                case 'north'|'south':
                    axes = [[P(0, size_sw), P(size_se, 0)]]
                    sides = ('positive',) if source_region == 'north' else ('negative',)
                    symmetry_axis = 'e/w'
                case 'east'|'west':
                    axes = [[P(0,0), P(size_se, size_sw)]]
                    sides = ('positive',) if source_region == 'east' else ('negative',)
                    symmetry_axis = 'n/s'
                case 'north-east'|'south-west':
                    axes = [[P(0, (size_sw)/2), P(size_se, (size_sw)/2)]]
                    sides = ('positive',) if source_region == 'north-east' else ('negative',)
                    symmetry_axis = 'nw/se'
                case 'north-west'|'south-east':
                    axes = [[P((size_se)/2, 0), P((size_se)/2, size_sw)]]
                    sides = ('positive',) if source_region == 'south-east' else ('negative',)
                    symmetry_axis = 'nw/se'
                case _:
                    print(f"invalid source region '{source_region}'")
                    raise SystemExit()
        case 4:
            # quadrants
            symmetry_type = 'rotation'
            if source_region in ('north', 'east', 'south', 'west'):
                symmetry_axes = 'diagonal'
                axes = [[P((size_se)/2, 0), P((size_se)/2, size_sw)],
                        [P(0, (size_sw)/2), P(size_se, (size_sw)/2)],]
                # sides contains the correct side values for each of the two axes for the given quadrant
                match source_region:
                    case 'north':
                        sides = ('negative', 'positive',)
                    case 'east':
                        sides = ('positive', 'positive',)
                    case 'south':
                        sides = ('positive', 'negative',)
                    case 'west':
                        sides = ('negative', 'negative',)
                        
            elif source_region in ('north-east', 'south-east', 'south-west', 'north-west'):
                symmetry_axes = 'orthogonal'
                axes = [[P(0,0), P(size_se, size_sw)],
                        [P(0, size_sw), P(size_se, 0)],]
                match source_region:
                    case 'north-east':
                        sides = ('positive', 'positive',)
                    case 'south-east':
                        sides = ('positive', 'negative',)
                    case 'south-west':
                        sides = ('negative', 'negative',)
                    case 'north-west':
                        sides = ('negative', 'positive',)
                         
            else:
                print(f"invalid source quadrant '{source_region}'\nsource quadrant must be one of ('north', 'east', 'south', 'west', 'north-east', 'south-east', 'south-west', 'north-west')")
                raise SystemExit()
        case _:
            print(f"invalid sections count '{sections}'\nsections must be 2 or 4")
            raise SystemExit()
    
    
    for se in range(size_se):
        for sw in range(size_sw):
            crosses = [cross(axis, P(se+0.5,sw+0.5), side) for axis, side in zip(axes, sides)]
            if all(crosses):
                print('----------------')
                print(f'initial: {P(se,sw)}')
                for pos in range(1, sections):
                    
                    debug = True if pos == 2 else False
                    new_pos = flipCoords(center, P(se+0.5, sw+0.5), symmetry_type, angle=rotational_offset*pos, axis=axes[0], debug=debug)
                    print(f'pos {pos}: {new_pos}')
                    tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)] = tgm.chunks['MGRD'].tiles[se][sw].copy()
                    new_tile = tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)]
                    if new_tile.layout in tile_symmetries:
                        #print(f'flipping tile')
                        try:
                            new_layout = tile_symmetries[new_tile.layout][symmetry_type]
                            new_tile.layout = new_layout[pos] if symmetry_type == 'rotation' else new_layout[symmetry_axis]
                        except Exception:
                            print('  missing tile rotation info')
                            new_tile.terrain1 = 0xE
                            new_tile.terrain2 = 0xE
                    else:
                        new_tile.terrain1 = 0xB
                        new_tile.terrain2 = 0xB
    
    ftrs_iter = tgm.chunks['FTRS'].features.copy()
    for f in ftrs_iter:
        crosses = [cross(axis, P(f.header.hotspot_se, f.header.hotspot_sw), side) for axis, side in zip(axes, sides)]
        if all(crosses):
            for pos in range(1, sections):
                f.fh = None
                new_f = deepcopy(f)
                new_pos = new_pos = flipCoords(center, P(f.header.hotspot_se, f.header.hotspot_sw), symmetry_type, angle=rotational_offset*pos, axis=axes[0])
                new_f.header.hotspot_se, new_f.header.hotspot_sw = new_pos.se, new_pos.sw
                # sets each player owned ftr to a new player per region
                if 0 <= new_f.header.player <= 7:
                    new_f.header.player = (new_f.header.player + pos) % 8
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
        crosses = [cross(axis, P(o.header.hotspot_se, o.header.hotspot_sw), side) for axis, side in zip(axes, sides)]
        if all(crosses):
            for pos in range(1, sections):
                # TODO Enable company mirroring
                if type(o) != tgmlib.Company:
                    o.fh = None
                    new_o = deepcopy(o)
                    new_pos = flipCoords(center, P(o.header.hotspot_se, o.header.hotspot_sw), symmetry_type, angle=rotational_offset*pos, axis=axes[0])
                    new_o.header.hotspot_se, new_o.header.hotspot_sw = new_pos.se, new_pos.sw
                    new_o.header.editor_id = tgm.chunks['GAME'].next_id
                    new_o.pos_se, new_o.pos_sw = int(new_pos.se), int(new_pos.sw)
                    # sets each player owned obj to a new player per region
                    if 0 <= new_o.header.player <= 7:
                        new_o.header.player = (new_o.header.player + pos) % 8
                    tgm.chunks['GAME'].next_id += 1
                    tgm.chunks['GAME'].ids[new_o.header.editor_id] = True
                    tgm.chunks['GAME'].load_flags[new_o.header.editor_id] = True
                    tgm.chunks['OBJS'].objs.append(new_o)
        else:
            tgm.chunks['GAME'].ids[o.header.editor_id] = False
            tgm.chunks['GAME'].load_flags[o.header.editor_id] = False
            tgm.chunks['OBJS'].objs.pop(tgm.chunks['OBJS'].objs.index(o))
    

