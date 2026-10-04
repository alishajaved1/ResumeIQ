import pandas as pd
from ai import analyze_resume

df = pd.read_csv("data/resumes_clean.csv")
print(analyze_resume(df.iloc[0]["Resume"]))