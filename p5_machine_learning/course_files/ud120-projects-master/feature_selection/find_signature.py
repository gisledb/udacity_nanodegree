#!/usr/bin/python

import pickle
import numpy
numpy.random.seed(42)


### The words (features) and authors (labels), already largely processed.
### These files should have been created from the previous (Lesson 10)
### mini-project.
words_file = "../text_learning/your_word_data.pkl" 
authors_file = "../text_learning/your_email_authors.pkl"
word_data = pickle.load( open(words_file, "rb"))
authors = pickle.load( open(authors_file, "rb") )



### test_size is the percentage of events assigned to the test set (the
### remainder go into training)
### feature matrices changed to dense representations for compatibility with
### classifier functions in versions 0.15.2 and earlier
from sklearn import cross_validation
features_train, features_test, labels_train, labels_test = cross_validation.train_test_split(word_data, authors, test_size=0.1, random_state=42)

from sklearn.feature_extraction.text import TfidfVectorizer
vectorizer = TfidfVectorizer(sublinear_tf=True, max_df=0.5,
                             stop_words='english')
features_train = vectorizer.fit_transform(features_train)
features_test  = vectorizer.transform(features_test)


### a classic way to overfit is to use a small number
### of data points and a large number of features;
### train on only 150 events to put ourselves in this regime
features_train = features_train[:150]
labels_train   = labels_train[:150]



### your code goes here

from sklearn import tree
from sklearn.metrics import accuracy_score


# Setting up classifier
clf = tree.DecisionTreeClassifier()

# Training classifier
clf.fit(features_train, labels_train)

# Prediction
pred = clf.predict(features_test)

# Getting accuracy score
score = accuracy_score(pred, labels_test)
print("Accuracy score:", score)

# Finding the score and index of feature with the highest importance score
max_importance = max(clf.feature_importances_)
max_index = numpy.where(clf.feature_importances_ == max_importance)[0][0]
print("Max index:", max_index, "Max feature importance:",max_importance)

# Printing out the most important feature (word)
print(vectorizer.get_feature_names()[max_index])

# vectorize_text.py has been updated. Looking for any remaining outliers (defined as importance>2)
count = 0
outliers = dict()
# outlier_imp = list()
# outlier_index = index()

for importance in clf.feature_importances_:

    if importance > 0.2:

        # outlier_imp.append(importance)
        # outlier_index.append(count)
        outliers[count] = importance
    
    count += 1

count = 0

if len(outliers) == 0:
    print("No outliers!")
else:
    for key,value in outliers.items():
        print("Outlier word:",vectorizer.get_feature_names()[key])
        print("Feature importance:", value)
        print("-----------")