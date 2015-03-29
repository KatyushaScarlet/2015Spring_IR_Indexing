__author__ = 'raccoon'

import os
from .record import WARCRecord


def get_file_size(_fn):
    return os.stat(_fn).st_size


class Parser:
    encoding = "ISO-8859-1"

    def __init__(self, file):
        self.warc_file = file
        self.warc_file_size = get_file_size(self.warc_file)
        self.f = open(self.warc_file, "rb")

    def fetch(self):
        while True:
            if self.f.tell() == self.warc_file_size:
                return None
            line = self.f.readline().decode(self.encoding)
            if line[0] == 'W':
                break
        warc_record = WARCRecord()
        warc_record.warc_version = line[:-1]
        while True:
            line = self.f.readline().decode(self.encoding)[:-1].split(":", 1)

            if line[0] == 'Content-Length':
                warc_record.content_length = int(line[1].strip())
                content = self.f.read(warc_record.content_length).decode(self.encoding)
                warc_record.content = content
                break
            else:
                warc_record.warc_header[line[0].strip()] = line[1].strip()
        return warc_record