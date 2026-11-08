"""Figures 2 and 7 of the revised paper, from the reviewer-check tables (outputs_reviewer/tables)."""
import sys
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg'); matplotlib.rcParams['pdf.fonttype'] = 42
import matplotlib.pyplot as plt
T = Path(sys.argv[1]) if len(sys.argv) > 1 else Path('outputs_reviewer/tables'); OUT = Path(sys.argv[2]) if len(sys.argv) > 2 else Path('.')

# ---- Figure 2: (a) coverage by calibration year (Lending Club, models trained before each calibration year); (b) coverage error vs CHANGE in gap
R1 = pd.read_csv(T / 'R1_rolling_origin_training_years.csv'); R1 = R1[R1.overlap_train_calibration == 0]
D = pd.read_csv(T / 'R2_gap_configs.csv')
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={'width_ratios': [1, 1.15]})
yrs = [2012, 2013, 2014, 2015]
for (_, r), m in zip(R1.iterrows(), ['o', 's', '^']):
    v = [r.get(f'cov_{y}', np.nan) for y in yrs]; xs = [y for y, c in zip(yrs, v) if pd.notna(c)]; ys = [c for c in v if pd.notna(c)]
    ax[0].plot(xs, ys, marker=m, ms=4, lw=1.2, label=f"calibrated on {int(r.calibration_year)}")
ax[0].axhline(0.9, c='k', ls=':', lw=0.9); ax[0].set_xticks(yrs); ax[0].set_ylim(0.85, 0.93)
ax[0].set_xlabel('test year'); ax[0].set_ylabel('static coverage (target 0.90)'); ax[0].set_title('(a) Lending Club: coverage by test year', fontsize=9); ax[0].legend(fontsize=7, frameon=False, loc='upper right')
for port, c, m in (('Lending Club', '#1f77b4', 'o'), ('Prosper', '#d62728', 's')):
    s = D[D.portfolio == port]; ax[1].scatter(s['d_gap'], s['cov_err'], s=12, c=c, marker=m, alpha=0.8, label=port)
b1, b0 = np.polyfit(D['d_gap'], D['cov_err'], 1); xs = np.linspace(D['d_gap'].min(), D['d_gap'].max(), 50); ax[1].plot(xs, b0 + b1 * xs, c='gray', lw=0.9, ls='--')
ax[1].axhline(0, c='k', lw=0.6); ax[1].axvline(0, c='k', lw=0.6)
ax[1].set_xlabel('change in gap since calibration year (points)'); ax[1].set_ylabel('static coverage minus 0.90 (points)')
ax[1].set_title('(b) coverage error follows the change in gap', fontsize=9); ax[1].legend(fontsize=7, frameon=False, loc='upper right')
plt.tight_layout(); fig.savefig(OUT / 'Figure_2.pdf'); fig.savefig(OUT / 'Figure_2.png', dpi=600); plt.close(fig)
print(f'Figure 2b: {len(D)} combinations, slope {b1:.3f}')

# ---- Figure 7: segment coverage with month-block bootstrap intervals
S = pd.read_csv(T / 'R5_segment_coverage_block_bootstrap.csv'); S = S[S.segment != 'ALL']
fig, ax = plt.subplots(1, 2, figsize=(7.2, 4.6))
for a, (port, dk, title) in zip(ax, (('Lending Club', '-', 'Lending Club 2013–2015'), ('Prosper', 'B', 'Prosper, design B'))):
    s = S[(S.portfolio == port) & (S.design == dk)].sort_values('cov').reset_index(drop=True); y = np.arange(len(s))
    col = np.where(s['sig_bh'], '#1f77b4', '#9aa5b1')
    a.errorbar(s['cov'], y, xerr=[s['cov'] - s['ci_lo'], s['ci_hi'] - s['cov']], fmt='none', ecolor=col, elinewidth=1)
    a.scatter(s['cov'], y, s=10, c=col, zorder=3); a.axvline(0.9, c='k', ls=':', lw=0.9)
    a.set_yticks(y); a.set_yticklabels([f"{g}: {v}" for g, v in zip(s['segment'], s['value'])], fontsize=5)
    a.set_xlabel('static coverage (95% month-block bootstrap interval)', fontsize=7); a.set_title(title, fontsize=9); a.tick_params(axis='x', labelsize=7)
plt.tight_layout(); fig.savefig(OUT / 'Figure_7.pdf'); fig.savefig(OUT / 'Figure_7.png', dpi=600); plt.close(fig)
print('Figure 7 written')
