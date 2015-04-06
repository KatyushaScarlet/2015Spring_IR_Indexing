WARC Indexer
============
#### 說明
1. 可以使用ClueWeb09_English_Sample.warc進行測試
2. 會產生

#### 使用方式
`python3 main.py filename [-m] [-gz]`
##### Parameters:
1. -m 使用多執行緒製作索引檔
2. -gz 將索引檔案使用gzip進行壓縮
##### Example:
`python3 main.py ClueWeb09_English_Sample.warc -m -gz`
##### Output
1. 產生 filename.warc_index.dict 的字典檔
2. 產生 filename.warc_index.idx 的 inverted index file
3. 備註：如使用gzip壓縮，檔名後面會再加上.gz
4. Sample Output
```
Start......
tmp/nJscQsoWkoIDUPhnfOSK
----------------------------------------------------------
Analysis document:
0.716609001159668 s
Average: 7.095138625343247 ms
Document process per second: 140.94157321015305 ps
----------------------------------------------------------
build full index ......
----------------------------------------------------------
Build full index:
0.1540229320526123 s
Average: 1.524979525273389 ms
DPS: 655.7465090036052 ps
----------------------------------------------------------
dump index from memory to file ClueWeb09_English_Sample.warc.index.txt
----------------------------------------------------------
dump index:
0.8909430503845215 s
----------------------------------------------------------
finish
----------------------------------------------------------
Total time analysis:
1.7947611808776855 s
Average 17.770000023416955 ms
DPS 56.274179017437866 ps
```

