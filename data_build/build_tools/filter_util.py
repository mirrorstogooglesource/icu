"""Shared functions and classes among the filters."""

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

class SavedStats(object):
    def __init__(self):
        self.source_size = 0
        self.cleaned_source_size = 0

    def update(self, locale_name, source, cleaned_source):
        self.source_size += len(source)
        self.cleaned_source_size += len(cleaned_source)
        saved = len(source) - len(cleaned_source)
        if saved != 0:
            print('%s: Saved %d bytes (%.0f%%)' %
                  (locale_name, saved, saved * 100.0 / len(source)))

    def total(self):
        saved = self.source_size - self.cleaned_source_size
        print('TOTAL: Saved %d bytes (%.0f%%)' %
              (saved, saved * 100.0 / self.source_size))

def create_arg_parser(kind):
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of %s ICU data files.' % kind))
    parser.add_argument('--strip', action='store_true')
    parser.add_argument('--verbose', action='store_true')
    parser.add_argument('--in-dir', required=True,
                        help='The %s data files' % kind)
    parser.add_argument('--out-dir', required=True,
                        help='The filtered/copied %s data files' % kind)

    return parser

def filter_icu_data(args, filter_fn, filter_info):
    in_dir = args.in_dir
    out_dir = args.out_dir
    strip = args.strip
    show_stats = args.verbose

    if not strip:
        copytree(in_dir, out_dir)
        return

    if show_stats:
        stats = SavedStats()

    if not os.path.isdir(out_dir):
            os.makedirs(out_dir)

    files = os.listdir(in_dir)
    # Could we easily parallelize this? Simple input, simple output.
    for icu_res_file in files:
        in_file_name = os.path.join(in_dir, icu_res_file)
        out_file_name = os.path.join(out_dir, icu_res_file)
        if not icu_res_file.endswith('.txt'):
            # For instance pool.res.
            shutil.copyfile(in_file_name, out_file_name)
            continue
        locale_name = os.path.splitext(icu_res_file)[0]
        with open(in_file_name) as in_file:
            source = in_file.read()
        cleaned_source = filter_fn(source, locale_name, **filter_info)
        with open(out_file_name, 'w') as out:
            out.write(cleaned_source)

        if show_stats:
            stats.update(locale_name, source, cleaned_source)

    if show_stats:
        stats.total()

def is_locale_or_parent_locale_in_list(locale, lang_list):
    for lang in lang_list:
        if locale == lang:
            return True
        # Need to keep zh_Hans if 'zh' in langs_to_keep.
        if (lang + '_') in locale:
            return True
    return False

def need_language_for_ui(locale_name,
                         ui_languages,
                         extra_languages_to_minimize):
    if locale_name == 'root':
        return True
    is_language_used_in_ui = is_locale_or_parent_locale_in_list(
        locale_name, ui_languages)
    return_value = (is_language_used_in_ui and
                    locale_name not in extra_languages_to_minimize)
    return return_value
