# -*- coding: utf-8 -*-
"""Графики: карта полюсов, АЧХ, ФЧХ, ИПФ (вариант 19, схема 1)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy import signal

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

R1, R2 = 900.0, 4900.0
C1, C2 = 1.59e-6, 0.36e-6
a2 = R1 * R2 * C1 * C2          # 2.524284e-06
a1 = R1 * C1 + (R1 + R2) * C2   # 3.519e-03
num, den = [1.0], [a2, a1, 1.0]
sys_tf = signal.TransferFunction(num, den)
p1, p2 = sys_tf.poles[1], sys_tf.poles[0]   # -397.53, -996.53
K = 1.0 / a2 / (p1 - p2)

# ---------- 1. Карта нулей и полюсов ----------
fig, ax = plt.subplots(figsize=(6.4, 3.4), dpi=200)
ax.axhline(0, color='k', lw=1)
ax.axvline(0, color='k', lw=1)
ax.plot([p1, p2], [0, 0], 'rx', ms=13, mew=2.5)
ax.annotate(f'p$_1$ = {p1:.2f}', (p1, 0), textcoords='offset points', xytext=(0, 12),
            ha='center', fontsize=12)
ax.annotate(f'p$_2$ = {p2:.2f}', (p2, 0), textcoords='offset points', xytext=(0, 12),
            ha='center', fontsize=12)
ax.set_xlim(-1250, 250)
ax.set_ylim(-260, 260)
ax.set_xlabel('Re(p)')
ax.set_ylabel('Im(p)')
ax.set_title('Карта нулей и полюсов')
ax.grid(True, ls=':', alpha=0.6)
plt.tight_layout()
plt.savefig('img/pzmap.png', bbox_inches='tight', facecolor='white')
plt.close()

# ---------- 2. АЧХ ----------
w = np.logspace(0, 5, 2000)
A_an = 1.0 / np.sqrt((1 - a2 * w**2)**2 + (a1 * w)**2)
w_out, mag_db, phase = signal.bode(sys_tf, w)
mag = 10.0 ** (mag_db / 20.0)

fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), dpi=200)
axs[0].semilogx(w, A_an, 'b-', lw=2)
axs[0].set_title('АЧХ (аналитически)')
axs[0].set_xlabel('ω, рад/с'); axs[0].set_ylabel('A(ω)')
axs[0].set_xlim(1, 1e5); axs[0].set_ylim(0, 1.1)
axs[0].grid(True, which='both', ls=':', alpha=0.6)
axs[1].semilogx(w_out, mag, 'r-', lw=2)
axs[1].set_title('АЧХ (встроенная функция bode)')
axs[1].set_xlabel('ω, рад/с'); axs[1].set_ylabel('A(ω)')
axs[1].set_xlim(1, 1e5); axs[1].set_ylim(0, 1.1)
axs[1].grid(True, which='both', ls=':', alpha=0.6)
plt.tight_layout()
plt.savefig('img/achh.png', bbox_inches='tight', facecolor='white')
plt.close()

# ---------- 3. ФЧХ ----------
phi_an = -np.degrees(np.arctan2(a1 * w, 1 - a2 * w**2))
fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), dpi=200)
axs[0].semilogx(w, phi_an, 'b-', lw=2)
axs[0].set_title('ФЧХ (аналитически)')
axs[0].set_xlabel('ω, рад/с'); axs[0].set_ylabel('φ(ω), град')
axs[0].set_xlim(1, 1e5); axs[0].set_ylim(-185, 5)
axs[0].set_yticks(range(-180, 1, 30))
axs[0].grid(True, which='both', ls=':', alpha=0.6)
axs[1].semilogx(w_out, phase, 'r-', lw=2)
axs[1].set_title('ФЧХ (встроенная функция bode)')
axs[1].set_xlabel('ω, рад/с'); axs[1].set_ylabel('φ(ω), град')
axs[1].set_xlim(1, 1e5); axs[1].set_ylim(-185, 5)
axs[1].set_yticks(range(-180, 1, 30))
axs[1].grid(True, which='both', ls=':', alpha=0.6)
plt.tight_layout()
plt.savefig('img/fchh.png', bbox_inches='tight', facecolor='white')
plt.close()

# ---------- 4. ИПФ ----------
t = np.linspace(0, 0.012, 2000)
h_an = K * (np.exp(p1 * t) - np.exp(p2 * t))
t_sys, h_sys = signal.impulse(sys_tf, T=t)

fig, axs = plt.subplots(1, 2, figsize=(11, 3.6), dpi=200)
axs[0].plot(t * 1000, h_an, 'b-', lw=2)
axs[0].set_title('ИПФ (аналитически)')
axs[0].set_xlabel('t, мс'); axs[0].set_ylabel('h(t), 1/с')
axs[0].set_xlim(0, 12); axs[0].set_ylim(0, 240)
axs[0].grid(True, ls=':', alpha=0.6)
axs[1].plot(t_sys * 1000, h_sys, 'r-', lw=2)
axs[1].set_title('ИПФ (встроенная функция impulse)')
axs[1].set_xlabel('t, мс'); axs[1].set_ylabel('h(t), 1/с')
axs[1].set_xlim(0, 12); axs[1].set_ylim(0, 240)
axs[1].grid(True, ls=':', alpha=0.6)
plt.tight_layout()
plt.savefig('img/ipf.png', bbox_inches='tight', facecolor='white')
plt.close()

# контроль совпадения
err_a = np.max(np.abs(A_an - mag))
err_h = np.max(np.abs(h_an - h_sys))
print(f'p1={p1:.2f}, p2={p2:.2f}, K={K:.2f}')
print(f'max |A_an - A_bode| = {err_a:.2e}')
print(f'max |h_an - h_impulse| = {err_h:.2e}')
print('saved img/pzmap.png, achh.png, fchh.png, ipf.png')
