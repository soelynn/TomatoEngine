from common import load_non_preprocessed_data, load_preprocessed_data, load_preprocessed_2_data,load_data
from classifiers import ClassifierOvOFeaturesReduction
from nltk.corpus import wordnet
from nltk.tokenize import word_tokenize
from sklearn.cross_validation import StratifiedKFold
from sklearn.ensemble import AdaBoostClassifier
from sklearn.ensemble import ExtraTreesClassifier
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.ensemble import RandomForestClassifier
from sklearn.ensemble import VotingClassifier
from sklearn.externals import joblib
from sklearn.feature_extraction.text import CountVectorizer, TfidfVectorizer
from sklearn.feature_extraction.text import TfidfTransformer
from sklearn.feature_selection import SelectKBest
from sklearn.feature_selection import chi2
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.metrics import accuracy_score
from sklearn.metrics import confusion_matrix
from sklearn.multiclass import fit_ovo
from sklearn.naive_bayes import GaussianNB
from sklearn.naive_bayes import BernoulliNB
from sklearn.neighbors import KNeighborsClassifier
from sklearn.pipeline import Pipeline
from sklearn.grid_search import GridSearchCV
from sklearn.svm import LinearSVC
from sklearn.svm import SVC
from sklearn.tree import DecisionTreeClassifier
from sklearn.metrics import f1_score
from sklearn.metrics import make_scorer
from preprocess import preprocessMain

import nltk
import numpy
import os
import csv

import warnings
warnings.filterwarnings("ignore", category=DeprecationWarning)

valid_classifiers = {
    "adaboosting": AdaBoostClassifier,
    "decisiontree": DecisionTreeClassifier,
    "extratree": ExtraTreesClassifier,
    "gradientboosting": GradientBoostingClassifier,
    "knn": KNeighborsClassifier,
    "linearsvc": LinearSVC,
    "randomforest": RandomForestClassifier,
    "sgd": SGDClassifier,
    "svc": SVC,
    "voting": VotingClassifier,
    "BernoulliNB": BernoulliNB,
    "GaussianNB": GaussianNB,
}

def main(classifier_name,
         classifier_args=None,
         ngram=2,
         folds=5,
         preprocessed=False,
         preprocess_records = None
         ):

  if preprocess_records:
    X,y = preprocess_records
  elif preprocessed:
    X, y = load_preprocessed_data()
  else:
    X, y = load_non_preprocessed_data()

  # StratifiedKFold makes sure that there's no unfortunate data split
  skf = StratifiedKFold(y, folds)

  ###############################
  # Training and testing models #
  ###############################

  print()
  print('training classifier')
  if classifier_args is None:
    classifier_args = {}
  classifier = valid_classifiers[classifier_name](**classifier_args)

  params = {
            # "tfidf__ngram_range": [(1, 2)],
            # "Classifier__class_weight": [{ 0: 1, 1: 100, 2: 1}, { 0: 1, 1: 1, 2: 1}],
            # "Classifier__C": [.01, .1, 1, 10, 100],
            # "Classifier__kernel": ['rbf', 'linear', 'poly', 'sigmoid'],
            # "Classifier__penalty": ['l1', 'l2', 'elasticnet'],
            # "Classifier__loss" : ['hinge', 'log', 'modified_huber', 'squared_hinge', 'perceptron'],
            # "Classifier__n_neighbors": [3, 5, 7, 11],
            # "Classifier__algorithm": ['auto', 'ball_tree', 'kd_tree', 'brute']
          }
  ml_pipeline = Pipeline([
                    ('tfidf', TfidfVectorizer(sublinear_tf=True, ngram_range=(1,ngram))),
                    # ('Vectorization', CountVectorizer(binary='false')),
                    # ('Feature Refinement', TfidfTransformer(use_idf=False)),
                    # ('Feature Selection', SelectKBest(chi2, 1000)),
                    ('Feature Reduction', ClassifierOvOFeaturesReduction()),
                    ('Classifier', classifier),
                    ])
  # f1_scorer = make_scorer(f1_score)
  gs = GridSearchCV(ml_pipeline, params, cv = folds, verbose=2, n_jobs=-1)
  gs.fit(X, y)

  # print(gs.best_params_)
  print(gs.best_score_)
  print('>>>>>>>>>>')
  # print(gs.grid_scores_)
  return(gs.best_score_)

  

if __name__ == '__main__':
  # classifier_name = "GaussianNB"
  # classifier_args = {}

  classifier_name = "adaboosting"
  classifier_args = {}

  # classifier_name = "BernoulliNB"
  # classifier_args = {}

  # classifier_name = "knn"
  # classifier_args = {}

  # classifier_name = "svc"
  # classifier_args = {'C': 1, 'kernel': 'linear'}

  # classifier_name = "sgd"
  # classifier_args = { 'loss': 'log', 'penalty': 'elasticnet' } 

  # classifier_name = "linearsvc"
  # classifier_args = { 'C': 1 } #{ "class_weight": { 0: 1, 1: 100, 2: 1} }

  # classifier_name = "voting"
  # classifier_args = {
  #   "estimators": [
  #       ('sgd', valid_classifiers['sgd'](loss='log', penalty='elasticnet')),
  #       ('BernoulliNB', valid_classifiers['BernoulliNB']()),
  #       ('knn', valid_classifiers['knn']()),
  #       ('linearsvc', valid_classifiers['linearsvc'](C=0.1)),
  #       ('svc', valid_classifiers['svc'](C=1, kernel='linear')),
  #     ]
  # }

  classifier_names = []
  classifier_argss = []
  # classifier_names = ["GaussianNB", "BernoulliNB", "linearsvc","sgd","extratree","knn", "decisiontree"]
  # classifier_argss = [{} , {},  {"C":1}, {"loss":"log", "penalty":"elasticnet"}, {"n_jobs": -1},{}, {"max_depth": 10}]
  # classifier_argss = [{} , {},  {}, {}, {},{}, {}]
  classifier_names.append(classifier_name)
  classifier_argss.append(classifier_args)

  # preprocessArgs = [[True,False,False],[False,True,False],[False,False,True],[True,True,False],[True,False,True],[False,True,True],[True,True,True]]
  preprocessArgs = [[True,False,False]]
  
  with open('data/results.csv', 'w') as result_file:
    writer = csv.writer(result_file, lineterminator='\n')
    header = [""] + classifier_names
    
    writer.writerow(header)
    for preprocessArg in preprocessArgs:
      basicWord = preprocessArg[0]
      lemmatize = preprocessArg[1]
      stopwords = preprocessArg[2]
      row = []
      row.append("_basic words" + str(preprocessArg[0]) + "_lemmatize" + str(preprocessArg[1]) + "_stop words" + str(preprocessArg[2]))
      # preprocessMain(stopword=stopwords, basic_word = basicWord, lemmatize=lemmatize)
      i=0

      for classifier_name in classifier_names:
        classifier_args = classifier_argss[i]


        if 'classifier_name' not in locals() or 'classifier_args' not in locals():
          print('invalid classifier')
          continue

        print('=======================================')
        print(classifier_name)
        print(classifier_args)
        print('=======================================')

        # preprocessedScore = main(classifier_name, classifier_args, preprocessed = True,ngram=2)
        unpreprocessedScore = main(classifier_name, classifier_args, preprocessed = False,ngram=2)
        row.append(unpreprocessedScore)
        i+=1
      writer.writerow(row)

