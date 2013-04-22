#!/usr/bin/env python

from flask import Flask, render_template
from pymongo import MongoClient, DESCENDING, ASCENDING

app = Flask("soundbites")

# Mongo connection objects.
client = MongoClient()
db = client.apps
menu_items = db.menu_items


@app.route('/week/<week_number>/')
def list_by_week(week_number):
    context = {"menu_items": []}
    for item in menu_items.find({"week": int(week_number)}):
        context['menu_items'].append(item)
    return render_template('index.html', **context)


@app.route('/')
def list_all():
    context = {"menu_items": []}
    for item in menu_items.find():
        context['menu_items'].append(item)
    return render_template('index.html', **context)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000)
