import pandas as pd
from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.decomposition import PCA

def load_data():
    return pd.read_csv("data.csv")

def train_models(df):

    X = df[['communication','telephone','sommeil','conflits']]
    y = df['stabilite']

    model = LinearRegression()
    model.fit(X, y)

    equation = f"{model.coef_[0]:.2f}C + {model.coef_[1]:.2f}T + {model.coef_[2]:.2f}S + {model.coef_[3]:.2f}K + {model.intercept_:.2f}"

    df['cluster'] = KMeans(n_clusters=2, random_state=0).fit_predict(X)

    df[['PC1','PC2']] = PCA(n_components=2).fit_transform(X)

    return df, equation
