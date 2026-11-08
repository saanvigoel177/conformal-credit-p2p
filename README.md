# Conformal prediction for credit decisions in peer-to-peer lending: replication package

**Paper:** *Uncertainty-aware credit decision systems in peer-to-peer lending: conformal prediction under temporal drift, label delay and human review*
**Authors:** Saanvi Goel and Syamasudha Veeragandham (corresponding author, syamasudha.v@vit.ac.in), School of Computer Science and Engineering, Vellore Institute of Technology, Vellore, India  
**Repository:** https://github.com/saanvigoel177/conformal-credit-p2p

This package holds everything needed to reproduce the paper's results from real loan data; nothing is simulated:
- the analysis code;
- the Lending Club data extracts we analysed, compressed;
- every result table, figure and executed notebook;
- a program that checks the paper's analytical results;
- SHA-256 checksums of every file.

## 1. Contents

```
README.md, LICENSE (MIT, code), LICENSE_results.txt (CC BY 4.0, results), requirements.txt, CHECKSUMS.txt
code/
  *.ipynb                       the nine analysis notebooks (stored without outputs)
  prepare_data.py               unpacks the Lending Club extracts and downloads and verifies the Prosper file
  check_analytical_results.py   checks every number the paper derives from Propositions 1-5 (needs numpy only)
  make_*.py                     helper scripts (figures, Lending Club payment and label-date extracts)
workspace/                      the folder the notebooks read from (set Q2_DIR to it)
  extra_data/*.csv.gz          Lending Club extracts (compressed) and raw_manifest.json (SHA-256 of the raw file and extracts)
  extra_data/prosper/          README.txt: where the Prosper file comes from and how to verify it
  lending_club_real_36m.csv.gz  15-column extract read by Conformal_Prediction_Credit_Risk_RUN.ipynb
  archive/                     place for the raw Lending Club file (only needed to rebuild the extracts)
results/
  lending_club_main/            tables and figures from Conformal_Prediction_Credit_Risk_RUN.ipynb
  feature_sets/                 tables and figures from Feature_Set_Analysis.ipynb
  prosper/                      tables from Prosper_Replication.ipynb (P1-P17)
  extensions/                   tables and figures from Extensions.ipynb
  audit/                        tables from Audit_and_Robustness.ipynb
  reviewer_checks/              tables and figures from Reviewer_Checks_v2.ipynb
  final_analysis/               section G tables from Final_Analysis.ipynb (G1-G5)
  executed_notebooks/           executed copies of the notebooks, with their printed outputs
paper_figures/                  Figure_1.png ... Figure_8.png, as in the manuscript
```

Three tables (`P1_data_summary_by_year`, `P2_breakeven` and `P3_label_lag_by_outcome`) are written by several notebooks. They are kept once, in `results/prosper/tables/`.

## 2. Data

| Data | In this package | How to get it |
|---|---|---|
| Lending Club extracts: `lending_club_36m_wide.csv` (582,113 resolved 36-month loans issued 2007-2015), `lending_club_60m_wide.csv`, `payments.csv`, `label_dates.csv`, `lending_club_real_36m.csv` | yes, as `.csv.gz` in `workspace/` | `python code/prepare_data.py` decompresses them and checks the SHA-256 of the wide extracts against `workspace/extra_data/raw_manifest.json` |
| Raw Lending Club file `accepted_2007_to_2018Q4.csv` (1.6 GB, SHA-256 `3eae03c2…d1f36a`) | no (size) | Kaggle, "All Lending Club loan data" (https://www.kaggle.com/datasets/wordsforthewise/lending-club, CC0), or the same file on Hugging Face (https://huggingface.co/datasets/codesignal/lending-club-loan-accepted, no login). Needed only to rebuild the extracts with `Extract_Extra_Data.ipynb`; put it in `workspace/archive/`. |
| Prosper snapshot `prosperLoanData.csv` (113,937 loans, SHA-256 `fce13408…`) | no (the snapshot carries no licence) | `python code/prepare_data.py` downloads it from the Udacity copy, converts its CRLF line endings, and checks the hash; see `workspace/extra_data/prosper/README.txt` |

The Lending Club extracts contain public loan-level data only. They keep the terms of their source (CC0 on the Kaggle page; the underlying data are published by Lending Club). If the rights holder objects to their redistribution, write to the corresponding author and they will be removed.

## 3. How to run

1. Install the packages in `requirements.txt` (Python 3.10 or newer).
2. Prepare the data: `python code/prepare_data.py` (it decompresses the Lending Club extracts, downloads the Prosper file, and checks the SHA-256 values).
3. Point the notebooks at the workspace, start Jupyter from the same shell, and run each notebook with **Run All**:
   - `export Q2_DIR="$PWD/workspace"`
   - Each notebook prints a list of failed sections at the end, and says which input is missing if any.
4. Check the analytical results with `python code/check_analytical_results.py`. It exits non-zero if any check fails, or if any of its planted faults goes undetected.

| Notebook | Needs | Time | Produces |
|---|---|---|---|
| `Extract_Extra_Data.ipynb` (optional) | raw Lending Club file | minutes | the wide Lending Club extracts |
| `Conformal_Prediction_Credit_Risk_RUN.ipynb` | `lending_club_real_36m.csv` | about 10 min | per-month-sample experiments; DtACI, recency-weighted and label-shift baselines |
| `Mega_Analysis.ipynb` | wide file, `payments.csv` | 2-5 min | model zoo, label delay, decisions on realised profit, robustness, 60-month replication |
| `Final_Analysis.ipynb` | wide file, `payments.csv`, `label_dates.csv` | 2-5 min | profit frontier, expected-return model, reviewer break-even, realistic label arrival, deployment-realistic training; section G: loan-level checks of the analytical results |
| `Prosper_Replication.ipynb` | Prosper file | about 15 min | second-lender replication; section 6: loan-level checks of the analytical results |
| `Extensions.ipynb` | wide file, Prosper file | about 3 min | segment coverage, monitoring, calibration age |
| `Audit_and_Robustness.ipynb` | wide file, Prosper file, `payments.csv` | about 3 min | data audit, independent recomputation, robustness, winsorised profit |
| `Feature_Set_Analysis.ipynb` | wide file | about 3 min | feature-set comparison, grade mix |
| `Reviewer_Checks_v2.ipynb` | wide file, Prosper file, `payments.csv`, `label_dates.csv` | about 5 min | inference and robustness checks (permutation tests, block intervals, gain and lag sweeps, number audit) |

## 4. Where each part of the paper comes from

| Paper | Source |
|---|---|
| Table 1; grade mix (Section 3.1); Section 4.4 expected-return and frontier results | `Final_Analysis` (`F1`, `A1`, `A2`, `B1`-`B3`); `Feature_Set_Analysis` (`F5_grade_mix_by_year`) |
| Tables 2-3; Table 4; uniform delays in Table 5; Table 8 | `Mega_Analysis` |
| Realistic arrival in Table 5; Table 6; Table 9; Table 13 | `Final_Analysis` (`D1`-`D3`, `C1`, `E1`) |
| Table 7 (DtACI, recency-weighted, label-shift weighted) | `Conformal_Prediction_Credit_Risk_RUN` (`19a_dtaci`, `19b_barber_weighted`, `15c_label_shift_conformal`) |
| Sections 3.2 and 4.5; Tables 10-12; Prosper rows of Tables 4, 6, 9 and 13 | `Prosper_Replication` (`P1`-`P13`) |
| Section 3.6 and loan-level checks in Sections 4.1, 4.2, 4.4 and 4.5 (ties, assumption A1, exact ranking cut, 1,000-repeat random halves, calibration size with an exchangeable benchmark, kappa) | `Final_Analysis` section G (`G1`-`G5`); `Prosper_Replication` section 6 (`P14`-`P17`) |
| Section 4.7; Tables 14-15; Figures 7-8 | `Extensions` (`E1`-`E3`) |
| Robustness paragraphs in Sections 4.1 and 4.5; winsorised profit (Section 4.4) | `Audit_and_Robustness` (`B`, `C1`-`C4`) |
| Inference checks cited in Sections 4.1-4.7 | `Reviewer_Checks_v2` (`R1`-`R17`) |
| Propositions 1-5 and the Appendix (numbers derived from them) | `code/check_analytical_results.py` |
| Figure 1; Figures 2 and 7; other figures | `code/make_framework_figure.py`; `code/make_revised_figures.py`; the notebooks and `code/make_paper_figures.py` (its output file names predate the final figure numbering; `paper_figures/` holds the final files) |

## 5. Reproducibility

* All nine notebooks were re-executed from the raw files in an independent environment: Python 3.14.7, numpy 2.5.4, pandas 3.1.1, scikit-learn 1.9.1, lightgbm 4.7.0, statsmodels 0.15.0 and seaborn 0.13.2.
  * The Lending Club raw file matched the SHA-256 in `raw_manifest.json`, and `Extract_Extra_Data` rebuilt both wide extracts byte for byte.
  * Every table and printed result matches the earlier runs, apart from three things:
    * the logistic-regression diagnostics in `P4_model_zoo` and `R2_gap_configs`, at the 4th-5th decimal, which move `R2_regressions` by at most 0.0016;
    * the printed form of the FICO-band labels in `E1_segment_coverage`;
    * the Lending Club profit checks in `Audit_and_Robustness`, which run once `payments.csv` exists.
* The executed copies of `Prosper_Replication`, `Final_Analysis` and `Audit_and_Robustness` come from that run; the other executed copies come from the earlier runs.
* An independently written split-conformal implementation (p-value form) reproduces 12 headline numbers (`results/audit/tables/B_manuscript_checks.csv`).
* Seeds are fixed (42) throughout.
  * The row-by-row online methods use a fixed-seed sample of at most 2,500 loans per issue month.
  * All intervals resample real loans.

## 6. Citation

Goel S, Veeragandham S (2026) Replication package for "Uncertainty-aware credit decision systems in peer-to-peer lending: conformal prediction under temporal drift, label delay and human review". GitHub. https://github.com/saanvigoel177/conformal-credit-p2p
