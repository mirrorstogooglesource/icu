#!/bin/bash

# set -x

ICUROOT="$(dirname "$0")/.."

if [ $# -lt 4 ];
then
  echo "Usage: "$0" (android|cast|chromeos|common|flutter|ios) icubuilddir1 icubuilddir2 res_file" >&2
  exit 1
fi

# Input Parameters
BUILD=$1
DIR1=$2
DIR2=$3
RES=$4

echo "======================================================="
echo "                ${BUILD} ${RES} DIFFERENCES"
echo "======================================================="
RESSUBDIR1=`ls ${DIR1}/dataout/${BUILD}/data/out/build`
RESDIR1="${DIR1}/dataout/${BUILD}/data/out/build/${RESSUBDIR1}"
RESSUBDIR2=`ls ${DIR2}/dataout/${BUILD}/data/out/build`
RESDIR2="${DIR2}/dataout/${BUILD}/data/out/build/${RESSUBDIR2}"

RESFILE1=dataout/${BUILD}/data/out/build/${RESSUBDIR1}/${RES}
RESFILE2=dataout/${BUILD}/data/out/build/${RESSUBDIR2}/${RES}
TXT1=/tmp/${BUILD}_RES_1.txt
TXT2=/tmp/${BUILD}_RES_2.txt
LD_LIBRARY_PATH=${DIR1}/lib ${DIR1}/bin/derb ${RESFILE1} -s ${DIR1}/ -c > ${TXT1}
LD_LIBRARY_PATH=${DIR2}/lib ${DIR2}/bin/derb ${RESFILE2} -s ${DIR2}/ -c > ${TXT2}

diff -u ${TXT1} ${TXT2}
