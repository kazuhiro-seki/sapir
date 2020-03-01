# -*- coding: utf-8 -*-

import os
import re
from datetime import datetime 
from flask import Flask, render_template, request, redirect, \
     url_for, send_from_directory, g, flash, session, jsonify, \
     make_response
from contextlib import closing

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from elasticsearch import Elasticsearch

app = Flask(__name__)
app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

#app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:////Users/seki/projects/finindex/demo/sapir.db'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///sapir.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

es = Elasticsearch('http://localhost:9200')

class SAPIR_MONTH(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    factor = db.Column(db.String(80), unique=False, nullable=False)
    month = db.Column(db.Integer, unique=False, nullable=False)
    index = db.Column(db.Float, unique=False, nullable=False)

    def __repr__(self):
        return '<%s %d %f>' % \
            (self.factor, self.month, self.index)
    
def insert_sapir():
    print('inserting sapir')
    with app.open_resource('method_c.csv', mode='r') as f:
        for line in f:
            month, index = line.rstrip().split(',')
            db.session.add(
                SAPIR_MONTH(factor='SAPIR',
                            month=month,
                            index=index))
    db.session.commit()

def insert_economy_watchers():
    print('inserting economy watchers di')

    keiki_2002_201812 = [35.5, 34.5, 41.6, 43.9, 45.3, 42.6, 42.1, 42.2, 41.8, 39.0, 38.4, 38.5, 38.9, 39.5, 38.8, 36.0, 37.7, 41.9, 44.3, 45.2, 47.9, 51.7, 49.8, 50.8, 51.6, 51.3, 51.5, 53.2, 51.8, 51.0, 53.6, 49.9, 46.7, 47.2, 46.7, 45.9, 48.4, 46.6, 47.0, 47.1, 49.6, 50.5, 49.8, 49.6, 51.1, 51.4, 54.3, 57.5, 55.6, 55.0, 54.8, 52.4, 50.4, 48.4, 47.4, 49.3, 50.4, 51.7, 50.4, 51.6, 51.0, 50.7, 48.1, 46.9, 45.6, 44.9, 43.3, 43.0, 42.2, 42.6, 41.1, 39.4, 35.9, 35.2, 34.4, 32.2, 30.4, 28.2, 27.0, 27.3, 27.5, 24.4, 23.5, 18.9, 21.3, 21.1, 25.8, 30.4, 34.5, 40.6, 39.6, 40.7, 42.9, 43.3, 37.1, 38.4, 42.8, 43.4, 44.2, 45.7, 45.2, 45.8, 46.8, 44.7, 42.0, 43.5, 47.1, 47.7, 47.9, 49.1, 24.0, 23.9, 33.5, 48.2, 50.0, 47.3, 46.8, 49.8, 48.6, 48.9, 46.6, 46.1, 47.5, 46.9, 45.0, 42.6, 42.3, 44.3, 43.4, 42.9, 43.9, 47.1, 51.1, 52.6, 53.2, 52.7, 53.9, 52.5, 50.7, 52.0, 54.9, 55.3, 56.9, 56.5, 55.7, 52.3, 54.1, 38.4, 43.4, 47.7, 50.1, 48.6, 49.2, 47.0, 44.3, 45.4, 46.1, 49.5, 49.3, 50.8, 51.8, 51.1, 50.5, 50.4, 48.8, 50.6, 48.6, 48.5, 47.3, 44.2, 42.5, 40.9, 42.0, 41.3, 44.1, 46.2, 46.3, 48.3, 50.5, 50.7, 49.4, 48.8, 47.9, 48.5, 49.1, 50.0, 49.9, 50.0, 51.1, 52.0, 54.1, 53.9, 49.9, 48.6, 48.9, 49.0, 47.1, 48.1, 46.6, 48.7, 48.3, 48.6, 49.5, 46.8]

    keiki = keiki_2002_201812[(2013-2002)*12:(2019-2002)*12]

    months = []
    for year in range(2013, 2019):
        months += ['{}{:02d}'.format(year, x) for x in range(1, 13)]
    
    for month, index in zip(months, keiki):
        db.session.add(
            SAPIR_MONTH(factor='EWDI',
                        month=month,
                        index=index))
    db.session.commit()

@app.route('/sapir')
def home():

    # retrieve watchlist from cookie
    watchlist = request.cookies.get('watchlist')
    print("Watchlist:", watchlist)
    if watchlist == None or watchlist == '':
        watchlist = []
    else:
        watchlist = watchlist.split('|')

    contribs = []
    for w in watchlist:
        contribs.append(SAPIR_MONTH.query.filter_by(factor=w).all())
    
    return render_template('index.html', sapir=sapir,
                           ewdi=ewdi, contribs=contribs)


@app.route('/sapir/search', methods = ['POST'])
def search():

    keyword = request.form['keyword']

    # retrieve watchlist from cookie
    watchlist = request.cookies.get('watchlist')
    if watchlist == None or watchlist == '':
        watchlist = [keyword]
    else:
        watchlist = watchlist.split('|')
        if keyword not in watchlist:
            watchlist.append(keyword)

    # get sentiment of watchlist
    contribs = []
    for w in watchlist:
        result = SAPIR_MONTH.query.filter_by(factor=w).all()
        if len(result) == 0:
            # query elasticsearch
            query = {
                "size": 0,
                "query": {
                    "match_phrase" : {
                        "sentence" : {
                            "query" : keyword,
                        }
                    }
                },
                "aggregations": {
                    "sum_month_sentiment": {
                        "date_histogram": {
                            "field": "date",
                            "interval": "month",
                            "format": "yyyyMMdd",
                        },
                        "aggregations": {
                            "sum_sentiment": {
                                "sum": {
                                    "field": "sentiment"
                                }
                            }
                        }
                    }
                }
            }
            for r in es.search(index='sapir', body=query)["aggregations"]["sum_month_sentiment"]['buckets']:
                date = r["key_as_string"]
                sentiment = r["sum_sentiment"]["value"] \
                    / int(month2cnt[date[:6]])
                db.session.add(SAPIR_MONTH(factor=keyword,
                                           month=date[:6],
                                           index=sentiment))
                result.append(
                    {"factor": keyword,
                     "month": date[:6],
                     "index": sentiment})
            if len(result) > 0:
                db.session.commit()

        if len(result) > 0:
            contribs.append(result)

    # update cookie
    res = make_response(
        render_template('index.html', sapir=sapir,
                        ewdi=ewdi, contribs=contribs))
    res.set_cookie('watchlist', '|'.join(watchlist),
                   max_age=60*60*24*expiration_days)
    
    return res

@app.route('/sapir/delete_factor')
def delete_factor():
    print('received:', request.args.get('id'))

    # update cookie
    watchlist = request.cookies.get('watchlist').split('|')
    print(watchlist)
    res = make_response('')
    watchlist.pop(int(request.args.get('id')))
    print(watchlist)
    res.set_cookie('watchlist', '|'.join(watchlist),
                   max_age=60*60*24*expiration_days)
    
    return res
        

@app.route('/sapir/delete/')
def delete_cookie():
    res = make_response(
        render_template('index.html', sapir=sapir,
                        ewdi=ewdi))
    res.set_cookie('watchlist', '', max_age=0)
    return res

# sql tables
db.drop_all()
db.create_all()
insert_sapir()
insert_economy_watchers()

# cookie expiration
expiration_days = 30

# business indices
sapir = SAPIR_MONTH.query.filter_by(factor='SAPIR').all()
ewdi = SAPIR_MONTH.query.filter_by(factor='EWDI').all()
    
# get doc counts
query = {
    "size": 0,
    "query": {
        "match_all": {}
    },
    "aggregations": {
        "cnt_month": {
            "date_histogram": {
                "field": "date",
                "interval": "month",
                "format": "yyyyMMdd",
            },
        }
    }
}
month2cnt = dict()
for r in es.search(index='sapir', body=query)["aggregations"]["cnt_month"]['buckets']:
    month2cnt[r["key_as_string"][:6]] = r["doc_count"]

