import sys
import os
import lucene
from pathlib import Path
from java.io import File
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, IndexReader, DirectoryReader
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
    def __init__(self, path):
        print('Searcher initialized...')
        self.path = path


    def search(self, term):
        self.hits = []

        analyzer = SmartChineseAnalyzer()
        reader = DirectoryReader.open(SimpleFSDirectory(Paths.get(self.path)))
        searcher = IndexSearcher(reader)
        indexreader = searcher.getIndexReader()
        print(indexreader.numDocs())
        parser = QueryParser('text', analyzer)
        query = parser.parse(term)

        hits = searcher.search(query, 20).scoreDocs

        for hit in hits:
            doc = searcher.doc(hit.doc)
            simpleHTMLFormatter = SimpleHTMLFormatter(prefixHTML, suffixHTML)
            highlighter = Highlighter(simpleHTMLFormatter, QueryScorer(query))
            highLightText = highlighter.getBestFragment(analyzer, 'text', recover_sentence(doc.get('text')))
            print(hit.score, hit.doc, hit.toString())
            print(highLightText)
            text = doc.get("text")
            print(text)
            self.hits.append(highLightText)
            
        print('search over')
        reader.close()
        return self.hits

    def search_phrase(self):
        self.hits = []

    def recover_sentence(self, terms):
        sentence = ''
        terms = terms.split(' ')
        for term in terms:
            term = term.split('\\')[0]
            sentence += term
        
        return sentence



