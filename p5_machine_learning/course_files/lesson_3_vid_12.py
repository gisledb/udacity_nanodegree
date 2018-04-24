
# coding: utf-8

# In[1]:


import sys
from class_vis import prettyPicture
from prep_terrain_data import makeTerrainData

import matplotlib.pyplot as plt
import copy
import numpy as np
import pylab as pl

from sklearn.metrics import accuracy_score
from sklearn.svm import SVC


# In[2]:


features_train, labels_train, features_test, labels_test = makeTerrainData()


# In[3]:


### we handle the (import statement and) SVC creation for you here

clf = SVC(kernel="linear")


# In[5]:


#### now your job is to fit the classifier
#### using the training features/labels, and to
#### make a set of predictions on the test data

clf.fit(features_train, labels_train)


# In[11]:


#### store your predictions in a list named pred

pred = clf.predict(features_test)


# In[12]:


pred


# In[10]:


acc = accuracy_score(pred, labels_test)

def submitAccuracy():
    return acc


# In[14]:


submitAccuracy()

