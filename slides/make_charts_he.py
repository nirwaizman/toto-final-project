"""Generate Hebrew-labelled chart images from project outputs for the Hebrew slide deck.

Numbers are read from the real artifacts (outputs/features.csv, outputs/evaluation_report.md)
so the deck always reflects the latest Flow run.
"""
import os
import re

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
import seaborn as sns
from bidi.algorithm import get_display

BASE = os.path.join(os.path.dirname(__file__), "..")
OUT = os.path.join(os.path.dirname(__file__), "charts_he")
os.makedirs(OUT, exist_ok=True)

FONT = "Arial Unicode MS"
plt.rcParams["font.family"] = FONT
sns.set_theme(style="whitegrid", font_scale=1.15, rc={"font.family": FONT})

BG = "#0F172A"
CARD = "#1E293B"
BLUE, ORANGE, GREEN, RED, PURPLE, GRAY = "#3B82F6", "#F97316", "#10B981", "#EF4444", "#8B5CF6", "#CBD5E1"


def he(s: str) -> str:
    # matplotlib on this system already shapes Hebrew RTL; set HE_BIDI=1 to force bidi reordering.
    return get_display(s) if os.environ.get("HE_BIDI") == "1" else s


def style(ax, title):
    ax.set_facecolor(CARD)
    ax.figure.set_facecolor(BG)
    ax.set_title(he(title), fontsize=18, fontweight="bold", color="white", pad=14)
    ax.tick_params(colors=GRAY, labelsize=12)
    ax.xaxis.label.set_color(GRAY)
    ax.yaxis.label.set_color(GRAY)
    for sp in ax.spines.values():
        sp.set_color("#334155")
    ax.grid(color="#334155", alpha=0.6)


def save(name):
    plt.tight_layout()
    plt.savefig(os.path.join(OUT, name), dpi=170, facecolor=BG)
    plt.close()


df = pd.read_csv(os.path.join(BASE, "outputs", "features.csv"))

# 1. Cancellation rate by hotel
fig, ax = plt.subplots(figsize=(7, 5))
rate = df.groupby("hotel")["is_canceled"].mean() * 100
labels = {"City Hotel": "מלון עירוני", "Resort Hotel": "מלון נופש"}
bars = ax.bar([he(labels[i]) for i in rate.index], rate.values, color=[BLUE, ORANGE], width=0.55)
for b in bars:
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.2, f"{b.get_height():.1f}%",
            ha="center", fontsize=16, fontweight="bold", color="white")
ax.set_ylabel(he("שיעור ביטולים (%)"), fontsize=13)
ax.set_ylim(0, 55)
style(ax, "שיעור ביטולים לפי סוג מלון")
save("cancel_by_hotel.png")

# 2. Cancellation by deposit type
fig, ax = plt.subplots(figsize=(7, 5))
rate2 = df.groupby("deposit_type")["is_canceled"].mean().sort_values(ascending=False) * 100
dep = {"Non Refund": "ללא החזר", "No Deposit": "ללא פיקדון", "Refundable": "ניתן להחזר"}
bars = ax.bar([he(dep.get(i, i)) for i in rate2.index], rate2.values, color=[RED, BLUE, GREEN][:len(rate2)], width=0.55)
for b in bars:
    ax.text(b.get_x() + b.get_width() / 2, b.get_height() + 1.5, f"{b.get_height():.1f}%",
            ha="center", fontsize=15, fontweight="bold", color="white")
ax.set_ylabel(he("שיעור ביטולים (%)"), fontsize=13)
ax.set_ylim(0, 110)
style(ax, "שיעור ביטולים לפי סוג פיקדון")
save("cancel_by_deposit.png")

# 3. Lead time distribution
fig, ax = plt.subplots(figsize=(7, 5))
sns.kdeplot(data=df[df.lead_time < 400], x="lead_time", hue="is_canceled", fill=True,
            common_norm=False, palette=[GREEN, RED], alpha=0.55, ax=ax, linewidth=1.5)
ax.set_xlabel(he("ימים בין ההזמנה להגעה (lead time)"), fontsize=13)
ax.set_ylabel(he("צפיפות"), fontsize=13)
leg = ax.get_legend()
if leg:
    leg.set_title(he("בוטלה?"))
    for t, lbl in zip(leg.texts, ["לא", "כן"]):
        t.set_text(he(lbl))
    leg.get_frame().set_facecolor(CARD)
    for t in leg.get_texts() + [leg.get_title()]:
        t.set_color("white")
style(ax, "זמן ההזמנה מראש: הזמנות שבוטלו לעומת שהתממשו")
save("lead_time_dist.png")

# 4. Bookings by month
fig, ax = plt.subplots(figsize=(9, 5))
month_order = ["January", "February", "March", "April", "May", "June", "July",
               "August", "September", "October", "November", "December"]
he_months = ["ינו", "פבר", "מרץ", "אפר", "מאי", "יוני", "יולי", "אוג", "ספט", "אוק", "נוב", "דצמ"]
counts = df["arrival_date_month"].value_counts().reindex(month_order)
colors = [ORANGE if m in ("July", "August") else BLUE for m in month_order]
ax.bar(range(12), counts.values, color=colors, width=0.7)
ax.set_xticks(range(12))
ax.set_xticklabels([he(m) for m in he_months])
ax.set_ylabel(he("מספר הזמנות"), fontsize=13)
style(ax, "נפח הזמנות לפי חודש הגעה")
save("bookings_by_month.png")

# 5. Model comparison — parsed from evaluation_report.md
report = open(os.path.join(BASE, "outputs", "evaluation_report.md"), encoding="utf-8").read()
rows = {}
for line in report.splitlines():
    m = re.match(r"\|\s*(RandomForestClassifier|GradientBoostingClassifier)[^|]*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|\s*([\d.]+)\s*\|", line)
    if m:
        rows[m.group(1)] = [float(x) for x in m.groups()[1:]]
best = "GradientBoostingClassifier" if "GradientBoostingClassifier ✅" in report else "RandomForestClassifier"
metric_names = ["Accuracy", "Precision", "Recall", "F1", "ROC-AUC"]
fig, ax = plt.subplots(figsize=(10, 5.5))
x = range(5)
w = 0.36
rf, gb = rows["RandomForestClassifier"], rows["GradientBoostingClassifier"]
ax.bar([i - w / 2 for i in x], rf, w, label="Random Forest" + (he("  ✓ נבחר") if best.startswith("Random") else ""), color=PURPLE)
ax.bar([i + w / 2 for i in x], gb, w, label="Gradient Boosting" + (he("  ✓ נבחר") if best.startswith("Gradient") else ""), color=GREEN)
ax.set_xticks(list(x))
ax.set_xticklabels(metric_names, fontsize=13)
ax.set_ylim(0, 1.0)
for i, (r, g) in enumerate(zip(rf, gb)):
    ax.text(i - w / 2, r + 0.02, f"{r:.3f}", ha="center", fontsize=10, color=GRAY)
    ax.text(i + w / 2, g + 0.02, f"{g:.3f}", ha="center", fontsize=10, fontweight="bold", color="white")
leg = ax.legend(loc="lower right", facecolor=CARD, edgecolor="#334155")
for t in leg.get_texts():
    t.set_color("white")
style(ax, "השוואת מודלים — סט מבחן (2017)")
save("model_comparison.png")

# 6. Class balance donut
fig, ax = plt.subplots(figsize=(6, 6))
vc = df["is_canceled"].value_counts()
wedges, _, autot = ax.pie(vc.values, labels=None, autopct="%1.1f%%", colors=[GREEN, RED], startangle=90,
                          pctdistance=0.78, wedgeprops=dict(width=0.42, edgecolor=BG, linewidth=3),
                          textprops={"fontsize": 16, "fontweight": "bold", "color": "white"})
ax.legend(wedges, [he("התממשה"), he("בוטלה")], loc="lower center", ncol=2, frameon=False,
          fontsize=14, labelcolor="white", bbox_to_anchor=(0.5, -0.05))
ax.text(0, 0, f"{len(df):,}\n" + he("הזמנות"), ha="center", va="center", fontsize=16, color="white", fontweight="bold")
fig.set_facecolor(BG)
ax.set_title(he("תוצאת ההזמנה"), fontsize=18, fontweight="bold", color="white")
save("class_balance.png")

# 7. Cancellation by market segment (new)
fig, ax = plt.subplots(figsize=(8, 5))
seg = df.groupby("market_segment")["is_canceled"].agg(["mean", "size"])
seg = seg[seg["size"] > 500].sort_values("mean", ascending=True)
seg_he = {"Online TA": "סוכנות אונליין (OTA)", "Offline TA/TO": "סוכנות אופליין", "Groups": "קבוצות",
          "Direct": "ישיר", "Corporate": "עסקי", "Complementary": "אירוח חינם", "Aviation": "תעופה"}
ax.barh([he(seg_he.get(i, i)) for i in seg.index], seg["mean"] * 100,
        color=[RED if v > 0.5 else ORANGE if v > 0.3 else GREEN for v in seg["mean"]])
for i, v in enumerate(seg["mean"] * 100):
    ax.text(v + 1, i, f"{v:.1f}%", va="center", color="white", fontsize=12, fontweight="bold")
ax.set_xlim(0, 75)
ax.set_xlabel(he("שיעור ביטולים (%)"), fontsize=13)
style(ax, "שיעור ביטולים לפי ערוץ שיווק")
save("cancel_by_segment.png")

print("Hebrew charts saved to", OUT, sorted(os.listdir(OUT)))
