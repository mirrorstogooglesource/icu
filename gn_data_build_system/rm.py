#!/usr/bin/env python
# Copyright 2018 the Chromium authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

"""This program deletes its arguments"""

import os
import sys

for file_name in sys.argv[1:]:
    if os.path.exists(file_name):
        os.remove(file_name)
#        assert not os.path.exists(file_name)
    with open(file_name + ".deleted", "w"):
        pass # Just a stamp file
