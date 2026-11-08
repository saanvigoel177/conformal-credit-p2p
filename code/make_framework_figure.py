import matplotlib
matplotlib.use('Agg')
matplotlib.rcParams['pdf.fonttype'] = 42
matplotlib.rcParams['font.family'] = 'DejaVu Sans'
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

fig, ax = plt.subplots(figsize=(7.2, 3.15))
ax.set_xlim(0, 100); ax.set_ylim(0, 44); ax.axis('off')
INK = '#1f2933'; EDGE = '#52606d'; FILL = '#f5f7fa'; ACC = '#1f77b4'; ACCF = '#e8f1fa'; MUTED = '#7b8794'

def box(x, y, w, h, title, body, sec=None, accent=False):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle='round,pad=0.25,rounding_size=1.2',
                                lw=1.0, ec=ACC if accent else EDGE, fc=ACCF if accent else FILL))
    ax.text(x + w / 2, y + h - 2.2, title, ha='center', va='top', fontsize=7.6, weight='bold', color=INK)
    ax.text(x + w / 2, y + h - 5.6, body, ha='center', va='top', fontsize=6.3, color=INK, linespacing=1.25)
    if sec:
        ax.text(x + w / 2, y - 1.4, sec, ha='center', va='top', fontsize=5.8, color=MUTED, style='italic')

def arrow(x0, y0, x1, y1, style='-|>', ls='-', color=EDGE, rad=0.0):
    ax.add_patch(FancyArrowPatch((x0, y0), (x1, y1), arrowstyle=style, mutation_scale=9, lw=1.0,
                                 color=color, linestyle=ls, connectionstyle=f'arc3,rad={rad}'))

top, h = 25, 15
box(0.5, top, 15.5, h, 'Application', 'origination\nfeatures\n(amount, income,\nDTI, FICO, ...)')
box(20, top, 17, h, 'Default model', 'LightGBM or\nlogistic regression\ntrained on early\nvintages', 'Sect. 3.3, 4.1')
box(41, top, 18.5, h, 'Conformal layer', 'static, class- or\nrisk-conditional sets;\nonline: ACI, rolling\nrecalibration', 'Sect. 3.4, 4.1–4.3', accent=True)
box(63.5, top, 15.5, h, 'Router', '{0} → approve\n{1} → reject\n{0,1} → refer', 'Sect. 4.2, 4.4')
box(83, top, 16.5, h, 'Human reviewer', 'resolves referrals\nwith accuracy q\nat cost c', 'Sect. 4.4')
for a, b in ((16.3, 19.7), (37.3, 40.7), (59.8, 63.2), (79.3, 82.7)):
    arrow(a, top + h / 2, b, top + h / 2)

bot, hb = 2.5, 11.5
box(63.5, bot, 36, hb, 'Decision scored on realised profit', 'approve / reject per loan; gain over approving everyone;\nbreak-even reviewer accuracy', 'Sect. 3.5, 4.4')
box(22, bot, 37, hb, 'Delayed, outcome-dependent labels', 'defaults are observed months before repayments;\nlabels known at deployment are default-enriched', 'Sect. 4.3, 4.6')
box(0.5, bot, 17.5, hb, 'Monitoring', 'calibration gap,\nsegment coverage', 'Sect. 4.7')
arrow(77.6, top - 0.3, 79.5, bot + hb + 0.3)
arrow(96.8, top - 0.3, 94.5, bot + hb + 0.3)
arrow(63.2, bot + hb / 2, 59.3, bot + hb / 2)              # outcomes flow back
arrow(57.6, bot + hb + 0.3, 57.6, top - 0.3, ls='--', color=ACC)  # recalibration
arrow(21.7, bot + hb / 2, 18.3, bot + hb / 2)
ax.text(56.8, (bot + hb + top) / 2 - 1.2, 'recalibrate', fontsize=6, color=ACC, va='center', ha='right')
plt.tight_layout(pad=0.2)
fig.savefig('Figure_1.pdf'); fig.savefig('Figure_1.png', dpi=600)
