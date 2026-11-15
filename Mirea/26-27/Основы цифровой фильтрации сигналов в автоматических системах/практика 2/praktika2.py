# Практическая работа 2. Разложение сигнала по системе функций Лагерра
# Оськин В.А., КВБО-11-24, вариант 19
# В таблице 16 вариантов, поэтому беру вариант 19 - 16 = 3: a = 40, b = 60
# ИПФ системы с двумя вещественными полюсами p1 = -a, p2 = -b

import math
import numpy as np
import matplotlib.pyplot as plt

a = 40
b = 60


# ИПФ системы второго порядка, формула (1.13)
def w_func(t):
    return 1 / (b - a) * np.exp(-a * t) + 1 / (a - b) * np.exp(-b * t)


# функция Лагерра номер n, формула (1.5)
def laguerre(n, t, alpha):
    s = np.zeros_like(t)
    for j in range(n + 1):
        k = (-1) ** j * math.comb(n, j) / math.factorial(j)
        s = s + k * (2 * alpha * t) ** j
    return math.sqrt(2 * alpha) * np.exp(-alpha * t) * s


# коэффициенты ряда c_n = интеграл от 0 до T от w(t)*l_n(t)
def coeffs(w, t, alpha, N):
    c = np.zeros(N)
    for n in range(N):
        c[n] = np.trapezoid(w * laguerre(n, t, alpha), t)
    return c


# частичная сумма ряда w*_N(t)
def approx(c, t, alpha, N):
    s = np.zeros_like(t)
    for n in range(N):
        s = s + c[n] * laguerre(n, t, alpha)
    return s


# длительность сигнала: после этого момента |x(t)| < 0.05 % от максимума
def duration(x, t):
    x = np.abs(x)
    return t[np.nonzero(x > 0.0005 * x.max())[0][-1]]


# ---------------- 1. Моделирование сигнала w(t) ----------------
t_long = np.linspace(0, 1, 100001)
w_long = w_func(t_long)
w_max = w_long.max()
t_max = t_long[np.argmax(w_long)]
T_min = duration(w_long, t_long)
T = math.ceil(T_min * 100) / 100      # округлил вверх до сотых

K = 1000                              # число интервалов, точек K+1 (> 50)
t = np.linspace(0, T, K + 1)
dt = t[1] - t[0]
w = w_func(t)

print('Вариант 19: a = %d, b = %d' % (a, b))
print('1) w_max = %.6f при t = %.4f c' % (w_max, t_max))
print('   0.05%% от максимума при t = %.4f c' % T_min)
print('   беру T = %.2f c, dt = %.5f c' % (T, dt))

fig = plt.figure(figsize=(8, 4.5))
fig.canvas.manager.set_window_title('Рисунок 2 – ИПФ w(t)')
plt.plot(t, w)
plt.plot(t_max, w_max, 'ro')
plt.title('Импульсная переходная функция w(t), a = %d, b = %d' % (a, b))
plt.xlabel('t, c')
plt.ylabel('w(t)')
plt.grid(True)

# ---------------- 2. Первые пять функций Лагерра ----------------
alpha = 2 * min(a, b)                 # формула (1.15)
L = [laguerre(n, t, alpha) for n in range(5)]

print('\n2) alpha = 2*min(a, b) = %d' % alpha)
print('   длительность w(t) = %.4f c, длительность l4(t) = %.4f c'
      % (T_min, duration(L[4], t)))

fig = plt.figure(figsize=(8, 4.5))
fig.canvas.manager.set_window_title('Рисунок 3 – Функции Лагерра')
for n in range(5):
    plt.plot(t, L[n], label='l%d(t)' % n)
w_scaled = w / w_max * math.sqrt(2 * alpha)    # w(t) в масштабе l_n(0)
plt.plot(t, w_scaled, 'k--', label='w(t) в масштабе')
plt.title('Первые пять функций Лагерра, alpha = %d' % alpha)
plt.xlabel('t, c')
plt.ylabel('l_n(t)')
plt.grid(True)
plt.legend()

# ---------------- 3. Проверка ортогональности ----------------
print('\n3) Интегралы от 0 до T от l_n(t)*l_m(t):')
print('       m=0       m=1       m=2       m=3       m=4')
for n in range(5):
    row = ''
    for m in range(5):
        row += '%10.5f' % np.trapezoid(L[n] * L[m], t)
    print('n=%d%s' % (n, row))

# ---------------- 4. Коэффициенты ряда ----------------
c = coeffs(w, t, alpha, 5)
print('\n4) Коэффициенты ряда:')
for n in range(5):
    print('   c%d = %11.4e' % (n, c[n]))

fig = plt.figure(figsize=(8, 4.5))
fig.canvas.manager.set_window_title('Рисунок 4 – Спектральная диаграмма')
plt.stem(range(5), c, basefmt='k-')
plt.title('Спектральная диаграмма коэффициентов c_n')
plt.xlabel('n')
plt.ylabel('c_n')
plt.xticks(range(5))
plt.grid(True)

# ---------------- 5-8. Аппроксимация, ошибка, энергия ----------------
E = np.trapezoid(w ** 2, t)           # полная энергия сигнала
print('\n5-8) Полная энергия сигнала E = %.4e' % E)
print('   N    E*_N        E*_N/E, %   sigma^2      max|eps|')

fig4 = plt.figure(figsize=(8, 4.5))
fig4.canvas.manager.set_window_title('Рисунок 5 – Аппроксимация w(t)')
plt.plot(t, w, 'k', linewidth=2.5, label='w(t)')

fig5 = plt.figure(figsize=(8, 4.5))
fig5.canvas.manager.set_window_title('Рисунок 6 – Ошибка аппроксимации')

for N in (3, 4, 5):
    wN = approx(c, t, alpha, N)
    eps = w - wN
    E_N = np.sum(c[:N] ** 2)          # формула (1.12)
    sigma2 = np.trapezoid(eps ** 2, t)
    print('   %d   %.4e   %8.3f    %.4e   %.4e'
          % (N, E_N, E_N / E * 100, sigma2, np.max(np.abs(eps))))

    plt.figure(fig4.number)
    plt.plot(t, wN, '--', label='w*_%d(t)' % N)
    plt.figure(fig5.number)
    plt.plot(t, eps, label='eps_%d(t)' % N)

plt.figure(fig4.number)
plt.title('ИПФ и ее аппроксимация рядом Лагерра, alpha = %d' % alpha)
plt.xlabel('t, c')
plt.ylabel('w(t)')
plt.grid(True)
plt.legend()

plt.figure(fig5.number)
plt.title('Ошибка аппроксимации eps_N(t) = w(t) - w*_N(t)')
plt.xlabel('t, c')
plt.ylabel('eps_N(t)')
plt.grid(True)
plt.legend()

# ---------------- 9. Влияние alpha при N = 5 ----------------
alphas = np.arange(20, 205, 5)
s2 = []
for al in alphas:
    ck = coeffs(w, t, al, 5)
    s2.append(np.trapezoid((w - approx(ck, t, al, 5)) ** 2, t))
s2 = np.array(s2)
i_best = np.argmin(s2)
i_80 = np.nonzero(alphas == alpha)[0][0]

print('\n9) N = 5, влияние alpha на sigma^2:')
for al in (20, 40, 50, 60, 80, 120, 160, 200):
    i = np.nonzero(alphas == al)[0][0]
    print('   alpha = %3d   sigma^2 = %.4e   sigma^2/E = %.2e'
          % (al, s2[i], s2[i] / E))
print('   минимум при alpha = %d, sigma^2 = %.4e'
      % (alphas[i_best], s2[i_best]))

fig = plt.figure(figsize=(8, 4.5))
fig.canvas.manager.set_window_title('Рисунок 7 – Ошибка от alpha')
plt.semilogy(alphas, s2, 'o-', markersize=4)
plt.semilogy(alpha, s2[i_80], 'rs', label='alpha = %d' % alpha)
plt.semilogy(alphas[i_best], s2[i_best], 'g^', markersize=9,
             label='минимум, alpha = %d' % alphas[i_best])
plt.title('Средняя квадратическая ошибка sigma^2 при N = 5')
plt.xlabel('alpha')
plt.ylabel('sigma^2')
plt.grid(True)
plt.legend()

fig = plt.figure(figsize=(8, 4.5))
fig.canvas.manager.set_window_title('Рисунок 8 – eps_5(t) при разных alpha')
for al in (30, 50, 80, 120, 160):
    ck = coeffs(w, t, al, 5)
    plt.plot(t, w - approx(ck, t, al, 5), label='alpha = %d' % al)
plt.title('Ошибка аппроксимации eps_5(t) при разных alpha')
plt.xlabel('t, c')
plt.ylabel('eps_5(t)')
plt.grid(True)
plt.legend()

plt.show()
