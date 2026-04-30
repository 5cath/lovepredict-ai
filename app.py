from flask import Flask, render_template, request, redirect
import pandas as pd
import numpy as np
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

from sklearn.linear_model import LinearRegression
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsClassifier
from sklearn.decomposition import PCA

app = Flask(__name__)

DATA_FILE = "data.csv"


# ---------------- INIT DATA ----------------
def init_csv():
    if not os.path.exists(DATA_FILE):
        df = pd.DataFrame(columns=[
            "communication",
            "telephone",
            "sommeil",
            "conflits",
            "stabilite"
        ])
        df.to_csv(DATA_FILE, index=False)


def load_data():
    return pd.read_csv(DATA_FILE)


def save_data(row):
    df = load_data()
    df = pd.concat([df, pd.DataFrame([row])], ignore_index=True)
    df.to_csv(DATA_FILE, index=False)


# ---------------- HOME ----------------
@app.route('/')
def index():
    return render_template('index.html')


# ---------------- SUBMIT ----------------
@app.route('/submit', methods=['POST'])
def submit():
    comm = float(request.form['communication'])
    tel = float(request.form['telephone'])
    som = float(request.form['sommeil'])
    conf = float(request.form['conflits'])

    stabilite = (8 * comm) - (5 * tel) + (4 * som) - (6 * conf) + np.random.normal(0, 5)

    save_data({
        "communication": comm,
        "telephone": tel,
        "sommeil": som,
        "conflits": conf,
        "stabilite": stabilite
    })

    return redirect('/dashboard')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    df = load_data()

    if len(df) < 5:
        return "Pas assez de données pour l'analyse (min 5)."

    os.makedirs("static", exist_ok=True)

    # ========== REGRESSION SIMPLE ==========
    X1 = df[['communication']]
    y = df['stabilite']

    reg1 = LinearRegression()
    reg1.fit(X1, y)

    eq_simple = f"Stabilité = {reg1.coef_[0]:.2f} * Communication + {reg1.intercept_:.2f}"

    # ========== REGRESSION MULTIPLE ==========
    X2 = df[['communication', 'telephone', 'sommeil', 'conflits']]
    reg2 = LinearRegression()
    reg2.fit(X2, y)

    eq_multi = (
        f"Stabilité = "
        f"{reg2.coef_[0]:.2f}*Comm + "
        f"{reg2.coef_[1]:.2f}*Tel + "
        f"{reg2.coef_[2]:.2f}*Som + "
        f"{reg2.coef_[3]:.2f}*Conf + "
        f"{reg2.intercept_:.2f}"
    )

    # ========== 🔥 STATUT DU COUPLE (AJOUT IMPORTANT) ==========
    score = df['stabilite'].mean()

    if score > 60:
        statut = "💚 Relation stable et saine"
        recommandation = "Continuez vos habitudes actuelles."
        prevention = "Attention aux petits conflits négligés."
    elif score > 30:
        statut = "🟡 Relation moyenne / instable"
        recommandation = "Améliorer la communication et réduire le téléphone."
        prevention = "Surveiller les tensions répétées."
    else:
        statut = "🔴 Relation à risque élevé"
        recommandation = "Revoir la communication et les comportements."
        prevention = "Éviter conflits non résolus."

    # ========== OBSERVATIONS ==========
    corr_comm = df['communication'].corr(df['stabilite'])
    obs_reg_simple = "La communication améliore la stabilité." if corr_comm > 0 else "Impact faible."

    obs_reg_multi = "La stabilité dépend de plusieurs facteurs combinés."

    # ========== KMEANS ==========
    kmeans = KMeans(n_clusters=2, n_init=10, random_state=0)
    df['cluster'] = kmeans.fit_predict(df[['communication', 'stabilite']])
    obs_kmeans = "Deux groupes détectés : couples stables / instables."

    # ========== KNN ==========
    df['label'] = np.where(df['stabilite'] > df['stabilite'].median(), "Stable", "Instable")
    knn = KNeighborsClassifier(n_neighbors=3)
    knn.fit(df[['communication', 'telephone', 'sommeil']], df['label'])
    df['prediction'] = knn.predict(df[['communication', 'telephone', 'sommeil']])
    obs_knn = "Le KNN prédit la stabilité selon les comportements."

    # ========== PCA ==========
    pca = PCA(n_components=2)
    comp = pca.fit_transform(df[['communication', 'telephone', 'sommeil', 'conflits']])
    df['PC1'] = comp[:, 0]
    df['PC2'] = comp[:, 1]
    obs_pca = "Réduction des dimensions pour visualisation."

    # ========== INTERPRETATION IA ==========
    interpretations = []
    for name, value in zip(
        ["Communication", "Téléphone", "Sommeil", "Conflits"],
        reg2.coef_
    ):
        if value > 0:
            interpretations.append(f"✅ {name} influence positivement la stabilité (+{value:.2f})")
        else:
            interpretations.append(f"⚠️ {name} influence négativement la stabilité ({value:.2f})")

    # ========== GRAPHIQUES ==========
    colors = df['cluster'].map({0: '#22c55e', 1: '#ef4444'})

    plt.figure(figsize=(8, 5))
    plt.scatter(df['communication'], df['stabilite'], c=colors)
    plt.plot(df['communication'], reg1.predict(X1))
    plt.savefig("static/scatter.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.hist(df['stabilite'], bins=8)
    plt.savefig("static/hist.png")
    plt.close()

    plt.figure(figsize=(8, 5))
    plt.scatter(df['PC1'], df['PC2'], c=colors)
    plt.savefig("static/pca.png")
    plt.close()

    # ========== TABLE ==========
    table = df.round(2).to_html(classes='data', index=False)

    # ========== RENDER FINAL ==========
    return render_template(
        'dashboard.html',
        eq_simple=eq_simple,
        eq_multi=eq_multi,
        table=table,

        # 🔥 AJOUT IMPORTANT
        statut=statut,
        recommandation=recommandation,
        prevention=prevention,

        obs_reg_simple=obs_reg_simple,
        obs_reg_multi=obs_reg_multi,
        obs_kmeans=obs_kmeans,
        obs_knn=obs_knn,
        obs_pca=obs_pca,
        interpretations=interpretations
    )


# ---------------- RUN ----------------
if __name__ == "__main__":
    init_csv()
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0", port=port)
