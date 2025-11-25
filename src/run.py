import pandas as pd
from pathlib import Path

root = Path(__file__).resolve().parent.parent
csv_path = str(root / "data" / "synthetic_fb_ads_undergarments.csv")

df = pd.read_csv(csv_path)

print(df.columns.tolist())
