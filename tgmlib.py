#!/usr/bin/python

import ifflib
import struct
from pathlib import Path
from dataclasses import dataclass, field


class tgmFile:
    """
    A class representing a .TGR game asset file,
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
            team: int = int.from_bytes(b'FFFF', 'little')
            
            @dataclass
            class Sai:
                name_len: int
                name: str
            
            def __post_init__(self):
                self.sai = {
                    'easy': self.Sai(0, ''),
                    'medium': self.Sai(0, ''),
                    'hard': self.Sai(0, ''),
                    }
        
        def __init__(self, filename: str, iff: ifflib.iff_file):
            with open(filename, "rb") as in_fh:
                in_fh.seek(iff.data.children[2].data_offset)
                # Skips unknown bytes
                in_fh.seek(4, 1)
                (self.name_len,) = struct.unpack('B', in_fh.read(1))
                (self.map_name,) = struct.unpack(f'{self.name_len}s', in_fh.read(self.name_len))
                (self.desc_len,) = struct.unpack('B', in_fh.read(1))
                (self.map_description,) = struct.unpack(f'{self.desc_len}s', in_fh.read(self.desc_len))
                # Skips unknown bytes
                in_fh.seek(36, 1)   
                self.kingdoms = []
                for i in range(0,8):
                    new_kingdom = self.Kingdom()
                    (new_kingdom.is_active,
                     new_kingdom.name_len,) = struct.unpack('BxxxB', in_fh.read(5))
                    (new_kingdom.name,) = struct.unpack(f'{new_kingdom.name_len}s', in_fh.read(new_kingdom.name_len))
                    
                    for k in new_kingdom.sai.keys():
                        (new_kingdom.sai[k].name_len,) = struct.unpack('B', in_fh.read(1))
                        (new_kingdom.sai[k].name,) = struct.unpack(f'{new_kingdom.sai[k].name_len}s', in_fh.read(new_kingdom.sai[k].name_len))
                    
                    self.kingdoms.append(new_kingdom)
        
            
            

        
# =============================================================================
#         kingdoms: dict = field(default_factory=lambda: {
#             'k1': Kingdom(),
#             })
# =============================================================================
        
        
        
        
        
# =============================================================================
#             
#             
# =============================================================================
        
# =============================================================================
#         
# =============================================================================

                    
# =============================================================================
#     def __init__(self, filename: str, iff: ifflib.iff_file):
#         with open(filename, "rb") as in_fh:
#             in_fh.seek(iff.data.children[2].data_offset)
#             # Skips unknown bytes
#             in_fh.seek(4, 1)
#             (self.name_len,) = struct.unpack('B', in_fh.read(1))
#             self.map_name = struct.unpack(f'{self.name_len}s', in_fh.read(self.name_len))
#             (self.desc_len,) = struct.unpack('B', in_fh.read(1))
#             self.map_description = struct.unpack(f'{self.desc_len}s', in_fh.read(self.desc_len))
#             # Skips unknown bytes
#             in_fh.seek(36, 1)         
# =============================================================================
    
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

