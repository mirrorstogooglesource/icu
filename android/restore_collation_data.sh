#!/bin/sh
# Copyright (c) 2017 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

treeroot="$(dirname "$0")/.."
cd "${treeroot}"

echo "Restoring collation tables from ICU data file configuration"

git checkout HEAD -- source/data/coll/collocal.mk
