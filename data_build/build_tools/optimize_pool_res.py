"""Generates a pool.res file for use by genrb when generating
optimal .res files"""

from __future__ import print_function

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

def main():
    parser = argparse.ArgumentParser(
        description=('Generates a pool.res file for use by genrb when ' +
                     'generating optimal .res file.'))

    parser.add_argument('--genrb-binary', required=True)
    parser.add_argument('--genrb-source-dir', required=True)
    parser.add_argument('--genrb-include-dir', required=True)
    parser.add_argument('--pool-destination', required=True,
                        help='name and location of generated pool.res')
    parser.add_argument('source_files', nargs='+')

    args = parser.parse_args()

    # Files can't be given with their path or pool.res will be larger
    # than necessary so just check that they are all given without
    # path or is in the source directory and strip the path.
    assert all([(x.startswith(args.genrb_source_dir) or
                 os.path.basename(x) == x)
                for x in args.source_files])
    temp_dir = tempfile.mkdtemp("_icudata")
    pool_res_file = os.path.join(temp_dir, "pool.res")
    current_cmd = None
    try:
        cmd = [
            args.genrb_binary,
            "--quiet",
            "--writePoolBundle",
            "-k",
            "-R",
            "-i",
            args.genrb_include_dir,
            "-s",
            args.genrb_source_dir,
            "-d",
            temp_dir,
        ] + [os.path.basename(x) for x in args.source_files]
        current_cmd = " ".join(cmd)
        subprocess.check_call(cmd, stdout=sys.stdout, stderr=sys.stderr)
        assert os.path.isfile(pool_res_file)
        current_cmd = None

        if not os.path.isdir(os.path.dirname(args.pool_destination)):
            os.makedirs(os.path.dirname(args.pool_destination))
        shutil.copy2(pool_res_file, args.pool_destination)
    finally:
        if current_cmd is not None:
            print("FAILED: " + current_cmd)
        shutil.rmtree(temp_dir)

if __name__ == '__main__':
    main()

