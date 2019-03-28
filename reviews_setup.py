#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Feb 23 19:52:03 2019

@author: michaelmerani
"""

import os
import pandas as pd
import numpy as np

neg_reviews = []

for filename in os.listdir('/Users/michaelmerani/Downloads/aclImdb/test/neg'):
    if filename.endswith('.txt'):
        with open(os.path.join('/Users/michaelmerani/Downloads/aclImdb/test/neg',filename)) as f:
            content = f.read()
            neg_reviews.append(content)
            
pos_reviews = []

for filename in os.listdir('/Users/michaelmerani/Downloads/aclImdb/test/pos'):
    if filename.endswith('.txt'):
        with open(os.path.join('/Users/michaelmerani/Downloads/aclImdb/test/pos',filename)) as f:
            content = f.read()
            pos_reviews.append(content)
            
df1 = pd.DataFrame(neg_reviews, columns=['Reviews'])
df1['Sentiment'] = 0

df2 = pd.DataFrame(pos_reviews, columns=['Reviews'])
df2['Sentiment'] = 1

reviews = df1.append(df2, ignore_index=True)

reviews.to_csv(r'/Users/michaelmerani/Desktop/youtube comments sentiment program/movie_reviews.csv')
