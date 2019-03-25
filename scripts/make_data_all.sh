#!/bin/bash

set -x

ICUROOT="$(dirname "$0")/.."

echo "Build the necessary tools"
"${ICUROOT}/source/runConfigureICU" --enable-debug --disable-release Linux/gcc --disable-tests
make clean
make -j 120

echo "Build the filtered data for common"
(cd data && make clean)
$ICUROOT/scripts/config_data.sh common
make -j 120
$ICUROOT/scripts/copy_data.sh common

echo "Build the filtered data for chromeos"
# For now just copy the build result from common
$ICUROOT/scripts/copy_data.sh chromeos

echo "Build the filtered data for cast"
(cd data && make clean)
#$ICUROOT/cast/patch_locale.sh
$ICUROOT/scripts/config_data.sh cast
make -j 120
$ICUROOT/scripts/copy_data.sh cast

echo "Build the filtered data for Android"
#$ICUROOT/android/patch_locale.sh
#$ICUROOT/scripts/make_data.sh
$ICUROOT/scripts/copy_data.sh android

echo "Build the filtered data for iOS"
#$ICUROOT/ios/patch_locale.sh
#$ICUROOT/scripts/make_data.sh
$ICUROOT/scripts/copy_data.sh ios

echo "Build the filtered data for flutter"
#$ICUROOT/flutter/patch_brkitr.sh
#$ICUROOT/scripts/make_data.sh
$ICUROOT/scripts/copy_data.sh flutter

echo "Clean up the git"
$ICUROOT/scripts/clean_up_data_source.sh
