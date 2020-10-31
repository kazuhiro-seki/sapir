import argparse
import csv
import os
import sys

import utils
from elasticsearch import Elasticsearch, helpers

def create_index(input, index='test_index'):

    es = Elasticsearch('http://localhost:9200')
    created = False

    # index settings
    settings = {
        "settings": {
            "analysis": {
                "analyzer": {
                    "my_analyzer": {
                        "type": "custom",
                        "tokenizer": "kuromoji_tokenizer",
                        "mode": "normal",
                    }
                }
            }
        },
        "mappings": {
            "_doc": {
                "properties": {
                    "sentence": {
                        "type": "text",
                        "index": "true",
                        "analyzer": "my_analyzer"
                    },
                    "date": {
                        "type": "date",
                        "index": "true",
                        "format": "yyyyMMdd",
                    },
                    "sentiment": {
                        "type": "float"
                    }
                }
            }
        }
    }
    
    try:
        if es.indices.exists(index):
            es.indices.delete(index=index)
        es.indices.create(index=index, body=settings)
        print('Created Index')
        created = True
    except Exception as ex:
        print(str(ex))

        
    def generate_data():
        with utils.open_by_suffix(input) as f:
            for i, line in enumerate(f):
                data = {
                    '_type': '_doc',
                    '_index': index,
                    '_id': i,
                }
                date, sentence, sentiment = line.rstrip().split()
                data['date'] = date
                data['sentence'] = sentence
                data['sentiment'] = sentiment
                yield data

    print(helpers.bulk(es, generate_data()))

'''
main
'''

if __name__ == '__main__':

    ap = argparse.ArgumentParser()
    ap.add_argument('--input')
    ap.add_argument('--index', default='sapir')
    args = ap.parse_args()

    create_index(args.input, args.index)

