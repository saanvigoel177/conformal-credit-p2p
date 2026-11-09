"""Checks for the analytical results in Section 3.6 and the Appendix, and for the numbers
the paper derives from them.

Inputs are copied from named files. Most come from the replication package (results/...).
Two come from the manuscript itself, and are marked: defaulter coverage by year (Table 11)
and the break-even targets (Table 7).

Checks of stated numbers have a failure control, a planted fault that must make them fail.
A few structural checks (simulated stability, the Beta law at one n) have none. The script exits
non-zero if any check fails or any control passes.

Scope: these checks test the arithmetic and the claims the paper makes from the
propositions. Propositions 1 and 3 are proved in the Appendix. Proposition 2 is exact
only for its linear model. Whether real ACI follows that model (constant kappa, fixed
target, no clipping) is not tested here, because the loan-level predictions and the
alpha_t paths are not saved in the package.

Run:  python check_analytical_results.py      (needs numpy)
"""
import math
import sys
import numpy as np

failures = []
def check(name, ok):
    print(('PASS ' if ok else 'FAIL ') + name)
    if not ok: failures.append(name)
def control(name, still_passes):
    print(('CONTROL OK  ' if not still_passes else 'CONTROL BAD ') + name)
    if still_passes: failures.append('control: ' + name)

# ======================================================= Proposition 1
# (a) Identity (4) with eps0 = 0.
#   pi:  reviewer_checks/tables/R17_number_audit.csv (recomputed)
#   c1:  manuscript Table 11, row "Lending Club, all labels" (3 decimals)
#   Cov: reviewer_checks/tables/R4_permutation_tests.csv (observed, baseline)
#   eps0 = 0: reviewer_checks/tables/R16_empty_set_shares.csv (static LC: empty 0, only_1 0)
lc = {2013: (0.1204, 0.317, 0.91778), 2014: (0.1332, 0.268, 0.90252), 2015: (0.1440, 0.236, 0.88995)}
TOL = 0.0002          # observed residuals are at most 3e-5; a 0.01 error in c1 moves Cov by >= 0.0012
def identity_ok(shift=0.0):
    return all(abs((1 - pi * (1 - (c1 + shift))) - cov) <= TOL for pi, c1, cov in lc.values())
check('P1 identity (4), Lending Club 2013-2015, to within 0.001 as stated', identity_ok())
control('P1 identity with defaulter coverage shifted by 0.01', identity_ok(shift=0.01))

# (b) Formula (5) itself, Prosper design B, selected pipeline, calibration year 2009
#   prosper/tables/P5_validity.csv: N=2047, actual_default=0.15193, cov_default=0.34727, share_reject_only=0.0
n, pi_hat, alpha = 2047, 0.15193, 0.10
n_def = round(n * pi_hat)                                # 311 defaulters
def c1_formula5(kfun):
    k = kfun(n, alpha)
    return 1 - (1 - k / n) / (n_def / n)
k_ok  = lambda n, a: math.ceil((n + 1) * (1 - a))      # equation (1)
k_bad = lambda n, a: math.ceil(n * (1 - a))            # planted fault: drop the +1
print(f'  Prosper B selected 2009: n={n}, defaulters={n_def}, k={k_ok(n, alpha)}, c1 by (5) = {c1_formula5(k_ok):.5f} (P5: 0.34727)')
check('P1 formula (5) gives Prosper in-sample defaulter coverage 0.347', abs(c1_formula5(k_ok) - 0.34727) < 5e-5)
control('P1 formula (5) with k = ceil(n(1-alpha)) instead of (1)', abs(c1_formula5(k_bad) - 0.34727) < 5e-5)

# (c) Lending Club 2012: 1 - alpha/pi_hat ~ 0.25 as stated; case (ii) at alpha = 0.20
pi12 = 0.1338                                            # R17: LC 2012 default rate
check('P1 Lending Club 2012: 1 - 0.10/0.134 rounds to 0.25', round(1 - 0.10 / pi12, 2) == 0.25)
control('P1 Lending Club 2012 with alpha = 0.05 instead of 0.10', round(1 - 0.05 / pi12, 2) == 0.25)
check('P1(ii) condition alpha >= pi_hat + 1/n holds at alpha = 0.20 (LC, n = 41,703)', 0.20 >= pi12 + 1 / 41703)
control('P1(ii) condition at alpha = 0.10', 0.10 >= pi12 + 1 / 41703)

# ======================================================= Corollary 1
# Decomposition values printed in Section 4.1 (c1_cal := 1 - alpha/pi_hat, Cov_cal := 0.90).
# The sum equals (4) by construction; the check here is that the PRINTED split is what the
# formula gives.
c1_cal = 1 - 0.10 / pi12
printed = {2015: (-0.76, -0.24), 2013: (1.0, 0.8)}       # Section 4.1, points, as rounded in the text
def split(yr, swap=False):
    pi_t, c1_t, _ = lc[yr]
    base = -(pi_t - pi12) * (1 - c1_cal); disc = pi_t * (c1_t - c1_cal)
    return (100 * disc, 100 * base) if swap else (100 * base, 100 * disc)
def printed_ok(swap=False):
    out = True
    for yr, (b, d) in printed.items():
        cb, cd = split(yr, swap); dec = 2 if yr == 2015 else 1
        out &= round(cb, dec) == b and round(cd, dec) == d
    return out
for yr in printed: print(f'  {yr}: base-rate {split(yr)[0]:+.2f}, defaulter-coverage {split(yr)[1]:+.2f} points')
check('C1 split printed in Section 4.1 (2015: -0.76/-0.24; 2013: +1.0/+0.8)', printed_ok())
control('C1 split with the two terms swapped', printed_ok(swap=True))

# Additional file 2, Note S6: per point of default-rate change the annual response is -1.33 (2013) and -0.99 (2015)
resp = {yr: (lc[yr][2] - 0.90) / (lc[yr][0] - pi12) for yr in (2013, 2015)}
check('C1 annual response per point of default rate: -1.33 (2013), -0.99 (2015)',
      round(resp[2013], 2) == -1.33 and round(resp[2015], 2) == -0.99)
control('C1 annual response computed against 0.89 instead of Cov_cal = 0.90',
        round((lc[2013][2] - 0.89) / (lc[2013][0] - pi12), 2) == -1.33)

# ======================================================= Proposition 3
# Per-applicant components: reviewer_checks/tables/R14_breakeven_sensitivity_specificity.csv,
# note rows. In the R14 code, R = profit of auto-rejected loans (used as A), P0 = profit of
# referred repayers (G), P1 = profit of referred defaulters (L = -P1), F = funded amount of
# referred loans. Targets: manuscript Table 7. Table 7 was itself computed with this formula,
# so this check tests transcription and arithmetic, not an independent derivation.
comp = {
    'LC static':             (0.0,  259.1, 139.7, 1552, 0.650, 0.689),
    'LC bin-conditional':    (0.0,  378.2, 188.2, 2420, 0.668, 0.710),
    'LC class-conditional':  (87.5, 1025.7, 407.6, 7350, 0.777, 0.828),
    'Prosper B static':      (5.4,  422.2, 185.0, 1643, 0.704, 0.731),
    'Prosper B bin-cond.':   (10.4, 495.0, 197.7, 1994, 0.730, 0.758),
    'Prosper B class-cond.': (97.6, 610.6, 183.2, 2899, 0.892, 0.929),
}
def qstar(A, G, L, F, c, drop_A=False): return (G + (0 if drop_A else A) + c * F) / (G + L)
def table9_ok(drop_A=False):
    return all(abs(qstar(A, G, L, F, 0, drop_A) - q0) <= 0.0015 and abs(qstar(A, G, L, F, 0.01, drop_A) - q1) <= 0.0015
               for A, G, L, F, q0, q1 in comp.values())
check('P3 equation (9) reproduces Table 7 (6 policies x 2 costs)', table9_ok())
control('P3 equation (9) with the auto-reject term A dropped', table9_ok(drop_A=True))
A, G, L, F = comp['LC static'][:4]
check('P3 asymmetric break-even, LC static: q0=0.7 -> 0.557, q0=0.9 -> 0.186 (R14: 0.55662, 0.18554)',
      abs((0.3 * G + A) / L - 0.55662) <= 0.002 and abs((0.1 * G + A) / L - 0.18554) <= 0.002)
control('P3 asymmetric break-even with q0 and 1 - q0 swapped',
        abs((0.7 * G + A) / L - 0.55662) <= 0.002 and abs((0.9 * G + A) / L - 0.18554) <= 0.002)
check('P3 "A + cF >= 0 in all six policies" (Section 3.6)', all(v[0] >= 0 and v[3] >= 0 for v in comp.values()))
perfect = (('LC static', 139.66), ('LC bin-conditional', 188.23), ('LC class-conditional', 320.09))
check('P3 perfect-reviewer gain L - A, LC static/bin/class = 139.66/188.23/320.09 (Section 4.4)',
      all(abs((comp[k][2] - comp[k][0]) - v) <= 0.1 for k, v in perfect))
control('P3 perfect-reviewer gain computed as L + A', all(abs((comp[k][2] + comp[k][0]) - v) <= 0.1 for k, v in perfect))

# ======================================================= Proposition 2
# Linear model x_{m+1} = x_m - a x_{m-k} with a = eta*kappa and k = d - 1.
# Timing (verified by reading aci_reveal in Reviewer_Checks_v2.ipynb; reveal = issue month + d,
# revealed when reveal <= current month, before the month's first loan is scored):
# alpha_m = alpha_{m-1} + eta (alpha - err_{m-d})  =>  lag k = d - 1.
def roots(a, k):
    c = np.zeros(k + 2); c[0] = 1.0; c[1] = -1.0; c[-1] = a
    return np.roots(c)
def rho(a, k): return max(abs(roots(a, k)))
def numeric_threshold(k):
    lo, hi = 1e-6, 2.0
    for _ in range(60):
        mid = (lo + hi) / 2
        lo, hi = (mid, hi) if rho(mid, k) < 1 else (lo, mid)
    return (lo + hi) / 2
closed = lambda k: 2 * math.cos(k * math.pi / (2 * k + 1))
wrong  = lambda k: 2 * math.cos(k * math.pi / (2 * k + 2))     # planted fault: close but wrong denominator
ks = range(1, 31)
num = {k: numeric_threshold(k) for k in ks}
check('P2 Levin-May threshold equals numeric root threshold, k = 1..30', all(abs(num[k] - closed(k)) < 1e-6 for k in ks))
control('P2 threshold against 2cos(k pi/(2k+2))', all(abs(num[k] - wrong(k)) < 1e-6 for k in ks))
bound = lambda d: closed(d - 1)
stated = {6: 0.285, 12: 0.136, 24: 0.067}
check('P2 bounds stated in Section 3.6 (0.285, 0.136, 0.067)', all(round(bound(d), 3) == v for d, v in stated.items()))
control('P2 bounds with lag k = d instead of d - 1', all(round(closed(d), 3) == v for d, v in stated.items()))

def simulate(a, k, steps):
    x = [1.0] * (k + 1)
    for _ in range(steps): x.append(x[-1] - a * x[-1 - k])
    return max(abs(v) for v in x[-(2 * k + 2):])
for d in (6, 12):
    k = d - 1
    check(f'P2 simulation, delay {d}: decays at 0.9x bound', simulate(0.9 * bound(d), k, 6000) < 1e-3)
    check(f'P2 simulation, delay {d}: grows at 1.1x bound', simulate(1.1 * bound(d), k, 6000) > 1e3)

# Decay times stated in Section 3.6: gain 0.25 at d=6 -> modulus 0.983, about five years;
# fastest damping at gain ~0.067 (d=6) and ~0.032 (d=12), 5.5 and 11.5 months.
tau = lambda a, k: -1 / math.log(rho(a, k))
grid = np.linspace(0.001, 0.3, 6000)
best = {d: grid[np.argmin([rho(a, d - 1) for a in grid])] for d in (6, 12)}
print(f'  d=6, gain 0.25: modulus {rho(0.25, 5):.3f}, decay time {tau(0.25, 5):.1f} months')
print(f'  fastest damping: d=6 gain {best[6]:.3f} ({tau(best[6], 5):.1f} months); d=12 gain {best[12]:.3f} ({tau(best[12], 11):.1f} months)')
check('P2 d=6, gain 0.25: modulus 0.983 and decay time 4-6 years',
      round(rho(0.25, 5), 3) == 0.983 and 48 <= tau(0.25, 5) <= 72)
control('P2 decay time 1/gain (the withdrawn claim) for d=6, gain 0.25', 48 <= 1 / 0.25 <= 72)
check('P2 fastest damping: ~0.067 / 5.5 months (d=6), ~0.032 / 11.5 months (d=12)',
      abs(best[6] - 0.067) < 0.002 and round(tau(best[6], 5), 1) == 5.5 and
      abs(best[12] - 0.032) < 0.002 and round(tau(best[12], 11), 1) == 11.5)
control('P2 fastest damping evaluated with lag k = d', abs(grid[np.argmin([rho(a, 6) for a in grid])] - 0.067) < 0.002)
check('P2 gain 2.5 is 9 to 37 times the bound for 6- to 24-month delays',
      round(2.5 / bound(6)) == 9 and round(2.5 / bound(24)) == 37)

# Empirical statements in Section 4.3 and Additional file 2, Note S3 (reviewer_checks/tables/R9_gain_sweep.csv, LC, pooled column).
# These describe the sweep relative to gain 0.01, as the text says. They do not test
# Proposition 2: the grid is too coarse to locate a threshold.
sweep = {6:  {0.01: 0.90563, 0.03: 0.90319, 0.1: 0.89772, 0.25: 0.89992, 0.5: 0.87758, 1.0: 0.85024, 2.0: 0.78616, 4.0: 0.66194},
         12: {0.01: 0.90608, 0.03: 0.90378, 0.1: 0.89491, 0.25: 0.88129, 0.5: 0.87471, 1.0: 0.85632, 2.0: 0.81476, 4.0: 0.73708}}
def sweep_ok(scale=1.0):
    ok = True
    for d, sw in sweep.items():
        b = scale * bound(d); ref = sw[0.01]
        ok &= max(abs(ref - v) for g, v in sw.items() if g < b) <= 0.0115          # "within 1.1 points"
        ok &= min(ref - v for g, v in sw.items() if g >= 2 * b) >= 0.030           # "3 points or more"
    return ok
check('Sweep: within 1.1 points below the bound; 3+ points lower at >= 2x the bound (vs gain 0.01)', sweep_ok())
control('Sweep statement with bounds doubled', sweep_ok(scale=2.0))

# ======================================================= Proposition 4
# Standard deviation of empirical coverage under exchangeability, random halves:
# Var = k(n+1-k)/((n+1)^2 (n+2)) + alpha(1-alpha)/m, with n = N//2 calibration and m = N - n test loans.
# Observed sds: Mega_Analysis_executed.ipynb section 4b (LC 2012: 0.0026; LC 2015: 0.0012; 50 repeats)
# and prosper/tables/P6_random_split_controls.csv (50 repeats; designs A and B share the same splits).
def sd_halves(N, a=0.10, drop_test=False):
    n = N // 2; m = N - n; k = math.ceil((n + 1) * (1 - a))
    v = k * (n + 1 - k) / ((n + 1) ** 2 * (n + 2)) + (0 if drop_test else a * (1 - a) / m)
    return math.sqrt(v)
controls = [('LC 2012', 41703, 0.0026), ('LC 2015', 263943, 0.0012), ('Prosper B 2009', 2047, 0.01354),
            ('Prosper B 2010', 5599, 0.00847), ('Prosper B 2011Q1', 1375, 0.01771), ('Prosper A 2008', 11551, 0.00566),
            ('Prosper A 2009', 2047, 0.01256), ('Prosper A 2010', 5599, 0.00794), ('Prosper A 2011Q1', 1375, 0.01488)]
ratio = {nm: obs / sd_halves(N) for nm, N, obs in controls}
for nm, N, obs in controls: print(f'  {nm}: predicted sd {sd_halves(N):.5f}, observed {obs}, ratio {ratio[nm]:.3f}')
pros = [v for k_, v in ratio.items() if k_.startswith('Prosper')]
# Additional file 2, Note S5: Prosper 50-repeat ratios 0.92-1.10, within about one SE.
check('P4 Prosper 50-repeat ratios 0.92-1.10', round(min(pros), 2) == 0.92 and round(max(pros), 2) == 1.10)
control('P4 Prosper 50-repeat ratios with the test term dropped', round(min(v / sd_halves(N, drop_test=True) * sd_halves(N) for (_, N, _), v in zip(controls[2:], pros)), 2) == 0.92)
# "within about one standard error": relative SE of an sd from 50 repeats is about 1/sqrt(98) = 0.10
se = 1 / math.sqrt(2 * 49)
check('P4 Prosper ratios within about one SE (|ratio - 1| <= 1.05 SE)', all(abs(v - 1) <= 1.05 * se for v in pros))
control('P4 Prosper ratios against half an SE', all(abs(v - 1) <= 0.5 * se for v in pros))

# Monte Carlo of the Beta law itself (independent of the data): U_(k) of n uniforms
rng = np.random.default_rng(0); n_mc = 2047; k_mc = math.ceil((n_mc + 1) * 0.9)
U = np.sort(rng.random((20000, n_mc)), axis=1)[:, k_mc - 1]
beta_sd = math.sqrt(k_mc * (n_mc + 1 - k_mc) / ((n_mc + 1) ** 2 * (n_mc + 2)))
check('P4 Beta(k, n+1-k) law: simulated mean and sd of U_(k) match (n = 2047)',
      abs(U.mean() - k_mc / (n_mc + 1)) < 2e-4 and abs(U.std() / beta_sd - 1) < 0.03)
control('P4 simulated mean against a wrong order statistic, k + 3', abs(U.mean() - (k_mc + 3) / (n_mc + 1)) < 2e-4)

# ======================================================= Loan-level checks on Lending Club (Sections 4.1, 4.2, 4.4)
# Copied from Final_Analysis.ipynb section G tables: G1_ties_and_A1, G2_prop5_exact_cut, G3_prop4_random_halves,
# G4_calibration_size_with_benchmark, G5_kappa (results/final_analysis/tables/).
g1_distinct = [0.99058, 0.98503, 1.0, 1.0]; g1_above_half_cal_baseline = 0.00096; g1_eps0_cal = [0.0, 0.0]
check('G1: more than 98.5% distinct; 0.10% of 2012 loans above 1/2 (baseline); eps0 = 0 for both pipelines',
      min(g1_distinct) > 0.985 and round(100 * g1_above_half_cal_baseline, 2) == 0.10 and all(e == 0 for e in g1_eps0_cal))
control('G1 with the withdrawn Prosper wording "more than 99.8% distinct"', min(g1_distinct) > 0.998)
g2 = [(True, -119.46193, -119.46193), (True, -705.60346, -705.60346), (True, -124.17628, -124.17628), (True, -798.5342, -798.5342)]
check('G2: Lending Club conformal approved sets identical to the ranking cut; gains equal to the cent (-119.46, -705.60, Table 6)',
      all(s_ and abs(a_ - b_) < 0.005 for s_, a_, b_ in g2) and round(g2[0][1], 2) == -119.46 and round(g2[1][1], 2) == -705.60)
control('G2 linear interpolation of the 90%/80% frontier points (-120.07) as the exact value', abs(-120.07 - g2[0][1]) < 0.005)
g3 = {'2012': (0.0029, 0.00294, 0.98809), '2015': (0.00118, 0.00117, 1.00687)}
check('G3: 1,000 halves: sd 0.0029 / 0.0012 against predictions 0.0029 / 0.0012, ratios 0.99 and 1.01',
      [round(g3[k][0], 4) for k in g3] == [0.0029, 0.0012] and [round(g3[k][1], 4) for k in g3] == [0.0029, 0.0012]
      and [round(g3[k][2], 2) for k in g3] == [0.99, 1.01])
check('G3: 50-repeat value 0.0026 is within two SE (rel. SE 0.10) of 0.0029', abs(0.0026 / 0.00294 - 1) <= 2 * (1 / math.sqrt(98)))
control('G3: 50-repeat value judged with the 1,000-repeat SE (0.022)', abs(0.0026 / 0.00294 - 1) <= 2 * 0.0224)
g4_bench, g4_test = 1.06476, [0.84964, 0.87155, 0.85389]
check('G4: benchmark 1.06 times prediction; test years 0.85-0.87', round(g4_bench, 2) == 1.06 and round(min(g4_test), 2) == 0.85 and round(max(g4_test), 2) == 0.87)
control('G4 claim "test years equal the benchmark within 2 SE"', all(abs(v - g4_bench) <= 2 * 0.0224 for v in g4_test))
g5_alpha = [0.85362, 0.87613, 0.86952]; g5_se = [0.02993, 0.02653, 0.02663]; g5_bench = (1.00588, 0.05059); g5_abar_pooled = (0.86436, 0.0235)
check('G5: kappa at alpha 0.85-0.88 (SE 0.03); benchmark 1.01 (0.05); kappa at alpha-bar pooled 0.86 (0.02)',
      round(min(g5_alpha), 2) == 0.85 and round(max(g5_alpha), 2) == 0.88 and all(round(v, 2) == 0.03 for v in g5_se)
      and [round(v, 2) for v in g5_bench] == [1.01, 0.05] and [round(v, 2) for v in g5_abar_pooled] == [0.86, 0.02])
control('G5 benchmark judged equal to the test-year kappa', abs(g5_bench[0] - min(g5_alpha)) <= g5_bench[1])
check('G4/G5 agree: calibration-size ratios and direct kappa within 0.03 in each test year',
      all(abs(a_ - b_) <= 0.03 for a_, b_ in zip(g4_test, g5_alpha)))
k_lc = g5_abar_pooled[0]
check('P2 on Lending Club: bound for a 6-month delay about 0.33; gain 0.25 damps over about 2.3 years',
      round(bound(6) / k_lc, 2) == 0.33 and round(tau(0.25 * k_lc, 5) / 12, 1) == 2.3)
control('P2 on Lending Club with kappa = 1 (bound 0.28, five years)', round(bound(6) / 1.0, 2) == 0.33)
check('Limitations: kappa bootstrap SEs range 0.02-0.33 across both lenders',
      round(min(0.0235, 0.02487, *g5_se), 2) == 0.02 and round(0.32598, 2) == 0.33)

# Section 4.4 and limitations: winsorised / trimmed profit on Lending Club
# (results/audit/tables/C4_profit_outliers.csv, Lending Club rows)
c4 = {'raw': (-119.46193, -75.04964), 'wins': (-123.66376, -77.96842), 'trim': (-127.40287, -80.58143)}
check('C4: static referrals rejected $119 raw, $124 winsorised, $127 trimmed; worst 10% out $75, $78, $81',
      [round(-c4[k][0]) for k in ('raw', 'wins', 'trim')] == [119, 124, 127] and [round(-c4[k][1]) for k in ('raw', 'wins', 'trim')] == [75, 78, 81])
control('C4 with winsorised and trimmed rows swapped', [round(-c4[k][0]) for k in ('raw', 'trim', 'wins')] == [119, 124, 127])

# ======================================================= Loan-level checks on Prosper (Section 4.5)
# Copied from results/prosper/tables/P14_ties_and_A1.csv, P15_prop5_exact_cut.csv, P16_prop4_random_halves.csv,
# P17_kappa.csv (Prosper_Replication.ipynb, section 6).
distinct_share = [0.99902, 0.99928, 1.0, 0.99986, 0.99948, 0.99889, 1.0, 1.0]            # P14 distinct_share
share_above_half_cal = [0.05423, 0.01026, 0.23548, 0.25755]                           # P14, calibration rows
eps0_B_baseline_cal, eps0_B_selected_cal = 0.00576, 0.0                                # P14 eps0
check('P14: more than 99.8% distinct; 1-26% of calibration loans above 1/2; eps0 0.6% (B baseline), 0 (B selected, 1.0% above 1/2)',
      min(distinct_share) > 0.998 and round(100 * min(share_above_half_cal)) == 1 and round(100 * max(share_above_half_cal)) == 26
      and round(100 * eps0_B_baseline_cal, 1) == 0.6 and eps0_B_selected_cal == 0 and round(100 * 0.01026, 1) == 1.0)
control('P14 the withdrawn wording: at least 99.9% distinct', min(distinct_share) >= 0.999)
p15 = [(True, -242.60424, -242.60424), (True, -525.07313, -525.07313), (True, -167.88279, -167.88279), (True, -521.12896, -521.12896),
       (True, -384.99993, -384.99993), (True, -474.63324, -474.63324), (True, -363.40467, -363.40467), (True, -460.53758, -460.53758)]
check('P15: all 8 conformal approved sets identical to the ranking cut; gains equal to the cent; B baseline static -242.60',
      all(s and abs(a - b) < 0.005 for s, a, b in p15) and round(p15[0][1], 2) == -242.60)
control('P15 compared with the Table 10 value at one decimal (-242.6) as if exact to the cent', round(p15[0][1], 2) == -242.6 + 0.01)
p16 = [0.9893, 1.00842, 1.0187, 0.98579, 0.97836, 1.0109, 0.9804]                     # P16 ratio, no jitter (jitter rows identical)
check('P16: 1,000-repeat ratios 0.98-1.02, SE 0.022 (1/sqrt(2*999))',
      round(min(p16), 2) == 0.98 and round(max(p16), 2) == 1.02 and round(1 / math.sqrt(2 * 999), 3) == 0.022)
control('P16 SE computed for 50 repeats instead of 1,000', round(1 / math.sqrt(2 * 49), 3) == 0.022)
kap = {'B_abar': (1.28404, 0.18441), 'A_abar': (0.85791, 0.07527), 'A_alpha': (0.42157, 0.04779), 'A_bench': (0.84138, 0.08019), 'B_bench': (1.03879, 0.25109)}
se_all = [0.25109, 0.15705, 0.29869, 0.16697, 0.08019, 0.09249, 0.05291, 0.08828, 0.04779, 0.29989, 0.17019, 0.32598, 0.18441, 0.1001, 0.09891, 0.09069, 0.18164, 0.07527]
check('P17: kappa at alpha-bar 1.28 (0.18) B, 0.86 (0.08) A; at alpha 0.42 in A; benchmark A 0.84 (0.08); SEs 0.05-0.33',
      [round(v, 2) for v in kap['B_abar']] == [1.28, 0.18] and [round(v, 2) for v in kap['A_abar']] == [0.86, 0.08]
      and round(kap['A_alpha'][0], 2) == 0.42 and [round(v, 2) for v in kap['A_bench']] == [0.84, 0.08]
      and round(min(se_all), 2) == 0.05 and round(max(se_all), 2) == 0.33)
control('P17 statement using kappa at alpha (1.19) for design B', round(1.18957, 2) == 1.28)
check('P17: bounds with kappa = 1 within about 30% for kappa at alpha-bar in both designs',
      all(abs(1 / kap[k][0] - 1) <= 0.30 for k in ('B_abar', 'A_abar')))
control('P17 the same claim for kappa at alpha in design A', abs(1 / kap['A_alpha'][0] - 1) <= 0.30)

print()
if failures:
    print('FAILED:', failures); sys.exit(1)
print('ALL CHECKS AND CONTROLS BEHAVED AS EXPECTED')
