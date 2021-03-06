# -*- coding: utf-8 -*-
"""
Automatically generated by Colaboratory.

Original file is located at
    https://colab.research.google.com/drive/1lhx7fFUpUov6NJt4dFeHQp0T4h0YGTJL

The SMS Spam Collection is a set of SMS tagged messages that have been collected for SMS Spam research. It contains one set of SMS messages in English of 5,574 messages, tagged acording being ham (legitimate) or spam. 

The aim of this project is to apply TFIDFVectorizer and compare performance of different algorithms.

I will be applying three methods to the data set and compare the results.
1. Random Forest
2. Logistic Regression
3. Naive Bayes
"""

#import libraries
# %matplotlib inline
from __future__ import print_function

from sklearn.cross_validation import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
import seaborn as sn

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt

import os
import re
from os import listdir
from os.path import isfile, join
from collections import Counter

def clean_text(texts):
        '''
        Utility function to clean text by removing links, special characters
        '''
        return ' '.join(re.sub("(@[A-Za-z0-9]+)|([^0-9A-Za-z \t])|(\w+:\/\/\S+)", " ", texts).split())

#upload file to google colab --- rerun this and upload file to run
from google.colab import files

uploaded = files.upload()

for fn in uploaded.keys():
  print('User uploaded file "{name}" with length {length} bytes'.format(
      name=fn, length=len(uploaded[fn])))

sms_data = pd.read_csv("spam.csv", encoding='cp437')

#removing last 3 column
sms_data.drop('Unnamed: 2',axis= 1,inplace=True)
sms_data.drop('Unnamed: 3',axis= 1,inplace=True)
sms_data.drop('Unnamed: 4',axis= 1,inplace=True)
sms_data.rename(index=str, columns={"v1": "indicator", "v2": "text"},inplace=True)

sms_data.head()

"""## Transformation of indicator and text

1. Encode indicators to {'ham':0} {'spam':1}
2. Removes digit and special characters from text
"""

le=LabelEncoder()
labels=le.fit_transform(sms_data['indicator'])

texts = sms_data['text']
clean_texts = []
for text in texts:
    result = ''.join([i for i in text if not i.isdigit()])
    result = clean_text(result)
    clean_texts.append(result)

nb_of_spam = int(np.mean(labels)*len(labels))
nb_of_non_spam = int(len(labels) - nb_of_spam)
print("There are",nb_of_spam,"spam texts and",nb_of_non_spam,"non-spam texts.")

"""## Transform text data -> matrices using TFIDF_Vectorizer

TFIDF_vectorizer transforms text to feature vectors that can be used as input to estimator.
This is done by converting each word(token) to feature index in a matrix, creating a bag of words.
Then normalisation in accordance to the length of sentence and document.
"""

no_features = 10000
tfidf_vectorizer = TfidfVectorizer(max_df=0.5, min_df=2, max_features=no_features, stop_words='english')
tfidf = tfidf_vectorizer.fit_transform(clean_texts)
tfidf_feature_names = tfidf_vectorizer.get_feature_names()
pd.DataFrame(tfidf.toarray(), columns=tfidf_vectorizer.get_feature_names())

#shape of matrix: (5572, 3554)
pd.DataFrame(tfidf.toarray(), columns=tfidf_vectorizer.get_feature_names()).shape

#Splitting data sets for cross-validation
X_train, X_test, y_train, y_test = train_test_split(tfidf.toarray(), labels, test_size = 0.20)

"""## Algorithm: Random Forest

Properties:
- Bootstrap estimation = True
- criterion = entropy
- number of trees = 50
- First, performance will be estimated using cross-validation. Results will be compared to Out of Bag estimates.
"""

#import RF library
from sklearn.ensemble import RandomForestClassifier
from sklearn.metrics import accuracy_score,precision_score,recall_score,f1_score,roc_curve, auc,confusion_matrix
from sklearn import metrics

clf=RandomForestClassifier(n_estimators=50,criterion='entropy',bootstrap=True)
clf.fit(X_train,y_train)
predRF=clf.predict(X_test)

print('Accuracy score: {}'.format(accuracy_score(y_test, predRF)))
print('Precision score: {}'.format(precision_score(y_test, predRF)))
print('Recall score: {}'.format(recall_score(y_test, predRF)))
print('F1 score: {}'.format(f1_score(y_test, predRF)))

#plotting ROC curve
prob_predRF=clf.predict_proba(X_test)

fpr = dict()
tpr = dict()
roc_auc = dict()
n_classes = 2
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test, prob_predRF[:,i])
    roc_auc[i] = auc(fpr[i], tpr[i])
    

plt.figure()
lw = 2
plt.plot(fpr[1], tpr[1], color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[1])
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Specificity')
plt.ylabel('Sensitivity')
plt.title('Receiver operating characteristic Curve')
plt.legend(loc="lower right")
plt.show()

conf_arr = confusion_matrix(y_test, predRF)

df_cm = pd.DataFrame(conf_arr, index = ['Ham','Spam'],
                  columns = ['Ham','Spam'])
plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True,cbar_kws={"orientation": "horizontal"})
plt.xlabel("Predicted Label")
plt.ylabel("True Label")

#comparing results with Out of Bag Estimates
clf=RandomForestClassifier(n_estimators=50,criterion='entropy',bootstrap=True,oob_score=True)
clf.fit(tfidf.toarray(),labels)
clf.oob_score_

"""## Algorithm: Logistic Regression"""

from sklearn.linear_model import LogisticRegression

clf = LogisticRegression()
clf.fit(X_train,y_train)
predLR = clf.predict(X_test)

print('Accuracy score: {}'.format(accuracy_score(y_test, predLR)))
print('Precision score: {}'.format(precision_score(y_test, predLR)))
print('Recall score: {}'.format(recall_score(y_test, predLR)))
print('F1 score: {}'.format(f1_score(y_test, predLR)))

#plotting ROC curve
prob_predLR=clf.predict_proba(X_test)

fpr = dict()
tpr = dict()
roc_auc = dict()
n_classes = 2
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test, prob_predLR[:,i])
    roc_auc[i] = auc(fpr[i], tpr[i])
    

plt.figure()
lw = 2
plt.plot(fpr[1], tpr[1], color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[1])
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Specificity')
plt.ylabel('Sensitivity')
plt.title('Receiver operating characteristic Curve')
plt.legend(loc="lower right")
plt.show()

conf_arr = confusion_matrix(y_test, predLR)

df_cm = pd.DataFrame(conf_arr, index = ['Ham','Spam'],
                  columns = ['Ham','Spam'])
plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True,cbar_kws={"orientation": "horizontal"})
plt.xlabel("Predicted Label")
plt.ylabel("True Label")

"""## Algorithm: Naive Bayes"""

from sklearn.naive_bayes import GaussianNB
clf = GaussianNB()
clf.fit(X_train,y_train)
predNB = clf.predict(X_test)

print('Accuracy score: {}'.format(accuracy_score(y_test, predNB)))
print('Precision score: {}'.format(precision_score(y_test, predNB)))
print('Recall score: {}'.format(recall_score(y_test, predNB)))
print('F1 score: {}'.format(f1_score(y_test, predNB)))

#plotting ROC curve
prob_predNB=clf.predict_proba(X_test)

fpr = dict()
tpr = dict()
roc_auc = dict()
n_classes = 2
for i in range(n_classes):
    fpr[i], tpr[i], _ = roc_curve(y_test, prob_predNB[:,i])
    roc_auc[i] = auc(fpr[i], tpr[i])
    

plt.figure()
lw = 2
plt.plot(fpr[1], tpr[1], color='darkorange',
         lw=lw, label='ROC curve (area = %0.2f)' % roc_auc[1])
plt.plot([0, 1], [0, 1], color='navy', lw=lw, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel('Specificity')
plt.ylabel('Sensitivity')
plt.title('Receiver operating characteristic Curve')
plt.legend(loc="lower right")
plt.show()

conf_arr = confusion_matrix(y_test, predNB)

df_cm = pd.DataFrame(conf_arr, index = ['Ham','Spam'],
                  columns = ['Ham','Spam'])
plt.figure(figsize = (10,7))
sn.heatmap(df_cm, annot=True,cbar_kws={"orientation": "horizontal"})
plt.xlabel("Predicted Label")
plt.ylabel("True Label")

"""## Results:

Due to the high dimension sparse matrix, it is unlikely to be linearly separable.
Thus, Random Forest is expected to be the best performing model and our findings have confirmed this hypothesis.
"""
