from __future__ import print_function

import argparse

import parse_res_source
import filter_util

def main():
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of some ICU data files.'))
    parser.add_argument('--strip', action="store_true")
    parser.add_argument('--in-dir', required=True,
                        help="The zone data files")
    parser.add_argument('--out-dir', required=True,
                        help="The filtered/copied zone data files")

    args = parser.parse_args()

    show_stats = True
    filter_util.filter_icu_data(args, _process_zone_file, {}, show_stats)

def _process_zone_file(source, locale_name):
    """Remove zone example cities. They are huge and only used in Chrome OS."""
    if locale_name == "tzdbNames":
        # This is not a resource file. Just copy.
        return source
    if locale_name == "root":
        # Keep all in root.txt
        return source
    parser = parse_res_source.Parser(source)
    tree = parser.parse(verbose=(False and locale_name == "root"),
                        debug=(False and locale_name == "root"))

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name == "zoneStrings":
            for zone_block in block.get_block_children():
                if ":" in zone_block.name and not "meta:" in zone_block.name:
                    # Remove things like America:Indiana:Winamac
                    # Keep meta:Africa_Southern
                    to_delete.append(zone_block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
