import requests
import json
from flask import Flask, request, render_template, session,redirect,url_for

import query

app = Flask(__name__)

file_name = "01.warc"
return_count = 10

@app.route("/", methods=["GET"])
def Index():
    return render_template("www/Index.html")

@app.route("/Search",methods=["GET"])
def Search():
    query_string = request.values["query-string"]
    # to lower case, trim, spit
    query_string = query_string.lower()
    query_string = query_string.strip()
    query_string = query_string.split()

    result = query.query(file_name,query_string,return_count)

    result_render = ""
    result_fetch = result[:return_count-1]

    for item in result_fetch:
        result_render += str(item.doc_id)
        result_render += "&nbsp;"
        result_render += str(item.doc_score)
        result_render += "<br />"

    return result_render
        
@app.route("/Fetch",methods=["GET"])
def Fetch():
    doc_id = request.values["id"]
    f = open("html/"+str(doc_id) + ".html","r",errors="ignore",encoding="utf-8")
    return f.read()


if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=8000)