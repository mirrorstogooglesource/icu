"""Rewrites data so that it becomes smaller after compilation."""

from __future__ import print_function

import argparse
import os
import shutil

def _mergetree(source_dir, dest_dir):
    files = os.listdir(source_dir)
    for f in files:
        src = os.path.join(source_dir, f)
        dest = os.path.join(dest_dir, f)
        if os.path.isdir(src):
            copytree(src, dest)
        else:
            shutil.copy2(src, dest)

def copytree(source, dest):
    """Like shutil.copytree but can handle that dest exists and
    merge/overwrite the files there in that case."""
    if not os.path.isdir(source):
        shutil.copy2(source, dest)
    elif os.path.isdir(dest):
        _mergetree(source, dest)
    else:
        shutil.copytree(source, dest)

def main():
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of some ICU data files.'))

    parser.add_argument('--strip-locales', action="store_true")

    parser.add_argument('--strip-currencies', action="store_true")

    parser.add_argument('--strip-languages', action="store_true")

    parser.add_argument('--strip-zone-example-cities', action="store_true")

    parser.add_argument('--replace-cjdict-with-word_ja', action="store_true")

    parser.add_argument('--in-word-txt',
                        required=True,
                        help='The word.txt to filter')

    parser.add_argument('--out-word-txt',
                        required=True,
                        help='The word.txt to filter')

    parser.add_argument('--in-brkitr-root-txt',
                        required=True,
                        help='The brkitr/root.txt to filter')

    parser.add_argument('--out-brkitr-root-txt',
                        required=True,
                        help='The brkitr/root.txt to filter')

    parser.add_argument('--in-brkitr-ja-txt',
                        required=True,
                        help='The brkitr/ja.txt to filter')

    parser.add_argument('--out-brkitr-ja-txt',
                        required=True,
                        help='The brkitr/ja.txt to filter')

    parser.add_argument('--currency-keep-list',
                        required=True,
                        help="The file with currencies to keep")

    parser.add_argument('--in-curr-dir',
                        required=True,
                        help="The currency data files")

    parser.add_argument('--out-curr-dir',
                        required=True,
                        help="The filtered/copied currency data files")

    parser.add_argument('--minimize-language-list',
                        required=True,
                        help=("Comma separated list of languages (locales) " +
                              "to minimize the data for."))

    parser.add_argument('--in-locales-dir',
                        required=True,
                        help="The locales data files")

    parser.add_argument('--out-locales-dir',
                        required=True,
                        help="The filtered/copied locales data files")

    parser.add_argument('--in-lang-dir',
                        required=True,
                        help="The lang data files")

    parser.add_argument('--out-lang-dir',
                        required=True,
                        help="The filtered/copied lang data files")

    parser.add_argument('--remove-data-already-existing-in-android',
                        action="store_true",
                        help=("Removes data in lang/region/... that " +
                              "can be fetched from Android APIs"))

    parser.add_argument('--in-zone-dir',
                        required=True,
                        help="The zone data files")

    parser.add_argument('--out-zone-dir',
                        required=True,
                        help="The filtered/copied zone data files")

    parser.add_argument('--ui-languages-list-file',
                        required=True,
                        help="File that lists languages that matter in the UI")

    args = parser.parse_args()

    with open(args.ui_languages_list_file) as f:
        ui_languages = f.read().splitlines()

    if args.strip_locales:
        minimize_data_for_locales(args.in_locales_dir,
                                  args.out_locales_dir,
                                  args.minimize_language_list,
                                  ui_languages)
    else:
        copytree(args.in_locales_dir, args.out_locales_dir)

    if args.strip_currencies:
        fix_currencies(args.currency_keep_list,
                       args.in_curr_dir,
                       args.out_curr_dir)
    else:
        copytree(args.in_curr_dir, args.out_curr_dir)

    if args.strip_languages:
        strip_android_langs = args.remove_data_already_existing_in_android
        filter_lang(args.in_lang_dir, args.out_lang_dir,
                    strip_android_langs)
    else:
        copytree(args.in_lang_dir, args.out_lang_dir)

    if args.replace_cjdict_with_word_ja:
        fix_brkitr_root_txt(args.in_brkitr_root_txt, args.out_brkitr_root_txt)
        fix_brkitr_ja_txt(args.in_brkitr_ja_txt, args.out_brkitr_ja_txt)
        fix_word_txt(args.in_word_txt, args.out_word_txt)
    else:
        shutil.copyfile(args.in_brkitr_root_txt, args.out_brkitr_root_txt)
        shutil.copyfile(args.in_brkitr_ja_txt, args.out_brkitr_ja_txt)
        shutil.copyfile(args.in_word_txt, args.out_word_txt)

    if args.strip_zone_example_cities:
        remove_zone_example_cities(args.in_zone_dir, args.out_zone_dir)
    else:
        copytree(args.in_zone_dir, args.out_zone_dir)

def fix_word_txt(source, dest):
    """Strip all references to dictionaryCJK and KanaKanji and
       HangulSymbal."""
    with open(source) as in_file:
        with open(dest, "w") as out:
            _process_word_txt(in_file, out)

WORD_TXT_REPLACEMENTS = (
    ("$ALetter-$dictionaryCJK", "$ALetter"),
    ("# leave CJK scripts out of ALetterPlus", None),
    ("$ComplexContext $dictionaryCJK", "$ComplexContext"),
    ("$dictionaryCJK", None),
    ("$HangulSyllable $HangulSyllable", None),
    ("$KanaKanji $KanaKanji", None),
)

def _process_word_txt(in_file, out):
    for line in in_file:
        for replacement_pattern, replace_with in WORD_TXT_REPLACEMENTS:
            if replacement_pattern in line:
                if replace_with is None:
                    # Delete line.
                    line = None
                else:
                    line = line.replace(replacement_pattern,
                                        replace_with)
                break
        if line is not None:
            out.write(line)

def fix_brkitr_root_txt(source, dest):
    """Strip all references to cjdict."""
    with open(source) as in_file:
        with open(dest, "w") as out:
            trigger1 = False
            for line in in_file:
                if "cjdict.dict" in line:
                    trigger1 = True
                    continue
                out.write(line)
            assert trigger1

def fix_brkitr_ja_txt(source, dest):
    """Strip all references to line_ja.brk."""
    with open(source) as in_file:
        with open(dest, "w") as out:
            trigger1 = False
            marker =  'line_strict:process(dependency){"line.brk"}'
            for line in in_file:
                if marker in line:
                    trigger1 = True
                    out.write(line)
                    out.write(
                        '        word:process(dependency){"word_ja.brk"}\n'
                    )
                else:
                    out.write(line)
            assert trigger1

def _print_block(line, in_file, out):
    indentation_count = 0
    for char in line:
        if char != " ":
            break
        indentation_count += 1
    indentation = " " * indentation_count

    if out is not None:
        out.write(line)
    if "}" in line:
        return

    line = in_file.next()
    while not line.startswith(indentation + "}"):
        if out is not None:
            out.write(line)
        line = in_file.next()
    if out is not None:
        out.write(line)

def _skip_block(line, in_file):
    _print_block(line, in_file, None)

def _print_or_skip_block(line, in_file, out, keep):
    if not keep:
        out = None
    _print_block(line, in_file, out)

def _block_name(line):
    assert "{" in line
    return line.split("{")[0].lstrip()

def _copy_start_of_file(in_file, out, locale_name):
    line = in_file.next()
    while not line.startswith("%s{" % locale_name):
        out.write(line)
        line = in_file.next()
    out.write(line)

def fix_currencies(keep_list_file, in_curr_dir, out_curr_dir):
    """Remove currencies that are not globally important."""

    with open(keep_list_file) as list_file:
        currencies_to_keep = set(list_file.read().split())
    currency_files = os.listdir(in_curr_dir)
    for currency_file in currency_files:
        in_file_name = os.path.join(in_curr_dir, currency_file)
        out_file_name = os.path.join(out_curr_dir, currency_file)
        if (not currency_file.endswith(".txt") or
            currency_file == "supplementalData.txt"):
            # For instance pool.res.
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(currency_file)[0]
        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _process_currency_file(in_file, out, locale_name,
                                       currencies_to_keep)

def _process_currency_file(in_file, out, locale_name, currencies_to_keep):
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True:
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                if block_name in ("Currencies",
                                  "Currencies%narrow",
                                  "CurrencyPlurals"):
                    # Keep only certain currencies, and if we keep no
                    # currencies, then skip the whole block so that
                    # currency fallback works. See crbug.com/791318
                    has_written_block = False
                    block_start_line = line
                    #out.write(line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            currency_name = _block_name(line)
                            keep_curr = currency_name in currencies_to_keep
                            if keep_curr and not has_written_block:
                                out.write(block_start_line)
                                has_written_block = True
                            _print_or_skip_block(line, in_file, out, keep_curr)
                        else:
                            if not has_written_block:
                                out.write(block_start_line)
                                has_written_block = True
                            out.write(line)
                        line = in_file.next()
                    if has_written_block:
                        # Only write the end of block if the block is
                        # non-empty.
                        out.write(line)
                else:
                    keep = block_name in ('"%%ALIAS"',
                                          "%%Parent",
                                          "currencyMap",
                                          "CurrencyMap",
                                          "currencyMeta",
                                          "CurrencyMeta",
                                          "currencySpacing",
                                          "CurrencySpacing",
                                          "currencyUnitPatterns",
                                          "CurrencyUnitPatterns",
                                          "Version")
                    _print_or_skip_block(line, in_file, out, keep)
            else:
                out.write(line)
    except StopIteration:
        pass

def is_interesting_calendar(locale_name, calendar_name):
    if calendar_name in ("generic", "gregorian"):
        return True
    interesting_calendar_map = {
        "am": ["ethiopic", "ethiopic-amete-alem"],
        "ar": ["islamic"],
        "fa": ["persian", "islamic"],
        "he": ["hebrew"],
        "hi": ["indian"],
        "ja": ["japanese"],
        "ko": ["dangi"],
        "th": ["buddhist"],
        "zh": ["chinese"],
        "zh_Hant": ["roc"],
        "root": ["buddhist", "chinese", "roc", "dangi", "ethiopic",
                 "ethiopic-amete-alem", "japanese", "hebrew", "islamic",
                 "islamic-umalqura", "islamic-civil",
                 "islamic-tbla", "islamic-rgsa",
                 "persian", "indian",
        ],
    }
    locale_parts = locale_name.split("_")
    for i in range(len(locale_parts)):
        base_locale = "_".join(locale_parts[:(i+1)])
        if calendar_name in interesting_calendar_map.get(base_locale, []):
            return True
    return False

def minimize_data_for_locales(locales_in_dir, locales_out_dir,
                              languages_to_minimize_str,
                              ui_languages):
    languages_to_minimize = set(languages_to_minimize_str.split(","))

    locale_files = os.listdir(locales_in_dir)
    for locale_file in locale_files:
        in_file_name = os.path.join(locales_in_dir, locale_file)
        out_file_name = os.path.join(locales_out_dir, locale_file)
        # NOTE: "wa.txt" is locally changed in the data import to
        # already be "good enough" for Chromium, i.e. contain whatever
        # is needed to end up in Accept-Language dropdown.
        if not locale_file.endswith(".txt") or locale_file == "wa.txt":
            # For instance pool.res.
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(locale_file)[0]
        is_language_used_in_ui = any(ui_language in locale_name
                                     for ui_language in ui_languages)

        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _process_locale_file(in_file, out, locale_name,
                                     languages_to_minimize,
                                     is_language_used_in_ui)

def _process_locale_file(in_file, out, locale_name, _languages_to_minimize,
                         is_language_used_in_ui):
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True: # Until StopIteration exception.
            # Keep all blocks after "Version" but only a few
            # blocks before that.
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                if is_language_used_in_ui and block_name in (
                        "calendar", "fields"):
                    # Keep parts of these (but remove most of them)
                    out.write(line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            if block_name == "calendar":
                                keep_sub_block = is_interesting_calendar(
                                    locale_name, sub_block_name)
                            else:
                                assert block_name == "fields"
                                keep_sub_block = True
                                if sub_block_name[:3] in (
                                        "mon", "tue", "wed", "thu",
                                        "fri", "sat", "sun"
                                ) and (len(sub_block_name) == 3 or
                                       sub_block_name[3] == "-"):
                                    keep_sub_block = False
                            _print_or_skip_block(line, in_file, out,
                                                 keep_sub_block)
                        else:
                            out.write(line)
                        line = in_file.next()
                    out.write(line)
                    continue

                # Do not include '%%Parent' line on purpose.
                keep = block_name in (
                    '"%%ALIAS"',
                    "LocaleScript",
                    "layout",
                    "Version")
                if not keep and is_language_used_in_ui:
                    # Keep a bit more
                    keep = block_name in (
                        "Ellipsis",
                        "ExemplarCharactersIndex",
                        "MoreInformation",
                        "NumberElements",
                        "contextTransforms",
                        "delimiters",
                        "listPattern",
                        "measurementSystemNames",
                        "parse",
                    )
                _print_or_skip_block(line, in_file, out, keep)
            else:
                out.write(line)
    except StopIteration:
        pass

    # Note: patch_locale.sh also has code to strip only some calendars
    # but since the calendar block is removed above that makes no
    # difference.

def filter_lang(in_lang_dir, out_lang_dir, _strip_android_langs):
    lang_files = os.listdir(in_lang_dir)
    for lang_file in lang_files:
        in_file_name = os.path.join(in_lang_dir, lang_file)
        out_file_name = os.path.join(out_lang_dir, lang_file)
        if not lang_file.endswith(".txt"):
            # For instance pool.res
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(lang_file)[0]
        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _process_lang_file(in_file, out, locale_name)

def _process_lang_file(in_file, out, locale_name):
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True: # Until StopIteration exception.
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                if block_name in ("Languages", "Scripts"):
                    out.write(line)
                    parts_to_keep = {
                        "Languages": ("zh{",),
                        "Scripts": ("Hans{", "Hant{") }[block_name]
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if line.strip().startswith(parts_to_keep):
                            out.write(line)
                        line = in_file.next()
                    out.write(line)
                else:
                    keep = True
                    if block_name in ("Keys",
                                      "LanguagesShort",
                                      "Types",
                                      "Variants",
                                      "calendar",
                                      "codePatterns",
                                      "localeDisplayPattern"):
                        # Delete the whole block.
                        keep = False
                    _print_or_skip_block(line, in_file, out, keep)
            else:
                out.write(line)
    except StopIteration:
        pass

def remove_zone_example_cities(in_zone_dir, out_zone_dir):
    zone_files = os.listdir(in_zone_dir)
    for zone_file in zone_files:
        locale_name = os.path.splitext(zone_file)[0]
        with open(os.path.join(in_zone_dir, zone_file)) as in_file:
            with open(os.path.join(out_zone_dir, zone_file), "w") as out:
                # Strip everything from zoneStrings to the first line with
                # a "meta:" name.
                pos = 0 # 0 = start -> keep, 1 = mid -> delete, 2 = end -> keep
                if locale_name == "root":
                    pos = 2 # Keep everything in root.txt.
                for line in in_file:
                    if pos == 0:
                        out.write(line)
                        if line.startswith("    zoneStrings"):
                            pos = 1
                    if pos == 1 and line.startswith("        \"meta:"):
                        pos = 2
                    if pos == 2:
                        out.write(line)

if __name__ == '__main__':
    main()

