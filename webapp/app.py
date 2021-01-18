from datetime import datetime
from flask import Flask, jsonify, request, render_template, redirect, url_for
from elasticsearch import Elasticsearch
from search import search_query


es = Elasticsearch('10.0.1.10', port=9200)

app = Flask(__name__, static_url_path="/static", static_folder="static")

@app.route("/")
def home():
    return render_template("search.html", tweets=[],)


@app.route("/search", methods=["GET", "POST"])
def search():

    query = request.args.get("search")
    user = request.args.get("profile")
    field = request.args.get("field")
    topic = request.args.get("topic")

    res, should = search_query(
        query,
        count=10,
        user=user,
        topic=topic,
        field = field,
    )

    return render_template(
        "search.html",
        tweets=res,
        query=query,
        should=should,
        count=10,
        user=user,
        topic=topic,
        field = field
    )

if __name__ == "__main__":
    app.run(debug=True)