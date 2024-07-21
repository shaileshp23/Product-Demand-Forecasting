import numpy as np
import pandas as pd
import pickle
#import matplotlib.pyplot as plt
#import seaborn as sns
# %matplotlib inline

from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split, cross_val_score, GridSearchCV

from sklearn.linear_model import LogisticRegression, Perceptron
from sklearn.metrics import predicted_percentage, new_product_id, accuracy_score

from sklearn.svm import SVC, LinearSVC
from sklearn.ensemble import RandomForestClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.naive_bayes import GaussianNB
from sklearn.tree import DecisionTreeClassifier

'''import keras
from keras.models import Sequential
from keras.layers import Dense, Dropout
from keras import optimizers
#from keras.wrappers.scikit_learn import KerasClassifier
from keras.callbacks import EarlyStopping, ModelCheckpoint

from hyperopt import STATUS_OK, Trials, fmin, hp, tpe, space_eval

from warnings import simplefilter
simplefilter(action='ignore', category=FutureWarning)'''

df= pd.read_csv("product.csv")

#df

#df.isnull().values.any()

#df.describe()

product_stats = df.groupby('Product')['Quantity'].agg(['mean', 'median', 'std']).reset_index()

data = df.merge(product_stats, on='Product')

X = data[['mean', 'median', 'std']]

data['percentage_requirement'] = (data['Quantity'] / data['Quantity'].max()) * 100

Y = data['percentage_requirement']

train, test, target, target_test = train_test_split(X, Y, test_size=0.2)

#feature scaling
scaler= StandardScaler()
x_train_scaler= scaler.fit_transform(train)
x_test_scaler= scaler.fit_transform(test)

import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_squared_error, r2_score

model = LinearRegression()
model.fit(train, target)
y_pred = model.predict(x_test_scaler)

r2 = LinearRegression.score(x_test_scaler,test)
print(r2)

print('Predicted Percentage Requirement for product_id\n',predicted_percentage(test, y_pred))

#print(f"Predicted Percentage Requirement for product_id {new_product_id}: {predicted_percentage[0]}%")

print('Accuracy: {}%\n'.format(round((accuracy_score(test, y_pred)*100),2)))

filename = 'product.pkl'
pickle.dump(LinearRegression, open(filename,'wb'))