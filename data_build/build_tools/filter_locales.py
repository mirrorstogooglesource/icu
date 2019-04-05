from __future__ import print_function

import sys
import os
import shutil

import parse_res_source
import filter_util

def main():
    parser = filter_util.create_arg_parser('locales')
    parser.add_argument('--strip-rare-calendars', action='store_true')
    parser.add_argument('--strip-almost-all-calendars', action='store_true')
    parser.add_argument('--strip-duplicate-root-eras', action='store_true')
    parser.add_argument('--minimize-language-list',
                        default='',
                        help=('Comma separated list of languages (locales) ' +
                              'to minimize the data for, despite them being ' +
                              'in ui and accept language lists.'))
    parser.add_argument('--ui-languages-list-file',
                        required=True,
                        help='File that lists languages that matter in the UI')

    args = parser.parse_args()

    with open(args.ui_languages_list_file) as f:
        ui_languages = [s for s in f.read().splitlines()
                            if not s.startswith('#')]

    extra_languages_to_minimize = set(args.minimize_language_list.split(','))

    filter_info = {
        'extra_languages_to_minimize': extra_languages_to_minimize,
        'ui_languages': ui_languages,
        'strip_almost_all_calendars': args.strip_almost_all_calendars,
        'strip_rare_calendars': args.strip_rare_calendars,
        'strip_duplicate_root_eras': args.strip_duplicate_root_eras,
    }
    filter_util.filter_icu_data(args, _process_locale_file, filter_info)

def is_interesting_calendar(locale_name, calendar_name,
                            strip_almost_all_calendars,
                            strip_rare_calendars):
    if not (strip_almost_all_calendars or strip_rare_calendars):
        return True
    if calendar_name in ('default', 'generic', 'gregorian'):
        return True
    if strip_almost_all_calendars:
        interesting_calendar_map = {
            'th': ['buddhist'],
        }
    else:
        assert strip_rare_calendars
        interesting_calendar_map = {
            'am': ['ethiopic', 'ethiopic-amete-alem'],
            'ar': ['islamic'],
            'fa': ['persian', 'islamic'],
            'he': ['hebrew'],
            'hi': ['indian'],
            'ja': ['japanese'],
            'ko': ['dangi'],
            'th': ['buddhist'],
            'zh': ['chinese'],
            'zh_Hant': ['roc'],
            'root': ['buddhist', 'chinese', 'roc', 'dangi', 'ethiopic',
                     'ethiopic-amete-alem', 'japanese', 'hebrew', 'islamic',
                     'islamic-umalqura', 'islamic-civil',
                     'islamic-tbla', 'islamic-rgsa',
                     'persian', 'indian',
            ],
        }
    locale_parts = locale_name.split('_')
    for i in range(len(locale_parts)):
        base_locale = '_'.join(locale_parts[:(i+1)])
        if calendar_name in interesting_calendar_map.get(base_locale, []):
            return True
    return False

def matching_children(block, child_block_name):
    return [x for x in block.get_block_children()
            if x.name == child_block_name]

def _process_locale_file(source, locale_name, ui_languages,
                         extra_languages_to_minimize,
                         strip_almost_all_calendars,
                         strip_rare_calendars, strip_duplicate_root_eras):
    need_language_for_ui = filter_util.need_language_for_ui(
        locale_name, ui_languages, extra_languages_to_minimize)
    parser = parse_res_source.Parser(source)
    tree = parser.parse()
    to_delete = []
    main_node = tree.main_node()
    for block in main_node.get_block_children():
        keep = block.name in (
            # Do not include '%%Parent' line on purpose.
            '"%%ALIAS"',
            'LocaleScript',
            'layout',
            'Version')
        # Keep a bit more if this is a UI language.
        keep = keep or (need_language_for_ui and block.name in (
            '%%Parent',
            'Ellipsis',
            'ExemplarCharactersIndex',
            'MoreInformation',
            'NumberElements',
            'contextTransforms',
            'delimiters',
            'listPattern',
            'measurementSystemNames',
            'parse',
        ))
        if not keep and need_language_for_ui and block.name == 'calendar':
            # Need some of this, but not all.
            for calendar_block in block.get_block_children():
                calendar_name = calendar_block.name
                if is_interesting_calendar(locale_name, calendar_name,
                                           strip_almost_all_calendars,
                                           strip_rare_calendars):
                    keep = True  # At least one calendar.

                    # We still strip japanese>eras, islamic>eras and
                    # islamic>monthNames in the root since they are
                    # large and already exist where they are needed.
                    if locale_name == 'root' and strip_duplicate_root_eras:
                        if calendar_name in ('japanese', 'islamic'):
                            to_delete.extend(matching_children(calendar_block,
                                                               'eras'))

                        if calendar_name == 'islamic':
                            to_delete.extend(matching_children(calendar_block,
                                                               'monthNames'))
                else:
                    to_delete.append(calendar_block)
        if not keep and need_language_for_ui and block.name == 'fields':
            # Keep parts of these (but remove most of them)
            for field_block in block.get_block_children():
                field_name = field_block.name
                # Remove day names but keep the rest.
                if (field_name[:3] in ('mon', 'tue', 'wed', 'thu',
                                       'fri', 'sat', 'sun') and
                    (len(field_name) == 3 or field_name[3] == '-')):
                    to_delete.append(field_block)
                else:
                    # Something here making it worth keeping |fields|.
                    keep = True

        if not keep:
            to_delete.append(block)

    if to_delete:
        cleaned_source = parser.get_cleaned_source(to_delete)
        return cleaned_source

    return source


if __name__ == '__main__':
    main()
