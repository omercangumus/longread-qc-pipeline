#!/usr/bin/env python3
"""
visualize.py
------------
Generates distribution plots and summary statistics from read_stats.csv output.

Plots generated:
  1. GC Content Distribution (histogram + KDE)
  2. Read Length Distribution (histogram, log-scale x-axis)
  3. Mean Quality Score Distribution (histogram + KDE)
  4. Combined Dashboard (2x2 grid with all metrics + stats table)

Usage:
    python scripts/visualize.py \
        --input results/stats/read_stats.csv \
        --outdir results/plots \
        --summary results/stats/summary_statistics.txt
"""

import argparse
import os
import sys
import numpy as np
import pandas as pd
import matplotlib
matplotlib.use('Agg')  # Non-interactive backend for server/pipeline use
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import seaborn as sns
from scipy import stats as scipy_stats


# ── Aesthetic settings ────────────────────────────────────────────────────────
sns.set_theme(style="whitegrid", palette="muted")
plt.rcParams.update({
    "font.family": "DejaVu Sans",
    "axes.titlesize": 14,
    "axes.labelsize": 12,
    "xtick.labelsize": 10,
    "ytick.labelsize": 10,
    "figure.dpi": 150,
})

COLORS = {
    "gc":      "#2196F3",   # Blue
    "length":  "#4CAF50",   # Green
    "quality": "#FF5722",   # Deep orange
}


def parse_args():
    parser = argparse.ArgumentParser(
        description="Generate QC visualizations from read statistics CSV."
    )
    parser.add_argument("--input",   "-i", required=True, help="Path to read_stats.csv")
    parser.add_argument("--outdir",  "-o", required=True, help="Output directory for plots")
    parser.add_argument("--summary", "-s", required=True, help="Path to summary statistics txt file")
    return parser.parse_args()


def load_data(csv_path: str) -> pd.DataFrame:
    """Load and validate the read statistics CSV."""
    print(f"[INFO] Loading data from: {csv_path}", file=sys.stderr)
    df = pd.read_csv(csv_path)
    required_cols = {"read_id", "read_length", "gc_content_pct", "mean_quality_score"}
    missing = required_cols - set(df.columns)
    if missing:
        print(f"[ERROR] Missing columns in CSV: {missing}", file=sys.stderr)
        sys.exit(1)
    print(f"[INFO] Loaded {len(df):,} reads.", file=sys.stderr)
    return df


def compute_summary_stats(df: pd.DataFrame) -> dict:
    """Compute mean, median, std, min, max, N50 for all three metrics."""
    summary = {}
    metrics = {
        "GC Content (%)":          "gc_content_pct",
        "Read Length (bp)":        "read_length",
        "Mean Quality Score (Q)":  "mean_quality_score",
    }
    for label, col in metrics.items():
        series = df[col].dropna()
        summary[label] = {
            "N":       len(series),
            "Mean":    round(series.mean(), 3),
            "Median":  round(series.median(), 3),
            "Std Dev": round(series.std(), 3),
            "Min":     round(series.min(), 3),
            "Max":     round(series.max(), 3),
        }
        # N50 only for read length
        if col == "read_length":
            sorted_lengths = np.sort(series.values)[::-1]
            cumsum = np.cumsum(sorted_lengths)
            n50 = sorted_lengths[np.searchsorted(cumsum, cumsum[-1] / 2)]
            summary[label]["N50"] = int(n50)
    return summary


def save_summary(summary: dict, output_path: str):
    """Write summary statistics to a text file."""
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, 'w') as f:
        f.write("=" * 60 + "\n")
        f.write("  LONG-READ QC — SUMMARY STATISTICS\n")
        f.write("=" * 60 + "\n\n")
        for metric, stats in summary.items():
            f.write(f"[ {metric} ]\n")
            f.write("-" * 40 + "\n")
            for key, val in stats.items():
                f.write(f"  {key:<12}: {val}\n")
            f.write("\n")
    print(f"[INFO] Summary statistics saved to: {output_path}", file=sys.stderr)

    # Also print to stdout
    with open(output_path, 'r') as f:
        print(f.read())


def plot_gc_content(df: pd.DataFrame, outdir: str):
    """Plot GC content distribution: histogram + KDE overlay."""
    fig, ax = plt.subplots(figsize=(8, 5))
    data = df["gc_content_pct"].dropna()

    ax.hist(data, bins=60, color=COLORS["gc"], alpha=0.7,
            edgecolor="white", linewidth=0.5, density=True, label="Histogram")

    kde = scipy_stats.gaussian_kde(data)
    x_range = np.linspace(data.min(), data.max(), 500)
    ax.plot(x_range, kde(x_range), color="#0D47A1", linewidth=2.5, label="KDE")

    ax.axvline(data.mean(),   color="red",    linestyle="--", linewidth=1.5,
               label=f"Mean = {data.mean():.1f}%")
    ax.axvline(data.median(), color="orange", linestyle=":",  linewidth=1.5,
               label=f"Median = {data.median():.1f}%")

    ax.set_title("GC Content Distribution", fontweight="bold")
    ax.set_xlabel("GC Content (%)")
    ax.set_ylabel("Density")
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = os.path.join(outdir, "gc_content_distribution.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved: {path}", file=sys.stderr)


def plot_read_length(df: pd.DataFrame, outdir: str):
    """Plot read length distribution on a log-scale x-axis (appropriate for long-reads)."""
    fig, ax = plt.subplots(figsize=(8, 5))
    data = df["read_length"].dropna()

    log_data = np.log10(data + 1)
    ax.hist(log_data, bins=80, color=COLORS["length"], alpha=0.7,
            edgecolor="white", linewidth=0.5, density=True)

    kde = scipy_stats.gaussian_kde(log_data)
    x_range = np.linspace(log_data.min(), log_data.max(), 500)
    ax.plot(x_range, kde(x_range), color="#1B5E20", linewidth=2.5, label="KDE")

    ax.axvline(np.log10(data.mean()),   color="red",    linestyle="--", linewidth=1.5,
               label=f"Mean = {data.mean():,.0f} bp")
    ax.axvline(np.log10(data.median()), color="orange", linestyle=":",  linewidth=1.5,
               label=f"Median = {data.median():,.0f} bp")

    # Set x-tick labels back to real values
    ticks = ax.get_xticks()
    ax.set_xticklabels([f"{10**t:,.0f}" if t > 0 else "1" for t in ticks])

    ax.set_title("Read Length Distribution (log\u2081\u2080 scale)", fontweight="bold")
    ax.set_xlabel("Read Length (bp) — log scale")
    ax.set_ylabel("Density")
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = os.path.join(outdir, "read_length_distribution.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved: {path}", file=sys.stderr)


def plot_mean_quality(df: pd.DataFrame, outdir: str):
    """Plot mean quality score distribution with Phred Q threshold lines."""
    fig, ax = plt.subplots(figsize=(8, 5))
    data = df["mean_quality_score"].dropna()

    ax.hist(data, bins=60, color=COLORS["quality"], alpha=0.7,
            edgecolor="white", linewidth=0.5, density=True, label="Histogram")

    kde = scipy_stats.gaussian_kde(data)
    x_range = np.linspace(data.min(), data.max(), 500)
    ax.plot(x_range, kde(x_range), color="#BF360C", linewidth=2.5, label="KDE")

    ax.axvline(data.mean(),   color="blue",   linestyle="--", linewidth=1.5,
               label=f"Mean = Q{data.mean():.1f}")
    ax.axvline(data.median(), color="purple", linestyle=":",  linewidth=1.5,
               label=f"Median = Q{data.median():.1f}")

    # ONT quality thresholds
    ax.axvline(7,  color="gray",  linestyle="-.", linewidth=1.0, alpha=0.7,
               label="Q7 (min ONT pass)")
    ax.axvline(10, color="black", linestyle="-.", linewidth=1.0, alpha=0.7,
               label="Q10 (high accuracy)")

    ax.set_title("Mean Read Quality Score Distribution", fontweight="bold")
    ax.set_xlabel("Mean Phred Quality Score (Q)")
    ax.set_ylabel("Density")
    ax.legend(fontsize=9)
    plt.tight_layout()
    path = os.path.join(outdir, "mean_quality_distribution.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved: {path}", file=sys.stderr)


def plot_combined_dashboard(df: pd.DataFrame, summary: dict, outdir: str):
    """2x2 dashboard: GC, Length, Quality distributions + summary stats table."""
    fig = plt.figure(figsize=(16, 12))
    gs = gridspec.GridSpec(2, 2, figure=fig, hspace=0.4, wspace=0.35)

    # ── Panel 1: GC Content ───────────────────────────────────────────────────
    ax1 = fig.add_subplot(gs[0, 0])
    gc_data = df["gc_content_pct"].dropna()
    ax1.hist(gc_data, bins=60, color=COLORS["gc"], alpha=0.75,
             edgecolor="white", linewidth=0.4, density=True)
    kde = scipy_stats.gaussian_kde(gc_data)
    xr = np.linspace(gc_data.min(), gc_data.max(), 400)
    ax1.plot(xr, kde(xr), color="#0D47A1", linewidth=2)
    ax1.axvline(gc_data.mean(), color="red", linestyle="--", linewidth=1.2,
                label=f"Mean={gc_data.mean():.1f}%")
    ax1.set_title("GC Content (%)", fontweight="bold")
    ax1.set_xlabel("GC Content (%)")
    ax1.set_ylabel("Density")
    ax1.legend(fontsize=8)

    # ── Panel 2: Read Length ──────────────────────────────────────────────────
    ax2 = fig.add_subplot(gs[0, 1])
    len_data = df["read_length"].dropna()
    log_len = np.log10(len_data + 1)
    ax2.hist(log_len, bins=80, color=COLORS["length"], alpha=0.75,
             edgecolor="white", linewidth=0.4, density=True)
    kde2 = scipy_stats.gaussian_kde(log_len)
    xr2 = np.linspace(log_len.min(), log_len.max(), 400)
    ax2.plot(xr2, kde2(xr2), color="#1B5E20", linewidth=2)
    ax2.axvline(np.log10(len_data.mean()), color="red", linestyle="--", linewidth=1.2,
                label=f"Mean={len_data.mean():,.0f}bp")
    ax2.set_title("Read Length Distribution (log\u2081\u2080)", fontweight="bold")
    ax2.set_xlabel("Read Length (bp, log scale)")
    ax2.set_ylabel("Density")
    ticks = ax2.get_xticks()
    ax2.set_xticklabels([f"{10**t:,.0f}" if t > 0 else "1" for t in ticks], fontsize=8)
    ax2.legend(fontsize=8)

    # ── Panel 3: Mean Quality ─────────────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 0])
    q_data = df["mean_quality_score"].dropna()
    ax3.hist(q_data, bins=60, color=COLORS["quality"], alpha=0.75,
             edgecolor="white", linewidth=0.4, density=True)
    kde3 = scipy_stats.gaussian_kde(q_data)
    xr3 = np.linspace(q_data.min(), q_data.max(), 400)
    ax3.plot(xr3, kde3(xr3), color="#BF360C", linewidth=2)
    ax3.axvline(q_data.mean(), color="blue", linestyle="--", linewidth=1.2,
                label=f"Mean=Q{q_data.mean():.1f}")
    ax3.axvline(10, color="black", linestyle="-.", linewidth=1.0, alpha=0.6,
                label="Q10 threshold")
    ax3.set_title("Mean Quality Score (Phred Q)", fontweight="bold")
    ax3.set_xlabel("Mean Phred Q Score")
    ax3.set_ylabel("Density")
    ax3.legend(fontsize=8)

    # ── Panel 4: Summary Statistics Table ────────────────────────────────────
    ax4 = fig.add_subplot(gs[1, 1])
    ax4.axis("off")
    table_data = []
    col_labels = ["Metric", "Mean", "Median", "Std", "Min", "Max"]
    for metric, stats in summary.items():
        short_name = metric.split("(")[0].strip()
        row = [
            short_name,
            str(stats["Mean"]),
            str(stats["Median"]),
            str(stats["Std Dev"]),
            str(stats["Min"]),
            str(stats["Max"]),
        ]
        table_data.append(row)

    table = ax4.table(
        cellText=table_data,
        colLabels=col_labels,
        loc="center",
        cellLoc="center"
    )
    table.auto_set_font_size(False)
    table.set_fontsize(9)
    table.scale(1.2, 1.8)
    # Style header row
    for j in range(len(col_labels)):
        table[0, j].set_facecolor("#37474F")
        table[0, j].set_text_props(color="white", fontweight="bold")
    ax4.set_title("Summary Statistics", fontweight="bold", pad=20)

    fig.suptitle("Long-Read Sequencing QC Dashboard", fontsize=18, fontweight="bold", y=1.01)
    path = os.path.join(outdir, "combined_dashboard.png")
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    print(f"[INFO] Saved: {path}", file=sys.stderr)


def main():
    args = parse_args()
    os.makedirs(args.outdir, exist_ok=True)

    df = load_data(args.input)
    summary = compute_summary_stats(df)

    save_summary(summary, args.summary)
    plot_gc_content(df, args.outdir)
    plot_read_length(df, args.outdir)
    plot_mean_quality(df, args.outdir)
    plot_combined_dashboard(df, summary, args.outdir)

    print("\n[INFO] All visualizations complete.", file=sys.stderr)


if __name__ == "__main__":
    main()
