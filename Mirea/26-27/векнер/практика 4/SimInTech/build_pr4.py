"""Сборка схем SimInTech для ПР4, вариант 13.

ПР4_1.xprt — часть 4.1: W(s), фробениусова (управляемая) форма, жорданова форма.
ПР4_2.xprt — часть 4.2: Φ(s) замкнутой FFG, форма Люенбергера (наблюдаемая),
             форма Коши–Фробениуса (управляемая).
"""
import os
import sys

import numpy as np
from scipy import signal

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_sit import Scheme, save  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))

# ======================================================================= 4.1
a = np.array([3., 6., 9., 3.])
b = np.array([1., 3., 6.])
an, bn = a / a[0], b / a[0]                 # s^3 + 2s^2 + 3s + 1
r, p, _ = signal.residue(bn, an)
i1 = int(np.argmin(abs(p.imag)))
lam1, r1 = p[i1].real, r[i1].real
ic = [k for k in range(3) if p[k].imag > 1e-9][0]
sig, om = p[ic].real, p[ic].imag
alf, bet = r[ic].real, r[ic].imag
c2, c3 = -2 * bet, 2 * alf                  # B = [1; 0; 1], C = [r1, c2, c3]

S = Scheme()
u = S.step('u', -440, 300)
w = S.tf('W', -60, 40, list(b[::-1]), list(a[::-1]),
         'W(s) = (s²+3s+6)/(3s³+6s²+9s+3)', w=180)

# --- фробениусова форма: x1'=x2, x2'=x3, x3' = -x1 - 3x2 - 2x3 + u
Y0 = 200
fa = S.summ('SF', -260, Y0, [1, -an[3], -an[2], -an[1]], 'u − x1 − 3x2 − 2x3')
f3 = S.integ('F3', -180, Y0, 'x3')
f2 = S.integ('F2', -100, Y0, 'x2')
f1 = S.integ('F1', -20, Y0, 'x1')
fy = S.summ('SFy', 120, 330, [bn[2], bn[1], bn[0]], 'y = 2x1 + x2 + x3/3')

# --- жорданова (вещественная) форма
J1, J2, J3 = 470, 580, 690
j1s = S.summ('SJ1', -260, J1, [1, lam1], 'u + λ1·x1')
j1 = S.integ('J1', -180, J1, 'x1')
j2s = S.summ('SJ2', -260, J2, [sig, om], 'σx2 + ωx3')
j2 = S.integ('J2', -180, J2, 'x2')
j3s = S.summ('SJ3', -260, J3, [-om, sig, 1], '−ωx2 + σx3 + u')
j3 = S.integ('J3', -180, J3, 'x3')
jy = S.summ('SJy', 60, J2, [r1, c2, c3], 'y = c1x1 + c2x2 + c3x3')

g = S.graph('G', 380, 330, 3, 'y(t): W, Фроб., Жорд.')
fl = S.tofile('FILE', 380, 470, 4, 'pr4_1.dat')

S.net(u, [(fa, 0, 120, 8), (w, 0), (j1s, 0, 420, 8), (j3s, 2, 740, 8), (fl, 0, 540, 8)])
S.net(fa, [(f3, 0)])
S.net(f3, [(f2, 0), (fa, 3, Y0 + 80, 32), (fy, 2)])
S.net(f2, [(f1, 0), (fa, 2, Y0 + 68, 24), (fy, 1)])
S.net(f1, [(fa, 1, Y0 + 56, 16), (fy, 0)])
S.net(w, [(g, 0), (fl, 1, 400, 8)], dx=24)
S.net(fy, [(g, 1), (fl, 2, 420, 16)], dx=24)
S.net(jy, [(g, 2, 380, 8), (fl, 3)], dx=24)
S.net(j1s, [(j1, 0)])
S.net(j2s, [(j2, 0)])
S.net(j3s, [(j3, 0)])
S.net(j1, [(j1s, 1, J1 + 44, 16), (jy, 0)])
S.net(j2, [(j2s, 0, J2 + 40, 8), (j3s, 0, J2 + 52, 24), (jy, 1)], dx=24)
S.net(j3, [(j2s, 1, J2 + 64, 16), (j3s, 1, J3 + 48, 16), (jy, 2)], dx=32)
save(S.render_page(20, 'ПР4_1'), os.path.join(HERE, 'ПР4_1.xprt'))

# ======================================================================= 4.2
num = [9., 57., 109., 80., 20.]                       # 9s^4+57s^3+109s^2+80s+20
den = [1., 13., 63., 147., 152., 61., 9.]             # s^6+13s^5+...+9
n = 6
bb = [0.] * (n - len(num)) + num                      # b1..b6 (b1 = 0)
aa = den[1:]                                          # a1..a6

S = Scheme()
u = S.step('u', -700, 330)
w = S.tf('Phi', -300, 40, num[::-1], den[::-1],
         'Φ(s) замкнутой системы FFG', w=300)

# --- форма Люенбергера (наблюдаемая): x_i' = x_{i+1} - a_i x1 + b_i u, y = x1
YL = 240
xs = {}
sums = {}
X0, DX = -620, 70
for k, i in enumerate(range(n, 0, -1)):            # i = 6..1 слева направо
    xsum = X0 + 2 * k * DX
    coefs, ins = [], []
    if bb[i - 1] != 0:
        coefs.append(bb[i - 1]); ins.append('u')
    if i < n:
        coefs.append(1.0); ins.append('x')
    coefs.append(-aa[i - 1]); ins.append('x1')
    sums[i] = (S.summ(f'SL{i}', xsum, YL, coefs, f"x{i}'"), ins)
    xs[i] = S.integ(f'L{i}', xsum + DX, YL, f'x{i}')

# --- форма Коши–Фробениуса (управляемая)
YF = 520
fa = S.summ('SF', -620, YF, [1.0] + [-c for c in aa[::-1]], "x6' = u − Σ a·x")
fx = {}
for k, i in enumerate(range(n, 0, -1)):
    fx[i] = S.integ(f'F{i}', -540 + k * 80, YF, f'x{i}')
fy = S.summ('SFy', 0, 760, num[::-1], 'y = 20x1+80x2+109x3+57x4+9x5')

g = S.graph('G', 380, 400, 3, 'y(t): Φ, Люенб., Фроб.')
fl = S.tofile('FILE', 380, 560, 4, 'pr4_2.dat')

# u: во все суммы с b_i ≠ 0, в Φ(s), в SF, в файл
udst = [(w, 0)]
for i in range(n, 0, -1):
    sm, ins = sums[i]
    if 'u' in ins:
        udst.append((sm, ins.index('u'), YL - 70, 8))
udst.append((fa, 0, YF - 90, 8))
udst.append((fl, 0, 640, 8))
S.net(u, udst)
# цепочка Люенбергера
for i in range(n, 0, -1):
    sm, ins = sums[i]
    S.net(sm, [(xs[i], 0)])
    if i > 1:
        sm2, ins2 = sums[i - 1]
        S.net(xs[i], [(sm2, ins2.index('x'))])
x1dst = []
for i in range(n, 0, -1):
    sm, ins = sums[i]
    x1dst.append((sm, ins.index('x1'), YL + 70, 8))
x1dst += [(g, 1, 330, 8), (fl, 2, 600, 16)]
S.net(xs[1], x1dst)
# цепочка Фробениуса
S.net(fa, [(fx[n], 0)])
for i in range(n, 0, -1):
    dst = []
    if i > 1:
        dst.append((fx[i - 1], 0))
    dst.append((fa, i, YF + 80 + 12 * i, 8 + 6 * i))
    if i <= len(num):
        dst.append((fy, i - 1))
    S.net(fx[i], dst)
S.net(w, [(g, 0, 90, 8), (fl, 1, 120, 8)], dx=24)
S.net(fy, [(g, 2, 700, 16), (fl, 3, 700, 24)], dx=24)
save(S.render_page(40, 'ПР4_2'), os.path.join(HERE, 'ПР4_2.xprt'))
print('ok', lam1, sig, om, r1, c2, c3)
