__author__ = 'raccoon'

from warc.parser import Parser
from indexing.preprocess import split_word
from indexing.word_count import WordCount

import multiprocessing
import time
import os
import sys
import random
import string

f = sys.argv[1]
p = Parser(f)
count = 0
p.fetch()


def processing(_content):
    t_wc = WordCount()
    split_data = split_word(_content)
    for line in split_data:
        if line not in [" ", "\n", "  ", ""]:
            word = line.split(' ')
            for w in word:
                if w not in [""]:
                    t_wc.push(w)
    return t_wc.get_dict()


def get_temp_dir_name():
    return ''.join(random.choice(string.ascii_letters) for x in range(20))


start_time = time.time()
print("Starting ... ")

tmp_dir_name = get_temp_dir_name()

os.mkdir(tmp_dir_name)

multiprocessing.freeze_support()
pool = multiprocessing.Pool()
result = []
result_count = 0
while True:
    data01 = p.fetch()
    count += 1
    # if count > 1000:
    # break

    if data01 is None:
        break
    result.append(pool.apply_async(processing, (data01.content, )))

    if count % 500 == 0:
        print("waiting for task finish.")
        pool.close()
        pool.join()
        print("write tmp file")
        for r in result:
            result_count += 1
            f = open(tmp_dir_name + '/' + str(result_count), "w")
            d = r.get()
            for k in d:
                f.write(k + " " + str(d[k]) + "\n")
            f.close()
        result = []
        pool = multiprocessing.Pool()

        # split_data = split_word(data01.content)
        # for line in split_data:
        # if line not in [" ", "\n", "  ", ""]:
        # word = line.split(' ')
        # for w in word:
        # if w not in [""]:
        # wc.push(w)

pool.close()
print("task insert finished.")
pool.join()
wc = WordCount()
for r in result:
    result_count += 1
    f = open(tmp_dir_name + '/' + str(result_count), "w")
    d = r.get()
    for k in d:
        f.write(k + " " + str(d[k]) + "\n")
    f.close()
    # d = r.get()
    # for k in d:
    # wc.push(k, d[k])
    # pass

print("Finishing ... file write ")

f = open("result.txt", "w")
d = wc.get_dict()

for k, v in ((k, d[k]) for k in sorted(d, key=d.get, reverse=True)):
    # print( k , v)
    f.write(k + " " + str(v) + "\n")

f.close()

print("finished.")
print((time.time() - start_time), "s")