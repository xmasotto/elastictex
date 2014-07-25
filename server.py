#!/usr/bin/env python
import api
import atexit
from flask import Flask
from flask import request
from flask import render_template

app = Flask(__name__)


@app.route('/')
def get():
    results = None
    q = request.args.get('q')
    if q:
        results = api.search(q)
    return render_template("index.html",
                           results=results)


@app.route('/upload', methods=['POST'])
def post():
    url = request.args.get('url')
    if url is None:
        return "Invalid URL"
    else:
        api.index(url, request.data)
        return "Indexed %s\n" % url

if __name__ == "__main__":
    api.init()
    app.run(debug=True)
