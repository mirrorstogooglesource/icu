from __future__ import print_function

import argparse

import parse_res_source
import filter_util

def main():
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of some ICU data files.'))
    parser.add_argument('--strip', action="store_true")
    parser.add_argument('--in-dir', required=True,
                        help="The region data files")
    parser.add_argument('--out-dir', required=True,
                        help="The filtered/copied region data files")

    args = parser.parse_args()

    show_stats = True
    filter_util.filter_icu_data(args, _process_region_file, {}, show_stats)

def _process_region_file(source, locale_name):
    # Remove the display names for numeric region codes other than
    # 419 (Latin America) because we don't use them.
    parser = parse_res_source.Parser(source)
    tree = parser.parse(debug=(False and locale_name == "en_NH"))
    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name in ("Countries",
                          "Countries%short",
                          "Countries%variant"):
            for country_name_block in block.get_block_children():
                country_name = country_name_block.name
                if country_name.isdigit() and int(country_name) != 419:
                    to_delete.append(country_name_block)
    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
