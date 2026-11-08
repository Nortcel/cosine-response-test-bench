#!/usr/bin/env python3
"""Reproduce the cosine-response analysis used in the HardwareX manuscript.

The retained 2017 workbooks contain three voltage scans per detector configuration.
Each workbook also includes a constructed -90 deg baseline row. This script reads the
three raw scans, prepends a 5.0 V baseline at -90 deg, computes the mean response,
normalises the mean-voltage response to its peak for the main table; individual-run normalisation is used for repeatability, compares it with cos(theta), and
exports metrics and publication figures.

Usage:
    python cosine_response_analysis_v2_1.py --input-dir ../data/workbook_cohort --output-dir output
"""
from __future__ import annotations

import argparse
import math
from pathlib import Path
from typing import Dict, List, Tuple

import numpy as np
import pandas as pd
from openpyxl import load_workbook
import matplotlib.pyplot as plt

CONFIGS: Dict[str, str] = {
    "PDB-C158-ND": "PDB-C158-ND Diode Measurement V1.xlsx",
    "PD438C/S46 (1080-1148-ND)": "1080-1148-ND Diode Measurement V1.xlsx",
    "ODD-3W-2-ND (left channel)": "ODD-3W-2-ND Diode Measurement V2 Left.xlsx",
    "ODD-3W-2-ND (single run)": "ODD-3W-2-ND Diode Measurement V1.xlsx",
    "PDB-C139-ND": "PDB-C139-ND Diode Measurement V1.xlsx",
    "ODD-3W-2-ND (right channel)": "ODD-3W-2-ND Diode Measurement V2 Right.xlsx",
    "ODD-5W-ND": "ODD-5W-ND Diode Measurement V1.xlsx",
    "PD333-3C/H0/L2 (1080-1143-ND)": "1080-1143-ND Diode Measurement V1.xlsx",
    "1080-1144-ND": "1080-1144-ND Diode Measurement V1.xlsx",
    "475-1077-ND": "475-1077-ND Diode Measurement V1.xlsx",
}

RUN_COLUMNS: Tuple[Tuple[str, str], ...] = (("B", "C"), ("G", "H"), ("L", "M"))
ANGLE_STEP_DEG = 1.8
N_POINTS = 101
VREF = 5.0


def read_raw_runs(path: Path) -> np.ndarray:
    """Return shape (3, 101), including a 5 V baseline at -90 deg."""
    wb = load_workbook(path, data_only=True, read_only=False)
    ws = wb.active
    runs: List[List[float]] = []
    for label_col, value_col in RUN_COLUMNS:
        values: List[float] = []
        for row in range(1, min(ws.max_row, 250) + 1):
            label = ws[f"{label_col}{row}"].value
            value = ws[f"{value_col}{row}"].value
            if isinstance(label, str) and "Voltage" in label and isinstance(value, (int, float)):
                values.append(float(value))
        if len(values) != 100:
            raise ValueError(f"{path.name}: expected 100 raw voltage values, found {len(values)}")
        runs.append([VREF] + values)
    return np.asarray(runs, dtype=float)


def response_from_voltage(voltage: np.ndarray) -> np.ndarray:
    response = np.abs(VREF - voltage)
    peak = np.max(response)
    if peak <= 0:
        raise ValueError("Response peak is zero; normalisation is undefined")
    return response / peak


def compute_metrics(angle: np.ndarray, mean_norm: np.ndarray) -> Dict[str, float]:
    ideal = np.cos(np.deg2rad(angle))
    mask80 = np.abs(angle) <= 80.0 + 1e-12
    error = mean_norm - ideal
    return {
        "RMSE full range": float(np.sqrt(np.mean(error**2))),
        "RMSE |theta| <= 80 deg": float(np.sqrt(np.mean(error[mask80]**2))),
        "MAE |theta| <= 80 deg": float(np.mean(np.abs(error[mask80]))),
        "Peak offset (deg)": float(angle[int(np.argmax(mean_norm))]),
        "Points |theta| <= 80 deg": int(np.sum(mask80)),
    }


def analyse(input_dir: Path):
    angle = np.linspace(-90.0, 90.0, N_POINTS)
    ideal = np.cos(np.deg2rad(angle))
    records = []
    detailed = {}

    for name, filename in CONFIGS.items():
        runs_v = read_raw_runs(input_dir / filename)
        runs_norm = np.vstack([response_from_voltage(v) for v in runs_v])
        mean_voltage = np.mean(runs_v, axis=0)
        mean_norm = response_from_voltage(mean_voltage)
        sd_norm = np.std(runs_norm, axis=0, ddof=1)
        metrics = compute_metrics(angle, mean_norm)

        run_rmse80 = []
        mask80 = np.abs(angle) <= 80.0 + 1e-12
        for run in runs_norm:
            run_rmse80.append(float(np.sqrt(np.mean((run[mask80] - ideal[mask80]) ** 2))))
        metrics["Run RMSE80 mean"] = float(np.mean(run_rmse80))
        metrics["Run RMSE80 SD"] = float(np.std(run_rmse80, ddof=1))
        records.append({"Detector configuration": name, **metrics})
        detailed[name] = {
            "angle": angle,
            "ideal": ideal,
            "runs_voltage": runs_v,
            "runs_norm": runs_norm,
            "mean_voltage": mean_voltage,
            "mean_norm": mean_norm,
            "sd_norm": sd_norm,
            "error": mean_norm - ideal,
        }

    summary = pd.DataFrame(records).sort_values("RMSE |theta| <= 80 deg").reset_index(drop=True)
    summary.insert(0, "Rank", np.arange(1, len(summary) + 1))
    return summary, detailed


def export_tables(summary: pd.DataFrame, detailed: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(output_dir / "detector_configuration_metrics.csv", index=False)
    sensitivity = []
    for name, d in detailed.items():
        error = d["mean_norm"] - d["ideal"]
        sensitivity.append({"Detector configuration": name,
            "RMSE full range including constructed endpoint": float(np.sqrt(np.mean(error**2))),
            "RMSE measured points only": float(np.sqrt(np.mean(error[1:]**2))),
            "Measured points": len(error)-1, "Constructed points": 1})
    pd.DataFrame(sensitivity).to_csv(output_dir / "Full_range_sensitivity.csv", index=False)


    for rank, (name, d) in enumerate(detailed.items(), 1):
        frame = pd.DataFrame({
            "detector_configuration": name,
            "source_workbook": CONFIGS[name],
            "angle_deg": d["angle"],
            "constructed_endpoint": np.arange(len(d["angle"])) == 0,
            "run_1_voltage": d["runs_voltage"][0],
            "run_2_voltage": d["runs_voltage"][1],
            "run_3_voltage": d["runs_voltage"][2],
            "mean_voltage": d["mean_voltage"],
            "normalised_response_of_mean_voltage": d["mean_norm"],
            "mean_of_individually_normalised_runs": d["runs_norm"].mean(axis=0),
            "sample_sd_of_individually_normalised_runs": d["sd_norm"],
        })
        frame.to_csv(output_dir / (str(rank).zfill(2) + "_processed.csv"), index=False)


def style_axis(ax):
    ax.set_xlim(-90, 90)
    ax.set_ylim(-0.04, 1.08)
    ax.set_xlabel(r"Incidence angle, $\theta$ (deg)")
    ax.set_ylabel("Normalised response")
    ax.grid(True, linewidth=0.5, alpha=0.35)
    ax.axvspan(-90, -80, alpha=0.08, color="0.4", zorder=0)
    ax.axvspan(80, 90, alpha=0.08, color="0.4", zorder=0)
    ax.axvline(-80, color="0.45", linestyle=":", linewidth=0.9)
    ax.axvline(80, color="0.45", linestyle=":", linewidth=0.9)


def export_figures(summary: pd.DataFrame, detailed: dict, output_dir: Path) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    palette = ["#0072B2", "#E69F00", "#009E73", "#D55E00", "#CC79A7"]
    styles = ["-", "--", "-.", ":", (0, (5, 2, 1, 2))]

    def overlay(names: List[str], stem: str):
        fig, ax = plt.subplots(figsize=(7.2, 4.7))
        first = detailed[names[0]]
        ax.plot(first["angle"], first["ideal"], color="black", linewidth=2.2, label="Ideal cosine")
        for i, name in enumerate(names):
            d = detailed[name]
            ax.plot(d["angle"], d["mean_norm"], color=palette[i], linestyle=styles[i], linewidth=1.8,
                    marker=["o", "s", "^", "D", "v"][i], markersize=3, markevery=8, label=name)
        style_axis(ax)
        ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.23), ncol=2, frameon=False, fontsize=8)
        fig.subplots_adjust(bottom=0.31, left=0.12, right=0.98, top=0.98)
        for ext in ("png", "pdf", "svg"):
            kwargs = {"dpi": 450} if ext == "png" else {}
            fig.savefig(output_dir / f"{stem}.{ext}", bbox_inches="tight", **kwargs)
        plt.close(fig)

    top = summary.head(5)["Detector configuration"].tolist()
    bottom = summary.tail(5)["Detector configuration"].tolist()
    overlay(top, "Figure_5_top_five_cosine_response")
    overlay(bottom, "Figure_6_bottom_five_cosine_response")

    fig, ax = plt.subplots(figsize=(7.2, 4.8))
    ordered = summary.sort_values("RMSE |theta| <= 80 deg", ascending=True)
    y = np.arange(len(ordered))
    bars = ax.barh(y, ordered["RMSE |theta| <= 80 deg"], color="#0072B2")
    ax.set_yticks(y)
    ax.set_yticklabels(ordered["Detector configuration"], fontsize=8)
    ax.invert_yaxis()
    ax.set_xlabel(r"RMSE relative to ideal cosine, $|\theta| \leq 80^{\circ}$")
    ax.grid(axis="x", linewidth=0.5, alpha=0.35)
    for b, val in zip(bars, ordered["RMSE |theta| <= 80 deg"]):
        ax.text(val + 0.006, b.get_y() + b.get_height()/2, f"{val:.4f}", va="center", fontsize=8)
    ax.set_xlim(0, max(ordered["RMSE |theta| <= 80 deg"]) * 1.18)
    fig.subplots_adjust(left=0.39, right=0.97, bottom=0.14, top=0.98)
    for ext in ("png", "pdf", "svg"):
        kwargs = {"dpi": 450} if ext == "png" else {}
        fig.savefig(output_dir / f"Figure_7_rmse_ranking.{ext}", bbox_inches="tight", **kwargs)
    plt.close(fig)

    # Repeatability of the two top-ranked configurations
    fig, ax = plt.subplots(figsize=(7.2, 4.7))
    colors = ["#0072B2", "#E69F00"]
    for color, name in zip(colors, top[:2]):
        d = detailed[name]
        centre = d["runs_norm"].mean(axis=0)
        ax.plot(d["angle"], centre, color=color, linewidth=2, label=name)
        lower = np.clip(centre - d["sd_norm"], 0, None)
        upper = centre + d["sd_norm"]
        ax.fill_between(d["angle"], lower, upper, color=color, alpha=0.18, linewidth=0)
    ideal_ref = detailed[top[0]]
    ax.plot(ideal_ref["angle"], ideal_ref["ideal"], color="black", linewidth=2.2, label="Ideal cosine")
    style_axis(ax)
    ax.legend(loc="upper center", bbox_to_anchor=(0.5, -0.18), ncol=2, frameon=False, fontsize=8)
    fig.subplots_adjust(bottom=0.27, left=0.12, right=0.98, top=0.98)
    for ext in ("png", "pdf", "svg"):
        kwargs = {"dpi": 450} if ext == "png" else {}
        fig.savefig(output_dir / f"Figure_S1_top_two_repeatability.{ext}", bbox_inches="tight", **kwargs)
    plt.close(fig)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input-dir", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    summary, detailed = analyse(args.input_dir)
    export_tables(summary, detailed, args.output_dir)
    export_figures(summary, detailed, args.output_dir)
    print(summary.to_string(index=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
