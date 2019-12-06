import sys
import os
import lucene
import thulac
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
from org.apache.lucene.search import IndexSearcher, Query, PhraseQuery
from org.apache.lucene.search.highlight import Highlighter, QueryScorer, SimpleHTMLFormatter

prefixHTML = u"<font color='red'>"
suffixHTML = u"</font>"

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
	def __init__(self, path):
		print('Searcher initialized...')
		self.path = path
		self.analyzer = SmartChineseAnalyzer()
		# self.analyzer = WhitespaceAnalyzer(Version.LATEST)
		self.reader = DirectoryReader.open(SimpleFSDirectory(Paths.get(self.path)))
		self.searcher = IndexSearcher(self.reader)
		self.thu = thulac.thulac(deli='/')


	def search(self, term):
		self.hits = []
		indexreader = self.searcher.getIndexReader()
		# print(indexreader.document(10))
		parser = QueryParser('text', self.analyzer)
		query = parser.parse(term)

		hits = self.searcher.search(query, 20).scoreDocs

		for hit in hits:
			doc = self.searcher.doc(hit.doc)
			text = doc.get("text")
			phrase = doc.get('phrase')
			simpleHTMLFormatter = SimpleHTMLFormatter(prefixHTML, suffixHTML)
			highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(query))
			# highLightText = highlighter.getBestFragment(analyzer, 'text', self.recover_sentence(doc.get('text')))
			highLightText = highlighter.getBestFragment(self.analyzer, 'text', self.recover_sentence(text))
			print(hit.score, hit.doc, hit.toString())
			print(text)
			print(phrase)
			self.hits.append(highLightText)
			
		print('search over')
		# reader.close()
		return self.hits

	def search_phrase(self, term, phrase):
		self.hits = []
		parser = QueryParser('text', self.analyzer)
		query = parser.parse(term)   

		hits = self.searcher.search(query, 1000).scoreDocs
		if hits is None:
			return 

		for hit in hits:
			doc = self.searcher.doc(hit.doc)
			text = doc.get("text")
			token_text = doc.get("token_text")
			simpleHTMLFormatter = SimpleHTMLFormatter(prefixHTML, suffixHTML)
			highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(query))
			highLightText = highlighter.getBestFragment(analyzer, 'text', self.recover_sentence(doc.get('text')))
			# highLightText = highlighter.getBestFragment(self.analyzer, 'text', text)

			token_terms = token_text.split(' ')
			for token_term in token_terms:
				token = token_term.split('/')
				if token[0] == term:
					if token[1] == phrase:
						print('append %s' % term)
						self.hits.append(highLightText)
		return self.hits[:20]

	'''
		Using thulac for marking phrase of query
	'''
	def mark_term(self, query):
		marked_term = self.thu.cut(query, text=True)
		term_sentence = ''
		print(marked_term)
		if len(marked_term) > 1:
			for term in marked_term:
				term_sentence += term
		else:
			term_sentence = marked_term[0]
		return term_sentence
		
	'''
		convert words into sentence
	'''
	def recover_sentence(self, terms):
		print(terms)
		sentence = ''
		terms = terms.split(' ')
		print(terms)
		for term in terms:
			sentence += term
		return sentence


