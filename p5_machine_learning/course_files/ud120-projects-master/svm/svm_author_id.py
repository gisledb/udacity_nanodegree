#!/usr/bin/python

""" 
    This is the code to accompany the Lesson 2 (SVM) mini-project.

    Use a SVM to identify emails from the Enron corpus by their authors:    
    Sara has label 0
    Chris has label 1
"""
    
import sys
from time import time
sys.path.append("../tools/")
from email_preprocess import preprocess


### features_train and features_test are the features for the training
### and testing datasets, respectively
### labels_train and labels_test are the corresponding item labels
features_train, features_test, labels_train, labels_test = preprocess()

#########################################################
### your code goes here ###

from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
import numpy as np

t0 = time()

# clf = SVC(kernel='linear')
clf = SVC(kernel='rbf', C = 10000)

# features_train = features_train[:int(len(features_train)/100)] 
# labels_train = labels_train[:int(len(labels_train)/100)] 

clf.fit(features_train, labels_train)

print("Training time: {0}".format(round(time()-t0, 3)))

t1 = time()

pred = clf.predict(features_test)

print("Prediction time: {0}".format(round(time()-t1, 3)))

print(accuracy_score(pred, labels_test))

predict_3 = [10, 26, 50]

for i in predict_3:
	print("Predicton for #{0}:".format(i), pred[i])

count_chris = np.count_nonzero(pred == 1)

print("Count of Chris predictions:", count_chris)
#########################################################


