#!/bin/bash
# Copyright (c) 2019 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -e

# This assumes that exemplar city ("ec") is only present in
# non-meta zones and that meta zones are listed after non-meta
# zones.
function remove_exemplar_cities {
  for i in ${dataroot}/zone/*.txt
  do
    [ $i != "${dataroot}/zone/root.txt" ] && \
    sed -i '/^    zoneStrings/, /^        "meta:/ {
      /^    zoneStrings/ p
      /^        "meta:/ p
      d
    }' $i
  done
}

treeroot="$(dirname "$0")/.."
dataroot="${treeroot}/source/data"
scriptdir="${treeroot}/scripts"
localedatapath="${dataroot}/locales"
langdatapath="${dataroot}/lang"

# Chromium OS needs exemplar cities for timezones, but not Chromium.
# It'll save 400kB (uncompressed), but the size difference in
# 7z compressed installer is <= 100kB.
remove_exemplar_cities
