# coding=utf-8
from indexer import *
from retriever import *
from pathlib import Path
import os
from flask import Flask, render_template, request, redirect, url_for

#INDEX_DIR = '/root/IR_system/flask_app/data'
INDEX_DIR = '/Users/kim/Desktop/Git/IRsystem/flask_app/data'
app = Flask(__name__, instance_relative_config=True)


# a simple page that says hello
@app.route('/')
def hello():
	return redirect(url_for('home'))

@app.route('/home')
def home():
	return render_template('home.html')

@app.route('/search_phrase')
def search_phrase(query, retriever):
	query = query.split('/')
	term = query[0]
	phrase = query[1]
	hits = retriever.search_phrase(term, phrase)
	if hits:
		return render_template('result.html', hits=hits)
	else:
		return 'Nothing found'

	


@app.route('/search', methods=['GET', 'POST'])
def search():
	query = request.args.get('query')
	retriever = Retriever(INDEX_DIR)
	if '/' in query:
		hits = search_phrase(query, retriever) 
	else:
		hits = retriever.search(query)
	if hits:
		return render_template('result.html', hits=hits)
	else:
		return 'Nothing found'




if __name__ == '__main__':
	# initialize indexer
	print('Initializing...')
	# combine_files()
	lucene.initVM()
	#if len(os.listdir(path=INDEX_DIR)) < 2: # always exists a file named .DS_store(Cant use in linux)
	Indexer(INDEX_DIR)
	app.run()

	# for file in ['Sogou0015_raw', 'Sogou0017_raw', 'Sogou0011_raw', 'Sogou0010_raw', 'Sogou0007_raw', 'Sogou0005_raw']:
	#     f = open('/Users/kim/Desktop/raw_corpus/' + file, 'r')
	#     line = f.readline()
	#     print(line)
	#     f.close()
