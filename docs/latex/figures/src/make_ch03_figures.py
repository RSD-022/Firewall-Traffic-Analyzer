"""Figures for Chapter 3 of the report (data and EDA).

Run from the repository root:  python docs/latex/figures/src/make_ch03_figures.py
Writes PNG files to docs/latex/figures/ch03/. Every number shown comes from data/raw/log2.csv.
"""
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[4]
OUT = ROOT / "docs" / "latex" / "figures" / "ch03"
OUT.mkdir(parents=True, exist_ok=True)

ACTIONS = ["allow", "deny", "drop", "reset-both"]
COLORS = {"allow": "#2a78d6", "deny": "#eb6834", "drop": "#1baf7a", "reset-both": "#eda100"}
plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False,
                     "axes.grid": True, "grid.color": "#e6e5e0", "axes.axisbelow": True})

raw = pd.read_csv(ROOT / "data" / "raw" / "log2.csv")
raw["Action"] = raw["Action"].str.strip().str.lower()
uniq = raw.drop_duplicates()


def save(fig, name):
    fig.savefig(OUT / f"{name}.png", dpi=200, bbox_inches="tight")
    plt.close(fig)
    print("saved", name)


# 1. Class distribution, original vs unique flows (log scale so reset-both is visible)
fig, ax = plt.subplots(figsize=(7.5, 3.6))
x = np.arange(len(ACTIONS)); w = 0.38
for k, (data, label, alpha) in enumerate([(raw, "original (65,532)", 1.0), (uniq, "unique flows (57,170)", 0.55)]):
    counts = data["Action"].value_counts().reindex(ACTIONS)
    bars = ax.bar(x + (k - 0.5) * w, counts, w - 0.03, color=[COLORS[a] for a in ACTIONS], alpha=alpha, label=label)
    for b, c in zip(bars, counts):
        ax.text(b.get_x() + b.get_width() / 2, c * 1.15, f"{c:,}", ha="center", fontsize=8)
ax.set_yscale("log"); ax.set_ylim(10, 2e5)
ax.set_xticks(x, ACTIONS); ax.set_ylabel("Number of flows (log scale)")
ax.legend(frameon=False, fontsize=8, loc="upper right")
ax.set_title("Distribution of firewall actions", loc="left")
save(fig, "class_distribution")

# 2. Skewness: raw vs log1p for three volume/time features
feats = ["Bytes", "Packets", "Elapsed Time (sec)"]
fig, axes = plt.subplots(2, 3, figsize=(11, 5.2))
for j, f in enumerate(feats):
    v = uniq[f]
    axes[0, j].hist(v, bins=60, color="#2a78d6")
    axes[0, j].set_title(f"{f} — raw (skew = {v.skew():.1f})", fontsize=9)
    axes[0, j].set_yscale("log")
    lv = np.log1p(v)
    axes[1, j].hist(lv, bins=60, color="#1baf7a")
    axes[1, j].set_title(f"log1p({f}) (skew = {lv.skew():.2f})", fontsize=9)
axes[0, 0].set_ylabel("count (log scale)"); axes[1, 0].set_ylabel("count")
fig.suptitle("Effect of the log1p transformation on skewed features (unique flows)", x=0.01, ha="left")
fig.tight_layout()
save(fig, "skewness_log_transform")

# 3. Box plots by action on the log scale
fig, axes = plt.subplots(1, 3, figsize=(11, 3.6))
for ax, f in zip(axes, feats):
    data = [np.log1p(uniq.loc[uniq["Action"] == a, f]) for a in ACTIONS]
    bp = ax.boxplot(data, patch_artist=True, showfliers=False, widths=0.6, medianprops={"color": "black"})
    for patch, a in zip(bp["boxes"], ACTIONS):
        patch.set_facecolor(COLORS[a]); patch.set_alpha(0.8)
    ax.set_xticks(range(1, 5), ACTIONS, fontsize=8)
    ax.set_title(f"log1p({f})", fontsize=9)
fig.suptitle("Distribution of volume and duration by action (outliers hidden)", x=0.01, ha="left")
fig.tight_layout()
save(fig, "boxplots_by_action")

# 4. Top destination ports by action (stacked, unique flows)
top = uniq["Destination Port"].value_counts().index[:12]
ct = (pd.crosstab(uniq["Destination Port"].where(uniq["Destination Port"].isin(top), -1), uniq["Action"])
      .reindex(columns=ACTIONS, fill_value=0))
ct = ct.loc[[p for p in top] + [-1]]
labels = [str(p) for p in top] + ["other"]
fig, ax = plt.subplots(figsize=(9, 4.4))
left = np.zeros(len(ct))
for a in ACTIONS:
    ax.barh(labels, ct[a], left=left, color=COLORS[a], label=a, height=0.7, edgecolor="white", linewidth=0.5)
    left += ct[a].to_numpy()
ax.invert_yaxis(); ax.set_xlabel("Number of unique flows"); ax.set_ylabel("Destination port")
ax.legend(frameon=False, ncol=4, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
ax.set_title("Twelve most frequent destination ports and the action applied", loc="left", pad=22)
save(fig, "destination_ports_by_action")

# 5. NAT source port status by action (row-normalised)
nat = np.where(uniq["NAT Source Port"] == 0, "NAT source port = 0", "NAT source port > 0")
ct = pd.crosstab(uniq["Action"], nat, normalize="index").reindex(ACTIONS)
fig, ax = plt.subplots(figsize=(7.5, 3.0))
left = np.zeros(len(ct))
for col, color in zip(ct.columns, ["#2a78d6", "#b8b7b2"]):
    ax.barh(ct.index, ct[col], left=left, color=color, label=col, height=0.6, edgecolor="white")
    for y, (l, v) in enumerate(zip(left, ct[col])):
        if v > 0.06:
            ax.text(l + v / 2, y, f"{v:.1%}", ha="center", va="center", fontsize=8,
                    color="white" if color == "#2a78d6" else "black")
    left += ct[col].to_numpy()
ax.invert_yaxis(); ax.set_xlim(0, 1); ax.set_xlabel("Share of the action's flows")
ax.legend(frameon=False, ncol=2, loc="lower center", bbox_to_anchor=(0.5, 1.0), fontsize=8)
save(fig, "nat_status_by_action")
