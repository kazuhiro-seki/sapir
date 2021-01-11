# -*- coding: utf-8 -*-

import os
import re
import logging
from datetime import datetime, timezone
from flask import Flask, render_template, request, redirect, \
     url_for, send_from_directory, g, flash, session, jsonify, \
     make_response
from contextlib import closing

from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine

from elasticsearch import Elasticsearch

from io import StringIO
import csv
from urllib.parse import quote

logging.basicConfig(level=logging.INFO)
app = Flask(__name__)

app.config.from_object(__name__)
app.config.from_envvar('FLASKR_SETTINGS', silent=True)

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
    app.logger.info('inserting sapir')
    with app.open_resource('method_c.csv', mode='r') as f:
        for line in f:
            month, index = line.rstrip().split(',')
            db.session.add(
                SAPIR_MONTH(factor='SAPIR',
                            month=month,
                            index=index))
    db.session.commit()

def insert_economy_watchers():
    app.logger.info('inserting economy watchers di')

    keiki_industry_2002_202006 = [33.6, 35.6, 41.3, 44.0, 48.3, 44.6, 44.1, 43.2, 42.7, 40.0, 40.7, 41.8, 40.1, 40.6, 39.4, 37.1, 39.4, 43.0, 45.9, 47.2, 50.0, 52.7, 52.0, 51.9, 53.3, 52.4, 53.6, 55.8, 55.0, 53.4, 54.6, 52.3, 48.7, 48.4, 47.2, 44.5, 47.0, 47.1, 48.1, 47.9, 49.9, 48.7, 48.5, 50.5, 52.3, 52.8, 55.6, 57.7, 56.0, 56.0, 55.5, 52.1, 50.0, 49.2, 48.6, 48.7, 50.2, 51.6, 51.3, 52.5, 51.7, 50.9, 49.0, 47.5, 44.8, 44.6, 45.4, 42.5, 42.7, 42.0, 41.1, 38.9, 36.2, 35.7, 34.3, 32.8, 31.1, 29.3, 25.0, 27.3, 27.3, 24.0, 22.1, 15.1, 19.1, 18.1, 25.5, 30.2, 35.3, 40.5, 42.7, 43.8, 46.0, 47.3, 41.7, 40.7, 44.5, 44.8, 46.0, 48.1, 47.1, 45.0, 45.0, 41.8, 42.3, 42.1, 47.0, 46.5, 47.6, 47.4, 28.0, 25.7, 32.8, 45.6, 48.7, 47.9, 47.5, 49.5, 48.7, 47.1, 44.8, 44.5, 48.2, 45.5, 44.6, 43.4, 42.2, 44.3, 41.9, 41.6, 43.5, 46.4, 51.7, 54.2, 53.0, 54.1, 56.4, 52.4, 52.5, 54.0, 57.7, 57.6, 58.6, 60.4, 58.5, 55.9, 55.7, 46.6, 47.2, 50.4, 52.5, 49.5, 49.3, 48.2, 46.1, 45.8, 47.3, 50.2, 50.5, 51.4, 50.5, 51.6, 51.5, 49.4, 47.9, 48.8, 48.5, 47.6, 46.5, 45.2, 45.1, 44.0, 44.2, 42.4, 44.7, 48.3, 48.9, 49.5, 50.7, 51.8, 50.5, 50.4, 49.7, 49.4, 52.1, 52.9, 52.1, 52.0, 52.0, 55.4, 54.3, 54.6, 52.4, 50.5, 51.3, 51.2, 50.7, 49.8, 49.7, 50.7, 50.0, 49.2, 48.8, 46.3, 46.4, 46.5, 45.0, 45.4, 43.6, 43.5, 42.8, 41.8, 44.7, 41.0, 39.2, 41.2, 41.7, 30.1, 19.2, 9.9, 15.0, 30.4]

    keiki = keiki_industry_2002_202006[(2008-2002)*12:(2021-2002)*12-6]

    months = []
    for year in range(2002, 2020):
        months += ['{}{:02d}'.format(year, x) for x in range(1, 13)]
    
    for month, index in zip(months[:len(keiki)], keiki):
        db.session.add(
            SAPIR_MONTH(factor='EWDI',
                        month=month,
                        index=index))
    db.session.commit()

@app.route('/')
def home():

    # retrieve watchlist from cookie
    watchlist = request.cookies.get('watchlist')
    if watchlist != None:
        app.logger.info("Watchlist: " + watchlist)

    if watchlist == None or watchlist == '':
        watchlist = []
    else:
        watchlist = watchlist.split('|')

    contribs = []
    for w in watchlist:
        contribs.append(SAPIR_MONTH.query.filter_by(factor=w).all())
    
    return render_template('index.html', sapir=sapir,
                           ewdi=ewdi, contribs=contribs)


@app.route('/search', methods = ['POST'])
def search():

    keyword = request.form['keyword']
    app.logger.info('query is ' + keyword)
    
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
    to_be_removed = []
    for w in watchlist:

        # inquire database first
        result = SAPIR_MONTH.query.filter_by(factor=w).all()

        # use elasticsearch if not found
        if len(result) == 0:

            # need to set min and max date for correct adjustment
            min = int(datetime(\
                2008,1,1,tzinfo=timezone.utc).timestamp() * 1000)
            max = int(datetime(\
                2020,6,30,23,59,59,tzinfo=timezone.utc).timestamp() * 1000)

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
                            "extended_bounds" : {
                                "min" : min,
                                "max" : max
                            },
                            "format": "yyyyMMdd"
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
        else:
            to_be_removed.append(w)

    # remove unknown words
    for w in to_be_removed:
        watchlist.remove(w)
            
    # update cookie
    res = make_response(
        render_template('index.html', sapir=sapir,
                        ewdi=ewdi, contribs=contribs))
    res.set_cookie('watchlist', '|'.join(watchlist),
                   max_age=60*60*24*expiration_days)
    
    return res

@app.route('/delete_factor')
def delete_factor():
    app.logger.info('received: ' + request.args.get('word'))

    # update cookie
    watchlist = request.cookies.get('watchlist').split('|')
    app.logger.debug('before: ' + ' '.join(watchlist))
    watchlist.remove(request.args.get('word'))
    app.logger.debug('after:  ' + ' '.join(watchlist))

    res = make_response('')
    res.set_cookie('watchlist', '|'.join(watchlist),
                   max_age=60*60*24*expiration_days)
    
    return res

@app.route("/<word>/download")
def download(word):

    app.logger.info('received: ' + word)
    
    # get keyword by given id
    watchlist = request.cookies.get('watchlist').split('|')
    
    # inquire database
    result = SAPIR_MONTH.query.filter_by(factor=word).all()

    # dynamically prepare csv file
    f = StringIO()
    writer = csv.writer(f)

    writer.writerow(['date','sentiment'])
    for row in result:
        writer.writerow([row.month, row.index])

    res = make_response(f.getvalue())
    res.headers['Content-Type'] = 'text/csv'
    file_expr = "filename*=utf-8''{}".format(quote(word+'.csv'))
    res.headers['Content-Disposition'] = \
        'attachment; {}'.format(file_expr)
    
    return res

'''
Hidden page to clear cache
'''
@app.route('/delete/')
def delete_cookie():
    res = make_response(
        render_template('index.html', sapir=sapir,
                        ewdi=ewdi))
    res.set_cookie('watchlist', '', max_age=0)
    return res

'''
main
'''

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

