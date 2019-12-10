import sys
import os
import lucene
import thulac
import time
from functools import cmp_to_key
from pathlib import Path
from java.io import File
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, IndexReader, DirectoryReader, Term
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, Query, PhraseQuery, TermQuery
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleHTMLFormatter

prefixHTML = u"<font color='red'>"
suffixHTML = u"</font>"

# Add stopwords 
with open('stopwords.txt', 'r') as f:
	punctuation = []
	for p in f:
		punctuation.append(p.strip('\n'))
print(punctuation[:50])

# some pucntuation for additional
punctuation2 = '。  ， ,  .  、 ： ； “ ” ‘ ’ 【 】 「 」 、 | 《  》 · - —— = + % < > ; : 0 （ ） ( )'
punctuation2 = punctuation2.split()

'''
	Retrieving query in indexed file, return results
'''
class Retriever():
	# __init__ should not return value
	hits = []
	path = ''
	analyzer = ''
	reader = ''
	searcher = ''
	thu = ''

	# cmp para for sort
	sort_para = ''
	def __init__(self, path):
		print('Searcher initialized...')
		self.path = path
		self.analyzer = SmartChineseAnalyzer()
		# self.analyzer = WhitespaceAnalyzer(Version.LATEST)
		self.reader = DirectoryReader.open(SimpleFSDirectory(Paths.get(self.path)))
		self.searcher = IndexSearcher(self.reader)
		self.thu = thulac.thulac(deli='/')

	'''
		Main Search function of system, contains normal search, window-limit search, multi-terms search
	'''
	def search(self, term, window=2):
		self.hits = []
		index_list = []
		sort_para = term

		parser = QueryParser('text', self.analyzer)
		query = parser.parse(term)
		print(query)

		# Jump to multi-terms search if there are several words
		if self.multi_terms(query):
			self.search_multi_terms(query) 
			return self.hits[:40]

		hits = self.searcher.search(query, 1000).scoreDocs

		for hit in hits:
			index = []
			doc = self.searcher.doc(hit.doc)
			text = doc.get("text")
			self.hits.append(text)
			# save indexes of target term in each document
			terms = text.split()
			for i in range(len(terms)):
				if term == terms[i]:
					index.append(i)
			index_list.append(index)

		self.recover_sentence(index_list, window)
		hits_copy = self.hits
		self.hits = []
		for hit in hits_copy:
			simpleHTMLFormatter = SimpleHTMLFormatter(prefixHTML, suffixHTML)
			highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(query))
			highLightText = highlighter.getBestFragment(self.analyzer, 'text', hit)
			if highLightText is not None:
				self.hits.append(highLightText)
		print('search over')
		return self.hits[:40]

	'''
		Phrase search for system, it will return result if the phrase is same
	'''
	def search_phrase(self, term, phrase):
		print('Phrase search')
		self.hits = []
		index_list = []
		parser = QueryParser('text', self.analyzer)
		query = parser.parse(term)   

		hits = self.searcher.search(query, 1000).scoreDocs
		if hits is None:
			return 

		for hit in hits:
			index = []
			doc = self.searcher.doc(hit.doc)
			text = doc.get("text")
			phrases = doc.get("phrase")

			# processing with saved text and phrase
			terms = text.split()
			phrases = phrases.split()
			flag = 1 # this flag is judging for phrase in every target term in text
			index = [] # index number for searched term, maybe many terms
			for i in range(len(terms)):
				if term == terms[i]:
					index.append(i)
					if not phrase == phrases[i]:
						flag = 0
						break;
			if flag == 1:
				self.hits.append(text)
				index_list.append(index)
		self.recover_sentence(index_list)
		hits_copy = self.hits
		self.hits = []
		# add font tags for terms
		for hit in hits_copy:
			simpleHTMLFormatter = SimpleHTMLFormatter(prefixHTML, suffixHTML)
			highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(query))
			highLightText = highlighter.getBestFragment(self.analyzer, 'text', hit)
			if highLightText is not None:
				self.hits.append(highLightText)

		return self.hits[:40]
	

	def search_multi_terms(self, query):
		print('Multiterms search')
		hits = self.searcher.search(query, 100).scoreDocs
		for hit in hits:
			doc = self.searcher.doc(hit.doc)
			text = doc.get("text")
			terms = text.split()
			sentence = ''
			for term in terms:
				sentence += term
			simpleHTMLFormatter = SimpleHTMLFormatter(prefixHTML, suffixHTML)
			highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(query))
			highLightText = highlighter.getBestFragment(self.analyzer, 'text', sentence)
			if highLightText is not None:
				self.hits.append(highLightText)
		
	'''
		convert words into sentence
		we just need two or three words for giving out results

		:param
			indexs : list of target term indexes
			terms : str of target sentence -> terms[len(terms)] = ' ', terms[len(terms)-1] = punctuation (usually '。')
		:return
			No return, self.hits become [:20] -> can change value
	'''
	def recover_sentence(self, indexs, window=2):
		hits_copy = self.hits
		self.hits = []
		for i in range(len(hits_copy)):
			terms = hits_copy[i].split()
			length = len(terms)

			for index in indexs[i]:
				combination = ''
				if index == 0: 
					sentence = terms[0] + terms[1] if terms[1] not in punctuation else terms[0]
					combination += sentence + ' '
				elif index == 1:
					sentence = terms[0] + terms[1] + terms[2] if terms[2] not in punctuation else terms[0] + terms[1]
					combination += sentence + ' '
				elif index == length-2:
					sentence = terms[length-3] + terms[length-2] if terms[length-3] not in punctuation else terms[length-2]
					combination += sentence + ' '
				elif index == length-3:
					sentence = terms[length-4] + terms[length-3] + terms[length-2] if terms[length-4] not in punctuation else terms[length-3] + terms[length-2]
				elif index >= 2 and index <= length-4:
					combination = self.check_available(index, terms, window)
				
				# delete punc at first of sentence
				combination = self.replace_punc(combination)
				self.hits.append(combination)

		
		# delete duplicated datas and null data
		self.hits = list(set(self.hits))
		self.hits.sort(key=cmp_to_key(lambda x, y : self.compare(x, y)))
		if '' in self.hits:
			self.hits.remove('')
		self.hits = self.hits[:100]
		# print(self.hits)

	''' 
		check for term combinations with window size
	'''
	def check_available(self, index, terms, window=2):
		sentence = terms[index]
		length = len(terms)
		left = index - window if index - window >= 0 else 0
		right = index + window if index + window <= length-1 else length-1
		l = index - 1
		r = index + 1
		while left < l and r < right:
			if terms[l] not in punctuation:
				temp = terms[l]
				temp += sentence
				sentence = temp
				l -= 1
			if terms[r] not in punctuation:
				sentence += terms[r]
				r += 1
			if terms[l] in punctuation and terms[r] in punctuation:
				break
		return sentence
	'''
		Key for sort results
	'''
	def compare(self, x, y):
		x_index = x.find(self.sort_para)
		y_index = y.find(self.sort_para)
		return x_index - y_index
	
	'''
		Judge whether it is multiquery or not
	'''
	def multi_terms(self, query):
		count = 0
		query_str = query.toString().split()
		for q in query_str:
			count += 1
		return True if count > 1 else False
	'''
		Replace punctuations 
	'''
	def replace_punc(self, text):
		for p in punctuation2:
			if p in text:
				text = text.replace(p, ' ')
		# remove first index if it is a spacebar
		if text[:1] == '':
			text = text[1:-1]
		return text