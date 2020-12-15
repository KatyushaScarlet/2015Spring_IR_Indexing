import requests
import json
from flask import Flask, request, render_template, session,redirect,url_for

import query

app = Flask(__name__)

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

@app.route("/Search",methods=["GET"])
def Search():
    query_string = request.values["query"]
    # to lower case, trim, spit
    query_string = query_string.lower()
    query_string = query_string.strip()
    query_string = query_string.split()

    result_fetch = query.query(file_name,query_string,return_count)

    # result_render = ""
    # result_fetch = result[:return_count-1]
    count = len(result_fetch)

    # for item in result_fetch:
    #     result_render += str(item.doc_id)
    #     result_render += "&nbsp;"
    #     result_render += str(item.doc_score)
    #     result_render += "&nbsp;"
    #     result_render += str(get_document_title(item.doc_id))
    #     result_render += "<br />"

    # return result_render

    for item in result_fetch:
        item.doc_title = str(get_document_title(item.doc_id))

    return render_template("www/Search.html",count=count,documentList=result_fetch)
        
@app.route("/Retrieve",methods=["GET"])
def Retrieve():
    doc_id = request.values["id"]
    f = open("html/"+str(doc_id) + ".html","r",encoding="utf-8",errors="ignore")
    return f.read()

def get_document_title(id):
    return titles[int(id)-1]

if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=8000)