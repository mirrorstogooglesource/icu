#!/usr/bin/env python
# Copyright 2018 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""Check that filter_data_for_size seems to work."""

from __future__ import print_function

import cStringIO
import unittest

import parse_res_source

class ParserTest(unittest.TestCase):

  def testIntvector(self):
    # Example data from curr/supplementalData.txt:
    ex1 = \
"""        SR{
            {
                from:intvector{
                    249,
                    -826624000,
                }
                id{"SRD"}
            }
"""
    parser = parse_res_source.Parser(ex1)
    parser.parse()
    sr = parser.get_tree().main_node()
    block = sr.get_block_children()[0].get_block_children()[0]
    self.assertEqual(block.name, "from")
    self.assertEqual(block.block_type, "intvector")

  def testNofallback(self):
    #Example data from misc/supplementalData.txt
    ex2 = \
"""supplementalData:table(nofallback){
    calendarData{
        buddhist{
            eras{
                0{
                    start:intvector{
                        -542,
                        1,
                        1,
                    }
                }
            }
            system{"solar"}
        }
        chinese{
"""
    parser = parse_res_source.Parser(ex2)
    parser.parse()
    block = parser.get_tree().main_node()
    self.assertEqual(block.name, "supplementalData")
    self.assertEqual(block.block_type, "table(nofallback)")

  def testBOM(self):
    ex3 = \
          """\xef\xbb\xbf// \xc2\xa9 2016 and later: """
    parser = parse_res_source.Parser(ex3)
    parser.parse()
    block = parser.get_tree().main_node()
    self.assertEqual(block, None)

  def testEmpty(self):
    ex5 = \
          """{}"""
    parser = parse_res_source.Parser(ex5)
    parser.parse()
    block = parser.get_tree().main_node()
    self.assertEqual(block.name, '<anon>')
    self.assertEqual(block.children, [])

    ex6 = \
          """{{}}"""
    parser = parse_res_source.Parser(ex6)
    parser.parse()
    block = parser.get_tree().main_node()
    self.assertEqual(block.name, '<anon>')
    self.assertEqual(block.block_type, 'block')
    block = block.children[0]
    self.assertEqual(block.name, '<anon>')
    self.assertEqual(block.block_type, 'block')
    self.assertEqual(block.children, [])

    ex7 = \
          """{ { } }"""
    parser = parse_res_source.Parser(ex7)
    parser.parse()
    block = parser.get_tree().main_node()
    self.assertEqual(block.name, '<anon>')
    self.assertEqual(block.block_type, 'block')
    block = block.children[1]
    self.assertEqual(block.name, '<anon>')
    self.assertEqual(block.block_type, 'block')
    self.assertEqual(len(block.children), 1)  # Whitespace Text node

  def testNameWithColon(self):
    ex8 = \
          """\"name:foo\"{}"""
    parser = parse_res_source.Parser(ex8)
    parser.parse()
    self.assertEqual(parser.get_tree().children[0].name, '"name:foo"')
    self.assertEqual(parser.get_tree().children[0].block_type, 'block')

    ex9 = \
      """name:foo{}"""
    parser = parse_res_source.Parser(ex9)
    parser.parse()
    self.assertEqual(parser.get_tree().children[0].name, 'name')
    self.assertEqual(parser.get_tree().children[0].block_type, 'foo')

    # Not supported (or used?)
    # ex10 = \
    #        """\"name:foo\":bar{}"""

if __name__ == '__main__':
  unittest.main()
