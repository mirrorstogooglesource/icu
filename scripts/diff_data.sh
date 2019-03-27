#!/bin/bash

#set -x

ICUROOT="$(dirname "$0")/.."

if [ $# -lt 2 ];
then
  echo "Usage: "$0" icubuilddir1 icubuilddir2" >&2
  exit 1
fi

for subdir in "chromeos" "common" "cast" "android" "ios" "flutter"
do
  echo "#######################################################"
  echo "       COMPARING $subdir"
  echo "#######################################################"
  RESSUBDIR1=`ls $1/dataout/${subdir}/data/out/build`
  RESDIR1="$1/dataout/${subdir}/data/out/build/${RESSUBDIR1}"
  ICUDATA_LST1="$1/dataout/${subdir}/data/out/tmp/icudata.lst"
  RESSUBDIR2=`ls $2/dataout/${subdir}/data/out/build`
  RESDIR2="$2/dataout/${subdir}/data/out/build/${RESSUBDIR2}"
  ICUDATA_LST2="$2/dataout/${subdir}/data/out/tmp/icudata.lst"
  # echo ${RESDIR1}
  # echo ${RESDIR2}
  SORTED_ICUDATA_LST1=/tmp/${subdir}1_icudata_lst
  SORTED_ICUDATA_LST2=/tmp/${subdir}2_icudata_lst
  sort ${ICUDATA_LST1} >${SORTED_ICUDATA_LST1}
  sort ${ICUDATA_LST2} >${SORTED_ICUDATA_LST2}
  diff -u ${SORTED_ICUDATA_LST1} ${SORTED_ICUDATA_LST2}

done
