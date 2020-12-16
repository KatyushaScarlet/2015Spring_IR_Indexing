import requests
import json
from flask import Flask, request, render_template, session,redirect,url_for
from flask_paginate import Pagination, get_page_parameter
import query

app = Flask(__name__,
            static_url_path='', 
            static_folder='static',
            template_folder='templates')

file_name = "01.warc"
return_count = 10000
# get titles
titles = []
title_file = open("html/titles.txt","r",encoding="utf-8",errors="ignore")
for line in title_file.readlines():
    titles.append(line)
title_file.close()

@app.route("/", methods=["GET"])
def Index():
    return render_template("www/Index.html")

@app.route("/About", methods=["GET"])
def About():
    return render_template("www/About.html")

@app.route("/Search",methods=["GET"])
def Search():
    search = False
    limit=request.values["limit"]
    limit=int(limit)
    query_string = request.values["query"]
    if query_string:
        search = True
    # to lower case, trim, spit
    query_string = query_string.lower()
    query_string = query_string.strip()
    query_string = query_string.split()

    result_fetch = query.query(file_name,query_string,return_count)


    count = len(result_fetch)
    page = request.args.get(get_page_parameter(), type=int, default=1)
    pagination = Pagination(page=page, total=count, css_framework='bootstrap4',per_page=limit)
    start = (page - 1) * limit
    end = page * limit if count > page * limit else count


    ret = result_fetch[start:end]
    for item in result_fetch:
        item.doc_title = str(get_document_title(item.doc_id))

    return render_template("www/Search.html", count=count, documentList=ret, pagination=pagination,search=search, record_name='result_fetch')
        
@app.route("/Retrieve",methods=["GET"])
def Retrieve():
    doc_id = request.values["id"]
    f = open("html/"+str(doc_id) + ".html","r",encoding="utf-8",errors="ignore")
    return f.read()

def get_document_title(id):
    return titles[int(id)-1]

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=8080)
