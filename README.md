# COMP34612 Group 12 Project

Adaptive Stackelberg pricing leader for the COMP34612 Computational Game Theory group project.

## Submission Files

- `game/comp34612_project_READY.ipynb` - final Colab notebook with our leaders inserted.
- `game/comp34612.zip` - project platform files required by the notebook.
- `COMP34612_Group12_Journal.md` - group journal draft for the written-materials component.
- `COMP34612_presentation.pptx` / `COMP34612_presentation.pdf` - final presentation files.

## Leader Mapping

| Leader | Followers | Strategy Space |
|---|---|---|
| `AdaptiveLeader` | MK1, MK2, MK4, MK5 | `[1.00, +inf)` |
| `BoundedAdaptiveLeader` | MK3, MK6 | `[1.00, 15.00]` |

The two leaders share the same adaptive learning core. `BoundedAdaptiveLeader` only adds the required upper bound for MK3/MK6-style followers.

## Method Summary

The leader:

1. loads the 100 days of historical data,
2. filters major outliers using median absolute deviation,
3. detects time trends,
4. fits a follower reaction function using OLS,
5. probes at `u_L = 12` on day 101,
6. updates online using a hybrid OLS/RLS scheme,
7. computes the Stackelberg-optimal leader price while respecting bounds.

Only `numpy` is required by our leader implementation.

## Running

Open `game/comp34612_project_READY.ipynb` in Google Colab and run the cells in order. If running from a cloned repository, the notebook can use `game/comp34612.zip` directly. If running in a separate Colab upload, upload `comp34612.zip` alongside the notebook.
