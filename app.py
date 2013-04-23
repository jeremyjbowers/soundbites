#!/usr/bin/env python

import datetime
import json

from flask import Flask, render_template
from pymongo import MongoClient, DESCENDING, ASCENDING

app = Flask("soundbites")

# Mongo connection objects.
client = MongoClient()
db = client.apps
menu_items = db.menu_items


@app.route('/soundbites/raw/')
def raw_find():
    from flask import request
    q = request.args.get('q', None)

    query = menu_items.find()
    if q:
        query = menu_items.find(json.loads(q))

    response = {}
    response['items'] = []
    start = datetime.datetime.now()
    for item in query:
        del(item['_id'])
        response['items'].append(item)
    response['meta'] = {}
    response['meta']['count'] = len(response['items'])
    elapsed = datetime.datetime.now() - start
    response['meta']['time_elapsed'] = float('%s.%s' % (elapsed.seconds, elapsed.microseconds))
    return json.dumps(response)

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=8000, debug=True)
