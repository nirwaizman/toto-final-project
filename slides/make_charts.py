"""Generate real chart images from project outputs for the slide deck."""
import json
import pandas as pd
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import seaborn as sns

sns.set_theme(style="whitegrid", font_scale=1.15)
PALETTE = ["#2563eb", "#f97316", "#10b981", "#ef4444", "#8b5cf6"]
OUT = "slides/charts"
import os
os.makedirs(OUT, exist_ok=True)

df = pd.read_csv("outputs/features.csv")

# 1. Cancellation rate by hotel type
fig, ax = plt.subplots(figsize=(7, 5))
rate = df.groupby("hotel")["is_canceled"].mean() * 100
bars = ax.bar(rate.index, rate.values, color=[PALETTE[0], PALETTE[1]])
for b in bars:
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{b.get_height():.1f}%",
            ha="center", fontsize=14, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)")
ax.set_title("Cancellation Rate by Hotel Type", fontsize=16, fontweight="bold")
ax.set_ylim(0, 55)
plt.tight_layout()
plt.savefig(f"{OUT}/cancel_by_hotel.png", dpi=150)
plt.close()

# 2. Cancellation rate by deposit type
fig, ax = plt.subplots(figsize=(7, 5))
rate2 = df.groupby("deposit_type")["is_canceled"].mean().sort_values(ascending=False) * 100
bars = ax.bar(rate2.index, rate2.values, color=PALETTE[:len(rate2)])
for b in bars:
    ax.text(b.get_x() + b.get_width()/2, b.get_height() + 1, f"{b.get_height():.1f}%",
            ha="center", fontsize=14, fontweight="bold")
ax.set_ylabel("Cancellation Rate (%)")
ax.set_title("Cancellation Rate by Deposit Type", fontsize=16, fontweight="bold")
ax.set_ylim(0, 105)
plt.tight_layout()
plt.savefig(f"{OUT}/cancel_by_deposit.png", dpi=150)
plt.close()

# 3. Lead time distribution (canceled vs not)
fig, ax = plt.subplots(figsize=(7, 5))
sns.kdeplot(data=df[df.lead_time < 400], x="lead_time", hue="is_canceled",
            fill=True, common_norm=False, palette=[PALETTE[2], PALETTE[3]], alpha=0.5, ax=ax)
ax.set_title("Booking Lead Time: Canceled vs Not", fontsize=16, fontweight="bold")
ax.set_xlabel("Lead Time (days)")
legend = ax.get_legend()
if legend:
    legend.set_title("Canceled")
    for t, lbl in zip(legend.texts, ["No", "Yes"]):
        t.set_text(lbl)
plt.tight_layout()
plt.savefig(f"{OUT}/lead_time_dist.png", dpi=150)
plt.close()

# 4. Bookings by month
fig, ax = plt.subplots(figsize=(9, 5))
month_order = ["January","February","March","April","May","June","July",
               "August","September","October","November","December"]
counts = df["arrival_date_month"].value_counts().reindex(month_order)
ax.bar(range(len(counts)), counts.values, color=PALETTE[0])
ax.set_xticks(range(len(counts)))
ax.set_xticklabels([m[:3] for m in month_order], rotation=0)
ax.set_ylabel("Number of Bookings")
ax.set_title("Booking Volume by Month", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/bookings_by_month.png", dpi=150)
plt.close()

# 5. Model comparison bar chart (from evaluation_report.md numbers)
metrics = {
    "Accuracy": [0.7871, 0.7872],
    "Precision": [0.7874, 0.7913],
    "Recall": [0.6216, 0.6166],
    "F1": [0.6947, 0.6931],
    "ROC-AUC": [0.8713, 0.8750],
}
models = ["Random\nForest", "Gradient\nBoosting ✓"]
fig, ax = plt.subplots(figsize=(10, 5.5))
x = range(len(metrics))
width = 0.35
rf_vals = [v[0] for v in metrics.values()]
gb_vals = [v[1] for v in metrics.values()]
ax.bar([i - width/2 for i in x], rf_vals, width, label="Random Forest", color=PALETTE[4])
ax.bar([i + width/2 for i in x], gb_vals, width, label="Gradient Boosting (selected)", color=PALETTE[2])
ax.set_xticks(list(x))
ax.set_xticklabels(metrics.keys())
ax.set_ylim(0, 1.0)
ax.set_title("Model Comparison — Test Set (2017)", fontsize=16, fontweight="bold")
ax.legend(loc="lower right")
for i, (r, g) in enumerate(zip(rf_vals, gb_vals)):
    ax.text(i - width/2, r + 0.02, f"{r:.2f}", ha="center", fontsize=10)
    ax.text(i + width/2, g + 0.02, f"{g:.2f}", ha="center", fontsize=10, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/model_comparison.png", dpi=150)
plt.close()

# 6. Class balance pie
fig, ax = plt.subplots(figsize=(6, 6))
vc = df["is_canceled"].value_counts()
ax.pie(vc.values, labels=["Not Canceled", "Canceled"], autopct="%1.1f%%",
       colors=[PALETTE[2], PALETTE[3]], startangle=90,
       textprops={"fontsize": 13, "fontweight": "bold"})
ax.set_title("Booking Outcome Distribution", fontsize=16, fontweight="bold")
plt.tight_layout()
plt.savefig(f"{OUT}/class_balance.png", dpi=150)
plt.close()

print("Charts saved to", OUT)
print(os.listdir(OUT))
