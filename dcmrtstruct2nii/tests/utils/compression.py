import shutil
import gzip

from pathlib import Path


def decompress_gzip(infile, outfile):
    infile = Path(infile)
    outfile = Path(outfile)

    with gzip.open(infile, 'rb') as f_in:
        with open(outfile, 'wb') as f_out:
            shutil.copyfileobj(f_in, f_out)
