# coding=utf-8
from indexer import *
from retriever import *
from pathlib import Path
import os
from flask import Flask, render_template, request, redirect, url_for

# define with your path
CORPUS_DIR = '/Users/kim/Desktop/corpus/'
INDEX_DIR = 'data/'
app = Flask(__name__, instance_relative_config=True)

# initialize model
lucene.initVM()
retriever = Retriever(INDEX_DIR)


# home page
@app.route('/')
def hello():
	return redirect(url_for('home'))

@app.route('/home')
def home():
	return render_template('home.html')

# search for phrase
@app.route('/search_phrase')
def search_phrase(query, retriever):
	query = query.split('/')
	term = query[0]
	phrase = query[1]
	hits = retriever.search_phrase(term, phrase)
	if hits:
		return hits
	else:
		return ''

@app.route('/search_synonym')
def search_synonym(query, retriever):
	hits = retriever.search_synonym(query)
	if hits:
		return hits
	else:
		return ''

# other searches
@app.route('/search', methods=['GET', 'POST'])
def search():
	query = request.args.get('query')
	synonym = True if request.args.get('synonym') == 'on' else False
	print(query)
	
	if query == '':
		return render_template('nothing.html')
	window = 2 if request.args.get('window') is '' else int(request.args.get('window'))
	if '/' in query or synonym:
		if '/' in query:
			hits = search_phrase(query, retriever) 
		else:
			hits = search_synonym(query, retriever)
	else:
		hits = retriever.search(query, window)
	print(len(hits))
	return render_template('result.html', hits=hits, synonym=synonym, hits_count=len(hits)) if hits != '' and len(hits) > 0 else render_template('nothing.html')

if __name__ == '__main__':
	# initialize indexer
	print('Initializing...')
	# just need once for indexing all corpus
	# Indexer(INDEX_DIR)
	app.run()