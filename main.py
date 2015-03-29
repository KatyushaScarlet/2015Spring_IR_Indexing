__author__ = 'raccoon'

from warc.parser import Parser
import sys

f = sys.argv[1]
p = Parser(f)
count = 0
while True:
    r = p.fetch()
    if r:
        print(r)
        count += 1
        # print(r.content)
    else:
        break

print("")
print("Count: ", count)