WARC Search Engine
============

## Usage
`python3 index.py [warcfile] [-gz] [-cf] [-sw] [-st]`

`python3 query.py -w [warcfile] -q [query term]`

`python3 main.py`

### index.py
Use for construct index file
1. -gz use gzip compress index file
2. -cf use case folding
3. -sw use stop word removal
4. -st use stemming
### main.py
After building index file through index.py, run `main.py` to open the web interface.

The default url is `http://127.0.0.1:8080`.

### query.py
You can also run `query.py` to make query without web interface.

## Example:
`python3 index.py 01.warc -cf -sw -st`

`python3 query.py -w 01.warc -q taiwan`

`python3 main.py`

## Screenshot

### Index
![index](/screenshot/index.png)

### Search
![search](/screenshot/search.png)

### About
![about](/screenshot/about.png)