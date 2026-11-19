"""Рисунки для отчёта ПР4 (вариант 13): графики по данным SimInTech,
сигнальные графы и структурные схемы."""
import os

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
from matplotlib.patches import Circle, FancyArrowPatch, Rectangle  # noqa: E402
from scipy import signal  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, 'Рисунки')
SIT = os.path.join(HERE, 'SimInTech')
os.makedirs(OUT, exist_ok=True)

plt.rcParams.update({
    'font.family': 'Times New Roman', 'mathtext.fontset': 'stix',
    'font.size': 12, 'axes.grid': True, 'grid.color': '#d9d9d9', 'grid.linewidth': 0.6,
    'axes.edgecolor': '#555555', 'axes.linewidth': 0.8, 'savefig.dpi': 200,
})
C1, C2, C3 = '#2a78d6', '#eb6834', '#1baf7a'
from matplotlib.ticker import FuncFormatter  # noqa: E402
COMMA = FuncFormatter(lambda v, p: f'{v:g}'.replace('.', ','))


def cm(v, d=4):
    return f'{v:.{d}f}'.replace('.', '{,}')
INK = '#222222'


# ------------------------------------------------------------- переходные
def step_fig(datfile, num, den, names, title_y, fname, tmax):
    d = np.loadtxt(os.path.join(SIT, datfile))
    t = d[:, 0]
    # точная переходная функция: h(t) = sum r_i e^(p_i t) для W(s)/s
    rr, pp, _ = signal.residue(num, np.polymul(den, [1, 0]))
    yr = np.real(sum(ri * np.exp(pi * t) for ri, pi in zip(rr, pp)))
    err = np.max(abs(d[:, 2:] - yr[:, None]))
    ex = int(np.floor(np.log10(err)))
    sc = 10.0 ** (-ex)
    sup = str(ex).replace('-', '⁻').translate(str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))
    yinf = num[-1] / den[-1]
    fig, (ax, ax2) = plt.subplots(2, 1, figsize=(7.2, 6.4), sharex=True,
                                  gridspec_kw={'height_ratios': [3, 1.4]})
    ax.plot(t, d[:, 1], color='#888888', lw=1.2, label='u(t) = 1(t)')
    styles = [dict(color=C1, lw=2.6, ls='-'),
              dict(color=C2, lw=2.0, ls=(0, (6, 4))),
              dict(color=C3, lw=2.0, ls=(0, (1.5, 2.5)))]
    for k, (nm, st) in enumerate(zip(names, styles)):
        ax.plot(t, d[:, 2 + k], label=nm, **st)
    ax.axhline(yinf, color='#999999', lw=0.8, ls='--')
    ax.text(t[-1] * 0.98, yinf - 0.04, f'h(∞) = {yinf:.4f}'.replace('.', ','), va='top', ha='right', color=INK, fontsize=11)
    ax.set_ylabel(title_y)
    ax.legend(loc='lower right', frameon=True, framealpha=0.95, fontsize=11)
    ax.set_xlim(0, tmax)
    ax.set_ylim(0, max(1.2, yinf * 1.15))
    for k, (nm, st) in enumerate(zip(names, styles)):
        ax2.plot(t, (d[:, 2 + k] - yr) * sc, label=nm, color=st['color'],
                 lw=1.6 if k == 0 else 1.2, ls=st['ls'])
    ax2.set_ylabel(f'y − h, ×10{sup}')
    ax2.set_xlabel('t, с')
    for a_ in (ax, ax2):
        a_.xaxis.set_major_formatter(COMMA); a_.yaxis.set_major_formatter(COMMA)
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, fname))
    plt.close(fig)
    return float(np.max(abs(d[:, 2:] - yr[:, None]))), d


# ------------------------------------------------------------- примитивы схем
def arrow(ax, p, q, text=None, off=(0, 0.12), rad=0.0, color=INK, fs=12, lw=1.1, tpos=0.5,
          ha='center', va='bottom'):
    a = FancyArrowPatch(p, q, arrowstyle='-|>', mutation_scale=11, lw=lw, color=color,
                        connectionstyle=f'arc3,rad={rad}', shrinkA=0, shrinkB=0)
    ax.add_patch(a)
    if text:
        if rad == 0:
            mx = p[0] + (q[0] - p[0]) * tpos
            my = p[1] + (q[1] - p[1]) * tpos
        else:   # середина дуги
            mx0, my0 = (p[0] + q[0]) / 2, (p[1] + q[1]) / 2
            dx, dy = q[0] - p[0], q[1] - p[1]
            mx, my = mx0 + 0.5 * rad * dy, my0 - 0.5 * rad * dx
        ax.text(mx + off[0], my + off[1], text, ha=ha, va=va, fontsize=fs, color=INK)


def node(ax, xy, label, pos='above', r=0.07, fs=13):
    ax.add_patch(Circle(xy, r, fc='white', ec=INK, lw=1.1, zorder=5))
    dx, dy = {'above': (0, 0.16), 'below': (0, -0.2), 'left': (-0.18, 0),
              'right': (0.18, 0), 'ul': (-0.22, 0.17), 'll': (-0.22, -0.19)}[pos]
    ax.text(xy[0] + dx, xy[1] + dy, label, ha='center', va='center', fontsize=fs, zorder=6)


def sfg_frob_41():
    fig, ax = plt.subplots(figsize=(8.2, 3.9))
    ax.set_aspect('equal'); ax.axis('off')
    X = {'u': 0, 'd3': 1.6, 'x3': 3.2, 'x2': 4.8, 'x1': 6.4, 'y': 8.0}
    P = {k: (v, 0) for k, v in X.items()}
    lab = {'u': '$u$', 'd3': r'$\dot x_3$', 'x3': r'$x_3=\dot x_2$', 'x2': r'$x_2=\dot x_1$',
           'x1': '$x_1$', 'y': '$y$'}
    arrow(ax, P['u'], (P['d3'][0] - 0.07, 0), '1')
    arrow(ax, (P['d3'][0] + 0.07, 0), (P['x3'][0] - 0.07, 0), '$s^{-1}$')
    arrow(ax, (P['x3'][0] + 0.07, 0), (P['x2'][0] - 0.07, 0), '$s^{-1}$')
    arrow(ax, (P['x2'][0] + 0.07, 0), (P['x1'][0] - 0.07, 0), '$s^{-1}$')
    arrow(ax, (P['x1'][0] + 0.07, 0), (P['y'][0] - 0.07, 0), '2')
    # выход
    arrow(ax, (P['x2'][0], 0.07), (P['y'][0] - 0.05, 0.05), '1', rad=-0.35, off=(0, 0.03))
    arrow(ax, (P['x3'][0], 0.07), (P['y'][0] - 0.03, 0.07), '1/3', rad=-0.4, off=(0, 0.03))
    # обратные связи
    arrow(ax, (P['x3'][0], -0.07), (P['d3'][0] + 0.03, -0.07), '−2', rad=-0.3, off=(0, -0.05), va='top')
    arrow(ax, (P['x2'][0], -0.07), (P['d3'][0] + 0.02, -0.07), '−3', rad=-0.55, off=(0, -0.05), va='top')
    arrow(ax, (P['x1'][0], -0.07), (P['d3'][0], -0.07), '−1', rad=-0.7, off=(0, -0.05), va='top')
    for k in X:
        node(ax, P[k], lab[k], 'above' if k in ('u', 'd3', 'y') else 'below')
    ax.set_xlim(-0.4, 8.4); ax.set_ylim(-2.0, 1.6)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'sfg_frob_41.png')); plt.close(fig)


def sfg_jordan_41(lam1, sig, om, r1, c2, c3):
    fig, ax = plt.subplots(figsize=(8.2, 5.2))
    ax.set_aspect('equal'); ax.axis('off')
    U, Y = (0, 0), (6.6, 0)
    rows = {1: 1.7, 2: 0.0, 3: -1.7}
    D = {i: (1.8, y) for i, y in rows.items()}
    Xn = {i: (4.0, y) for i, y in rows.items()}
    arrow(ax, (0.06, 0.05), (D[1][0] - 0.06, D[1][1] - 0.03), '1', off=(-0.2, 0))
    arrow(ax, (0.06, -0.05), (D[3][0] - 0.06, D[3][1] + 0.03), '1', off=(-0.2, -0.3))
    for i in (1, 2, 3):
        arrow(ax, (D[i][0] + 0.07, D[i][1]), (Xn[i][0] - 0.07, Xn[i][1]), '$s^{-1}$',
              off=(0, -0.1 if i != 3 else 0.08), va='top' if i != 3 else 'bottom', tpos=0.62)
    # петли
    arrow(ax, (Xn[1][0], 1.7 + 0.07), (D[1][0], 1.7 + 0.07), rf'$\lambda_1={cm(lam1)}$',
          rad=0.6, off=(0, 0.03))
    arrow(ax, (Xn[2][0] - 0.03, 0.07), (D[2][0] + 0.03, 0.07), rf'$\sigma={cm(sig)}$',
          rad=0.45, off=(0, 0.03))
    arrow(ax, (Xn[3][0], -1.7 - 0.07), (D[3][0], -1.7 - 0.07), rf'$\sigma={cm(sig)}$',
          rad=-0.6, off=(0, -0.05), va='top')
    # перекрёстные связи комплексной пары
    arrow(ax, (Xn[3][0] - 0.05, -1.7 + 0.05), (D[2][0] + 0.05, -0.05), rf'$\omega={cm(om)}$',
          off=(-0.1, 0.02), tpos=0.75, ha='right')
    arrow(ax, (Xn[2][0] - 0.05, -0.05), (D[3][0] + 0.05, -1.7 + 0.05), rf'$-\omega$',
          off=(-0.1, -0.2), tpos=0.75, ha='right')
    # выход
    arrow(ax, (Xn[1][0] + 0.06, 1.7 - 0.03), (Y[0] - 0.06, 0.05), rf'$c_1={cm(r1)}$', off=(0.35, 0))
    arrow(ax, (Xn[2][0] + 0.07, 0), (Y[0] - 0.07, 0), rf'$c_2={cm(c2)}$')
    arrow(ax, (Xn[3][0] + 0.06, -1.7 + 0.03), (Y[0] - 0.06, -0.05), rf'$c_3={cm(c3)}$',
          off=(0.4, -0.35))
    node(ax, U, '$u$', 'left'); node(ax, Y, '$y$', 'right')
    for i in (1, 2, 3):
        node(ax, D[i], rf'$\dot x_{i}$', {1: 'ul', 2: 'left', 3: 'll'}[i])
        node(ax, Xn[i], rf'$x_{i}$', {1: 'below', 2: 'below', 3: 'above'}[i] if i != 2 else 'below')
    ax.set_xlim(-0.5, 7.1); ax.set_ylim(-2.75, 2.75)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'sfg_jordan_41.png')); plt.close(fig)


def box(ax, xy, w, h, text, fs=12):
    ax.add_patch(Rectangle((xy[0] - w / 2, xy[1] - h / 2), w, h, fc='white', ec=INK, lw=1.1, zorder=4))
    ax.text(xy[0], xy[1], text, ha='center', va='center', fontsize=fs, zorder=5)


def summer(ax, xy, r=0.17):
    ax.add_patch(Circle(xy, r, fc='white', ec=INK, lw=1.1, zorder=4))
    ax.plot([xy[0] - r * 0.707, xy[0] + r * 0.707], [xy[1] - r * 0.707, xy[1] + r * 0.707], color=INK, lw=0.8, zorder=5)
    ax.plot([xy[0] - r * 0.707, xy[0] + r * 0.707], [xy[1] + r * 0.707, xy[1] - r * 0.707], color=INK, lw=0.8, zorder=5)


def line(ax, pts, arrow_end=False, dot_start=False):
    xs, ys = zip(*pts)
    ax.plot(xs, ys, color=INK, lw=1.1, zorder=3)
    if arrow_end:
        ax.add_patch(FancyArrowPatch(pts[-2], pts[-1], arrowstyle='-|>', mutation_scale=10, lw=1.1,
                                     color=INK, shrinkA=0, shrinkB=0, zorder=3))
    if dot_start:
        ax.plot(*pts[0], 'o', color=INK, ms=3.5, zorder=6)


def ffg_scheme():
    fig, ax = plt.subplots(figsize=(8.0, 2.9))
    ax.set_aspect('equal'); ax.axis('off')
    s = (1.0, 0)
    summer(ax, s)
    line(ax, [(0, 0), (s[0] - 0.17, 0)], True)
    ax.text(0.05, 0.12, '$u$', fontsize=13)
    box(ax, (2.6, 0), 1.9, 0.7, r'$W_F(s)=\dfrac{3s+2}{s^2+4s+1}$', fs=11)
    box(ax, (5.0, 0), 1.9, 0.7, r'$W_F(s)=\dfrac{3s+2}{s^2+4s+1}$', fs=11)
    box(ax, (3.8, -1.3), 1.9, 0.7, r'$W_G(s)=\dfrac{s+1}{s^2+5s+5}$', fs=11)
    line(ax, [(s[0] + 0.17, 0), (1.65, 0)], True)
    line(ax, [(3.55, 0), (4.05, 0)], True)
    line(ax, [(5.95, 0), (7.2, 0)], True)
    ax.text(6.95, 0.12, '$y$', fontsize=13)
    line(ax, [(6.4, 0), (6.4, -1.3), (4.75, -1.3)], True, dot_start=True)
    line(ax, [(2.85, -1.3), (1.0, -1.3), (1.0, -0.17)], True)
    ax.text(1.07, -0.42, '−', fontsize=15)
    ax.text(0.62, 0.1, '+', fontsize=12)
    ax.set_xlim(-0.2, 7.4); ax.set_ylim(-1.8, 0.6)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'ffg_scheme.png')); plt.close(fig)


def luenberger_scheme(aa, bb):
    n = 6
    fig, ax = plt.subplots(figsize=(10.5, 4.0))
    ax.set_aspect('equal'); ax.axis('off')
    DX = 1.55
    yU, yB, yA, yX1 = 1.55, 0.85, -0.85, -1.55
    x0 = 0.6
    ax.text(-0.15, yU, '$u$', fontsize=13, va='center')
    line(ax, [(0, yU), (x0 + DX * (n - 2), yU)])
    prev_out = None
    for k, i in enumerate(range(n, 0, -1)):
        xs = x0 + k * DX
        summer(ax, (xs, 0))
        box(ax, (xs + 0.75, 0), 0.5, 0.42, r'$\dfrac{1}{s}$', fs=11)
        line(ax, [(xs + 0.17, 0), (xs + 0.5, 0)], True)
        ax.text(xs + 0.75, 0.32, f'$x_{i}$', ha='center', fontsize=11)
        if prev_out is not None:
            line(ax, [prev_out, (xs - 0.17, 0)], True)
        prev_out = (xs + 1.0, 0)
        if bb[i - 1] != 0:
            box(ax, (xs, yB), 0.5, 0.36, f'{bb[i - 1]:g}', fs=11)
            line(ax, [(xs, yU), (xs, yB + 0.18)], True, dot_start=True)
            line(ax, [(xs, yB - 0.18), (xs, 0.17)], True)
        box(ax, (xs, yA), 0.5, 0.36, f'{aa[i - 1]:g}', fs=11)
        line(ax, [(xs, yX1), (xs, yA - 0.18)], True, dot_start=True)
        line(ax, [(xs, yA + 0.18), (xs, -0.17)], True)
        ax.text(xs + 0.06, -0.36, '−', fontsize=13)
    xe = prev_out[0] + 0.9
    line(ax, [prev_out, (xe, 0)], True)
    ax.text(xe - 0.15, 0.12, '$y=x_1$', fontsize=12, ha='right')
    line(ax, [(prev_out[0] + 0.4, 0), (prev_out[0] + 0.4, yX1), (x0, yX1)], dot_start=True)
    ax.set_xlim(-0.4, xe + 0.2); ax.set_ylim(-1.9, 1.9)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'luenberger_scheme.png')); plt.close(fig)


def frob_scheme_42(aa, num):
    n = 6
    fig, ax = plt.subplots(figsize=(10.5, 5.0))
    ax.set_aspect('equal'); ax.axis('off')
    DX = 1.45
    xs = 0.8
    r = 0.15
    summer(ax, (xs, 0))
    ax.text(-0.1, 0.12, '$u$', fontsize=13)
    line(ax, [(0, 0), (xs - 0.17, 0)], True)
    prev = (xs + 0.17, 0)
    taps = {}
    for k, i in enumerate(range(n, 0, -1)):
        xb = xs + 0.85 + k * DX
        box(ax, (xb, 0), 0.5, 0.42, r'$\dfrac{1}{s}$', fs=11)
        line(ax, [prev, (xb - 0.25, 0)], True)
        prev = (xb + 0.25, 0)
        tx = xb + 0.25 + (DX - 0.5) / 2
        taps[i] = tx
        ax.text(tx + 0.05, 0.1, f'$x_{i}$', ha='left', fontsize=11)
    line(ax, [prev, (taps[1], 0)])
    # обратная связь: x_i -> a_{n-i+1} -> цепочка сумматоров справа налево
    yg, yb = -0.85, -1.6
    for i in range(1, n + 1):
        tx = taps[i]
        line(ax, [(tx, 0), (tx, yg + 0.15)], True, dot_start=True)
        box(ax, (tx, yg), 0.5, 0.3, f'{aa[n - i]:g}', fs=11)
        if i == 1:
            line(ax, [(tx, yg - 0.15), (tx, yb), (taps[2] + r, yb)], True)
        else:
            summer(ax, (tx, yb), r)
            line(ax, [(tx, yg - 0.15), (tx, yb + r)], True)
            if i < n:
                line(ax, [(tx - r, yb), (taps[i + 1] + r, yb)], True)
    line(ax, [(taps[n] - r, yb), (xs, yb), (xs, -0.17)], True)
    ax.text(xs + 0.07, -0.42, '−', fontsize=14)
    # выход: x_i -> b -> цепочка сумматоров слева направо
    yg2, yb2 = 0.85, 1.6
    m = len(num)
    for i in range(m, 0, -1):
        tx = taps[i]
        coef = num[::-1][i - 1]
        line(ax, [(tx, 0), (tx, yg2 - 0.15)], True, dot_start=True)
        box(ax, (tx, yg2), 0.5, 0.3, f'{coef:g}', fs=11)
        if i == m:
            line(ax, [(tx, yg2 + 0.15), (tx, yb2), (taps[i - 1] - r, yb2)], True)
        else:
            summer(ax, (tx, yb2), r)
            line(ax, [(tx, yg2 + 0.15), (tx, yb2 - r)], True)
            if i > 1:
                line(ax, [(tx + r, yb2), (taps[i - 1] - r, yb2)], True)
    xe = taps[1] + 0.9
    line(ax, [(taps[1] + r, yb2), (xe, yb2)], True)
    ax.text(xe - 0.1, yb2 + 0.12, '$y$', fontsize=13)
    ax.set_xlim(-0.3, xe + 0.2); ax.set_ylim(-2.0, 2.0)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'frob_scheme_42.png')); plt.close(fig)


def poles_fig(den_bad, den_ok):
    fig, ax = plt.subplots(figsize=(7.0, 4.0))
    pb, po = np.roots(den_bad), np.roots(den_ok)
    ax.axvline(0, color='#777777', lw=1.0)
    ax.axhline(0, color='#777777', lw=0.6)
    ax.plot(pb.real, pb.imag, 'x', color=C2, ms=9, mew=2, label='исходные A (неустойчива)')
    ax.plot(po.real, po.imag, 'o', color=C1, ms=8, mfc='white', mew=2, label='A → −A (устойчива)')
    ax.set_xlabel('Re s'); ax.set_ylabel('Im s')
    ax.xaxis.set_major_formatter(COMMA); ax.yaxis.set_major_formatter(COMMA)
    ax.legend(loc='upper left', fontsize=11)
    fig.tight_layout(); fig.savefig(os.path.join(OUT, 'poles_42.png')); plt.close(fig)


if __name__ == '__main__':
    e1, _ = step_fig('pr4_1.dat', [1, 3, 6], [3, 6, 9, 3],
                     ['W(s) (передаточная функция)', 'фробениусова форма', 'жорданова форма'],
                     'y(t)', 'step_41.png', 20)
    e2, _ = step_fig('pr4_2.dat', [9, 57, 109, 80, 20], [1, 13, 63, 147, 152, 61, 9],
                     ['Φ(s) (передаточная функция)', 'форма Люенбергера', 'форма Коши–Фробениуса'],
                     'y(t)', 'step_42.png', 40)
    print('max err 4.1 =', e1, ' 4.2 =', e2)
    b, a = np.array([1., 3., 6.]) / 3, np.array([3., 6., 9., 3.]) / 3
    r, p, _ = signal.residue(b, a)
    i1 = int(np.argmin(abs(p.imag))); ic = [k for k in range(3) if p[k].imag > 1e-9][0]
    sfg_frob_41()
    sfg_jordan_41(p[i1].real, p[ic].real, p[ic].imag, r[i1].real, -2 * r[ic].imag, 2 * r[ic].real)
    ffg_scheme()
    aa = [13, 63, 147, 152, 61, 9]
    bb = [0, 9, 57, 109, 80, 20]
    luenberger_scheme(aa, bb)
    frob_scheme_42(aa, [9, 57, 109, 80, 20])
    poles_fig([1, -13, 63, -129, 110, -29, 1], [1, 13, 63, 147, 152, 61, 9])
    print('done')
