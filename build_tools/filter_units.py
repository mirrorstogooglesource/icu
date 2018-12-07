from __future__ import print_function

import parse_res_source
import filter_util

def main():
    parser = filter_util.create_arg_parser('unit')
    args = parser.parse_args()
    filter_util.filter_icu_data(args, _process_unit_file, {})

def _process_unit_file(source, locale_name):
    parser = parse_res_source.Parser(source)
    tree = parser.parse()

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if (block.name in ('unitsNarrow', 'unitsShort', 'units') and
            block.block_type == 'block'): # Don't touch block type 'alias'.
            # Keep parts (duration/compound) of these but
            # remove the rest.
            kept_something = False
            for unit_type_block in block.get_block_children():
                if unit_type_block.name in ('duration', 'compound'):
                    kept_something = True
                else:
                    to_delete.append(unit_type_block)

            # Delete empty units,units{Narrow|Short} block. Otherwise,
            # locale fallback fails. See crbug.com/707515.
            if not kept_something:
                to_delete.append(block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
