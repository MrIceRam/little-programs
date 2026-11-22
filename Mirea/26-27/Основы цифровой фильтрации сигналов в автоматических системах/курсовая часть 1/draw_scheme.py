# -*- coding: utf-8 -*-
"""Схема 1 с контурными токами (вариант 19)."""
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Arc, FancyArrowPatch
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 13

fig, ax = plt.subplots(figsize=(9, 4.6), dpi=200)
ax.set_xlim(0, 10)
ax.set_ylim(0, 5.2)
ax.axis('off')
ax.set_aspect('equal')

LW = 2.2
yT, yB = 3.8, 0.8          # верхний и нижний проводники
xA, xB = 4.6, 7.6          # узлы A (между R1,R2) и B (выход)

# провода верхнего плеча
ax.plot([1.0, 2.4], [yT, yT], 'k', lw=LW)          # вход -> R1
ax.plot([3.6, xB], [yT, yT], 'k', lw=LW)           # R1 -> R2 (через узел A)
ax.plot([6.0, 9.2], [yT, yT], 'k', lw=LW)          # R2 -> выход
# нижний проводник
ax.plot([1.0, 9.2], [yB, yB], 'k', lw=LW)
# входные/выходные клеммы
ax.plot(1.0, yT, 'ko', ms=5); ax.plot(1.0, yB, 'ko', ms=5)
ax.plot(9.2, yT, 'ko', ms=5); ax.plot(9.2, yB, 'ko', ms=5)

def resistor(ax, x0, y, w=1.2, h=0.5, label='', dy=0.42):
    ax.add_patch(Rectangle((x0, y - h/2), w, h, fill=True, fc='white', ec='k', lw=LW))
    ax.text(x0 + w/2, y + h/2 + dy, label, ha='center', va='bottom', fontsize=16, style='italic')

def resistor_v(ax, x, y0, w=0.5, h=1.2, label='', dx=-0.55):
    ax.add_patch(Rectangle((x - w/2, y0), w, h, fill=True, fc='white', ec='k', lw=LW))
    ax.text(x + dx, y0 + h/2, label, ha='right', va='center', fontsize=16, style='italic')

def capacitor_v(ax, x, y0, gap=0.16, plate=0.55, label='', dx=-0.45):
    # y0 - центр конденсатора
    ax.plot([x - plate/2, x + plate/2], [y0 + gap/2, y0 + gap/2], 'k', lw=3)
    ax.plot([x - plate/2, x + plate/2], [y0 - gap/2, y0 - gap/2], 'k', lw=3)
    ax.text(x + dx, y0, label, ha='right', va='center', fontsize=16, style='italic')

# R1 на верхнем плече (2.4..3.6)
resistor(ax, 2.4, yT, label='R$_1$')
# R2 на верхнем плече (4.8..6.0)
resistor(ax, 4.8, yT, label='R$_2$')

# ветвь C1 из узла A
ax.plot([xA, xA], [yT, 2.75], 'k', lw=LW)
capacitor_v(ax, xA, 2.3, label='C$_1$')
ax.plot([xA, xA], [1.85, yB], 'k', lw=LW)

# ветвь C2 из узла B
ax.plot([xB, xB], [yT, 2.75], 'k', lw=LW)
capacitor_v(ax, xB, 2.3, label='C$_2$')
ax.plot([xB, xB], [1.85, yB], 'k', lw=LW)

# подписи U и V
ax.text(0.45, (yT+yB)/2 + 0.15, 'U', ha='center', va='center', fontsize=17, style='italic')
ax.text(9.75, (yT+yB)/2 + 0.15, 'V', ha='center', va='center', fontsize=17, style='italic')

# контурные токи I1 и I2 (по часовой)
def loop_current(ax, xc, yc, r, label):
    arc = Arc((xc, yc), 2*r, 2*r, angle=0, theta1=35, theta2=325, lw=1.6, color='tab:blue')
    ax.add_patch(arc)
    a = np.deg2rad(35)
    x1, y1 = xc + r*np.cos(a), yc + r*np.sin(a)
    ax.annotate('', xy=(x1 + 0.16, y1 + 0.06), xytext=(x1, y1),
                arrowprops=dict(arrowstyle='-|>', color='tab:blue', lw=1.6))
    ax.text(xc, yc, label, ha='center', va='center', fontsize=15, style='italic', color='tab:blue')

loop_current(ax, 2.75, 2.3, 0.62, 'I$_1$')
loop_current(ax, 6.15, 2.3, 0.62, 'I$_2$')

plt.tight_layout()
plt.savefig('img/scheme.png', bbox_inches='tight', facecolor='white')
print('saved img/scheme.png')
