"""Generates the data necessary for gn_data_build_system/BUILD.gn and
icu_data.gyp from a minimal maintenance json file."""

from __future__ import print_function

import argparse
import json
import os
import sys

def change_ext(path, new_ext):
    return os.path.splitext(path)[0] + new_ext

def main():
    parser = argparse.ArgumentParser(
        description=('Generates build system data.'))

    parser.add_argument('--config-data',
                        required=True,
                        help='The json file with the configuration.')

    parser.add_argument('--out',
                        required=True,
                        help=('The file that will be written containing the ' +
                              'with the generated configuration'))

    args = parser.parse_args()

    with open(args.config_data) as data_file:
        data = json.load(data_file)

    with open(args.out, "w") as out:
        write_header(out)
        write_start_block(out)
        write_nrm(out, data["nrm"])
        write_ucm(out, data["mappings"])
        write_brkitr_brk(out)
        write_brkitr_res(out, data["brkitr_res"])
        write_locales(out, data["locales"], data["locales_aliases"])
        write_misc(out, data["misc"])
        write_curr(out, data["curr"], data["curr_aliases"])
        write_lang(out, data["lang"], data["lang_aliases"])
        write_region(out, data["region"], data["region_aliases"])
        write_zone(out, data["zone"], data["zone_aliases"])
        write_unit(out, data["unit"], data["unit_aliases"])
        write_coll(out, data["coll"], data["coll_aliases"])
        write_end_block(out)

def write_header(out):
    out.write("""\
# Copyright 2015 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

""")

def write_start_block(out):
    out.write("""\
{
    'variables': {
""")

def _write_var_list_start(out, var_name):
    out.write("""\
        '%s': [
""" % var_name)

def _write_var_list_end(out):
    out.write("""\
        ],
""")

def _write_var_list(out, var, pattern, items):
    _write_var_list_start(out, var)
    line_pattern = """\
            '%s',
""" % pattern
    for item in items:
        out.write(line_pattern % item)
    _write_var_list_end(out)

def write_nrm(out, files):
    for var, pattern in (("icu_data_nrm_sources", "source/data/in/%s.nrm"),
                         ("icu_data_nrm_generated", "<(icu_gen_dir)/%s.nrm")):
        _write_var_list(out, var, pattern, files)

def write_ucm(out, files):
    for var, pattern in (
            ("icu_data_ucm_sources", "source/data/mappings/%s.ucm"),
            ("icu_data_ucm_generated", "<(icu_gen_dir)/%s.cnv")):
        _write_var_list(out, var, pattern, files)

def write_brkitr_brk(out):
    files = (
        'char',
        'line',
        'line_fi',
        'sent',
        'sent_el',
        'title',
        'word', # Special directory for this one since Android patches it.
        'word_ja') # word_ja is a workaround when cjdict.dict is missing.
    source_files = []
    for f in files:
        if f == "word":
            source_files.append("<(icu_gen_tmp_dir)/brkitr/%s.txt" % f)
        else:
            source_files.append("source/data/brkitr/%s.txt" % f)
    _write_var_list(out, "icu_data_brkitr_brk_sources", "%s", source_files)
    _write_var_list(out, "icu_data_brkitr_brk_generated",
                    "<(icu_gen_dir)/brkitr/%s.brk", files)

def write_brkitr_res(out, files):
    _write_var_list_triplet(out, "brkitr_res_root", "brkitr", ["root"])

    _write_var_list(out, "icu_data_brkitr_res_sources",
                    "source/data/brkitr/%s.txt", files)

    # ja.txt is a workaround when cjdict.dict is missing.
    filtered_files = ["ja"]
    _write_var_list(out, "icu_data_brkitr_res_filtered_sources",
                    "<(icu_gen_tmp_dir)/brkitr/%s.txt", filtered_files)
    all_files = files + filtered_files
    _write_var_list(out, "icu_data_brkitr_res_generated",
                    "<(icu_gen_dir)/brkitr/%s.res", all_files)


def write_locales(out, files, alias_files):
    for var, pattern in (
            ("icu_data_locales_res_root_sources", "source/data/locales/%s.txt"),
            ("icu_data_locales_res_root_generated", "<(icu_gen_dir)/%s.res")):
        _write_var_list(out, var, pattern, ["root"])

    for var_name_middle, file_list in (
            ("locales_res", files),
            ("locales_res_alias", alias_files)):
        for var, pattern in (
            ("icu_data_%s_raw_sources" % var_name_middle,
             "source/data/locales/%s.txt"),
            ("icu_data_%s_filtered_sources" % var_name_middle,
             "<(icu_gen_tmp_dir)/locales/%s.txt"),
            ("icu_data_%s_generated" % var_name_middle,
             "<(icu_gen_dir)/%s.res")):
            _write_var_list(out, var, pattern, file_list)

def write_misc(out, files):
    for var, pattern in (
            ("icu_data_misc_res_sources", "source/data/misc/%s.txt"),
            ("icu_data_misc_res_generated", "<(icu_gen_dir)/%s.res")):
        _write_var_list(out, var, pattern, files)

def write_curr(out, files, alias_files):
    _write_var_list_pair(out, "curr_res_root", "curr", ["root"])
    _write_var_list_triplet(out, "curr_res_supplemental",
                            "curr", ["supplementalData"])
    _write_var_list_triplet(out, "curr_res", "curr", files)
    _write_var_list_triplet(out, "curr_res_alias", "curr", alias_files)

def write_lang(out, files, alias_files):
    _write_var_list_pair(out, "lang_res_root", "lang", ["root"])
    _write_var_list_triplet(out, "lang_res", "lang", files)
    _write_var_list_triplet(out, "lang_res_alias", "lang", alias_files)

def write_region(out, files, alias_files):
    _write_var_list_pair(out, "region_res_root", "region", ["root"])
    _write_var_list_pair(out, "region_res", "region", files)
    _write_var_list_pair(out, "region_res_alias", "region", alias_files)

def write_zone(out, files, alias_files):
    _write_var_list_pair(out, "zone_res_root", "zone", ["root"])
    _write_var_list_pair(out, "zone_res_extra",
                         "zone", ["tzdbNames"])
    _write_var_list_triplet(out, "zone_res", "zone", files)
    _write_var_list_triplet(out, "zone_res_alias", "zone", alias_files)

def write_unit(out, files, alias_files):
    _write_var_list_pair(out, "unit_res_root", "unit", ["root"])
    _write_var_list_pair(out, "unit_res", "unit", files)
    _write_var_list_pair(out, "unit_res_alias", "unit", alias_files)

def write_coll(out, files, alias_files):
    _write_var_list_pair(out, "coll_res_root", "coll", ["root"])
    _write_var_list_pair(out, "coll_res", "coll", files)
    _write_var_list_pair(out, "coll_res_alias", "coll", alias_files)

def _write_var_list_triplet(out, var_name_middle, res_dir, files):
    for var, pattern in (
            ("icu_data_%s_raw_sources" % var_name_middle,
             "source/data/%s/%%s.txt" % res_dir),
            ("icu_data_%s_filtered_sources" % var_name_middle,
             "<(icu_gen_tmp_dir)/%s/%%s.txt" % res_dir),
            ("icu_data_%s_generated" % var_name_middle,
             "<(icu_gen_dir)/%s/%%s.res" % res_dir)):
        _write_var_list(out, var, pattern, files)

def _write_var_list_pair(out, var_name_middle, res_dir, files):
    for var, pattern in (
            ("icu_data_%s_sources" % var_name_middle,
             "source/data/%s/%%s.txt" % res_dir),
            ("icu_data_%s_generated" % var_name_middle,
             "<(icu_gen_dir)/%s/%%s.res" % res_dir)):
        _write_var_list(out, var, pattern, files)

def write_end_block(out):
    out.write("""\
}
""")

if __name__ == '__main__':
    main()
