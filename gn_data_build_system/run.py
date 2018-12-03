#!/usr/bin/env python
# Copyright 2014 the V8 project authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This program wraps an arbitrary command since gn currently can only execute
scripts."""

import os
import subprocess
import sys

try:
    res = subprocess.call(sys.argv[1:], stdout=sys.stdout, stderr=sys.stderr)
except Exception as e:
    res = 1
    print("%s" % e)

if res != 0:
    print("In %s" % os.getcwd())
    print("%s" % sys.argv)

sys.exit(res)
