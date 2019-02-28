#!/bin/bash
# Copyright (c) 2014 The Chromium Authors. All rights reserved.
# Use of this source code is governed by a BSD-style license that can be
# found in the LICENSE file.

set -e

# Keep only duration and compound in units* sections.
function filter_unit_data {
  for i in ${dataroot}/unit/*.txt
  do
    echo Overwriting $i ...
    sed -r -i \
      '/^    units(|Narrow|Short)\{$/, /^    \}$/ {
         /^    units(|Narrow|Short)\{$/ p
         /^        (duration|compound)\{$/, /^        \}$/ p
         /^    \}$/ p
         d
       }' ${i}

    # Delete empty units,units{Narrow|Short} block. Otherwise, locale fallback
    # fails. See crbug.com/707515.
    sed -r -i \
      '/^    units(|Narrow|Short)\{$/ {
         N
         /^    units(|Narrow|Short)\{\n    \}/ d
      }' ${i}
  done
}

treeroot="$(dirname "$0")/.."
dataroot="${treeroot}/source/data"

filter_unit_data
