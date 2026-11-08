"""Reproduces Figures 1-5 of the manuscript.

Figures 6 and 7 are written by Extensions.ipynb (results/extensions/figures).

Lending Club values are copied from the tables printed by Mega_Analysis.ipynb and Final_Analysis.ipynb
(see the executed notebooks in results/executed_notebooks; the source table is named next to each block).
Prosper values are read from results/prosper/tables/*.csv.
Run from this folder:  python make_paper_figures.py   ->  ../paper_figures/Figure{1..5}.{png,pdf}
"""
from pathlib import Path
import numpy as np, pandas as pd, matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parent.parent; T = ROOT / 'results' / 'prosper' / 'tables'; OUT = ROOT / 'paper_figures'; OUT.mkdir(exist_ok=True)
plt.rcParams.update({'font.size': 9, 'axes.linewidth': 0.7, 'font.family': 'DejaVu Sans'})
def save(fig, name): fig.savefig(OUT / f'{name}.png', dpi=300, bbox_inches='tight'); fig.savefig(OUT / f'{name}.pdf', bbox_inches='tight'); plt.close(fig)

# ---- Figure 1 --------------------------------------------------------------------------------------------------
# (a) Mega_Analysis M4a rolling origin (baseline, static coverage by calibration/test year)
# (b) coverage error vs calibration gap: Lending Club model zoo (Mega M1, 2015 columns) + Prosper validity/zoo tables
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={'width_ratios': [1, 1.15]})
yrs = [2012, 2013, 2014, 2015]; data = {'calibrated on 2011': [0.872, 0.889, 0.876, 0.862], 'calibrated on 2012': [None, 0.918, 0.903, 0.890], 'calibrated on 2013': [None, None, 0.886, 0.874]}
for (k, v), m in zip(data.items(), ['o', 's', '^']):
    ax[0].plot([y for y, c in zip(yrs, v) if c is not None], [c for c in v if c is not None], marker=m, ms=4, lw=1.2, label=k)
ax[0].axhline(0.9, c='k', ls=':', lw=0.9); ax[0].set_xticks(yrs); ax[0].set_ylim(0.85, 0.93); ax[0].set_xlabel('test year'); ax[0].set_ylabel('static coverage (target 0.90)'); ax[0].set_title('(a) Lending Club: coverage by test year', fontsize=9); ax[0].legend(fontsize=7, frameon=False, loc='upper right')
lc = [(-1.6, 0.918), (0.4, 0.903), (2.65, 0.890), (3.31, 0.8824), (3.21, 0.8831), (2.07, 0.8935), (2.07, 0.8910), (2.15, 0.8875), (2.22, 0.8966), (2.48, 0.8930), (2.33, 0.8911), (3.36, 0.8921), (3.45, 0.8911), (3.22, 0.8849)]
pb = [(-10.8, 0.914), (-11.5, 0.926), (-2.6, 0.896), (0.0, 0.889)]; pa = [(-11.1, 0.947), (-13.2, 0.955), (-15.2, 0.977), (-0.2, 0.887), (0.1, 0.878), (2.4, 0.855)]
for pts, lab, c, m in ((lc, 'Lending Club', '#1f77b4', 'o'), (pb + pa, 'Prosper', '#d62728', 's')):
    ax[1].scatter([p[0] for p in pts], [100 * (p[1] - 0.9) for p in pts], s=16, c=c, marker=m, label=lab, alpha=0.85)
allp = lc + pb + pa; gx = np.array([p[0] for p in allp]); gy = np.array([100 * (p[1] - 0.9) for p in allp]); b1, b0 = np.polyfit(gx, gy, 1); xs = np.linspace(-16, 4, 50); ax[1].plot(xs, b0 + b1 * xs, c='gray', lw=0.9, ls='--')
ax[1].axhline(0, c='k', lw=0.6); ax[1].axvline(0, c='k', lw=0.6); ax[1].set_xlabel('actual minus predicted default rate (points)'); ax[1].set_ylabel('static coverage minus 0.90 (points)'); ax[1].set_title('(b) coverage error follows the calibration gap', fontsize=9); ax[1].legend(fontsize=7, frameon=False, loc='upper right')
plt.tight_layout(); save(fig, 'Figure1')

# ---- Figure 2: alpha sensitivity (Lending Club: Mega M4c, 2015; Prosper: P7, design B, 2010) -------------------------
p10 = pd.read_csv(T / 'P7_alpha_sensitivity.csv'); p10 = p10[(p10.design == 'B') & (p10.period == '2010')]
lcA = {'static': {'cov': [.937, .890, .799], 'cd': [.566, .236, .000]}, 'class-conditional': {'cov': [.951, .904, .822], 'cd': [.913, .847, .733]}}
al = [0.05, 0.10, 0.20]; fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
for a_, title, get in ((ax[0], '(a) Lending Club, 2015', lambda m, k: lcA[m][k]), (ax[1], '(b) Prosper, 2010 (design B)', lambda m, k: list(p10[p10.method == m].sort_values('alpha')['cov' if k == 'cov' else 'cov_default']))):
    for m, c in (('static', '#1f77b4'), ('class-conditional', '#d62728')):
        a_.plot(al, get(m, 'cov'), marker='o', c=c, ls='-', label=f'{m}: all loans'); a_.plot(al, get(m, 'cd'), marker='s', c=c, ls='--', label=f'{m}: defaulters only')
    a_.plot(al, [1 - x for x in al], c='k', ls=':', lw=0.9, label='target'); a_.set_xticks(al); a_.set_xlabel('miscoverage level alpha'); a_.set_title(title, fontsize=9)
ax[0].set_ylabel('coverage'); ax[0].legend(fontsize=6.5, frameon=False, loc='lower left'); plt.tight_layout(); save(fig, 'Figure2')

# ---- Figure 3: label timing (Final_Analysis D1/D2 for Lending Club; Prosper P3, P9) ----------------------------------
lag = pd.read_csv(T / 'P3_label_lag_by_outcome.csv').set_index('outcome'); fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.1), gridspec_kw={'width_ratios': [1.1, 1]})
groups = [('Lending Club\ndefault', 20, 10, 34, '#8b1a1a'), ('Lending Club\nrepaid', 29, 9, 36, '#2a7f7f'), ('Prosper\ndefault', lag.loc['default', '50%'], lag.loc['default', '10%'], lag.loc['default', '90%'], '#8b1a1a'), ('Prosper\nrepaid', lag.loc['repaid', '50%'], lag.loc['repaid', '10%'], lag.loc['repaid', '90%'], '#2a7f7f')]
xs = np.arange(4); ax[0].bar(xs, [g[1] for g in groups], color=[g[4] for g in groups], width=0.6, alpha=0.9)
ax[0].errorbar(xs, [g[1] for g in groups], yerr=[[g[1] - g[2] for g in groups], [g[3] - g[1] for g in groups]], fmt='none', c='k', capsize=3, lw=0.9); ax[0].set_xticks(xs); ax[0].set_xticklabels([g[0] for g in groups], fontsize=7.5)
ax[0].set_ylabel('months from origination to known outcome'); ax[0].set_title('(a) outcome-dependent arrival (median, 10-90th pct.)', fontsize=8.5)
snap = ['LC\nDec 2013', 'LC\nDec 2014', 'LC\nDec 2015', 'Prosper\nJan 2010', 'Prosper\nJan 2011']; ev = [12.2, 12.9, 13.6, 34.2, 26.2]; kn = [18.2, 17.6, 15.8, 52.0, 42.8]; x = np.arange(5); w = 0.38
ax[1].bar(x - w / 2, ev, w, label='eventual (all loans)', color='#9ecae1'); ax[1].bar(x + w / 2, kn, w, label='among labels known at the time', color='#08519c'); ax[1].set_xticks(x); ax[1].set_xticklabels(snap, fontsize=7)
ax[1].set_ylabel('default rate (%)'); ax[1].set_title('(b) known labels over-represent defaults', fontsize=8.5); ax[1].legend(fontsize=7, frameon=False, loc='upper left'); plt.tight_layout(); save(fig, 'Figure3')

# ---- Figure 4: profit frontier (Lending Club: Final_Analysis A1; Prosper: P11) -------------------------------------
fr = pd.read_csv(T / 'P11_profit_frontier.csv'); fb = fr[fr.design == 'B']; sh = [1.0, 0.95, 0.90, 0.80]
lcr = {'default probability': [0, -37.0, -75.0, -158.1], 'expected return (applicant-only)': [0, -27.1, -58.2, -124.3], "lender's interest rate": [0, -45.7, -87.4, -192.1], 'hindsight oracle': [0, 478.0, 625.0, 618.9]}
prr = {'default probability': 'default prob (baseline)', 'expected return (applicant-only)': 'expected return, P3', "lender's interest rate": "lender's rate (lower=better)", 'hindsight oracle': 'hindsight oracle'}
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.2))
for (k, v), m in zip(lcr.items(), ['o', 's', '^', 'x']): ax[0].plot(sh, v, marker=m, ms=4, lw=1.2, label=k, ls='--' if 'oracle' in k else '-')
for (k, _), m in zip(lcr.items(), ['o', 's', '^', 'x']):
    r = fb[fb.ranker == prr[k]].copy(); r['share'] = np.round(r.share_approved.values, 2); vals = {s: g for s, g in zip(r.share, r.gain_vs_approve_all)}
    ax[1].plot(sh, [0 if s == 1.0 else vals[s] for s in sh], marker=m, ms=4, lw=1.2, ls='--' if 'oracle' in k else '-')
for a_, t in zip(ax, ('(a) Lending Club, 2013-2015', '(b) Prosper, 2010-2011Q1')): a_.axhline(0, c='k', lw=0.7); a_.set_xlim(1.01, 0.78); a_.set_xlabel('share of applicants approved'); a_.set_title(t, fontsize=9); a_.set_ylabel('gain over approving everyone\n($ per applicant)')
ax[0].legend(fontsize=6.8, frameon=False, loc='center left'); plt.tight_layout(); save(fig, 'Figure4')

# ---- Figure 5: reviewer break-even (Lending Club: Final_Analysis C1; Prosper: P12) ----------------------------------
lcb = {'Static': [(.650, .628, .671), (.689, .667, .710)], 'Bin-conditional': [(.668, .649, .687), (.710, .692, .729)], 'Class-conditional': [(.777, .750, .805), (.828, .802, .857)]}
be = pd.read_csv(T / 'P12_reviewer_breakeven.csv'); be = be[(be.design == 'B') & be.pipeline.str.startswith('baseline')]
nm = {'static': 'Static', 'bin-conditional': 'Bin-conditional', 'class-conditional': 'Class-conditional'}
fig, ax = plt.subplots(1, 2, figsize=(7.2, 3.0), sharey=True)
for a_, t, getter in ((ax[0], '(a) Lending Club', lambda p, c: lcb[p][c]), (ax[1], '(b) Prosper (design B)', lambda p, c: tuple(be[(be.policy == [k for k, v in nm.items() if v == p][0]) & (be.review_cost == [0.0, 0.01][c])][['breakeven_accuracy', 'ci_lo', 'ci_hi']].iloc[0]))):
    for j, p in enumerate(['Static', 'Bin-conditional', 'Class-conditional']):
        for c_, (col, off) in enumerate((('#4c72b0', -0.12), ('#dd8452', 0.12))):
            v = getter(p, c_); a_.errorbar(j + off, v[0], yerr=[[v[0] - v[1]], [v[2] - v[0]]], fmt='o', c=col, capsize=3, ms=4, label=['review cost 0%', 'review cost 1%'][c_] if j == 0 else None)
    a_.axhline(0.5, c='gray', ls=':', lw=0.8); a_.set_xticks(range(3)); a_.set_xticklabels(['Static', 'Bin-\nconditional', 'Class-\nconditional'], fontsize=8); a_.set_title(t, fontsize=9); a_.set_ylim(0.45, 1.02)
ax[0].set_ylabel('break-even reviewer accuracy'); ax[0].legend(fontsize=7, frameon=False, loc='upper left'); plt.tight_layout(); save(fig, 'Figure5')
print('wrote', sorted(p.name for p in OUT.iterdir()))
