from __future__ import print_function

import argparse

import parse_res_source
import filter_util

def main():
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of some ICU data files.'))
    parser.add_argument('--strip', action="store_true")
    parser.add_argument('--in-dir', required=True,
                        help="The curr data files")
    parser.add_argument('--out-dir', required=True,
                        help="The filtered/copied curr data files")
    parser.add_argument('--currency-keep-list',
                        required=True,
                        help="The file with currencies to keep")

    args = parser.parse_args()

    with open(args.currency_keep_list) as list_file:
        currencies_to_keep = set(list_file.read().split())

    show_stats = True
    filter_info = { "currencies_to_keep": currencies_to_keep }
    filter_util.filter_icu_data(args, _process_curr_file,
                                filter_info, show_stats)

def _process_curr_file(source, locale_name, currencies_to_keep):
    if locale_name == "supplementalData":
        # Not a currency file per se. Just copy.
        return source

    parser = parse_res_source.Parser(source)
    tree = parser.parse(verbose=(False and locale_name == "root"),
                        debug=(False and locale_name == "root"))

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name in ("Currencies",
                          "Currencies%narrow",
                          "CurrencyPlurals"):
            # Keep only certain currencies, and if we keep no
            # currencies, then skip the whole block so that currency
            # fallback works. See crbug.com/791318
            kept_something = False
            for curr_block in block.get_block_children():
                if curr_block.name in currencies_to_keep:
                    kept_something = True
                else:
                    to_delete.append(curr_block)
            if not kept_something:
                to_delete.append(block)
        elif block.name not in (
                '"%%ALIAS"',
                "%%Parent",
                "currencyMap",
                "CurrencyMap",
                "currencyMeta",
                "CurrencyMeta",
                "currencySpacing",
                "CurrencySpacing",
                "currencyUnitPatterns",
                "CurrencyUnitPatterns",
                "Version",
        ):
            # Keep only the blocks listed above.
            to_delete.append(block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
