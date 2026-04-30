from flask import Flask, render_template, request, redirect
import os
import csv

app = Flask(__name__)

DATA_FILE = "data.csv"


# ---------------- INIT DATA ----------------
def init_csv():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "communication",
                "telephone",
                "sommeil",
                "conflits",
                "stabilite"
            ])


def save_data(row):
    with open(DATA_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def load_data():
    data = []
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                data.append(row)
    return data


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

    # Simple “model” (no ML, just logic)
    stabilite = (8 * comm) - (5 * tel) + (4 * som) - (6 * conf)

    save_data([comm, tel, som, conf, stabilite])

    return redirect('/dashboard')


# ---------------- DASHBOARD ----------------
@app.route('/dashboard')
def dashboard():

    data = load_data()

    if len(data) == 0:
        return "Pas encore de données."

    # Convert to floats
    scores = [float(row["stabilite"]) for row in data]

    avg = sum(scores) / len(scores)

    # Status logic
    if avg > 60:
        statut = "💚 Relation stable"
        conseil = "Continuez vos habitudes positives."
    elif avg > 30:
        statut = "🟡 Relation moyenne"
        conseil = "Améliorer communication et réduire conflits."
    else:
        statut = "🔴 Relation instable"
        conseil = "Travail sur la communication urgent."

    return f"""
    <h1>Dashboard</h1>
    <p><b>Moyenne stabilité :</b> {avg:.2f}</p>
    <p><b>Statut :</b> {statut}</p>
    <p><b>Conseil :</b> {conseil}</p>
    """


# ---------------- RUN ----------------
if __name__ == "__main__":
    init_csv()
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
