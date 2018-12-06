from __future__ import print_function

import argparse

import parse_res_source
import filter_util

def main():
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of some ICU data files.'))
    parser.add_argument('--strip', action="store_true")
    parser.add_argument('--in-dir', required=True,
                        help="The coll data files")
    parser.add_argument('--out-dir', required=True,
                        help="The filtered/copied coll data files")

    args = parser.parse_args()

    show_stats = True
    filter_util.filter_icu_data(args, _process_coll_file, {}, show_stats)

def _process_coll_file(source, locale_name):
    """big5han and gb2312han collation do not make any sense and nobody
    uses them in zh."""
    if locale_name != "zh":
        return source
    parser = parse_res_source.Parser(source)
    tree = parser.parse(verbose=(False and locale_name == "root"),
                        debug=(False and locale_name == "root"))

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name == "collations":
            for coll_block in block.get_block_children():
                if coll_block.name in ("unihan", "big5han", "gb2312han"):
                    to_delete.append(coll_block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
