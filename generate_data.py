
import numpy as np
import pandas as pd

np.random.seed(42)

n = 100

df = pd.DataFrame({
    "communication": np.random.randint(1,10,n),
    "telephone": np.random.randint(1,10,n),
    "sommeil": np.random.randint(3,10,n),
    "conflits": np.random.randint(0,6,n),
})

df["stabilite"] = (
    10
    + 8*df["communication"]
    - 5*df["telephone"]
    + 3*df["sommeil"]
    - 7*df["conflits"]
    + np.random.normal(0,5,n)
)

df.to_csv("data.csv", index=False)

print("data.csv généré avec succès")
