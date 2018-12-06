"""Writes the icupkg.inc file pkgdata needs to build an object file."""

from __future__ import print_function

import argparse
import os
import sys


def main():
    parser = argparse.ArgumentParser(
        description=('Generates an icupkg.inc file to be used by pkgdata.'))

    parser.add_argument('--outfile',
                        required=True,
                        help='File that will contain an ICU formatted list.')

    parser.add_argument('--ver',
                        required=True,
                        help='The ICU version.')

    parser.add_argument('--icu-dir',
                        required=True,
                        help='The directory where icu can be found.')

    args = parser.parse_args()

    with open(args.outfile, "w") as out:
        out.write("""\
GENCCODE_ASSEMBLY_TYPE=-a gcc
SO=so
SOBJ=so
A=a
LIBPREFIX=lib
LIB_EXT_ORDER=.%(ver)s.1
COMPILE=gcc -D_REENTRANT  -DU_HAVE_ELF_H=1 -DU_HAVE_ATOMIC=1  -DU_ATTRIBUTE_DEPRECATED= -O3  -std=c99 -Wall -pedantic -Wshadow -Wpointer-arith -Wmissing-prototypes -Wwrite-strings   -c
LIBFLAGS=-I%(icu_dir)s/source/common -DPIC -fPIC
GENLIB=gcc -O3  -std=c99 -Wall -pedantic -Wshadow -Wpointer-arith -Wmissing-prototypes -Wwrite-strings    -shared -Wl,-Bsymbolic
LDICUDTFLAGS=-nodefaultlibs -nostdlib
LD_SONAME=-Wl,-soname -Wl,
RPATH_FLAGS=
BIR_LDFLAGS=-Wl,-Bsymbolic
AR=ar
ARFLAGS=r
RANLIB=ranlib
INSTALL_CMD=/usr/bin/install -c
""" % {
    'ver': args.ver,
    'icu_dir': args.icu_dir,
      })

if __name__ == '__main__':
    main()
