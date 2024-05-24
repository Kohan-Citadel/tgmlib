import argparse
import json
import tgmlib
import update_map
import mirror_map
from pathlib import Path

def update(args: argparse.Namespace):
    with open(args.name_mapping, 'r') as fp:
        name_mapping = json.load(fp)
    
    ref_map = tgmlib.tgmFile(args.type_ref)
    ref_map.load()
    dest_path = Path(args.dest)
    source_path = Path(args.source)
    read_from = source_path.suffix.upper()
    match read_from:
        case '.TGM':
            if dest_path.suffix.upper() == '.TGM':
                filename = dest_path.name
                dest_path = dest_path.parent
            else:
                filename = source_path.name    
            dest_path.mkdir(exist_ok=True, parents=True)
            
            old_map = tgmlib.tgmFile(source_path)
            old_map.load()
            update_map.update(old_map, ref_map, name_mapping, dest_path / filename)
        case '':
            filelist = list(source_path.glob('*'))
            
            if dest_path.suffix != '':
                print(f'tgmtool.py(32) {dest_path.name} is not a valid folder name. Make sure the destination path does not end with a file extension.')
                exit()
            
            dest_path.mkdir(exist_ok=True, parents=True)
            for f in filelist:
                if f.suffix.upper() == '.TGM':
                    old_map = tgmlib.tgmFile(f)
                    old_map.load()
                    update_map.update(old_map, ref_map, name_mapping, dest_path/f.name)

def mirror(args: argparse.Namespace):
    source_path = Path(args.source).resolve()
    if source_path.suffix.upper() != '.TGM':
        print(f'tgmtool.py(45) {source_path.name} is not a .TGM file.')
        exit()
    map_file = tgmlib.tgmFile(source_path)
    map_file.load()
    mirror_map.mirror(map_file, symmetry_axis=args.symmetry_axis, symmetry_type=args.symmetry_type, side=args.side)
    if args.output:
        dest_path = Path(args.output).resolve()
    else:
        dest_path = source_path.parent / (source_path.stem + '_mirrored.tgm')
    if source_path == dest_path:
        res = input(f'Are you sure you want to overwrite {source_path.stem} with the mirrored result? [y/N]')
        if res == '' or res.upper() == 'N':
            dest_path = source_path.parent / (source_path.stem + '_mirrored.tgm')
    map_file.write(dest_path)

## Define parsers
main_parse = argparse.ArgumentParser(prog="tgmtool")
sub_parsers = main_parse.add_subparsers(required=True, help="available commands")

update_parse = sub_parsers.add_parser("update")
update_parse.set_defaults(func=update)
update_parse.add_argument('source', type=str, help='path to target TGM file or folder containing TGM files')
update_parse.add_argument('dest', type=str, help='path to save source file, or containing folder if multiple source files')
update_parse.add_argument('type_ref', type=str, help='path to reference TGM file created with desired mod version(s)')
update_parse.add_argument('name_mapping', type=str, help='path to JSON mapping between old and new type-names')

mirror_parse = sub_parsers.add_parser("mirror")
mirror_parse.set_defaults(func=mirror)
mirror_parse.add_argument('source', type=str, help='path to target TGM file')
mirror_parse.add_argument('-o', '--output', type=str, help='path to save source file')
mirror_parse.add_argument('-a', '--symmetry-axis', type=str, default='n/s', choices=('north/south', 'n/s', 'east/west', 'e/w', 'north-east/south-west', 'ne/sw', 'north-west/south-east', 'nw/se'), help='the line to use as the axis of symmetry')
mirror_parse.add_argument('-t', '--symmetry-type', type=str, default='rotation', choices=('rotation', 'reflection',), help='the type of symmetry. use reflection for a mirror image, reflection for a filpped mirror image')
mirror_parse.add_argument('-s', '--side', type=str, default='positive', choices=('positive', 'negative',), help='which side of the axis to mirror (the other side will be overwritten). positive and negative refer to an implementation detail and do not visually relate to the sides of the axis, so try negative if positive does not work correctly.')

if __name__ == '__main__':
    args = main_parse.parse_args()
    print(args)
    args.func(args)