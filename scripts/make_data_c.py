#!/usr/bin/python2

# Copyright 2016 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

import binascii
import optparse
import sys

parser = optparse.OptionParser()
parser.set_usage("""make_data_c  icu_data [target_c_file]
    icu_data: ICU data file to generate assembly from.
    target_c_file: Output file converted from icu_data file.""")
(options, args) = parser.parse_args()

if len(args) < 1:
  parser.error("ICU data file is not given.")

input_file = args[0]
n = input_file.find(".dat")
if n == -1:
  sys.exit("%s is not an ICU .dat file." % input_file)

if len(args) < 2:
  output_file = input_file[0:n] + "_dat.S"
else:
  output_file = args[1]

if input_file.find("l.dat") == -1:
  if input_file.find("b.dat") == -1:
    sys.exit("%s has no endianness marker." % input_file)
  else:
    step = 1
else:
  step = -1

input_data = open(input_file, 'rb').read()
n = input_data.find("icudt")
if n == -1:
  sys.exit("Cannot find a version number in %s." % input_file)

version_number = input_data[n + 5:n + 7]

output = open(output_file, 'w')

split = [binascii.hexlify(input_data[i:i + 4][::step]).upper().lstrip('0')
        for i in range(0, len(input_data), 4)]

output.write('#include <stdint.h>\n'
             'extern "C" {\n'
             'uint32_t icudt67_dat[' + str(len(split)) + '] {\n')

for i in range(len(split)):
  if (len(split[i]) == 0):
    value = '0'
  elif (len(split[i]) == 1):
    if not any((c in '123456789') for c in split[i]):
      value = '0x0' + split[i]
    else:
      value = split[i]
  elif (len(split[i]) % 2 == 1):
    value = '0x0' + split[i]
  else:
    value = '0x' + split[i]

  if i % 32 == 0:
    if i != 0:
      output.write(",\n  ")
  else:
    output.write(",")
  output.write(value)

output.write("\n};\n}\n")
output.close()
print "Generated " + output_file
