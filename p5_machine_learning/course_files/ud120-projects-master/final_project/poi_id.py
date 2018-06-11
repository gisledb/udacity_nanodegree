#!/usr/bin/python

import sys
import pickle
sys.path.append("../tools/")

from feature_format import featureFormat, targetFeatureSplit
from tester import dump_classifier_and_data

import pandas as pd
import numpy as np

from sklearn.ensemble import RandomForestClassifier

from sklearn.metrics import accuracy_score
from sklearn.metrics import recall_score
from sklearn.metrics import precision_score
from sklearn.metrics import classification_report

from sklearn.preprocessing import Normalizer
from sklearn.cross_validation import train_test_split

from imblearn.over_sampling import SMOTE
from imblearn.pipeline import Pipeline



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

# Splitting the dataset into training and test sets
features_train, features_test, labels_train, labels_test = \
train_test_split(features, labels, random_state = 42, test_size = 0.3)


# Setting up the pipeline with a fine-tuned random forest classifier

clf = Pipeline(steps = [
    ('oversample', SMOTE(k=None, k_neighbors=5, kind='regular', m=None, m_neighbors=10, 
    n_jobs=1, out_step=0.5, random_state=42, ratio='auto', svm_estimator=None)),
    ('scaler', Normalizer()),
    ('clf', RandomForestClassifier(bootstrap=True, class_weight=None, criterion='entropy',
             max_depth=5, max_features=5, max_leaf_nodes=None,
             min_impurity_decrease=0.0, min_impurity_split=None,
             min_samples_leaf=10, min_samples_split=5,
             min_weight_fraction_leaf=0.0, n_estimators=100, n_jobs=-1,
             oob_score=False, random_state=None, verbose=0,
             warm_start=False))
])

clf.fit(features_train, labels_train)

pred = clf.predict(features_test)

print(classification_report(labels_test, pred))

### Task 6: Dump your classifier, dataset, and features_list so anyone can
### check your results. You do not need to change anything below, but make sure
### that the version of poi_id.py that you submit can be run on its own and
### generates the necessary .pkl files for validating your results.

dump_classifier_and_data(clf, my_dataset, features_list)