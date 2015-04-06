__author__ = 'raccoon'

import sys
import os
import time
import re
import multiprocessing
import random
import string
import gc

from warc.parser import Parser
from html.parser import HTMLParser
from indexing.partial_index import PartialIndex
from indexing.index import Index

CASE_FOLDING = False

class WarcHTMLParser(HTMLParser):
    lineCount = []
    index = PartialIndex()
    pre_offset = 0

    def __init__(self):
        HTMLParser.__init__(self)
        self.index = PartialIndex()
        self.lineCount = []

    def calc_lineno_offset_to_offset(self, lineno, offset):
        return self.lineCount[lineno - 1] + offset

    def feed(self, data):
        lines = data.split('\n')
        c = 1
        self.lineCount.append(0)
        for line in lines:
            self.lineCount.append(self.lineCount[c - 1] + len(line) + 1)
            c += 1
        HTMLParser.feed(self, data)

    def handle_data(self, data):
        if self.lasttag not in ['script', 'style']:
            offset = self.calc_lineno_offset_to_offset(self.getpos()[0], self.getpos()[1]) + self.pre_offset
            word = re.compile('[A-Za-z]+')
            words = word.finditer(data)
            for w in words:
                if CASE_FOLDING:
                    self.index.push(w.group(0).lower(), w.start() + offset)
                else:
                    self.index.push(w.group(0), w.start() + offset)


def processing(_content: str, offset: int) -> PartialIndex:
    ph = WarcHTMLParser()
    ph.pre_offset = offset
    ph.feed(_content)
    return ph.index


def processing_async(idx: int, _content: str):
    c = re.compile("Content-Length: (\d+)\n\n")
    html_start = c.search(_content)
    html = _content[html_start.span()[1]:]
    return idx, processing(html, html_start.span()[1])


def get_temp_dir_name():
    """
    random dir name in 20 letters
    :return: String
    """
    random.seed()
    return ''.join(random.choice(string.ascii_letters) for x in range(20))


def multi_version(_parser: Parser) -> int:
    multiprocessing.freeze_support()
    pool = multiprocessing.Pool()
    count = 0
    result = []

    start_time = time.time()
    tmp_dir_name = "tmp/" + get_temp_dir_name()
    print(tmp_dir_name)
    os.mkdir(tmp_dir_name)

    while True:
        d = _parser.fetch()
        count += 1
        if d is not None:
            result.append(pool.apply_async(processing_async, (count, d.content,)))

            if count % 1000 == 0:
                print("waiting...", int(count / 1000))
                pool.close()
                pool.join()
                for r in result:
                    cnt, idx = r.get()
                    idx.dump(tmp_dir_name + "/" + str(cnt))
                pool = multiprocessing.Pool()
                result = []
        else:
            pool.close()
            pool.join()
            for r in result:
                cnt, idx = r.get()
                idx.dump(tmp_dir_name + "/" + str(cnt))
            break
    print("----------------------------------------------------------")
    print("Analysis document:")
    end_time = time.time()
    print(end_time - start_time, "s")
    print("Average:", (end_time - start_time) * 1000 / count, "ms")
    print("Document process per second:", count / (end_time - start_time), "ps")
    print("----------------------------------------------------------")
    print("build full index ......")
    start_time = time.time()
    idx = Index()
    for i in range(1, count):
        if count % 500 == 0:
            gc.collect()
        idx.read_partial_index(i, PartialIndex.read(tmp_dir_name + "/" + str(i)))
        os.remove(tmp_dir_name + "/" + str(i))
    os.rmdir(tmp_dir_name)
    print("----------------------------------------------------------")
    print("Build full index:")
    end_time = time.time()
    print(end_time - start_time, "s")
    print("Average:", (end_time - start_time) * 1000 / count, "ms")
    print("DPS:", count / (end_time - start_time), "ps")
    print("----------------------------------------------------------")
    return count, idx


def single_version(_parser: Parser):
    count = 0
    start_tiem = time.time()
    try:
        # _parser.goto(1)

        tmp_dir_name = "tmp/" + get_temp_dir_name()
        print("create tmp index directory:", tmp_dir_name)
        os.mkdir(tmp_dir_name)
        # make index
        while True:
            count += 1
            d = _parser.fetch()
            if d is not None:
                c = re.compile("Content-Length: (\d+)\n\n")
                html_start = c.search(d.content)
                # result = processing(d.content[html_start.span()[1]+1:])
                html = d.content[html_start.span()[1]:]
                result = processing(html, html_start.span()[1])
                result.dump(tmp_dir_name + "/" + str(count))

                if count == 1:
                    pass
                if count % 1000 == 0:
                    print("waiting...", int(count / 1000))
            else:
                break
        print("----------------------------------------------------------")
        print("Analysis document:")
        end_time = time.time()
        print(end_time - start_tiem, "s")
        print("Average:", (end_time - start_tiem) * 1000 / count, "ms")
        print("DPS:", count / (end_time - start_tiem), "ps")
        print("----------------------------------------------------------")
        print("build full index ......")
        start_tiem = time.time()
        idx = Index()
        for i in range(1, count):
            if count % 500 == 0:
                gc.collect()
            idx.read_partial_index(i, PartialIndex.read(tmp_dir_name + "/" + str(i)))
            os.remove(tmp_dir_name + "/" + str(i))
        os.rmdir(tmp_dir_name)
        print("----------------------------------------------------------")
        print("Build full index:")
        end_time = time.time()
        print(end_time - start_tiem, "s")
        print("Average:", (end_time - start_tiem) * 1000 / count, "ms")
        print("DPS:", count / (end_time - start_tiem), "ps")
        print("----------------------------------------------------------")
    except KeyboardInterrupt:
        print("Closing worker...")
        return count
    return count, idx


def main():
    f = sys.argv[1]

    multi_flag = False
    gzip_flag = False
    if "-cf" in sys.argv:
        CASE_FOLDING = True
    if "-gz" in sys.argv:
        gzip_flag = True
    if "-m" in sys.argv:
        multi_flag = True

    p = Parser(f)
    # skip header record
    p.fetch()

    starttime = time.time()

    print("Start......")
    if multi_flag:
        count, index = multi_version(p)
    else:
        count, index = single_version(p)

    print("dump index from memory to file " + f + ".index.txt")
    dump_start_time = time.time()
    if gzip_flag:
        index.dump_gzip(f + "_index")
    else:
        index.dump(f + "_index")
    dump_end_time = time.time()
    print("----------------------------------------------------------")
    print("dump index:")
    print(dump_end_time - dump_start_time, "s")
    print("----------------------------------------------------------")
    print("finish")
    print("----------------------------------------------------------")
    print("Total time analysis:")
    print(time.time() - starttime, "s")
    print("Average", (time.time() - starttime) * 1000 / count, "ms")
    print("DPS", count / (time.time() - starttime), "ps")


if __name__ == "__main__":
    main()