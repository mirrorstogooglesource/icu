from __future__ import print_function

import parse_res_source
import filter_util

def main():
    parser = filter_util.create_arg_parser('coll')
    args = parser.parse_args()
    filter_util.filter_icu_data(args, _process_region_file, {})

def _process_region_file(source, _locale_name):
    # Remove the display names for numeric region codes other than
    # 419 (Latin America) because we don't use them.
    parser = parse_res_source.Parser(source)
    tree = parser.parse()
    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name in ('Countries',
                          'Countries%short',
                          'Countries%variant'):
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
