from __future__ import print_function

import argparse

import parse_res_source
import filter_util

def main():
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of some ICU data files.'))
    parser.add_argument('--strip', action="store_true")
    parser.add_argument('--in-dir', required=True,
                        help="The unit data files")
    parser.add_argument('--out-dir', required=True,
                        help="The filtered/copied unit data files")

    args = parser.parse_args()

    show_stats = True
    filter_util.filter_icu_data(args, _process_unit_file, {}, show_stats)

def _process_unit_file(source, locale_name):
    parser = parse_res_source.Parser(source)
    tree = parser.parse(verbose=(False and locale_name == "root"),
                        debug=(False and locale_name == "root"))

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name in ("unitsNarrow", "unitsShort", "units"):
            # Keep parts (duration/compound) of these but
            # remove the rest.
            for unit_type_block in block.get_block_children():
                if unit_type_block.name not in ("duration", "compound"):
                    to_delete.append(unit_type_block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
