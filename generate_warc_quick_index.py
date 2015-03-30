__author__ = 'raccoon'

import sys
import os
import gzip
from warc.parser import Parser

if __name__ == "__main__":
    file = sys.argv[1]
    idx_file = file + ".idx"
    if os.path.isfile(idx_file):
        print("idx file for", file, " is exist.")
        quit()

    with gzip.open(idx_file, "wb") as f:
        p = Parser(file)

        while True:
            r = p.fetch()
            if not r:
                break
            c = r.warc_header["WARC-Record-ID"] + " " + str(r.offset_seek) + "\n"
            f.write(bytes(c, p.encoding))