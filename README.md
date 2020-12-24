WARC Search Engine
============

## Usage
`python3 index.py [warcfile]`

`python3 query.py -w [warcfile] -q [query term]`

`python3 main.py`

### index.py
Use for construct index file

### main.py
After building index file through index.py, run `main.py` to open the web interface.

The default url is `http://127.0.0.1:8080`.

### query.py
You can also run `query.py` to make query without web interface.

## Example:
`python3 index.py 01.warc`

`python3 query.py -w 01.warc -q taiwan`

`python3 main.py`

## Screenshot

### Index
![index](/screenshot/index.png)

### Search
![search](/screenshot/search.png)

### About
![about](/screenshot/about.png)