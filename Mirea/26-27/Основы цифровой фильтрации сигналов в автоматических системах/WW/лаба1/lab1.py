# Лабораторная работа 1. Гармонический анализ сигналов. Вариант 19
# Сигнал: рампа 0 -> 2 В на [-1; 0) мс, полка 1 В на [0; 0.5) мс, T = 10 мс.
# Время в программе измеряется в мс, круговая частота — в рад/мс (= 10^3 рад/с).
import json
import os

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "figures")
os.makedirs(OUT, exist_ok=True)
plt.rcParams.update({"font.size": 11, "figure.dpi": 100, "axes.grid": True,
                     "grid.alpha": 0.4})

T = 10.0                 # период, мс
W0 = 2 * np.pi / T       # основная круговая частота, рад/мс
T1, T2 = -1.0, 0.5       # границы импульса, мс


def pulse(t):
    """Одиночный импульс варианта 19 (непериодический сигнал)."""
    t = np.asarray(t, dtype=float)
    x = np.zeros_like(t)
    ramp = (t >= -1) & (t < 0)
    x[ramp] = 2 * (t[ramp] + 1)
    x[(t >= 0) & (t < 0.5)] = 1.0
    return x


def s_periodic(t):
    """Периодическое продолжение импульса с периодом T."""
    t = np.asarray(t, dtype=float)
    return pulse(np.mod(t - T1, T) + T1)


def integrate(f, pieces=((-1.0, 0.0), (0.0, 0.5)), m=20001):
    """Интеграл по участкам непрерывности сигнала (метод трапеций)."""
    total = 0.0
    for a, b in pieces:
        t = np.linspace(a, b, m)
        # на правой границе берём предел слева, чтобы не захватить скачок
        y = f(np.append(t[:-1], b - 1e-12))
        total += np.trapezoid(y, t)
    return total


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(OUT, name), dpi=150)
    plt.close(fig)


# ---------------------------------------------------------------- Задание 1.1
def coeffs_numeric(N):
    a = np.zeros(N + 1)
    b = np.zeros(N + 1)
    for n in range(N + 1):
        a[n] = 2 / T * integrate(lambda t: pulse(t) * np.cos(n * W0 * t))
        b[n] = 2 / T * integrate(lambda t: pulse(t) * np.sin(n * W0 * t))
    return a, b


def coeffs_analytic(n):
    """Аналитические формулы для a_n, b_n (n >= 1)."""
    w = n * W0
    a = 2 / T * (2 * (1 - np.cos(w)) / w**2 + np.sin(w / 2) / w)
    b = 2 / T * (2 * (np.sin(w) - w) / w**2 + (1 - np.cos(w / 2)) / w)
    return a, b


NMAX = 10
a, b = coeffs_numeric(NMAX)
A = np.hypot(a, b)
A[0] = abs(a[0]) / 2                  # для n = 0 амплитуда — постоянная составляющая
phi = np.arctan2(-b, a)               # s(t) = a0/2 + sum A_n cos(n W0 t + phi_n)
phi[0] = 0.0
A[np.abs(A) < 1e-9] = 0.0
phi[A == 0] = 0.0

n_an = np.arange(1, NMAX + 1)
a_an, b_an = coeffs_analytic(n_an)
err_coef = max(np.max(np.abs(a_an - a[1:])), np.max(np.abs(b_an - b[1:])),
               abs(a[0] - 0.3))

print("Задание 1.1. Коэффициенты ряда Фурье (T = 10 мс)")
print(f"{'n':>3} {'a_n':>9} {'b_n':>9} {'A_n':>9} {'phi_n,рад':>10} {'phi_n,°':>9}")
for n in range(NMAX + 1):
    print(f"{n:>3} {a[n]:9.5f} {b[n]:9.5f} {A[n]:9.5f} {phi[n]:10.4f} "
          f"{np.degrees(phi[n]):9.2f}")
print(f"Макс. расхождение численного и аналитического расчёта: {err_coef:.2e}")

# мощность сигнала: прямой расчёт и по теореме Парсеваля
P_direct = integrate(lambda t: pulse(t) ** 2) / T


def partial_sum(t, N):
    aN, bN = coeffs_numeric(N)
    x = np.full_like(t, aN[0] / 2)
    for n in range(1, N + 1):
        x += aN[n] * np.cos(n * W0 * t) + bN[n] * np.sin(n * W0 * t)
    return x, aN, bN


t = np.linspace(-12, 22, 34001)
s = s_periodic(t)

fig, ax = plt.subplots(figsize=(10, 3.6))
ax.plot(t, s, "b")
ax.set(xlabel="t, мс", ylabel="s(t), В",
       title="Периодический сигнал s(t), вариант 19 (T = 10 мс)")
save(fig, "fig01_signal.png")

fig, ax = plt.subplots(figsize=(7, 3.8))
ax.stem(range(NMAX + 1), A, basefmt="k-")
ax.set(xlabel="n", ylabel="$A_n$, В", title="Амплитудный спектр $A_n$",
       xticks=range(NMAX + 1))
save(fig, "fig02_amp_spectrum.png")

fig, ax = plt.subplots(figsize=(7, 3.8))
ax.stem(range(NMAX + 1), phi, basefmt="k-")
ax.set(xlabel="n", ylabel="$\\varphi_n$, рад", title="Фазовый спектр $\\varphi_n$",
       xticks=range(NMAX + 1))
save(fig, "fig03_phase_spectrum.png")

approx = {}
colors = {5: "tab:orange", 10: "tab:green", 20: "tab:red"}
for k, N in enumerate((5, 10, 20)):
    xN, aN, bN = partial_sum(t, N)
    eps = s - xN
    in_period = (t >= -1) & (t < 9)
    approx[N] = {
        "rms": float(np.sqrt(np.mean(eps[in_period] ** 2))),
        "max": float(np.max(np.abs(eps))),
        "peak": float(np.max(xN)),
        "P": float(aN[0] ** 2 / 4 + 0.5 * np.sum(aN[1:] ** 2 + bN[1:] ** 2)),
    }
    fig, ax = plt.subplots(figsize=(10, 3.8))
    ax.plot(t, s, "b", lw=1.2, label="исходный s(t)")
    ax.plot(t, xN, color=colors[N], lw=1.4, label=f"$s^*_{{{N}}}(t)$")
    ax.set(xlabel="t, мс", ylabel="В", title=f"Аппроксимация рядом Фурье, N = {N}")
    ax.legend(loc="upper right")
    save(fig, f"fig{4 + k:02d}_approx_N{N}.png")

    fig, ax = plt.subplots(figsize=(10, 3.4))
    ax.plot(t, eps, color=colors[N], lw=1.2)
    ax.set(xlabel="t, мс", ylabel="ε(t), В",
           title=f"Сигнал ошибки ε(t) = s(t) − $s^*_{{{N}}}(t)$, N = {N}")
    save(fig, f"fig{7 + k:02d}_error_N{N}.png")

# крупный план одного импульса: все три аппроксимации вместе
tz = np.linspace(-2, 1.5, 4001)
fig, ax = plt.subplots(figsize=(9, 4))
ax.plot(tz, s_periodic(tz), "b", lw=2, label="s(t)")
for N in (5, 10, 20):
    ax.plot(tz, partial_sum(tz, N)[0], color=colors[N], label=f"N = {N}")
ax.set(xlabel="t, мс", ylabel="В", title="Сравнение аппроксимаций на одном импульсе")
ax.legend()
save(fig, "fig10_approx_zoom.png")

print(f"\nМощность: прямой расчёт P = {P_direct:.5f} В^2")
for N, r in approx.items():
    print(f"N = {N:2d}: СКО ошибки = {r['rms']:.4f} В, max|ε| = {r['max']:.4f} В, "
          f"P_N = {r['P']:.5f} В^2 ({100 * r['P'] / P_direct:.1f} %)")

# ---------------------------------------------------------------- Задание 1.2
def X_numeric(w):
    """Прямое преобразование Фурье X(jw) = ∫ x(t) e^{-jwt} dt (численно)."""
    w = np.atleast_1d(w)
    X = np.zeros(w.shape, dtype=complex)
    for a_, b_ in ((-1.0, 0.0), (0.0, 0.5)):
        tt = np.linspace(a_, b_, 3001)
        xt = pulse(np.append(tt[:-1], b_ - 1e-12))
        X += np.trapezoid(xt[None, :] * np.exp(-1j * np.outer(w, tt)), tt, axis=1)
    return X


def X_analytic(w):
    w = np.asarray(w, dtype=float)
    X = np.full(w.shape, 1.5, dtype=complex)
    nz = w != 0
    wn = w[nz]
    X[nz] = (2 * (1 + 1j * wn - np.exp(1j * wn)) / wn**2
             + (1 - np.exp(-0.5j * wn)) / (1j * wn))
    return X


def restore(t, wc, dw=0.002):
    """Обратное преобразование по формуле (2.15) на интервале [0, wc]."""
    w = np.arange(0, wc + dw / 2, dw)
    X = X_analytic(w)
    a_w, b_w = X.real, -X.imag
    x = np.empty_like(t)
    for i in range(0, len(t), 200):
        tt = t[i:i + 200]
        integrand = (a_w[None, :] * np.cos(np.outer(tt, w))
                     + b_w[None, :] * np.sin(np.outer(tt, w)))
        x[i:i + 200] = np.trapezoid(integrand, w, axis=1) / np.pi
    return x


WC = 20.0                                  # основной интервал [0, wc], рад/мс
w = np.linspace(0, WC, 4001)
Xw = X_numeric(w)
err_X = float(np.max(np.abs(Xw - X_analytic(w))))
Xmag = np.abs(Xw)
Xph = np.angle(Xw)
print(f"\nЗадание 1.2. X(0) = {Xw[0].real:.4f} В·мс, "
      f"расхождение численного и аналитического X(jw): {err_X:.2e}")

tp = np.linspace(-4, 4, 8001)
fig, ax = plt.subplots(figsize=(9, 3.6))
ax.plot(tp, pulse(tp), "b")
ax.set(xlabel="t, мс", ylabel="x(t), В", title="Одиночный импульс x(t), вариант 19")
save(fig, "fig11_pulse.png")

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(w, Xmag, "b")
ax.set(xlabel="ω, 10³ рад/с", ylabel="X(ω), В·мс",
       title="Амплитудная спектральная характеристика X(ω)")
save(fig, "fig12_X_amp.png")

fig, ax = plt.subplots(figsize=(9, 3.8))
ax.plot(w, Xph, "r")
ax.set(xlabel="ω, 10³ рад/с", ylabel="φ(ω), рад",
       title="Фазовая спектральная характеристика φ(ω)")
save(fig, "fig13_X_phase.png")

# годограф спектральной характеристики
fig, ax = plt.subplots(figsize=(8, 4))
ax.plot(Xw.real, -Xw.imag, "b")
ax.plot(Xw.real[0], -Xw.imag[0], "ko")
ax.annotate("ω = 0", (Xw.real[0], -Xw.imag[0]), textcoords="offset points",
            xytext=(-40, 8))
ax.set(xlabel="a(ω), В·мс", ylabel="−b(ω), В·мс",
       title="Годограф X(jω), ω = 0…20·10³ рад/с")
save(fig, "fig14_hodograph.png")

restored = {}
tr = np.linspace(-3, 3, 3001)
xr_true = pulse(tr)
for k, wc in enumerate((20.0, 5.0, 100.0)):
    xr = restore(tr, wc)
    restored[wc] = {"rms": float(np.sqrt(np.mean((xr - xr_true) ** 2))),
                    "peak": float(xr.max())}
    fig, ax = plt.subplots(figsize=(9, 3.8))
    ax.plot(tr, xr_true, "b", lw=1.5, label="исходный x(t)")
    ax.plot(tr, xr, "r", lw=1.2, label="восстановленный $x_в(t)$")
    ax.set(xlabel="t, мс", ylabel="В",
           title=f"Восстановление сигнала, интервал [0; {wc:g}·10³] рад/с")
    ax.legend(loc="upper right")
    save(fig, f"fig{15 + k}_restore_wc{int(wc)}.png")

for wc, r in restored.items():
    print(f"wc = {wc:5.0f}·10^3 рад/с: СКО = {r['rms']:.4f} В, max x_в = {r['peak']:.3f} В")

# энергия импульса: во временной и в частотной области (Рэлей)
E_t = integrate(lambda t: pulse(t) ** 2)
wE = np.linspace(0, 2000, 400001)
E_w = np.trapezoid(np.abs(X_analytic(wE)) ** 2, wE) / np.pi
print(f"Энергия: E_t = {E_t:.4f} В²·мс, E_ω = {E_w:.4f} В²·мс")

# связь спектров: a_n - j b_n = 2 X(j n W0) / T
link = np.max(np.abs((a[1:] - 1j * b[1:]) - 2 * X_analytic(n_an * W0) / T))
print(f"Проверка a_n - j b_n = 2X(jnΩ0)/T: расхождение {link:.2e}")

with open(os.path.join(OUT, "results.json"), "w", encoding="utf-8") as f:
    json.dump({
        "a": a.tolist(), "b": b.tolist(), "A": A.tolist(), "phi": phi.tolist(),
        "err_coef": err_coef, "P_direct": P_direct,
        "approx": {str(k): v for k, v in approx.items()},
        "err_X": err_X, "X0": float(Xw[0].real),
        "restored": {str(int(k)): v for k, v in restored.items()},
        "E_t": E_t, "E_w": float(E_w), "link": float(link),
    }, f, ensure_ascii=False, indent=1)
