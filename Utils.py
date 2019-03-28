#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 13:13:12 2019

@author: michaelmerani
"""

import numpy as np
import string
import re
import nltk
from nltk.corpus import stopwords
from nltk.stem.wordnet import WordNetLemmatizer
from scipy.sparse import coo_matrix

#nltk.download('wordnet')
#nltk.download('stopwords')

def preprocess(column):
    
    new_column = []
    
    for review in column:
        #remove non-ascii unicode
        review = ''.join([x for x in review if ord(x) < 128])
        #remove uppercase
        review = review.lower()
        #remove punctuation
        punct_exclude = set(string.punctuation)
        review = ''.join(char for char in review if char not in punct_exclude)
        #remove numbers
        review = re.sub('\d+','',review)
        #strip extra whitespace
        review = ' '.join(review.split())
        #remove stopwords
        stops = stopwords.words('english')
        word_list = review.split(' ')
        text_words = [word for word in word_list if word not in stops]
        review = ' '.join(text_words)
        # stem words
        lmtzr = WordNetLemmatizer()
        word_list = review.split(' ')
        stemmed_words = [lmtzr.lemmatize(word) for word in word_list]
        review = ' '.join(stemmed_words)
        
        new_column.append(review)
        
    return new_column
        
def tdm(reviews):
    # create list for use later
    review_data = reviews.values.tolist()
    
    #create a document storage matrix
    clean_reviews = reviews['Reviews']
    docs = {}
    labels = []
    
    for ix, row in enumerate(clean_reviews):
        labels = review_data[ix][0]
        docs[ix] = row.split(' ')
        
    # keep track of unqiue words
    num_nonzero = 0
    vocab = set()
    
    for word_list in docs.values():
        unique_terms = set(word_list)
        vocab.update(unique_terms)
        num_nonzero += len(unique_terms)
    doc_key_list = list(docs.keys())
    
    #convert into numpy array
    doc_key_list = np.array(doc_key_list)
    vocab = np.array(list(vocab))
    
    #map indices to the matrix so we can look them up later
    vocab_sorter = np.argsort(vocab)
    
    # initialize sparse matrix
    num_docs = len(doc_key_list)
    vocab_size = len(vocab)
    
    data = np.empty(num_nonzero, dtype=np.intc)
    rows = np.empty(num_nonzero, dtype=np.intc)
    cols = np.empty(num_nonzero, dtype=np.intc)
    
    #go through all documents with their terms
    ix = 0
    
    for doc_key, terms in docs.items():
        term_indices = vocab_sorter[np.searchsorted(vocab, terms, sorter=vocab_sorter)]
        
        #count the unique terms of the document and get their vocab indicies
        uniq_indices, counts = np.unique(term_indices,return_counts=True)
        n_vals = len(uniq_indices)
        ix_end = ix + n_vals
        
        data[ix:ix_end] = counts
        cols[ix:ix_end] = uniq_indices
        doc_ix = np.where(doc_key_list == doc_key)
        rows[ix:ix_end] = np.repeat(doc_ix, n_vals)
        
        ix = ix_end
        
    #create the sparse matrix
    doc_term_matrix = coo_matrix((data,(rows,cols)),shape=(num_docs,vocab_size),dtype=np.intc)
    return doc_term_matrix
    
def word_count(matrix):
    word_counts = matrix.sum(axis=0)
    cutoff = 15
    word_count_list = word_counts.tolist()[0]
    col_cutoff = [ix for ix, count in enumerate(word_count_list) if count>cutoff]
    
    return len(col_cutoff)
    

    
    