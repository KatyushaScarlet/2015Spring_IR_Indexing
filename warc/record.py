__author__ = 'raccoon'


class WARCRecord:
    warc_version = ""
    warc_header = {}
    content_length = 0
    content = ""

    def __str__(self):
        return "WARC Version: " + self.warc_version + "\nWARC Header: " + str(
            self.warc_header) + "\nContent Length: " + str(self.content_length)