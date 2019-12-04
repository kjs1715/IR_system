import sys
import os
import time
import lucene
from pathlib import Path
from java.io import File
from java.nio.file import Paths
from org.apache.lucene.store import SimpleFSDirectory, FSDirectory
from org.apache.lucene.document import Document, Field, FieldType
from org.apache.lucene.analysis.cjk import CJKAnalyzer
from org.apache.lucene.analysis.cn.smart import SmartChineseAnalyzer
from org.apache.lucene.analysis.standard import StandardAnalyzer
from org.apache.lucene.index import IndexWriter, IndexWriterConfig, IndexOptions, IndexReader, DirectoryReader
from org.apache.lucene.util import Version
from org.apache.lucene.queryparser.classic import QueryParser
from org.apache.lucene.search import IndexSearcher, Query, PhraseQuery

CORPUS_DIR = '/Users/kim/Desktop/corpus/'
RAW_CORPUS_DIR = '/Users/kim/Desktop/raw_corpus/'
SUFFIX = '_raw'
LINE_LIMIT = 300000

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
                term = term.split('\\')[0]
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

    def recover_sentence(self, terms):
        sentence = ''
        terms = terms.split(' ')
        for term in terms:
            term = term.split('\\')[0]
            sentence += term
        
        return sentence

'''
    Indexing all corpus in Chinese with lucene
'''
class Indexer():
    def __init__(self, path):
        p = Path(path)
        if not p.is_dir():
            os.mkdir(path)
        storeDir = SimpleFSDirectory(Paths.get(path))
        # analyzer = CJKAnalyzer()
        analyzer = SmartChineseAnalyzer()
        config = IndexWriterConfig(analyzer)
        index_writer = IndexWriter(storeDir, config)
        self.IndexDocs(index_writer)

    def IndexDocs(self, writer):
        line_count = 0
        # for fileName in ['2_1','2_10','2_3']:
        with open('/Users/kim/Desktop/corpus/rmrb2_10_raw.txt', 'r') as f:
            f1 = open('/Users/kim/Desktop/corpus/rmrb2_10.txt', 'r')
            start = time.time()
            line =  f1.readline()
            raw_line = f.readline()
            while line:
                line_count += 1

                # field(raw)
                fieldtype1 = FieldType()
                fieldtype1.setIndexOptions(IndexOptions.DOCS_AND_FREQS_AND_POSITIONS)
                fieldtype1.setStored(True)
                # fieldtype1.setTokenized(True)

                # field(result)
                fieldtype2 = FieldType()
                fieldtype2.setStored(True)

                doc = Document()
                doc.add(Field('raw_text', raw_line, fieldtype1))
                doc.add(Field('text', line, fieldtype2))

                writer.addDocument(doc)
                # if line_count % LINE_LIMIT == 0:
                #     break
                line = f1.readline()
                raw_line = f.readline()

            writer.close()
            print('indexing completed')
            f1.close()
            end = time.time()
            print('time: %f' % (end - start))
            print(line_count)
            line_count = 0
        f.close()

        