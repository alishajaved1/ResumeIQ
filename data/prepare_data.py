import re
import pandas as pd

df = pd.read_csv("data/resumes_raw.csv")
print("Original rows:", len(df))


def clean(text):
    text = str(text)
    text = text.replace("\\r\\n", "\n").replace("\\n", "\n").replace("\\r", "\n")
    text = re.sub(r"[^\x00-\x7F]+", " ", text)   # ajeeb symbols hatao
    text = re.sub(r"[ \t]+", " ", text)           # extra spaces
    text = re.sub(r"\n\s*\n+", "\n", text)        # extra khali lines
    return text.strip()


df["Resume"] = df["Resume"].apply(clean)
df = df.drop_duplicates(subset="Resume").reset_index(drop=True)
df.insert(0, "resume_id", range(1, len(df) + 1))
df["length"] = df["Resume"].str.len()

df.to_csv("data/resumes_clean.csv", index=False)
print("Clean rows:", len(df))
print("Categories:", df["Category"].nunique())
print(df["Category"].value_counts().head(10))