# coding=utf-8
from indexer import *
from retriever import *
from pathlib import Path
import os
from flask import Flask, render_template, request, redirect, url_for

#INDEX_DIR = '/root/IR_system/flask_app/data'
INDEX_DIR = '/Users/kim/Desktop/Git/IRsystem/flask_app/data/'
CORPUS_DIR = '/Users/kim/Desktop/corpus/'
app = Flask(__name__, instance_relative_config=True)

# initialize model
lucene.initVM()
retriever = Retriever(INDEX_DIR)


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
		return hits
	else:
		return ''

	


@app.route('/search', methods=['GET', 'POST'])
def search():
	query = request.args.get('query')
	if query == '':
		return render_template('nothing.html')
	window = 2 if request.args.get('window') is '' else int(request.args.get('window'))
	if '/' in query:
		hits = search_phrase(query, retriever) 
	else:
		hits = retriever.search(query, window)
	return render_template('result.html', hits=hits) if hits != '' else render_template('nothing.html')




if __name__ == '__main__':
	# initialize indexer
	print('Initializing...')
	# combine_files()
	#if len(os.listdir(path=INDEX_DIR)) < 2: # always exists a file named .DS_store(Cant use in linux)
	# Indexer(INDEX_DIR)
	app.run()

	# count = 0
	# for file in os.listdir(CORPUS_DIR):
	# 	if not file == '.DS_Store' and not file == 'Sogou0007':
	# 		print(file)
	# 		with open(CORPUS_DIR + file, 'r') as f:
	# 			for line in f:
	# 				count += 1
	# 		f.close()
				
	# for file in ['Sogou0015_raw', 'Sogou0017_raw', 'Sogou0011_raw', 'Sogou0010_raw', 'Sogou0007_raw', 'Sogou0005_raw']:
	#     f = open('/Users/kim/Desktop/raw_corpus/' + file, 'r')
	#     line = f.readline()
	#     print(line)
	#     f.close()
