#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

import pandas as pd
import numpy as np

from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score

from sklearn.cross_validation import train_test_split

### Task 1: Select what features you'll use.
### features_list is a list of strings, each of which is a feature name.
### The first feature must be "poi".

### Load the dictionary containing the dataset
with open("final_project_dataset.pkl", "rb") as data_file:
    data_dict = pickle.load(data_file)

# Loading the data into a Pandas dataframe
df_people = pd.DataFrame(data_dict).transpose()
# Setting proper NaN values
df_people.replace(to_replace='NaN', value=np.nan, inplace=True)
# Making list of features to use
features_to_use = ['bonus', 'deferred_income', 'from_poi_to_this_person', 
                   'from_this_person_to_poi', 'long_term_incentive', 'restricted_stock', 
                   'salary', 'shared_receipt_with_poi', 'total_stock_value']

### Task 2: Remove outliers
# Removing outlier: row with aggregated total values
df_people = df_people.drop('TOTAL')

### Task 3: Create new feature(s)
# Creating new features

# function for creating fraction/ratio features
def fraction_feature(feat_a, feat_b):
    return np.round(df_people[feat_a].divide(
        df_people[feat_b], axis='index').fillna(0),4)

# new feature for fraction of messages sent from person to a poi
df_people['fraction_to_poi'] = fraction_feature('from_this_person_to_poi', 'from_messages')
# new feature for fraction of messages sent to a person from a poi
df_people['fraction_from_poi'] = fraction_feature('from_poi_to_this_person', 'to_messages')
# new feature for fraction of messages sent to a person from a poi
df_people['fraction_shared_with_poi'] = fraction_feature('shared_receipt_with_poi', 'to_messages')
# new feature for bonus to salary ratio
df_people['bonus_to_salary_ratio'] = fraction_feature('bonus', 'salary')

new_features = ['fraction_to_poi', 'fraction_from_poi', 
                'fraction_shared_with_poi', 'bonus_to_salary_ratio']

features_list = ['poi'] + features_to_use + new_features

### Store to my_dataset for easy export below.
my_dataset = df_people.fillna('NaN').to_dict(orient='index')

### Extract features and labels from dataset for local testing
data = featureFormat(my_dataset, features_list, sort_keys = True)
labels, features = targetFeatureSplit(data)

features_train, features_test, labels_train, labels_test = \
train_test_split(features, labels, random_state = 42, test_size = 0.3)

### Task 4: Try a varity of classifiers
### Please name your classifier clf for easy export below.
### Note that if you want to do PCA or other multi-stage operations,
### you'll need to use Pipelines. For more info:
### http://scikit-learn.org/stable/modules/pipeline.html

def report_scores():
    
    print("Number of predicted POIs:",sum(pred))
    print("Number of people in test set:",len(pred))
    print("Number of actual POIs on test set:",sum(labels_test))
    
    accuracy = accuracy_score(labels_test, pred)
    precision = precision_score(labels_test, pred)
    recall = recall_score(labels_test, pred)
    
    print("Accuracy score:", round(accuracy, 4))
    print("Precision score:", round(precision, 4))
    print("Recall score:", round(recall, 4))

from sklearn.naive_bayes import GaussianNB

clf = GaussianNB()

clf.fit(features_train, labels_train)

pred = clf.predict(features_test)

# report_scores()
### Task 5: Tune your classifier to achieve better than .3 precision and recall 
### using our testing script. Check the tester.py script in the final project
### folder for details on the evaluation method, especially the test_classifier
### function. Because of the small size of the dataset, the script uses
### stratified shuffle split cross validation. For more info: 
### http://scikit-learn.org/stable/modules/generated/sklearn.cross_validation.StratifiedShuffleSplit.html

# # Example starting point. Try investigating other evaluation techniques!
# from sklearn.cross_validation import train_test_split
# features_train, features_test, labels_train, labels_test = \
#     train_test_split(features, labels, test_size=0.3, random_state=42)

from sklearn.ensemble import RandomForestClassifier

clf = RandomForestClassifier(n_estimators = 500, max_leaf_nodes = 16, max_depth=4)

clf.fit(features_train, labels_train)
pred = clf.predict(features_test)
report_scores()

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)