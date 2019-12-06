import sys
import os
import time
import lucene
from pathlib import Path
from java.io import File
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory
from org.apache.lucene.document import Document, Field, FieldType, StringField
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.analysis import CharArraySet, TokenStream, tokenattributes
from org.apache.lucene.analysis.core import WhitespaceAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, IndexReader, DirectoryReader
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, Query, PhraseQuery

CORPUS_DIR = '/Users/kim/Desktop/corpus/'
RAW_CORPUS_DIR = '/Users/kim/Desktop/raw_corpus/'
SUFFIX = '_raw'
LINE_LIMIT = 100000

stopwords_dic = [' ', '\\', '\\n', '\\np', '\\ns', '\\ni', '\\nz', '\\m', '\\m', '\\q', '\\mq', '\\t', '\\f', '\\s', '\\v', '\\a', '\\d', '\\h', '\\k', '\\i', '\\j', '\\r', '\\c', '\\p', '\\u', '\\y', '\\e', '\\o', '\\g', '\\w', '\\x']

'''
	Combine seperated terms into sentences
'''
def combine_sentences(fileName):
	line_count = 0
	sentence = ''

	with open(CORPUS_DIR + fileName, 'r') as f:
		line = f.readline()
		while(line):
			line_count += 1
			terms = line.split(' ')
			for term in terms:
				term = term.split('/')[0]
				sentence += term
			sentence += '\n'
			line = f.readline()
	f.close()
	with open(RAW_CORPUS_DIR + fileName + SUFFIX, 'w') as f1:
		f1.write(sentence)
	f1.close()
'''
	Convert all files into raw_text
'''
def combine_files():
	for file in ['Sogou0005', 'Sogou0007', 'Sogou0011', 'Sogou0010', 'Sogou0015', 'Sogou0017']:
		start = time.time()
		combine_sentences(file)
		end = time.time()
		print(file + ' completed, time : %f' % (end - start))

'''
	Indexing all corpus in Chinese with lucene
'''

def recover_sentence(terms):
	sentence = ''
	terms = terms.split(' ')
	for term in terms:
		term = term.split('\\')[0]
		sentence += term
	
	return sentence

def test_analyzer():
	analyzer = WhitespaceAnalyzer(Version.LATEST)
	# tokenStream = analyzer.tokenStream('text', '')

'''
	Indexer constructed with Lucene
'''
class Indexer():
	def __init__(self, path):
		stopwords = self.AddStopWords()
		print(stopwords)

		p = Path(path)
		if not p.is_dir():
			os.mkdir(path)
		storeDir = SimpleFSDirectory(Paths.get(path))
		# analyzer = StandardAnalyzer()
		# analyzer = SmartChineseAnalyzer(stopwords)
		analyzer = WhitespaceAnalyzer(Version.LATEST)
		config = IndexWriterConfig(analyzer)
		config.setOpenMode(IndexWriterConfig.OpenMode.CREATE_OR_APPEND)
		index_writer = IndexWriter(storeDir, config)
		self.IndexDocs(index_writer)

	def IndexDocs(self, writer):
		start = time.time()
		line_count = 0
		# for fileName in ['2_1','2_10','2_3']:
		# with open('/root/corpus/corpus/Sogou0017', 'r') as f:
		
		# f1 = open(CORPUS_DIR + 'rmrb0010', 'r')
		with open(CORPUS_DIR + 'Sogou0017', 'r') as f:
			for line in f:
				terms, phrases = self.split_phrase(line)
				line_count += 1
				# token_line = f1.readline()

				# field(raw)
				fieldtype = FieldType()
				fieldtype.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
				fieldtype.setStored(True)
				fieldtype.setTokenized(True)

				# field(tokenized)
				fieldtype2 = FieldType()
				fieldtype2.setStored(True)

				doc = Document()
				doc.add(Field('text', terms, fieldtype))
				doc.add(Field('phrase', phrases, fieldtype2))

				writer.addDocument(doc)
				# if line_count % LINE_LIMIT == 0:
				# 	break
		writer.close()
		print('indexing completed')
		end = time.time()
		print('time: %f' % (end - start))
		print(line_count)
		line_count = 0
		f.close()

	def AddStopWords(self):
		count = 0
		f1 = open('stopwords1.txt', 'r' )
		f2 = open('stopwords2.txt', 'r')
		array_set = CharArraySet(2690, True)
		for word in f1:
			word = word.strip('\n')
			array_set.add(word)
		for word in f2:
			array_set.add(word)
		for word in stopwords_dic:
				array_set.add(word)
		f1.close()
		f2.close()

		return array_set

	def split_phrase(self, sentence):
		term_combine = ''
		phrase_combine = ''
		terms = sentence.split(' ')
		for term in terms:
			temp = term.split('/')
			term_combine += temp[0] + ' '
			phrase_combine += temp[1] + ' '
		
		return term_combine, phrase_combine
		
