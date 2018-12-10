from __future__ import print_function

import parse_res_source
import filter_util

def main():
    parser = filter_util.create_arg_parser('lang')
    parser.add_argument('--minimize-language-list',
                        default='',
                        help=('Comma separated list of languages (locales) ' +
                              'to minimize the data for, despite them being ' +
                              'in ui and accept language lists.'))
    parser.add_argument('--remove-data-already-existing-in-android',
                        action='store_true',
                        help=('Removes data in lang/region/... that ' +
                              'can be fetched from Android APIs'))
    parser.add_argument('--ui-languages-list-file',
                        required=True,
                        help='File that lists languages that matter in the UI')
    parser.add_argument('--accept-languages-list-file',
                        required=True,
                        help=('File that lists languages that can be ' +
                              'selected as Accept Language'))

    args = parser.parse_args()

    with open(args.ui_languages_list_file) as f:
        ui_languages = [s for s in f.read().splitlines()
                            if not s.startswith('#')]

    with open(args.accept_languages_list_file) as f:
        accept_languages = [s for s in f.read().splitlines()
                            if not s.startswith('#')]

    extra_languages_to_minimize = set(args.minimize_language_list.split(','))

    filter_info = {
        'extra_languages_to_minimize': extra_languages_to_minimize,
        'ui_languages': ui_languages,
        'lang_names_to_keep': accept_languages,
        'strip_android_langs': args.remove_data_already_existing_in_android,
    }
    filter_util.filter_icu_data(args, _process_lang_file, filter_info)

def _process_lang_file(source, locale_name,
                       extra_languages_to_minimize,
                       ui_languages,
                       lang_names_to_keep,
                       strip_android_langs):
    """Remove various data we don't need."""
    need_language_for_ui = filter_util.need_language_for_ui(
        locale_name, ui_languages, extra_languages_to_minimize)

    parser = parse_res_source.Parser(source)
    tree = parser.parse()

    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        if block.name == 'Languages':
            kept_something = False
            for lang in block.get_block_children():
                if not need_language_for_ui and locale_name != lang.name:
                    keep = False
                else:
                    keep = filter_util.is_locale_or_parent_locale_in_list(
                        lang.name, lang_names_to_keep)
                    if keep and strip_android_langs:
                        # On Android Java API is used to get lang
                        # data, except for the language and script
                        # names for zh_Hans and zh_Hant which are not
                        # supported by Java API.  Here remove all lang
                        # data except those names.  See the comments
                        # in GetDisplayNameForLocale() (in Chromium's
                        # src/ui/base/l10n/l10n_util.cc) about why we
                        # need the scripts.

                        # This was previously implemented as "keep zh
                        # unless the desktop data file had already
                        # removed it". That was probably a bug.
                        keep = (lang.name == 'zh')
                if keep:
                    kept_something = True
                else:
                    to_delete.append(lang)
            if not kept_something:
                to_delete.append(block)
        elif (block.name == 'Scripts' and
              need_language_for_ui and
              strip_android_langs):
            for script_block in block.get_block_children():
                if script_block.name not in ('Hans', 'Hant'):
                    to_delete.append(script_block)
        elif not need_language_for_ui:
            # Minimal file.
            # Do not include '%%Parent' line on purpose.
            if block.name != '"%%ALIAS"':
                to_delete.append(block)
        elif (strip_android_langs and block.name in (
                'Keys',
                # TODO: Should this be Languages%short? And what about
                # Languages%variant? And what about
                # Scripts%stand-alone and Scripts%variant, shouldn't
                # the be removed too?
                'LanguagesShort',
                'Types',
                'Variants',
                'calendar',
                'codePatterns',
                'localeDisplayPattern')):
            # Easier with a whitelist? Seems to be all but
            # languages and scripts.
            to_delete.append(block)
        elif block.name in (
                'Keys',
                'Types',
                'Types%short',
                'characterLabelPattern',
                'Variants'):
            to_delete.append(block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source

if __name__ == '__main__':
    main()
