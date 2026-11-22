# -*- coding: utf-8 -*-
"""Расчёты для практического задания 1, вариант 19 (схема 1)."""
import numpy as np
from scipy import signal

# Исходные данные (таблица 1, столбец 1)
R1 = 900.0      # Ом
R2 = 4900.0     # Ом
C1 = 1.59e-6    # Ф
C2 = 0.36e-6    # Ф

# Коэффициенты W(p) = 1 / (a2*p^2 + a1*p + 1)
a2 = R1 * R2 * C1 * C2
a1 = R1 * C1 + (R1 + R2) * C2
a0 = 1.0

print(f"a2 = R1*R2*C1*C2 = {a2:.6e} с^2")
print(f"a1 = R1*C1 + (R1+R2)*C2 = {a1:.6e} с")
print(f"  R1*C1 = {R1*C1:.6e}, (R1+R2)*C2 = {(R1+R2)*C2:.6e}")

# Полюсы
D = a1**2 - 4 * a2 * a0
print(f"\nD = a1^2 - 4*a2 = {D:.6e}")
sqrtD = np.sqrt(D)
p1 = (-a1 + sqrtD) / (2 * a2)
p2 = (-a1 - sqrtD) / (2 * a2)
print(f"sqrt(D) = {sqrtD:.6e}")
print(f"p1 = {p1:.4f} 1/с")
print(f"p2 = {p2:.4f} 1/с")
print(f"проверка: p1+p2 = {p1+p2:.4f}, -a1/a2 = {-a1/a2:.4f}")
print(f"проверка: p1*p2 = {p1*p2:.4f}, a0/a2 = {a0/a2:.4f}")

# scipy проверка
sys_tf = signal.TransferFunction([1.0], [a2, a1, a0])
print(f"\nscipy poles: {sys_tf.poles}")
print(f"scipy zeros: {sys_tf.zeros}")

# ИПФ: h(t) = (1/a2) * (exp(p1*t) - exp(p2*t)) / (p1 - p2)
K = 1.0 / a2 / (p1 - p2)
print(f"\nИПФ: h(t) = K*(exp(p1*t) - exp(p2*t)), K = 1/(a2*(p1-p2)) = {K:.4f}")
print(f"h(t) = {K:.2f}*exp({p1:.2f}*t) - {K:.2f}*exp({p2:.2f}*t)")
# h(0) = 0, начальный наклон = K*(p1-p2) = 1/a2
print(f"h(0) = {K*(1-1):.2f}, h'(0) = {K*(p1-p2):.4f} = 1/a2 = {1/a2:.4f}")
tmax = 5 / abs(p1)  # ~5 постоянных времени медленного полюса
print(f"характерное время затухания ~ {1/abs(p1)*1000:.3f} мс, берём интервал 0..{tmax*1000:.1f} мс")
t_pk = np.log(p2 / p1) / (p1 - p2)
print(f"максимум ИПФ при t = {t_pk*1000:.4f} мс, h_max = {K*(np.exp(p1*t_pk)-np.exp(p2*t_pk)):.2f} 1/с")

# АЧХ/ФЧХ характерные точки
for w in [0, 100, 300, 400, 500, 1000, 2000, 10000]:
    W = 1.0 / (a2 * (1j * w) ** 2 + a1 * 1j * w + a0)
    print(f"w={w:>6} рад/с: A={abs(W):.4f}, phi={np.degrees(np.angle(W)):8.2f} град")

# частота среза по уровню 0.707
from scipy.optimize import brentq
wc = brentq(lambda w: abs(1.0/(a2*(1j*w)**2 + a1*1j*w + 1)) - 1/np.sqrt(2), 1, 1e5)
print(f"\nчастота среза (A=0.707): w_c = {wc:.1f} рад/с, f_c = {wc/2/np.pi:.1f} Гц")
