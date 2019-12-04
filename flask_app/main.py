# coding=utf-8
from indexer import *
from retriever import *
from pathlib import Path
import os
from flask import Flask, render_template, request, redirect, url_for

INDEX_DIR = '/Users/kim/Desktop/Git/IRsystem/flask_app/data'
app = Flask(__name__, instance_relative_config=True)


# a simple page that says hello
@app.route('/')
def hello():
    return redirect(url_for('home'))

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/search', methods=['GET', 'POST'])
def search():
    query = request.args.get('query')
    retriever = Retriever(INDEX_DIR)
    hits = retriever.search(query)
    if hits:
        return render_template('result.html', hits=hits)
    else:
        return 'Nothing found'

@app.route('/search_phrase')
def search_phrase():
    query = request.args.get('query')


if __name__ == '__main__':
    # initialize indexer
    # combine_files()
    lucene.initVM()
    if len(os.listdir(path=INDEX_DIR)) < 2: # always exists a file named .DS_store
        Indexer(INDEX_DIR)
    app.run()

    # for file in ['Sogou0015', 'Sogou0017', 'Sogou0011', 'Sogou0010', 'Sogou0007', 'Sogou0005']:
    #     f = open('/Users/kim/Desktop/corpus/' + file, 'r')
    #     line = f.readline()
    #     print(line)
    #     f.close()

    # f = open('/Users/kim/Desktop/corpus/Sogou0010', 'r')
    # line_count = 0
    # line = f.readline()
    # while line:
    #     line_count += 1
    #     print(line)
    #     if line_count == 100:
    #         break
    #     line = f.readline()