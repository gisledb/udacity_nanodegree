#!/usr/bin/python

import matplotlib.pyplot as plt
from prep_terrain_data import makeTerrainData
from class_vis import prettyPicture

features_train, labels_train, features_test, labels_test = makeTerrainData()


### the training data (features_train, labels_train) have both "fast" and "slow"
### points mixed together--separate them so we can give them different colors
### in the scatterplot and identify them visually
grade_fast = [features_train[ii][0] for ii in range(0, len(features_train)) if labels_train[ii]==0]
bumpy_fast = [features_train[ii][1] for ii in range(0, len(features_train)) if labels_train[ii]==0]
grade_slow = [features_train[ii][0] for ii in range(0, len(features_train)) if labels_train[ii]==1]
bumpy_slow = [features_train[ii][1] for ii in range(0, len(features_train)) if labels_train[ii]==1]

print("Starting")
#### initial visualization
# plt.xlim(0.0, 1.0)
# print(1)
# plt.ylim(0.0, 1.0)
# print(2)
# plt.scatter(bumpy_fast, grade_fast, color = "b", label="fast")
# print(3)
# plt.scatter(grade_slow, bumpy_slow, color = "r", label="slow")
# print(4)
# plt.legend()
# print(5)
# plt.xlabel("bumpiness")
# print(6)
# plt.ylabel("grade")
# print(7)
# plt.show()
# print(8)
################################################################################

### your code here!  name your classifier object clf if you want the 
### visualization code (prettyPicture) to show you the decision boundary

print("figured")

from sklearn import ensemble 
from sklearn.metrics import accuracy_score
from time import time

#timing defining
t0 = time()

# Setting up random forest classifier



# My SVC
from sklearn.svm import SVC
clf = SVC(kernel='rbf', C = 20000)

clf = ensemble.RandomForestClassifier(n_estimators = 500, max_leaf_nodes = 16, max_depth=4,#                                       min_samples_split=20, n_jobs = -1, criterion='entropy')

print("Defining time: {0}".format( round( time() - t0, 3) ) )

# Timing algorithm
t1 = time()

# Training classifier
# clf.fit(features_train[:1000], labels_train[:1000])
clf.fit(features_train, labels_train)

print("Training time: {0}".format( round( time() - t1, 3) ) )

# Predicting outcome of test dataset
pred = clf.predict(features_test)

# The accuracy of prediction on test dataset
accuracy = accuracy_score(pred, labels_test)

print("Accuracy:", accuracy)

# Number of features
print("Number of features:", len(features_train[0]))


try:
    prettyPicture(clf, features_test, labels_test)
except NameError:
    pass
