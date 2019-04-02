import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn import datasets
from sklearn.metrics import mean_squared_error
import pickle
from sklearn.model_selection import train_test_split

from sklearn import ensemble

X = pickle.load(open("X.pickle", "rb"))
y = pickle.load(open("y.pickle", "rb"))

def train_model(X, y):

	params = {'n_estimators': 1000, 'max_depth': 6, 'min_samples_split': 2, 'min_samples_leaf': 3,
	'max_features': 1.0, 'learning_rate': 0.01, 'loss': 'ls', 'validation_fraction': .2, 'verbose': True}

	model = ensemble.GradientBoostingRegressor(**params)

	model.fit(X, y)

	pickle_out = open("models/modelv2.sav", "wb")
	pickle.dump(model, pickle_out)
	pickle_out.close()

train_model(X, y)