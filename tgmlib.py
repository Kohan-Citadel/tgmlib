#!/usr/bin/python

import ifflib
import struct
from pathlib import Path
from dataclasses import dataclass, field


class tgmFile:
    """
    A class representing a .TGM game asset file,
    which as a format is based on the IFF file structure
    """
    def __init__(self, filename: str):
        self.filename = Path(filename)
        self.read_from = self.filename.suffix.upper()
        match self.read_from:
            case '.TGM':
                self.iff = ifflib.iff_file(self.filename)
            case _:
                print(f"Error: invalid read type {self.read_from}")
        return
    
   
    class EdtrChunk:
        
        @dataclass
        class Kingdom:
            is_active: bool = False
            name_len: int = 0
            name: str = ''
            unknown: str = ''
            team: int = int.from_bytes(b'FFFF', 'little')
            sai: dict = field(default_factory=lambda: {
                'easy': {'name_len': 0, 'name': ''},
                'medium': {'name_len': 0, 'name': ''},
                'hard': {'name_len': 0, 'name': ''},
                })     
        
        
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[2].data_offset)
                # Skips unknown bytes
                (self.unknown1,) = struct.unpack('4s', in_fh.read(4))
                (self.name_len,) = struct.unpack('B', in_fh.read(1))
                (self.map_name,) = struct.unpack(f'{self.name_len}s', in_fh.read(self.name_len))
                (self.desc_len,) = struct.unpack('B', in_fh.read(1))
                (self.map_description,) = struct.unpack(f'{self.desc_len}s', in_fh.read(self.desc_len))
                # Skips unknown bytes
                (self.unknown2,) = struct.unpack('36s', in_fh.read(36))
                
                self.kingdoms = []
                for i in range(0,8):
                    print(f'reading kingdom {i} at {in_fh.tell()}')
                    new_kingdom = self.Kingdom()
                    (new_kingdom.is_active,
                     new_kingdom.name_len,) = struct.unpack('BxxxB', in_fh.read(5))
                    (new_kingdom.name,) = struct.unpack(f'{new_kingdom.name_len}s', in_fh.read(new_kingdom.name_len))
                    (new_kingdom.unknown,
                     new_kingdom.team,) = struct.unpack('4sI', in_fh.read(8))
                    
                    for k in new_kingdom.sai.keys():
                        print(f'  reading sai {k} at {in_fh.tell()}')
                        (new_kingdom.sai[k]['name_len'],) = struct.unpack('B', in_fh.read(1))
                        (new_kingdom.sai[k]['name'],) = struct.unpack(f"{new_kingdom.sai[k]['name_len']}s", in_fh.read(new_kingdom.sai[k]['name_len']))
                    
                    self.kingdoms.append(new_kingdom)
                
                self.teams = []
                for i in range(0,4):
                    print(f'reading team {i} at {in_fh.tell()}')
                    new_team = {}
                    (new_team['unknown0'],
                     new_team['name_len'],) = struct.unpack('4sB', in_fh.read(5))
                    (new_team['name'],) = struct.unpack(f"{new_team['name_len']}s", in_fh.read(new_team['name_len']))
                    (new_team['unknown1'],) = struct.unpack('12s', in_fh.read(12))
                    self.teams.append(new_team)
                
                # Skips unknown bytes
                (self.unknown2,) = struct.unpack('84s', in_fh.read(84))
                print(f'Reading Players at {in_fh.tell()}')
                self.players = []
                for i in range(0,8):
                    new_player = {}
                    (new_player['name_len'],) = struct.unpack('B', in_fh.read(1))
                    (new_player['name'],) = struct.unpack(f"{new_player['name_len']}s", in_fh.read(new_player['name_len']))
                    (new_player['unknown1'],
                    new_player['faction'],
                    new_player['team'],
                    new_player['unknown2'],) = struct.unpack('4sII4s', in_fh.read(16))
                    
                    self.players.append(new_player)

    
    def load(self):
        match self.read_from:
            case '.TGM':
                self.iff.load()
                if self.iff.data.formtype != "TGSV":
                    print(f"Error: invalid file type: {self.iff.data.formtype}")
                self.EDTR = self.EdtrChunk(self.filename, self.iff)
        return

        
                
                
                
                
testTGM = tgmFile("../../hero-randomizer/bonehenge-KG.tgm")
testTGM.load()
print(testTGM.EDTR.players[0]['name_len'])

