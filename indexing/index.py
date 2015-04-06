__author__ = 'raccoon'

import gzip
from .partial_index import PartialIndex


class Index:
    index = {}

    def read_partial_index(self, doc_id: int, pi: PartialIndex):
        for i in pi.index:
            if i not in self.index:
                self.index[i] = {}
            self.index[i][doc_id] = pi.index[i]

    def dump(self, filename: str):
        f = open(filename + ".idx", "w")
        fdic = open(filename + ".dict", "w")
        for k, v in ((k, self.index[k]) for k in sorted(self.index)):
            fdic.write(k + "\n")
            f.write(k + ", " + str(len(v)) + ":<")
            for doc in v:
                f.write(str(doc) + ", " + str(len(v[doc])) + ":<")
                fr = True
                for pos in v[doc]:
                    if fr:
                        f.write(str(pos))
                        fr = False
                    else:
                        f.write(", " + str(pos))
                f.write(">;")
            f.write(">;\n")
        f.close()
        fdic.close()

    def dump_gzip(self, filename: str):
        f = gzip.open(filename + ".idx.gz", "w")
        fdic = gzip.open(filename + ".dict.gz", "w")
        for k, v in ((k, self.index[k]) for k in sorted(self.index)):
            fdic.write(bytes(k + "\n", "utf8"))
            f.write(bytes(k + ", " + str(len(v)) + ":<", "utf8"))
            for doc in v:
                f.write(bytes(str(doc) + ", " + str(len(v[doc])) + ":<", "utf8"))
                fr = True
                for pos in v[doc]:
                    if fr:
                        f.write(bytes(str(pos), "utf8"))
                        fr = False
                    else:
                        f.write(bytes(", " + str(pos), "utf8"))
                f.write(bytes(">;", "utf8"))
            f.write(bytes(">;\n", "utf8"))
        f.close()
        fdic.close()