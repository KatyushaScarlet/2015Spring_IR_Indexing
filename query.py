__author__ = 'raccoon'

import sys
import string
import math
from warc.parser import Parser

from indexing.index import Index

# file_name = "ClueWeb09_English_Sample.warc"
file_name = "00.warc"


def query():
    idx_file = file_name + "_index.idx"
    dict_file = file_name + "_index.dict"
    N = 0
    parser = Parser(file_name)
    return_count = 10
    while True:
        if parser.fetch() is not None:
            N += 1
        else:
            break

    dict_file = open(dict_file)
    dict = {}
    for d in dict_file:
        (key, offset) = d.split(', ')
        dict[key] = int(offset)

    # index = Index.read(idx_file)
    # for term in index.index:
    # print(term)
    if len(sys.argv) >= 3:
        if "-r" in sys.argv:
            return_count = int(sys.argv[sys.argv.index("-r") + 1])

        if "-q" in sys.argv:
            query_string = sys.argv[sys.argv.index("-q") + 1:]
        term_index = {}
        query_table = {}
        docs_table = {}
        docs_set = set()
        docs_score = {}
        for term in query_string:
            if term in dict:
                term_index[term] = Index.read_index_by_offset(idx_file, dict[term]).index[term]
                for doc in term_index[term]:
                    docs_set.add(int(doc))
                query_table[term] = {}
                query_table[term]["tf"] = 1
                query_table[term]["df"] = len(term_index[term])
                query_table[term]["idf"] = math.log(N / query_table[term]["df"], 10)
                query_table[term]["w"] = (1 + math.log(query_table[term]["tf"])) * query_table[term]["idf"]
            else:
                query_table[term] = {}
                query_table[term]["tf"] = 1
                query_table[term]["df"] = 0
                query_table[term]["idf"] = 0
                query_table[term]["w"] = 0
                pass
        euclidean_length = 0
        while True:
            try:
                element = str(docs_set.pop())
                docs_table[element] = {}
                for term in query_string:
                    docs_table[element][term] = {}
                    if element in term_index[term]:
                        docs_table[element][term]["tf"] = len(term_index[term][str(element)])
                    else:
                        docs_table[element][term]["tf"] = 0
                    euclidean_length += docs_table[element][term]["tf"] * docs_table[element][term]["tf"]
            except KeyError:
                break
        euclidean_length = math.sqrt(euclidean_length)
        for doc in docs_table:
            for term in query_string:
                docs_table[doc][term]["w"] = docs_table[doc][term]["tf"] / euclidean_length

        query_len = 0
        for term in query_string:
            query_len += query_table[term]["w"] * query_table[term]["w"]
        query_len = math.sqrt(query_len)

        for doc in docs_table:
            up_part = 0
            doc_len = 0
            for term in query_string:
                up_part += docs_table[doc][term]["w"] * query_table[term]["w"]
                doc_len += docs_table[doc][term]["w"] * docs_table[doc][term]["w"]
            docs_score[doc] = up_part / (math.sqrt(doc_len) * query_len)

        print("doc#\tscore")

        for i in sorted(docs_score, key=docs_score.get, reverse=True):
            return_count -= 1
            if return_count < 0: break
            print("%d\t%.3f" % (int(i), docs_score[i]))




    else:
        exit()
    pass


if __name__ == "__main__":
    query()


