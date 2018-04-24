#!/usr/bin/python

""" 
    This is the code to accompany the Lesson 3 (decision tree) mini-project.

    Use a Decision Tree to identify emails from the Enron corpus by author:    
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
print(len(features_train))
# Importing libraries
from sklearn import tree
from sklearn.metrics import accuracy_score

# Defining clarisifer algorithm including parameter tuning
clf = tree.DecisionTreeClassifier(min_samples_split=40)

# Timing algorithm
t0 = time()

# Training classifier
# clf.fit(features_train[:1000], labels_train[:1000])
clf.fit(features_train, labels_train)

print("Processing time: {0}".format( round( time() - t0, 3) ) )

# Predicting outcome of test dataset
pred = clf.predict(features_test)

# Accuracy score
accuracy = accuracy_score(pred, labels_test)

print("Accuracy:", accuracy)

# Number of features
print("Number of features:", len(features_train[0]))
#########################################################


