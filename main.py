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

    result = query.query(file_name,query_string,return_count)

    return result


if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=8000)