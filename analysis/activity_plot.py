import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("sample_data.csv")

df["duration_sec"] = pd.to_numeric(df["duration_sec"], errors="coerce")
df = df.dropna(subset=["duration_sec", "action"])

grouped = df.groupby("action")["duration_sec"]

data = [group for _, group in grouped]
labels = [action for action, _ in grouped]

n = len(labels)
width = max(6, n * 0.8)   # scale width with number of actions
height = 6

plt.figure(figsize=(width, height))

plot = plt.boxplot(
    data,
    tick_labels=labels,
    patch_artist=True,
    boxprops=dict(facecolor="#4C72B0"),
    medianprops=dict(color="black"),
    whiskerprops=dict(color="black"),
    capprops=dict(color="black"),
)

plt.xlabel("Action")
plt.xticks(rotation=45, ha="right")
plt.ylabel("Duration")
plt.title("Duration Distribution by Action")

plt.tight_layout()
plt.show()