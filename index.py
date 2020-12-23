__author__ = 'raccoon'

import sys
import os
import time
import re
import multiprocessing
import random
import string
import gc

import ctypes
from stemming.porter2 import stem

from warc.parser import Parser
from html.parser import HTMLParser
from indexing.partial_index import PartialIndex
from indexing.index import Index

import shutil


class WarcHTMLParser(HTMLParser):
    lineCount = []
    index = PartialIndex()
    pre_offset = 0
    case_folding = False
    stopword_remove = False
    stemming = False
    position = 0
    stopwords = ['a', 'about', 'above', 'across', 'after', 'again', 'against', 'all', 'almost', 'alone', 'along',
                 'already',
                 'also', 'although', 'always', 'among', 'an', 'and', 'another', 'any', 'anybody', 'anyone', 'anything',
                 'anywhere', 'are', 'area', 'areas', 'around', 'as', 'ask', 'asked', 'asking', 'asks', 'at', 'away',
                 'b',
                 'back', 'backed', 'backing', 'backs', 'be', 'became', 'because', 'become', 'becomes', 'been', 'before',
                 'began', 'behind', 'being', 'beings', 'best', 'better', 'between', 'big', 'both', 'but', 'by', 'c',
                 'came',
                 'can', 'cannot', 'case', 'cases', 'certain', 'certainly', 'clear', 'clearly', 'come', 'could', 'd',
                 'did',
                 'differ', 'different', 'differently', 'do', 'does', 'done', 'down', 'down', 'downed', 'downing',
                 'downs',
                 'during', 'e', 'each', 'early', 'either', 'end', 'ended', 'ending', 'ends', 'enough', 'even', 'evenly',
                 'ever', 'every', 'everybody', 'everyone', 'everything', 'everywhere', 'f', 'face', 'faces', 'fact',
                 'facts',
                 'far', 'felt', 'few', 'find', 'finds', 'first', 'for', 'four', 'from', 'full', 'fully', 'further',
                 'furthered', 'furthering', 'furthers', 'g', 'gave', 'general', 'generally', 'get', 'gets', 'give',
                 'given',
                 'gives', 'go', 'going', 'good', 'goods', 'got', 'great', 'greater', 'greatest', 'group', 'grouped',
                 'grouping', 'groups', 'h', 'had', 'has', 'have', 'having', 'he', 'her', 'here', 'herself', 'high',
                 'high',
                 'high', 'higher', 'highest', 'him', 'himself', 'his', 'how', 'however', 'i', 'if', 'important', 'in',
                 'interest', 'interested', 'interesting', 'interests', 'into', 'is', 'it', 'its', 'itself', 'j', 'just',
                 'k',
                 'keep', 'keeps', 'kind', 'knew', 'know', 'known', 'knows', 'l', 'large', 'largely', 'last', 'later',
                 'latest', 'least', 'less', 'let', 'lets', 'like', 'likely', 'long', 'longer', 'longest', 'm', 'made',
                 'make', 'making', 'man', 'many', 'may', 'me', 'member', 'members', 'men', 'might', 'more', 'most',
                 'mostly',
                 'mr', 'mrs', 'much', 'must', 'my', 'myself', 'n', 'necessary', 'need', 'needed', 'needing', 'needs',
                 'never', 'new', 'new', 'newer', 'newest', 'next', 'no', 'nobody', 'non', 'noone', 'not', 'nothing',
                 'now',
                 'nowhere', 'number', 'numbers', 'o', 'of', 'off', 'often', 'old', 'older', 'oldest', 'on', 'once',
                 'one',
                 'only', 'open', 'opened', 'opening', 'opens', 'or', 'order', 'ordered', 'ordering', 'orders', 'other',
                 'others', 'our', 'out', 'over', 'p', 'part', 'parted', 'parting', 'parts', 'per', 'perhaps', 'place',
                 'places', 'point', 'pointed', 'pointing', 'points', 'possible', 'present', 'presented', 'presenting',
                 'presents', 'problem', 'problems', 'put', 'puts', 'q', 'quite', 'r', 'rather', 'really', 'right',
                 'right',
                 'room', 'rooms', 's', 'said', 'same', 'saw', 'say', 'says', 'second', 'seconds', 'see', 'seem',
                 'seemed',
                 'seeming', 'seems', 'sees', 'several', 'shall', 'she', 'should', 'show', 'showed', 'showing', 'shows',
                 'side', 'sides', 'since', 'small', 'smaller', 'smallest', 'so', 'some', 'somebody', 'someone',
                 'something',
                 'somewhere', 'state', 'states', 'still', 'still', 'such', 'sure', 't', 'take', 'taken', 'than', 'that',
                 'the', 'their', 'them', 'then', 'there', 'therefore', 'these', 'they', 'thing', 'things', 'think',
                 'thinks',
                 'this', 'those', 'though', 'thought', 'thoughts', 'three', 'through', 'thus', 'to', 'today',
                 'together',
                 'too', 'took', 'toward', 'turn', 'turned', 'turning', 'turns', 'two', 'u', 'under', 'until', 'up',
                 'upon',
                 'us', 'use', 'used', 'uses', 'v', 'very', 'w', 'want', 'wanted', 'wanting', 'wants', 'was', 'way',
                 'ways',
                 'we', 'well', 'wells', 'went', 'were', 'what', 'when', 'where', 'whether', 'which', 'while', 'who',
                 'whole',
                 'whose', 'why', 'will', 'with', 'within', 'without', 'work', 'worked', 'working', 'works', 'would',
                 'x',
                 'y', 'year', 'years', 'yet', 'you', 'young', 'younger', 'youngest', 'your', 'yours', 'z']

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
                if WarcHTMLParser.stopword_remove:
                    if w.group(0).lower() in self.stopwords:
                        continue
                if WarcHTMLParser.case_folding:
                    if WarcHTMLParser.stemming:
                        # self.index.push(stem(w.group(0).lower()), w.start() + offset)
                        self.index.push(stem(w.group(0).lower()), self.position)
                    else:
                        # self.index.push(w.group(0).lower(), w.start() + offset)
                        self.index.push(w.group(0).lower(), self.position)
                else:
                    if WarcHTMLParser.stemming:
                        self.index.push(stem(w.group(0)), w.start() + offset)
                        self.index.push(stem(w.group(0)), self.position)
                    else:
                        # self.index.push(w.group(0), w.start() + offset)
                        self.index.push(w.group(0), self.position)
                self.position += 1


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

    tmp_dir_path = "tmp/"
    check_dir(tmp_dir_path)
    html_dir_path = "html/"
    check_dir(html_dir_path)

    start_time = time.time()
    tmp_dir_name = tmp_dir_path + get_temp_dir_name()
    print(tmp_dir_name)
    os.mkdir(tmp_dir_name)

    # titles
    title_names = ""

    while True:
        d = _parser.fetch()
        #print (d.content)
        count += 1
        
        if d is not None:
            result.append(pool.apply_async(processing_async, (count, d.content,)))
            with open(html_dir_path+str(count) + ".html","w",encoding="utf-8",errors="ignore") as out:
                out.write(d.content)

            # get title

            title_name = ""
            title_tag = re.compile(r'<(title|TITLE)[^>]*>(.*?)</(title|TITLE)>')
            title_result = title_tag.search((d.content))

            if title_result:
                title_name = title_result.group().replace('<title>', '').replace('</title>', '').replace('\n', '').replace('\r', '').replace('<TITLE>', '').replace('</TITLE>', '').strip()
                
                if title_name == "":
                    title_name = "Untitle"
            else:
                title_name = "Untitle"

            title_names += title_name + "\n"

            print("Now processing: %d" % count)
            if count % 1000 == 0:
                # print("waiting...", int(count / 1000))
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
                #print(idx)
                #print(getattr(idx,'index'))
                #get_value=ctypes.cast(idx, ctypes.py_object).value #读取地址中的变量
                #print(get_value)
                idx.dump(tmp_dir_name + "/" + str(cnt))
                
                
            break

    title_file = open("html/titles.txt","w",encoding="utf-8",errors="ignore")
    title_file.write(title_names)

    print("----------------------------------------------------------")
    print("Analysis document:")
    end_time = time.time()
    print(end_time - start_time, "s")
    print("Average:", (end_time - start_time) * 1000 / count, "ms")
    print("DPS:", count / (end_time - start_time), "ps")
    print("----------------------------------------------------------")
    print("Building full index ......")
    start_time = time.time()
    idx = Index()
    for i in range(1, count):
        if count % 500 == 0:
            gc.collect()
        idx.read_partial_index(i, PartialIndex.read(tmp_dir_name + "/" + str(i)))
        os.remove(tmp_dir_name + "/" + str(i))
    try:
        os.rmdir(tmp_dir_name)
    except Exception:
        pass
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

    tmp_dir_path = "tmp/"
    check_dir(tmp_dir_path)

    start_tiem = time.time()
    try:
        # _parser.goto(1)

        tmp_dir_name = tmp_dir_path + get_temp_dir_name()
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
        try:
            os.rmdir(tmp_dir_name)
        except Exception:
            pass
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

    multi_flag = True
    gzip_flag = False

    if "-st" in sys.argv:
        WarcHTMLParser.stemming = True
    if "-sw" in sys.argv:
        WarcHTMLParser.stopword_remove = True
    if "-cf" in sys.argv:
        WarcHTMLParser.case_folding = True
    if "-gz" in sys.argv:
        gzip_flag = True
    # if "-m" in sys.argv:
    #     multi_flag = True

    p = Parser(f)
    # skip header record
    p.fetch()

    starttime = time.time()

    print("Start building index")
    if multi_flag:
        count, index = multi_version(p)
    else:
        count, index = single_version(p)

    print("Dump index from memory to " + f + ".index.txt")
    dump_start_time = time.time()
    if gzip_flag:
        index.dump_gzip(f + "_index")
    else:
        index.dump(f + "_index")
    dump_end_time = time.time()
    print("----------------------------------------------------------")
    print("Dump index:")
    print(dump_end_time - dump_start_time, "s")
    print("----------------------------------------------------------")
    print("Finish")
    print("----------------------------------------------------------")
    print("Total time:")
    print(time.time() - starttime, "s")
    print("Average", (time.time() - starttime) * 1000 / count, "ms")
    print("DPS", count / (time.time() - starttime), "ps")

def check_dir(dir_path):
    if os.path.exists(dir_path):
        print("Remove last result (%s)" % dir_path)
        shutil.rmtree(dir_path,ignore_errors=True)

    os.makedirs(dir_path)

if __name__ == "__main__":
    main()