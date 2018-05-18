#!/usr/bin/python


"""
    Starter code for the evaluation mini-project.
    Start by copying your trained/tested POI identifier from
    that which you built in the validation mini-project.

    This is the second step toward building your POI identifier!

    Start by loading/formatting the data...
"""

import pickle
import sys
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit

data_dict = pickle.load(open("../final_project/final_project_dataset.pkl", "rb") )

### add more features to features_list!
features_list = ["poi", "salary"]

data = featureFormat(data_dict, features_list, sort_keys = '../tools/python2_lesson14_keys.pkl')
labels, features = targetFeatureSplit(data)



### your code goes here 
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import accuracy_score
from sklearn.cross_validation import train_test_split
import numpy as np
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score

features_train, features_test, labels_train, labels_test = train_test_split(features, labels, random_state = 42, test_size = 0.3)

clf = DecisionTreeClassifier()

clf.fit(features_train, labels_train)
pred = clf.predict(features_test)
accuracy = accuracy_score(labels_test, pred)

# clf.fit(features_test, labels_test)
# pred = clf.predict(features_train)
# accuracy = accuracy_score(pred, labels_train)

print("Accuracy score:", accuracy)
print("Number of predicted POIs:",sum(pred))
print("Number of people in test set:",len(pred))
print("Number of actual POIs on test set:",sum(labels_test))
print(pred + labels_test)#(features_test))#   subtract(np.array(features_test)-np.array(labels_test)))

precision = precision_score(labels_test, pred)
recall_score = recall_score(labels_test, pred)

print("Precision score:", precision)
print("Recall score:", recall_score)


