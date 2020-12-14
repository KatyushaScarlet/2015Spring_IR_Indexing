import requests
import json
from flask import Flask, request, render_template, session,redirect,url_for

app = Flask(__name__)




@app.route("/", methods=["GET"])
def Index():
    return render_template("www/Index.html")

@app.route("/Search",methods=["GET"])
def Search():
    keyword = request.values["keyword"]
    return "searching:%s" % keyword


if __name__ == "__main__":
    app.run(debug = True, host = "0.0.0.0", port=8000)