#!/usr/bin/python

import pickle
import sys
import matplotlib.pyplot
sys.path.append("../tools/")
from feature_format import featureFormat, targetFeatureSplit


### read in data dictionary, convert to numpy array
data_dict = pickle.load( open("../final_project/final_project_dataset.pkl", "rb") )
features = ["salary", "bonus"]
data = featureFormat(data_dict, features)

def salary_bonus_plot():
    for point in data:
        salary = point[0]
        bonus = point[1]
        matplotlib.pyplot.scatter( salary, bonus )

    matplotlib.pyplot.xlabel("salary")
    matplotlib.pyplot.ylabel("bonus")
    matplotlib.pyplot.show()

### your code below

# Importing pandas and numpy for easier analysis
import numpy as np
import pandas as pd


df = pd.DataFrame(data_dict).transpose()
# Replacing string Nan with np.nan
df = df.replace('NaN', np.nan)

df.sort_values('bonus', ascending=False).head(5)

data_dict.pop('TOTAL')

data = featureFormat(data_dict, features)

salary_bonus_plot()