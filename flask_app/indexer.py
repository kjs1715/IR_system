import sys
import os
import time
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


LINE_LIMIT = 300000

'''
    Combine seperated terms into sentences
'''
def combine_sentences(fileName):
    line_count = 0
    sentence = ''

    with open(fileName, 'r') as f:
        line = f.readline()
        while(line):
            line_count += 1
            terms = line.split(' ')
            for term in terms:
                term = term.split('\\')[0]
                sentence += term
            sentence += '\n'
            if line_count % LINE_LIMIT == 0:
                with open('/Users/kim/Desktop/corpus/rmrb2_10_raw.txt', 'w') as f1:
                    f1.write(sentence)
                break
            line = f.readline()
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
        f.close()