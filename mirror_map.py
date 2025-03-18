import tgmlib
from copy import deepcopy
import math
from PyQt5 import QtCore, QtWidgets, QtGui
from pathlib import Path
from PIL import Image
from io import BytesIO
import qt_shared

debug = False

class P:
    def __init__(self, se: float=0, sw: float=0):
        self.se = se
        self.sw = sw
    
    def set(self, se: float=0, sw: float=0):
        self.se = se
        self.sw = sw
    
    def to_pixels(self, size: int):
        tile_x = 6
        tile_y = 4
        axis_angle = math.atan2(tile_y/2, tile_x/2)
        axis_scaling = (tile_x/2)/math.cos(axis_angle)
        self.x = round(axis_scaling * (self.se * math.cos(axis_angle) + self.sw * math.cos(math.pi - axis_angle)) + (size/2) * tile_x)
        self.y = round(axis_scaling * (self.se * math.sin(axis_angle) + self.sw * math.sin(math.pi - axis_angle)))
    
    def copy(self):
        return P(se=self.se, sw=self.sw)
    
    def __str__(self):
        out = f'map coordinates: ({self.se}, {self.sw})'
        if hasattr(self, 'x'):
            out += f' pixel coordinate: ({self.x}, {self.y})'
        return out
    
    def __add__(self, other):
        return P(se=self.se + other.se, sw=self.sw + other.sw)
    
    def __sub__(self, other):
        return P(se=self.se - other.se, sw=self.sw - other.sw)
    
    def __mul__(self, scalar):
        return P(se=self.se * scalar, sw=self.sw * scalar)
    
    def __truediv__(self, scalar):
        return P(se=self.se / scalar, sw=self.sw / scalar)
    
    def __len__(self):
        return round(math.sqrt(pow(self.se, 2) + pow(self.sw, 2)))

class Widget(QtWidgets.QWidget):
    def __init__(self, parent=None):
        super(Widget, self).__init__(parent)
        
        self.tgm_loaded = False
        
        #self.setWindowTitle("Kohan Duels Map Randomizer")
        
        self.mirror_settings = MirrorSettings(self)
        self.mirror_settings.select_map.clicked.connect(self.selectMap)
        self.mirror_settings.mirror_map.clicked.connect(self.mirrorMap)
        self.mirror_settings.save_map.clicked.connect(self.saveMap)
        
        self.thumbnail = Thumbnail(self)
        self.mirror_settings.mirror_map.clicked.connect(self.thumbnail.render)
        
        interface = QtWidgets.QHBoxLayout()
        interface.addWidget(self.mirror_settings)
        interface.addWidget(self.thumbnail)
        
        layout = QtWidgets.QVBoxLayout()
        layout.addLayout(interface)
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
            self.mirror_settings.mirror_map.setEnabled(True)
            self.thumbnail.render()
    
    def loadTGM(self):
        self.tgm = tgmlib.tgmFile(self.filename)
        self.tgm.load()
        self.mirror_settings.select_map.setText(self.filename.stem)
        self.tgm_loaded = True
    
    def mirrorMap(self):
        if not self.tgm_loaded:
            self.loadTGM()
        self.tgm_loaded = False
        print(f'Mirroring {self.tgm.filename} ... ', end='')
        mirror(self.tgm,
               self.mirror_settings.sections.currentText(),
               self.mirror_settings.source_region.currentText(),
               symmetry_type=self.mirror_settings.symmetry.currentText())
        print('finished!')
        self.mirror_settings.save_map.setEnabled(True)
        
    
    def saveMap(self):
        save_name = self.filename.parent/(self.filename.stem+'-mirrored.tgm')
        outfile = Path(qt_shared.FileDialog(directory=self.filename.parent,
                                       forOpen=False,
                                       isFolder=False,
                                       default_name=save_name,
                                       default_extension="tgm")[0])
        print(f'saving map to {outfile}')
        outfile.parent.mkdir(exist_ok=True, parents=True)
        self.tgm.write(outfile)

class MirrorSettings(QtWidgets.QWidget):
    def __init__(self, parent):
        super(MirrorSettings, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        
        self.select_map = QtWidgets.QPushButton('Select Map')
        layout.addWidget(self.select_map)
    
        self.sections = QtWidgets.QComboBox()
        self.sections.addItems(['Half Map', 'Quarter Map',])
        l1 = QtWidgets.QHBoxLayout()
        l1.addWidget(QtWidgets.QLabel('Region Size'))
        l1.addWidget(self.sections)
        layout.addLayout(l1)
        
        self.source_region = QtWidgets.QComboBox()
        self.source_region.addItems(['north', 'north-east', 'east', 'south-east', 'south', 'south-west', 'west', 'north-west',])
        l2 = QtWidgets.QHBoxLayout()
        l2.addWidget(QtWidgets.QLabel('Region Position'))
        l2.addWidget(self.source_region)
        layout.addLayout(l2)
        
        self.symmetry = QtWidgets.QComboBox()
        self.symmetry.addItems(['rotation', 'reflection',])
        l3 = QtWidgets.QHBoxLayout()
        l3.addWidget(QtWidgets.QLabel('Symmetry Type'))
        l3.addWidget(self.symmetry)
        layout.addLayout(l3)
        
        self.mirror_map = QtWidgets.QPushButton('Mirror Map')
        self.mirror_map.setEnabled(False)
        layout.addWidget(self.mirror_map)
        
        self.save_map = QtWidgets.QPushButton('Save Map')
        self.save_map.setEnabled(False)
        layout.addWidget(self.save_map)
        self.setLayout(layout)


class Thumbnail(QtWidgets.QWidget):
    def __init__(self, parent):
        super(Thumbnail, self).__init__(parent)
        layout = QtWidgets.QVBoxLayout()
        layout.addWidget(QtWidgets.QLabel('Preview'))
        self.map_display = QtWidgets.QLabel()
        layout.addWidget(self.map_display)
        self.setLayout(layout)
        
    def render(self):
        print('Rendering thumbnail ... ', end='')
        map_size = self.parent().tgm.chunks['EDTR'].size_se
        render_x = map_size * 6 #x dim of tile
        render_y = map_size * 4 #y dim of tile
        rendered_map = Image.new('RGBA', (render_x, render_y), color=(0,0,0,0))
        img_cache = {}
        for c in ('green', 'beige', 'gray', 'brown', 'white', 'blue'):
            img_cache[c] = Image.open(tgmlib.resolve_path(f'./Data/Tiles/{c}-small.png'))
        for se, row in enumerate(self.parent().tgm.chunks['MGRD'].tiles):
            for sw, tile in enumerate(row):
                match tile.terrain1:
                    case 0|6|15|4|1|7:
                        color = 'green'
                    case 3|5:
                        color = 'beige'
                    case 2|14:
                        color = 'gray'
                    case 12|10:
                        color = 'brown'
                    case 8|9:
                        color = 'white'
                    case 11:
                        color = 'blue'            
                pos = P(se, sw)
                pos.to_pixels(map_size)
                # this should be 50% of the x dimension of the tile
                hsx, hsy = (3, 0)
                box = (pos.x - hsx, pos.y - hsy)
                rendered_map.paste(img_cache[color], box=box, mask=img_cache[color])
        
        img_buffer = BytesIO()
        rendered_map.save(img_buffer, format='PNG')
        pixmap = QtGui.QPixmap()
        pixmap.loadFromData(img_buffer.getvalue())
        self.map_display.setPixmap(pixmap)
        print('finished!')

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


even_objs_to_offset = [
    "COUNCIL_FORTRESS",
    "COUNCIL_OUTPOST",
    "CEYAH_FORTRESS",
    "CEYAH_OUTPOST",
    "ROYALIST_FORTRESS",
    "ROYALIST_OUTPOST",
    "NATIONALIST_FORTRESS",
    "NATIONALIST_OUTPOST",
    "ASSAULT_FORT",
    "SLAAN_VILLAGE",
    "BRIGAND_CAMP",
    "SPREADING_SLAAN_LAIR",
    "SLAAN_LAIR",
    ]


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
        
        rotated_position = center - P(se2, sw2)
        
        if math.isclose(point.se % 1, 0.999, abs_tol=1e-5):
            rotated_position.sw += 0.002
        elif math.isclose(point.se % 1, 0.001, abs_tol=1e-5):
            rotated_position.sw -= 0.002
            
        if math.isclose(point.sw % 1, 0.001, abs_tol=1e-5):
            rotated_position.se -= 0.002
        elif math.isclose(point.sw % 1, 0.999, abs_tol=1e-5):
            rotated_position.se += 0.002
        
        return rotated_position
    if symmetry_type == 'reflection':
        #print(f'   point: {point}')
        d = axis[1] - axis[0]
        det = d.se*d.se + d.sw*d.sw
        a = (d.sw*(point.sw-axis[0].sw)+d.se*(point.se-axis[0].se))/det
        closest = P(axis[0].se+a*d.se, axis[0].sw+a*d.sw)
        reflected_position = closest * 2 - point
        
        # Even-dimension features need to be centered at (0.999, 1.001) to appear at (1, 1)
        # if point.se is 0.999, reflected_position.sw will be 0.999 but it should be 1.001
        # so add 0.002 to rectify this
        # for some reason, certain objects (namely BARBARIAN_VILLAGE) are instead at (1.001, 0.999)
        # so we check for that as well
        if math.isclose(point.se % 1, 0.999, abs_tol=1e-5):
            reflected_position.sw += 0.002
        elif math.isclose(point.se % 1, 0.001, abs_tol=1e-5):
            reflected_position.sw -= 0.002
            
        if math.isclose(point.sw % 1, 0.001, abs_tol=1e-5):
            reflected_position.se -= 0.002
        elif math.isclose(point.sw % 1, 0.999, abs_tol=1e-5):
            reflected_position.se += 0.002
        
        return reflected_position

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
       
    match sections:
        case 'Half Map':
            sections = 2
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
        case 'Quarter Map':
            sections = 4
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
    
    # radians between mirroring regions
    rotational_offset = 2 * math.pi / sections
    
    for se in range(size_se):
        for sw in range(size_sw):
            # use cross product to determine if the coordinate in question is within the source region
            crosses = [cross(axis, P(se+0.5,sw+0.5), side) for axis, side in zip(axes, sides)]
            if all(crosses):
                # for each destination region:
                for section in range(1, sections):
                    new_pos = flipCoords(center, P(se+0.5, sw+0.5), symmetry_type, angle=rotational_offset*section, axis=axes[0], debug=debug)
                    tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)] = tgm.chunks['MGRD'].tiles[se][sw].copy()
                    new_tile = tgm.chunks['MGRD'].tiles[int(new_pos.se)][int(new_pos.sw)]
                    try:
                        new_layout = tile_symmetries[new_tile.layout][symmetry_type]
                        if symmetry_type == 'rotation':
                            if sections == 2:
                                # if a half-map rotational symmetry, tiles need to be rotated an adtl 90deg
                                key = section + 1
                            else:
                                key = section
                        else:
                            key = symmetry_axis
                        new_tile.layout = new_layout[key]
                    except Exception:
                        print(f'missing tile rotation info for ({se}, {sw})')
                        
    
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
                if new_f.header.editor_id < 0x8000:
                    tgm.chunks['GAME'].next_id += 1
                    tgm.chunks['GAME'].ids[new_f.header.editor_id] = True
                    tgm.chunks['GAME'].load_flags[new_f.header.editor_id] = True
                else:
                    print(f'GAME id overflow on feature {new_f}')
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
                    # if rotating, check if the object is a 2x2 building that has a hotspot at (0.5, 0.5)
                    # then subtract (0.5, 0.5) before flipping and add it back afterwards
                    old_hotspot = P(o.header.hotspot_se, o.header.hotspot_sw)
                    new_hotspot = P(0, 0)
                    if symmetry_type == 'rotation' and tgm.chunks['TYPE'].by_index[o.header.index]['name'] in even_objs_to_offset:
                        old_hotspot -= P(0.5, 0.5)
                        new_hotspot += P(0.5, 0.5)
                        
                    new_o = deepcopy(o)
                    new_hotspot += flipCoords(center, old_hotspot, symmetry_type, angle=rotational_offset*pos, axis=axes[0])
                    new_o.header.hotspot_se, new_o.header.hotspot_sw = new_hotspot.se, new_hotspot.sw
                    new_o.header.editor_id = tgm.chunks['GAME'].next_id
                    new_o.pos_se, new_o.pos_sw = int(new_hotspot.se), int(new_hotspot.sw)
                    
                    # sets each player owned obj to a new player per region
                    if 0 <= new_o.header.player <= 7:
                        new_o.header.player = (new_o.header.player + pos) % 8
                    tgm.chunks['GAME'].next_id += 1
                    tgm.chunks['GAME'].ids[new_o.header.editor_id] = True
                    tgm.chunks['GAME'].load_flags[new_o.header.editor_id] = True
                    tgm.chunks['OBJS'].objs.append(new_o)
        else:
            try:
                tgm.chunks['GAME'].ids[o.header.editor_id] = False
                tgm.chunks['GAME'].load_flags[o.header.editor_id] = False
                tgm.chunks['OBJS'].objs.pop(tgm.chunks['OBJS'].objs.index(o))
            except IndexError:
                print(f'Failed to delete object {o}: index overflow in GAME ids')
