from pathlib import Path

import os
for dirname, _, filenames in os.walk('datasets/kaggle/input'):
    for filename in filenames:
        print(os.path.join(dirname, filename))
        
#EDA exploratoring data analisis

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import pickle
import re

%matplotlib inline 

from sklearn.preprocessing import OneHotEncoder

# Models from Scikit-Learn
# Algorithms
from sklearn import linear_model
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import Perceptron
from sklearn.linear_model import SGDClassifier
from sklearn.tree import DecisionTreeClassifier
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC, LinearSVC
from sklearn.naive_bayes import GaussianNB


## Model evaluators
from sklearn.model_selection import train_test_split, cross_val_score, cross_val_predict
from sklearn.model_selection import RandomizedSearchCV, GridSearchCV
from sklearn.metrics import confusion_matrix, precision_recall_curve, roc_auc_score
from sklearn.metrics import precision_score, recall_score, f1_score, roc_curve


test = pd.read_csv("datasets/kaggle/input/titanic/test.csv")
test.isna().sum()
test.info()

train = pd.read_csv("datasets/kaggle/input/titanic/train.csv")
train.shape

train.describe()
train.info()
train.isna().sum()
train.Sex.value_counts()

## What is missing?
total = train.isnull().sum().sort_values(ascending=False)
percent_1 = train.isnull().sum()/train.isnull().count()*100
percent_2 = (round(percent_1, 1)).sort_values(ascending=False)
missing_data = pd.concat([total, percent_2], axis=1, keys=['Total', '%'])
missing_data.head(5)


## What features could contribute to a high survival rate ?
train.columns.values


### PLOTING ###

# plot1
pd.crosstab(train.Survived, train.Sex).plot(kind="bar", figsize=(10,6), color=["salmon", "lightblue"])

# Add some attributes to it
plt.title("Survived for Sex")
plt.xlabel("0 = No Survived, 1 = Survived")
plt.ylabel("Passengers")
plt.legend(["Female", "Male"])
plt.xticks(rotation=0); # keep the labels on the x-axis vertical


# plot2
plt.figure(figsize=(20, 12))

# Scatter with positive examples
plt.scatter(train.Age[train.Survived==1],
            train.Pclass[train.Survived==1],
            c="blue")

# Scatter with negative examples
plt.scatter(train.Age[train.Survived==0],
            train.Pclass[train.Survived==0],
            c="red")

# Add some helpful inf
plt.title("Survived in function of Age and Class")
plt.xlabel("Age")
plt.ylabel("Class")
plt.legend(["Survived", "No Survived"]);

# plot3
sns.barplot(x='Pclass', y='Survived', data=train)

# plot4
survived = 'survived'
not_survived = 'not survived'
fig, axes = plt.subplots(nrows=1, ncols=2,figsize=(10, 4))
women = train[train['Sex']=='female']
men = train[train['Sex']=='male']
ax = sns.histplot(women[women['Survived']==1].Age.dropna(), bins=18, label = survived, ax = axes[0], kde =False)
ax = sns.histplot(women[women['Survived']==0].Age.dropna(), bins=40, label = not_survived, ax = axes[0], kde =False)
ax.legend()
ax.set_title('Female')
ax = sns.distplot(men[men['Survived']==1].Age.dropna(), bins=18, label = survived, ax = axes[1], kde = False)
ax = sns.distplot(men[men['Survived']==0].Age.dropna(), bins=40, label = not_survived, ax = axes[1], kde = False)
ax.legend()
_ = ax.set_title('Male');

# plot5
grid = sns.FacetGrid(train, col='Survived', row='Pclass', size=2.3, aspect=1.9)
grid.map(plt.hist, 'Age', alpha=.5, bins=20)
grid.add_legend();

# plot6
FacetGrid = sns.FacetGrid(train, row='Embarked', size=4.5, aspect=1.6)
FacetGrid.map(sns.pointplot, 'Pclass', 'Survived', 'Sex', palette=None,  order=None, hue_order=None )
FacetGrid.add_legend()

# Combined feature, that shows the total number of relatives, a person has on the Titanic

data = [train, test]
for dataset in data:
    dataset['relatives'] = dataset['SibSp'] + dataset['Parch']
    dataset.loc[dataset['relatives'] > 0, 'not_alone'] = 0
    dataset.loc[dataset['relatives'] == 0, 'not_alone'] = 1
    dataset['not_alone'] = dataset['not_alone'].astype(int)
train['not_alone'].value_counts()

dataset['relatives']

axes = sns.factorplot('relatives','Survived', 
                      data=train, aspect = 2.5, )

### END PLOTING


## DATA PREPROCESING ###

train_tmp = train.copy()
test_tmp = test.copy()

train_tmp['Ticket'].describe()
train_tmp = train_tmp.drop(['Ticket',  'PassengerId'], axis=1)
test_tmp = test_tmp.drop(['Ticket'], axis=1)


deck = {"A": 1, "B": 2, "C": 3, "D": 4, "E": 5, "F": 6, "G": 7, "U": 8}
data = [train_tmp, test_tmp]

# cabin into deck
for dataset in data:
    dataset['Cabin'] = dataset['Cabin'].fillna("U0")
    dataset['Deck'] = dataset['Cabin'].map(lambda x: re.compile("([a-zA-Z]+)").search(x).group())
    dataset['Deck'] = dataset['Deck'].map(deck)
    dataset['Deck'] = dataset['Deck'].fillna(0)
    dataset['Deck'] = dataset['Deck'].astype(int)
# # we can now drop the cabin feature
train_tmp = train_tmp.drop(['Cabin'], axis=1)
test_tmp = test_tmp.drop(['Cabin'], axis=1)

# Age

data = [train_tmp, test_tmp]

for dataset in data:
    mean = train_tmp["Age"].mean()
    std = train_tmp["Age"].std()
    is_null = dataset["Age"].isnull().sum()
    # compute random numbers between the mean, std and is_null
    rand_age = np.random.randint(mean - std, mean + std, size = is_null)
    # fill NaN values in Age column with random values generated
    age_slice = dataset["Age"].copy()
    age_slice[np.isnan(age_slice)] = rand_age
    dataset["Age"] = age_slice
    dataset["Age"] = train_tmp["Age"].astype(int)
train_tmp["Age"].isnull().sum()

# Embarked

train_tmp['Embarked'].describe()

common_value = 'S'
data = [train_tmp, test_tmp]

for dataset in data:
    dataset['Embarked'] = dataset['Embarked'].fillna(common_value)
    
    
## Converting Features    

train_tmp.info()

# Fare

data = [train_tmp, test_tmp]

for dataset in data:
    dataset['Fare'] = dataset['Fare'].fillna(0)
    dataset['Fare'] = dataset['Fare'].astype(int)
    
# Name
data = [train_tmp, test_tmp]
titles = {"Mr": 1, "Miss": 2, "Mrs": 3, "Master": 4, "Rare": 5}

for dataset in data:
    # extract titles
    dataset['Title'] = dataset.Name.str.extract(' ([A-Za-z]+)\.', expand=False)
    # replace titles with a more common title or as Rare
    dataset['Title'] = dataset['Title'].replace(['Lady', 'Countess','Capt', 'Col','Don', 'Dr',\
                                            'Major', 'Rev', 'Sir', 'Jonkheer', 'Dona'], 'Rare')
    dataset['Title'] = dataset['Title'].replace('Mlle', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Ms', 'Miss')
    dataset['Title'] = dataset['Title'].replace('Mme', 'Mrs')
    # convert titles into numbers
    dataset['Title'] = dataset['Title'].map(titles)
    # filling NaN with 0, to get safe
    dataset['Title'] = dataset['Title'].fillna(0)
train_tmp = train_tmp.drop(['Name'], axis=1)
test_tmp = test_tmp.drop(['Name'], axis=1)    


## Sex

genders = {"male": 0, "female": 1}
data = [train_tmp, test_tmp]

for dataset in data:
    dataset['Sex'] = dataset['Sex'].map(genders)

## Ticket
## Drop ticket 681 unique tickets, it will be a bit tricky to convert them into useful categories.

#train_tmp = train_tmp.drop(['Ticket'], axis=1)
#test_tmp = test_tmp.drop(['Ticket'], axis=1)

## Embarked
ports = {"S": 0, "C": 1, "Q": 2}
data = [train_tmp, test_tmp]

for dataset in data:
    dataset['Embarked'] = dataset['Embarked'].map(ports)

### Creating Categories:
    
# Age

data = [train_tmp, test_tmp]
for dataset in data:
    dataset['Age'] = dataset['Age'].astype(int)
    dataset.loc[ dataset['Age'] <= 11, 'Age'] = 0
    dataset.loc[(dataset['Age'] > 11) & (dataset['Age'] <= 18), 'Age'] = 1
    dataset.loc[(dataset['Age'] > 18) & (dataset['Age'] <= 22), 'Age'] = 2
    dataset.loc[(dataset['Age'] > 22) & (dataset['Age'] <= 27), 'Age'] = 3
    dataset.loc[(dataset['Age'] > 27) & (dataset['Age'] <= 33), 'Age'] = 4
    dataset.loc[(dataset['Age'] > 33) & (dataset['Age'] <= 40), 'Age'] = 5
    dataset.loc[(dataset['Age'] > 40) & (dataset['Age'] <= 66), 'Age'] = 6
    dataset.loc[ dataset['Age'] > 66, 'Age'] = 6

# let's see how it's distributed train_df['Age'].value_counts()
    
# Fare

data = [train_tmp, test_tmp]

for dataset in data:
    dataset.loc[ dataset['Fare'] <= 7.91, 'Fare'] = 0
    dataset.loc[(dataset['Fare'] > 7.91) & (dataset['Fare'] <= 14.454), 'Fare'] = 1
    dataset.loc[(dataset['Fare'] > 14.454) & (dataset['Fare'] <= 31), 'Fare']   = 2
    dataset.loc[(dataset['Fare'] > 31) & (dataset['Fare'] <= 99), 'Fare']   = 3
    dataset.loc[(dataset['Fare'] > 99) & (dataset['Fare'] <= 250), 'Fare']   = 4
    dataset.loc[ dataset['Fare'] > 250, 'Fare'] = 5
    dataset['Fare'] = dataset['Fare'].astype(int)
    
### Creating new Features:
    
# Age times Class    
data = [train_tmp, test_tmp]
for dataset in data:
    dataset['Age_Class']= dataset['Age']* dataset['Pclass']
    
# Fare per Person
for dataset in data:
    dataset['Fare_Per_Person'] = dataset['Fare']/(dataset['relatives']+1)
    dataset['Fare_Per_Person'] = dataset['Fare_Per_Person'].astype(int)
    
    
# Let's take a last look at the training set, before we start training the models.
train_output = train_tmp.head(10)
    
## Building Machine Learning Models:
X_train = train_tmp.drop("Survived", axis=1)
Y_train = train_tmp["Survived"]
X_test  = test_tmp.drop("PassengerId", axis=1).copy()    


## Stochastic Gradient Descent (SGD):
    
sgd = linear_model.SGDClassifier(max_iter=5, tol=None)
sgd.fit(X_train, Y_train)
Y_pred = sgd.predict(X_test)

sgd.score(X_train, Y_train)

acc_sgd = round(sgd.score(X_train, Y_train) * 100, 2)    


## Random Forest:
    
random_forest = RandomForestClassifier(n_estimators=100)
random_forest.fit(X_train, Y_train)

Y_prediction = random_forest.predict(X_test)

random_forest.score(X_train, Y_train)
acc_random_forest = round(random_forest.score(X_train, Y_train) * 100, 2)    


## Logistic Regression:
    
logreg = LogisticRegression()
logreg.fit(X_train, Y_train)

Y_pred = logreg.predict(X_test)

acc_log = round(logreg.score(X_train, Y_train) * 100, 2)    

## K Nearest Neighbor:
    
knn = KNeighborsClassifier(n_neighbors = 3) 
knn.fit(X_train, Y_train)  
Y_pred = knn.predict(X_test)  
acc_knn = round(knn.score(X_train, Y_train) * 100, 2)        

## Gaussian Naive Bayes:
    
gaussian = GaussianNB() 
gaussian.fit(X_train, Y_train)  
Y_pred = gaussian.predict(X_test)  
acc_gaussian = round(gaussian.score(X_train, Y_train) * 100, 2)    

## Perceptron:
    
perceptron = Perceptron(max_iter=5)
perceptron.fit(X_train, Y_train)
Y_pred = perceptron.predict(X_test)
acc_perceptron = round(perceptron.score(X_train, Y_train) * 100, 2)    

## Linear Support Vector Machine:

linear_svc = LinearSVC()
linear_svc.fit(X_train, Y_train)
Y_pred = linear_svc.predict(X_test)
acc_linear_svc = round(linear_svc.score(X_train, Y_train) * 100, 2)    

## Decision Tree:
    
decision_tree = DecisionTreeClassifier() 
decision_tree.fit(X_train, Y_train)  
Y_pred = decision_tree.predict(X_test)  
acc_decision_tree = round(decision_tree.score(X_train, Y_train) * 100, 2)    

## Result

results = pd.DataFrame({
    'Model': ['Support Vector Machines', 'KNN', 'Logistic Regression', 
              'Random Forest', 'Naive Bayes', 'Perceptron', 
              'Stochastic Gradient Decent', 
              'Decision Tree'],
    'Score': [acc_linear_svc, acc_knn, acc_log, 
              acc_random_forest, acc_gaussian, acc_perceptron, 
              acc_sgd, acc_decision_tree]})
result_df = results.sort_values(by='Score', ascending=False)
result_df = result_df.set_index('Score')
result_df.head(9)

# Cross Validation:
    
rf = RandomForestClassifier(n_estimators=100)
scores = cross_val_score(rf, X_train, Y_train, cv=10, scoring = "accuracy")
print("Scores:", scores)
print("Mean:", scores.mean())
print("Standard Deviation:", scores.std())    

# Feature Importance

importances = pd.DataFrame(    
                        {'feature':X_train.columns,
                         'importance':np.round(random_forest.feature_importances_,3)
                     })
importances = importances.sort_values('importance',ascending=False).set_index('feature')
importances.head(15)

importances.plot.bar()

## not_alone and Parch doesn’t play a significant role in our random forest classifiers prediction process
train_tmp  = train_tmp.drop("not_alone", axis=1)
test_tmp  = test_tmp.drop("not_alone", axis=1)

train_tmp  = train_tmp.drop("Parch", axis=1)
test_tmp  = test_tmp.drop("Parch", axis=1)

## Training random forest without not_alone and Parch features

# Random Forest, out-of-bag samples to estimate the generalization accuracy

random_forest = RandomForestClassifier(n_estimators=100, oob_score = True)
random_forest.fit(X_train, Y_train)
Y_prediction = random_forest.predict(X_test)

random_forest.score(X_train, Y_train)

acc_random_forest = round(random_forest.score(X_train, Y_train) * 100, 2)
print(round(acc_random_forest,2,), "%")

print("oob score:", round(random_forest.oob_score_, 4)*100, "%")


### Hyperparameter Tuning

# I put this code into a markdown cell and not into a code cell, because it takes a long time to run it.
# Directly underneeth it, I put a screenshot of the gridsearch's output.

#param_grid = { "criterion" : ["gini", "entropy"], 
#               "min_samples_leaf" : [1, 5, 10, 25, 50, 70], 
#               "min_samples_split" : [2, 4, 10, 12, 16, 18, 25, 35], 
#               "n_estimators": [100, 400, 700, 1000, 1500]
#               }

#rf = RandomForestClassifier(n_estimators=100, max_features='auto', oob_score=True, random_state=1, n_jobs=-1)
#clf = GridSearchCV(estimator=rf, param_grid=param_grid, n_jobs=-1)
#clf.fit(X_train, Y_train)
#clf.bestparams

# { 'criterion' : 'gini'
#   'min_samples_leaf' : 1
#   'min_samples_split' : 10
#   'n_estimators': 100             
#   }


# Random Forest
random_forest = RandomForestClassifier(criterion = "gini", 
                                       min_samples_leaf = 1, 
                                       min_samples_split = 10,   
                                       n_estimators=100, 
                                       max_features='auto', 
                                       oob_score=True, 
                                       random_state=1, 
                                       n_jobs=-1)

random_forest.fit(X_train, Y_train)
Y_prediction = random_forest.predict(X_test)

random_forest.score(X_train, Y_train)

print("oob score:", round(random_forest.oob_score_, 4)*100, "%")

# Confusion Matrix:
predictions = cross_val_predict(random_forest, X_train, Y_train, cv=3)
confusion_matrix(Y_train, predictions)
    
# Precision and Recall:

print("Precision:", precision_score(Y_train, predictions))
print("Recall:",recall_score(Y_train, predictions))

# F1-Score

f1_score(Y_train, predictions)

## Precision Recall Curve

# getting the probabilities of our predictions
y_scores = random_forest.predict_proba(X_train)
y_scores = y_scores[:,1]

precision, recall, threshold = precision_recall_curve(Y_train, y_scores)
def plot_precision_and_recall(precision, recall, threshold):
    plt.plot(threshold, precision[:-1], "r-", label="precision", linewidth=5)
    plt.plot(threshold, recall[:-1], "b", label="recall", linewidth=5)
    plt.xlabel("threshold", fontsize=19)
    plt.legend(loc="upper right", fontsize=19)
    plt.ylim([0, 1])

plt.figure(figsize=(14, 7))
plot_precision_and_recall(precision, recall, threshold)
plt.show()


def plot_precision_vs_recall(precision, recall):
    plt.plot(recall, precision, "g--", linewidth=2.5)
    plt.ylabel("recall", fontsize=19)
    plt.xlabel("precision", fontsize=19)
    plt.axis([0, 1.5, 0, 1.5])

plt.figure(figsize=(14, 7))
plot_precision_vs_recall(precision, recall)
plt.show()


# ROC AUC Curve

# compute true positive rate and false positive rate
false_positive_rate, true_positive_rate, thresholds = roc_curve(Y_train, y_scores)
# plotting them against each other
def plot_roc_curve(false_positive_rate, true_positive_rate, label=None):
    plt.plot(false_positive_rate, true_positive_rate, linewidth=2, label=label)
    plt.plot([0, 1], [0, 1], 'r', linewidth=4)
    plt.axis([0, 1, 0, 1])
    plt.xlabel('False Positive Rate (FPR)', fontsize=16)
    plt.ylabel('True Positive Rate (TPR)', fontsize=16)

plt.figure(figsize=(14, 7))
plot_roc_curve(false_positive_rate, true_positive_rate)
plt.show()


r_a_score = roc_auc_score(Y_train, y_scores)
print("ROC-AUC-Score:", r_a_score)