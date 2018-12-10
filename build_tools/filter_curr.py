from __future__ import print_function

import parse_res_source
import filter_util

def main():
    parser = filter_util.create_arg_parser('curr')
    parser.add_argument('--currency-keep-list',
                        required=True,
                        help='The file with currencies to keep')

    args = parser.parse_args()

    with open(args.currency_keep_list) as list_file:
        currencies_to_keep = set(list_file.read().split())

    filter_info = { 'currencies_to_keep': currencies_to_keep }
    filter_util.filter_icu_data(args, _process_curr_file, filter_info)

def _process_curr_file(source, locale_name, currencies_to_keep):
    if locale_name == 'supplementalData':
        # Not a currency file per se. Just copy.
        return source

    parser = parse_res_source.Parser(source)
    tree = parser.parse()

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name in ('Currencies',
                          'Currencies%narrow',
                          'CurrencyPlurals'):
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
                '%%Parent',
                'CurrencyMap',
                'CurrencyMeta',
                'currencySpacing',  # Note lower case c.
                'CurrencyUnitPatterns',
                'Version',
        ):
            # Keep only the blocks listed above.
            to_delete.append(block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
