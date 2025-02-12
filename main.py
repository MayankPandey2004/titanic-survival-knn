import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.preprocessing import MinMaxScaler
from sklearn.neighbors import KNeighborsClassifier
from sklearn.metrics import accuracy_score, confusion_matrix

import matplotlib.pyplot as plt
import seaborn as sns

data = pd.read_csv("tested.csv")

# Data Cleaning
def preprocess_data(df):
    df.drop(columns=["PassengerId", "Name", "Ticket", "Cabin"], inplace=True)
    
    df["Embarked"].fillna("S", inplace=True)
    df.drop(columns=["Embarked"], inplace=True)

    fill_missing_ages(df)

    df["Sex"] = df["Sex"].map({'male': 1, 'female': 0})

    # Feature Engineering
    df["FamilySize"] = df["SibSp"] + df["Parch"]
    df["isAlone"] = (df["FamilySize"] == 0).astype(int)
    df["FareBin"] = pd.qcut(df["Fare"].fillna(df["Fare"].median()), 4, labels=False)
    df["AgeBin"] = pd.cut(df["Age"], bins=[0, 12, 20, 40, 60, np.inf], labels=False)

    df.drop(columns=["SibSp", "Parch", "Fare", "Age"], inplace=True)  # Dropping unused columns
    
    return df

def fill_missing_ages(df):
    df["Age"].fillna(df.groupby("Pclass")["Age"].transform("median"), inplace=True)

data = preprocess_data(data)

# Create Features and Target
X = data.drop(columns=["Survived"])
y = data["Survived"]

# Split Data
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.25, random_state=42)

# Scaling
scaler = MinMaxScaler()
X_train = scaler.fit_transform(X_train)
X_test = scaler.transform(X_test)

# Hyperparameter Tuning for KNN
def tune_model(X_train, y_train):
    param_grid = {
        "n_neighbors": range(1, 21),
        "metric": ["euclidean", "manhattan", "minkowski"],
        "weights": ["uniform", "distance"]
    }
    model = KNeighborsClassifier()
    grid_search = GridSearchCV(model, param_grid, cv=5, n_jobs=-1)
    grid_search.fit(X_train, y_train)
    return grid_search.best_estimator_

best_model = tune_model(X_train, y_train)

# Model Evaluation
def evaluate_model(model, X_test, y_test):
    prediction = model.predict(X_test)
    accuracy = accuracy_score(y_test, prediction)
    matrix = confusion_matrix(y_test, prediction)
    return accuracy, matrix

accuracy, matrix = evaluate_model(best_model, X_test, y_test)

print(f'Accuracy: {accuracy*100:.2f}%')
print(f'Confusion Matrix:\n{matrix}')


def plot_model(matrix):
    plt.figure(figsize=(10,7))
    sns.heatmap(matrix, annot=True, fmt="d", xticklabels=["Survived", "Not Survived"], yticklabels=["Not Survived","Survived"])
    plt.title("Confusion Matrix")
    plt.xlabel("Predicted Values")
    plt.show()

plot_model(matrix)