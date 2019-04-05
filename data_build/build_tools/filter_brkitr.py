"""Replaces some dict references to allow us to drop cjdict.dict."""

from __future__ import print_function

import argparse
import shutil

def main():
    parser = argparse.ArgumentParser(
        description=('Creates modified versions of some ICU data files.'))

    parser.add_argument('--replace-cjdict-with-word_ja', action="store_true")
    parser.add_argument('--in-word-txt', required=True,
                        help='The word.txt to filter')
    parser.add_argument('--out-word-txt', required=True,
                        help='The word.txt to filter')
    parser.add_argument('--in-brkitr-root-txt', required=True,
                        help='The brkitr/root.txt to filter')
    parser.add_argument('--out-brkitr-root-txt', required=True,
                        help='The brkitr/root.txt to filter')
    parser.add_argument('--in-brkitr-ja-txt', required=True,
                        help='The brkitr/ja.txt to filter')
    parser.add_argument('--out-brkitr-ja-txt', required=True,
                        help='The brkitr/ja.txt to filter')

    args = parser.parse_args()

    if args.replace_cjdict_with_word_ja:
        fix_brkitr_root_txt(args.in_brkitr_root_txt, args.out_brkitr_root_txt)
        fix_brkitr_ja_txt(args.in_brkitr_ja_txt, args.out_brkitr_ja_txt)
        fix_word_txt(args.in_word_txt, args.out_word_txt)
    else:
        shutil.copyfile(args.in_brkitr_root_txt, args.out_brkitr_root_txt)
        shutil.copyfile(args.in_brkitr_ja_txt, args.out_brkitr_ja_txt)
        shutil.copyfile(args.in_word_txt, args.out_word_txt)

def fix_word_txt(source, dest):
    """Strip all references to dictionaryCJK and KanaKanji and
       HangulSymbal."""
    with open(source) as in_file:
        with open(dest, "w") as out:
            _process_word_txt(in_file, out)

# Lines with a replacement of None will be deleted
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
            found_line_to_fix = False
            for line in in_file:
                if "cjdict.dict" in line:
                    found_line_to_fix = True
                    continue
                out.write(line)
            assert found_line_to_fix

def fix_brkitr_ja_txt(source, dest):
    """Strip all references to line_ja.brk."""
    with open(source) as in_file:
        with open(dest, "w") as out:
            found_marker = False
            marker =  'line_strict:process(dependency){"line.brk"}'
            for line in in_file:
                if marker in line:
                    found_marker = True
                    out.write(line)
                    out.write(
                        '        word:process(dependency){"word_ja.brk"}\n'
                    )
                else:
                    out.write(line)
            assert found_marker

if __name__ == '__main__':
    main()
