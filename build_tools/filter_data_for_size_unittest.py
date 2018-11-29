#!/usr/bin/env python
# Copyright 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Check that filter_data_for_size seems to work."""

import cStringIO
import unittest

import filter_data_for_size


class FilterTest(unittest.TestCase):

  def testFixWordTxt(self):
    test_input = cStringIO.StringIO("$ALetter-$dictionaryCJK")
    test_output = cStringIO.StringIO()
    filter_data_for_size._process_word_txt(test_input, test_output)
    self.assertEqual(test_output.getvalue(), "$ALetter")

  def testPrintBlock(self):
    test_data = """\
foo{aaa}
"""
    test_input = cStringIO.StringIO(test_data)
    test_output = cStringIO.StringIO()
    line = test_input.next()
    filter_data_for_size._print_block(line, test_input, test_output)
    self.assertEqual(test_output.getvalue(), test_data)

if __name__ == '__main__':
  unittest.main()
