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

    parser.add_argument('--strip-rare-calendars', action="store_true")

    parser.add_argument('--strip-almost-all-calendars', action="store_true")

    parser.add_argument('--strip-duplicate-root-eras', action="store_true")

    parser.add_argument('--strip-currencies', action="store_true")

    parser.add_argument('--strip-regions', action="store_true")

    parser.add_argument('--strip-units', action="store_true")

    parser.add_argument('--strip-languages', action="store_true")

    parser.add_argument('--strip-zone-example-cities', action="store_true")

    parser.add_argument('--strip-legacy-chinese-collation', action="store_true")

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

    parser.add_argument('--in-unit-dir',
                        required=True,
                        help="The unit data files")

    parser.add_argument('--out-unit-dir',
                        required=True,
                        help="The filtered/copied unit data files")

    parser.add_argument('--minimize-language-list',
                        default="",
                        help=("Comma separated list of languages (locales) " +
                              "to minimize the data for, despite them being " +
                              "in ui and accept language lists."))

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

    parser.add_argument('--in-region-dir',
                        required=True,
                        help="The region data files")

    parser.add_argument('--out-region-dir',
                        required=True,
                        help="The filtered/copied region data files")

    parser.add_argument('--in-coll-dir',
                        required=True,
                        help="The coll data files")

    parser.add_argument('--out-coll-dir',
                        required=True,
                        help="The filtered/copied coll data files")

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

    parser.add_argument('--accept-languages-list-file',
                        required=True,
                        help=("File that lists languages that can be " +
                              "selected as Accept Language"))

    args = parser.parse_args()

    with open(args.ui_languages_list_file) as f:
        ui_languages = [s for s in f.read().splitlines()
                            if not s.startswith("#")]

    with open(args.accept_languages_list_file) as f:
        accept_languages = [s for s in f.read().splitlines()
                            if not s.startswith("#")]

    # It's possible this list could by combining ui_languages and
    # accept_languages above so that there is some overlap. Is it even
    # used right now?
    extra_languages_to_minimize = set(args.minimize_language_list.split(","))

    if args.strip_locales:
        minimize_data_for_locales(args.in_locales_dir,
                                  args.out_locales_dir,
                                  extra_languages_to_minimize,
                                  ui_languages,
                                  args.strip_almost_all_calendars,
                                  args.strip_rare_calendars,
                                  args.strip_duplicate_root_eras)
    else:
        copytree(args.in_locales_dir, args.out_locales_dir)

    if args.strip_currencies:
        fix_currencies(args.currency_keep_list,
                       args.in_curr_dir,
                       args.out_curr_dir)
    else:
        copytree(args.in_curr_dir, args.out_curr_dir)

    if args.strip_units:
        strip_units(args.in_unit_dir,
                    args.out_unit_dir)
    else:
        copytree(args.in_unit_dir, args.out_unit_dir)

    if args.strip_languages:
        strip_android_langs = args.remove_data_already_existing_in_android
        filter_lang(args.in_lang_dir, args.out_lang_dir,
                    extra_languages_to_minimize,
                    ui_languages,
                    accept_languages,
                    strip_android_langs)
    else:
        copytree(args.in_lang_dir, args.out_lang_dir)

    if args.strip_legacy_chinese_collation:
        filter_coll(args.in_coll_dir, args.out_coll_dir)
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

    if args.strip_regions:
        filter_regions(args.in_region_dir, args.out_region_dir)
    else:
        copytree(args.in_region_dir, args.out_region_dir)

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

class DelayedBlockStart(object):
    """Sometimes we only want to write the block if it has contents. This
       takes care of that."""

    # TODO: Use this class much more? To solve inheritance problems
    # that the current sed scripts ignore?
    def __init__(self, out, start_line):
        self._out = out
        self._start_line = start_line

    def write(self, line):
        if self._start_line is not None:
            self._out.write(self._start_line)
            self._start_line = None
        self._out.write(line)

    def maybe_write_end(self, line):
        if self._start_line is None:
            self._out.write(line)

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
                    conditional_block = DelayedBlockStart(out, line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            currency_name = _block_name(line)
                            keep_curr = currency_name in currencies_to_keep
                            _print_or_skip_block(line, in_file,
                                                 conditional_block, keep_curr)
                        else:
                            conditional_block.write(line)
                        line = in_file.next()

                    conditional_block.maybe_write_end(line)
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

def is_interesting_calendar(locale_name, calendar_name,
                            strip_almost_all_calendars,
                            strip_rare_calendars):
    if not (strip_almost_all_calendars or strip_rare_calendars):
        return True
    if calendar_name in ("generic", "gregorian"):
        return True
    if strip_almost_all_calendars:
        interesting_calendar_map = {
            "th": ["buddhist"],
        }
    else:
        assert strip_rare_calendars
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

def filter_regions(regions_in_dir, regions_out_dir):
    region_files = os.listdir(regions_in_dir)
    for region_file in region_files:
        in_file_name = os.path.join(regions_in_dir, region_file)
        out_file_name = os.path.join(regions_out_dir, region_file)
        if not region_file.endswith(".txt"):
            # For instance pool.res.
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(region_file)[0]
        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _process_region_file(in_file, out, locale_name)

def _process_region_file(in_file, out, locale_name):
    # Remove the display names for numeric region codes other than
    # 419 (Latin America) because we don't use them.
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True: # Until StopIteration exception.
            # Keep all blocks after "Version" but only a few
            # blocks before that.
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                if block_name in ("Countries",
                                  "Countries%short",
                                  "Countries%variant"):
                    out.write(line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            keep_sub_block = (
                                not sub_block_name.isdigit() or
                                int(sub_block_name) == 419)
                            _print_or_skip_block(line, in_file, out,
                                                 keep_sub_block)
                        else:
                            out.write(line)
                        line = in_file.next()
                    out.write(line)
                else:
                    keep = True
                    _print_or_skip_block(line, in_file, out, keep)
            else:
                out.write(line)
    except StopIteration:
        pass

def _is_locale_or_parent_locale_in_list(locale, lang_list):
    if lang_list and locale == "root":
        return True
    for lang in lang_list:
        if locale == lang:
            return True
        # Need to keep zh_Hans if "zh" in langs_to_keep.
        if (lang + "_") in locale:
            return True
    return False

def minimize_data_for_locales(locales_in_dir, locales_out_dir,
                              extra_languages_to_minimize,
                              ui_languages,
                              strip_almost_all_calendars,
                              strip_rare_calendars,
                              strip_duplicate_root_eras):
    locale_files = os.listdir(locales_in_dir)
    for locale_file in locale_files:
        in_file_name = os.path.join(locales_in_dir, locale_file)
        out_file_name = os.path.join(locales_out_dir, locale_file)
        if not locale_file.endswith(".txt"):
            # For instance pool.res.
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(locale_file)[0]
        is_language_used_in_ui = _is_locale_or_parent_locale_in_list(
            locale_name, ui_languages)
        need_language_for_ui = (is_language_used_in_ui and
                                locale_name not in extra_languages_to_minimize)

        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _process_locale_file(in_file, out, locale_name,
                                     need_language_for_ui,
                                     strip_almost_all_calendars,
                                     strip_rare_calendars,
                                     strip_duplicate_root_eras)

def _process_locale_file(in_file, out, locale_name,
                         need_language_for_ui,
                         strip_almost_all_calendars,
                         strip_rare_calendars,
                         strip_duplicate_root_eras):
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True: # Until StopIteration exception.
            # Keep all blocks after "Version" but only a few
            # blocks before that.
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                if need_language_for_ui and block_name == "calendar":
                    # Keep parts of these (but remove most of them)
                    out.write(line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            keep_sub_block = is_interesting_calendar(
                                locale_name, sub_block_name,
                                strip_almost_all_calendars,
                                strip_rare_calendars)
                            if (keep_sub_block and locale_name == "root" and
                                strip_duplicate_root_eras and
                                sub_block_name in ("japanese", "islamic")):
                                # Keep most, but not japanese>eras,
                                # islamic>eras and islamic>monthNames
                                out.write(line)
                                line = in_file.next()
                                while not line.startswith("        }"):
                                    if "{" in line:
                                        sub_sub_block_name = _block_name(line)
                                        keep_sub_sub_block = not (
                                            sub_sub_block_name == "eras" or
                                            (sub_sub_block_name ==
                                             "monthNames" and
                                             sub_block_name == "islamic"))
                                        _print_or_skip_block(
                                            line, in_file, out,
                                            keep_sub_sub_block)
                                    else:
                                        out.write(line)
                                    line = in_file.next()
                                out.write(line)
                            else:
                                _print_or_skip_block(line, in_file, out,
                                                     keep_sub_block)
                        else:
                            out.write(line)
                        line = in_file.next()
                    out.write(line)
                    continue
                elif need_language_for_ui and block_name == "fields":
                    # Keep parts of these (but remove most of them)
                    conditional_block = DelayedBlockStart(out, line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            keep_sub_block = True
                            if sub_block_name[:3] in (
                                    "mon", "tue", "wed", "thu",
                                    "fri", "sat", "sun") and (
                                        len(sub_block_name) == 3 or
                                        sub_block_name[3] == "-"):
                                keep_sub_block = False
                            _print_or_skip_block(line, in_file,
                                                 conditional_block,
                                                 keep_sub_block)
                        else:
                            conditional_block.write(line)
                        line = in_file.next()
                    conditional_block.maybe_write_end(line)
                    continue

                # Do not include '%%Parent' line on purpose.
                keep = block_name in (
                    '"%%ALIAS"',
                    "LocaleScript",
                    "layout",
                    "Version")
                if need_language_for_ui and not keep:
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

def filter_lang(in_lang_dir, out_lang_dir,
                extra_languages_to_minimize,
                ui_languages,
                langs_to_keep,
                strip_android_langs):
    lang_files = os.listdir(in_lang_dir)
    for lang_file in lang_files:
        in_file_name = os.path.join(in_lang_dir, lang_file)
        out_file_name = os.path.join(out_lang_dir, lang_file)
        if not lang_file.endswith(".txt"):
            # For instance pool.res
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(lang_file)[0]
        is_language_used_in_ui = _is_locale_or_parent_locale_in_list(
            locale_name, ui_languages)
        need_language_for_ui = (is_language_used_in_ui and
                                locale_name not in extra_languages_to_minimize)
        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _process_lang_file(in_file, out, locale_name,
                                   need_language_for_ui,
                                   langs_to_keep,
                                   strip_android_langs)

def _process_lang_file(in_file, out, locale_name,
                       need_language_for_ui,
                       langs_to_keep,
                       remove_language_names_already_in_android):
    if remove_language_names_already_in_android:
        langs_to_keep = ["zh"]
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True: # Until StopIteration exception.
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                if block_name == "Languages":
                    # If "Languages" would end up empty, don't write
                    # it at all.
                    conditional_block = DelayedBlockStart(out, line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            keep_sub_block = (
                                _is_locale_or_parent_locale_in_list(
                                    sub_block_name, langs_to_keep))
                            if (not need_language_for_ui and
                                locale_name != sub_block_name):
                                keep_sub_block = False
                            _print_or_skip_block(line, in_file,
                                                 conditional_block,
                                                 keep_sub_block)
                        else:
                            conditional_block.write(line)
                        line = in_file.next()
                    conditional_block.maybe_write_end(line)
                elif (need_language_for_ui and
                      remove_language_names_already_in_android and
                      block_name == "Scripts"):
                    out.write(line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            keep_sub_block = sub_block_name in ("Hans", "Hant")
                            _print_or_skip_block(line, in_file, out,
                                                 keep_sub_block)
                        line = in_file.next()
                    out.write(line)
                elif not need_language_for_ui:
                    # Minimal file.
                    # Do not include '%%Parent' line on purpose.
                    keep = block_name == "%%ALIAS"
                    _print_or_skip_block(line, in_file, out, keep)
                elif (remove_language_names_already_in_android and
                      block_name in (
                          "Keys",
                          "LanguagesShort",
                          "Types",
                          "Variants",
                          "calendar",
                          "codePatterns",
                          "localeDisplayPattern")):
                    # Easier with a whitelist? Seems to be all but
                    # languages and scripts.
                    keep = False
                    _print_or_skip_block(line, in_file, out, keep)
                else:
                    keep = block_name not in (
                        "Keys",
                        "Types",
                        "Types%short",
                        "characterLabelPattern",
                        "Variants")
                    _print_or_skip_block(line, in_file, out, keep)
            else:
                out.write(line)
    except StopIteration:
        pass

def remove_zone_example_cities(in_zone_dir, out_zone_dir):
    zone_files = os.listdir(in_zone_dir)
    for zone_file in zone_files:
        if zone_file in ("tzdbNames.txt", "pool.res"):
            # Not zone files, don't touch or it will create races in
            # the build system.
            continue
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

# COLL
def filter_coll(in_coll_dir, out_coll_dir):
    coll_files = os.listdir(in_coll_dir)
    for coll_file in coll_files:
        in_file_name = os.path.join(in_coll_dir, coll_file)
        out_file_name = os.path.join(out_coll_dir, coll_file)
        if coll_file != "zh.txt":
            # Including pool.res
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(coll_file)[0]
        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _remove_legacy_chinese_codepoint_collation(
                    in_file, out, locale_name)

def _remove_legacy_chinese_codepoint_collation(in_file, out, locale_name):
    """big5han and gb2312han collation do not make any sense and nobody
    uses them."""
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True: # Until StopIteration exception.
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                keep = True
                if block_name == "collations":
                    out.write(line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            keep_sub_block = sub_block_name not in (
                                    "unihan", "big5han", "gb2312han")
                            _print_or_skip_block(line, in_file, out,
                                                 keep_sub_block)
                        line = in_file.next()
                    out.write(line)
                else:
                    _print_or_skip_block(line, in_file, out, keep)
            else:
                out.write(line)
    except StopIteration:
        pass

# UNIT
def strip_units(in_unit_dir, out_unit_dir):
    unit_files = os.listdir(in_unit_dir)
    for unit_file in unit_files:
        in_file_name = os.path.join(in_unit_dir, unit_file)
        out_file_name = os.path.join(out_unit_dir, unit_file)
        if not unit_file.endswith(".txt"):
            # For instance pool.res
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(unit_file)[0]
        with open(in_file_name) as in_file:
            with open(out_file_name, "w") as out:
                _process_unit_file(in_file, out, locale_name)

def _process_unit_file(in_file, out, locale_name):
    try:
        _copy_start_of_file(in_file, out, locale_name)
        while True: # Until StopIteration exception.
            line = in_file.next()
            if "{" in line:
                block_name = _block_name(line)
                keep = True
                if block_name in ("unitsNarrow", "unitsShort", "units"):
                    # Keep parts (duration/compound) of these but
                    # remove the rest.
                    conditional_block = DelayedBlockStart(out, line)
                    line = in_file.next()
                    while not line.startswith("    }"):
                        if "{" in line:
                            sub_block_name = _block_name(line)
                            keep_sub_block = sub_block_name in (
                                "duration", "compound")
                            _print_or_skip_block(line, in_file,
                                                 conditional_block,
                                                 keep_sub_block)
                        line = in_file.next()
                    conditional_block.maybe_write_end(line)
                else:
                    _print_or_skip_block(line, in_file, out, keep)
            else:
                out.write(line)
    except StopIteration:
        pass

if __name__ == '__main__':
    main()

