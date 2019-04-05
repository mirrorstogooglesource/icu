from __future__ import print_function

import parse_res_source
import filter_util

def main():
    parser = filter_util.create_arg_parser('zone')
    args = parser.parse_args()
    filter_util.filter_icu_data(args, _process_zone_file, {})

def _process_zone_file(source, locale_name):
    """Remove zone example cities. They are huge and only used in Chrome OS."""
    if locale_name == 'tzdbNames':
        # This is not a resource file. Just copy.
        return source
    if locale_name == 'root':
        # Keep all in root.txt
        return source
    parser = parse_res_source.Parser(source)
    tree = parser.parse()

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name == 'zoneStrings':
            for zone_block in block.get_block_children():
                if ':' in zone_block.name and not 'meta:' in zone_block.name:
                    # This assumes there are no 'ec' (example city) block in
                    # meta.
                    to_delete.append(zone_block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
