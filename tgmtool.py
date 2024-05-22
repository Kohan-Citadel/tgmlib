import argparse
import json
import tgmlib
import update_map
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

## Define parsers
main_parse = argparse.ArgumentParser(prog="tgmtool")
sub_parsers = main_parse.add_subparsers(required=True, help="available commands")

update_parse = sub_parsers.add_parser("update")
update_parse.set_defaults(func=update)
update_parse.add_argument('source', type=str, help='path to target TGM file or folder containing TGM files')
update_parse.add_argument('dest', type=str, help='path to save source file, or containing folder if multiple source files')
update_parse.add_argument('type_ref', type=str, help='path to reference TGM file created with desired mod version(s)')
update_parse.add_argument('name_mapping', type=str, help='path to JSON mapping between old and new type-names')

if __name__ == '__main__':
    args = main_parse.parse_args()
    print(args)
    args.func(args)