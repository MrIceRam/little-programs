# Курсовая работа по дисциплине
# «Основы цифровой фильтрации сигналов в автоматических системах»
# Тема: синтез цифровых фильтров с бесконечной импульсной характеристикой
# Оськин В.А., КВБО-11-24, вариант 19
# Вариант 19: схема 1 (две RC-цепочки), набор параметров 1,
# методы синтеза - метод инвариантной импульсной характеристики (ИИХ)
# и метод билинейного преобразования
# (в методичке расчёты в Matlab, здесь то же самое на Python: numpy + scipy)

import os
import json
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# ---------------- исходные данные ----------------
R1 = 900.0          # Ом
R2 = 4900.0         # Ом
C1 = 1.59e-6        # Ф
C2 = 0.36e-6        # Ф

papka = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'графики')
os.makedirs(papka, exist_ok=True)
res = {}            # сюда складываю числа для отчёта


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(papka, name), dpi=130)
    plt.close(fig)


def db(x):
    return 20 * np.log10(np.abs(x) + 1e-300)


print('Вариант 19, схема 1: R1 = %g Ом, R2 = %g Ом, C1 = %g мкФ, C2 = %g мкФ'
      % (R1, R2, C1 * 1e6, C2 * 1e6))

# ======================= 1. Аналоговый прототип =======================
# Метод узловых потенциалов, узел 1 - между R1 и R2, узел 2 - выход V:
#   (U - V1)/R1 = C1*p*V1 + (V1 - V)/R2
#   (V1 - V)/R2 = C2*p*V
# Из второго V1 = V*(1 + R2*C2*p), подставляю в первое и получаю
#   W(p) = V/U = 1 / (a2*p^2 + a1*p + 1)
a2 = R1 * C1 * R2 * C2
a1 = R1 * C1 + R2 * C2 + R1 * C2
num_a = np.array([1.0])
den_a = np.array([a2, a1, 1.0])
print('\n1) Аналоговый прототип W(p) = 1 / (a2*p^2 + a1*p + 1)')
print('   R1*C1 = %.4e c, R2*C2 = %.4e c, R1*C2 = %.4e c' % (R1 * C1, R2 * C2, R1 * C2))
print('   a2 = R1*C1*R2*C2 = %.6e c^2' % a2)
print('   a1 = R1*C1 + R2*C2 + R1*C2 = %.6e c' % a1)

# полюса
D = a1 ** 2 - 4 * a2
p1 = (-a1 + np.sqrt(D)) / (2 * a2)
p2 = (-a1 - np.sqrt(D)) / (2 * a2)
print('   дискриминант D = a1^2 - 4*a2 = %.6e > 0 -> полюса вещественные' % D)
print('   p1 = %.4f 1/c, p2 = %.4f 1/c' % (p1, p2))
print('   проверка np.roots:', np.round(np.roots(den_a), 4))
T1, T2 = -1 / p1, -1 / p2
print('   постоянные времени T1 = %.4f мс, T2 = %.4f мс' % (T1 * 1e3, T2 * 1e3))

# разложение на простые дроби W(p) = Ck1/(p - p1) + Ck2/(p - p2)
k0 = 1 / a2
Ck1 = k0 / (p1 - p2)
Ck2 = k0 / (p2 - p1)
r, pp, _ = signal.residue(num_a, den_a)
print('   W(p) = %.4f/(p - (%.4f)) + (%.4f)/(p - (%.4f))' % (Ck1, p1, Ck2, p2))
print('   проверка residue: вычеты', np.round(r, 4), 'полюса', np.round(pp, 4))

# собственная частота и затухание
w0 = 1 / np.sqrt(a2)
dz = a1 / (2 * np.sqrt(a2))
print('   w0 = 1/sqrt(a2) = %.3f рад/с (%.3f Гц), коэф. затухания = %.4f'
      % (w0, w0 / 2 / np.pi, dz))


# АЧХ и ФЧХ аналитически
def A_an(w):
    return 1 / np.sqrt((1 - a2 * w ** 2) ** 2 + (a1 * w) ** 2)


def phi_an(w):
    return -np.arctan2(a1 * w, 1 - a2 * w ** 2)


def w_an(t):        # ИПФ
    return Ck1 * np.exp(p1 * t) + Ck2 * np.exp(p2 * t)


# частота среза по уровню 0.707 и ширина спектра по уровню 0.05
from scipy.optimize import brentq
w_c = brentq(lambda w: A_an(w) - 1 / np.sqrt(2), 1, 1e5)
w_m = brentq(lambda w: A_an(w) - 0.05, 1, 1e6)
print('   частота среза (|W| = 0.707): w_c = %.2f рад/с, f_c = %.2f Гц' % (w_c, w_c / 2 / np.pi))
print('   ширина спектра (|W| = 0.05): w_m = %.2f рад/с, f_m = %.2f Гц' % (w_m, w_m / 2 / np.pi))
print('   W(0) = %.4f -> ФНЧ, на высоких частотах |W| ~ 1/(a2*w^2), -40 дБ/дек' % A_an(0))

wmax = 10000
w = np.linspace(0, wmax, 4001)
w[0] = 1e-9
_, H_s = signal.freqs(num_a, den_a, worN=w)
t = np.linspace(0, 0.015, 1501)
_, h_s = signal.impulse((num_a, den_a), T=t)
print('   макс. расхождение аналитики и scipy: АЧХ %.2e, ФЧХ %.2e рад, ИПФ %.2e'
      % (np.max(np.abs(A_an(w) - np.abs(H_s))),
         np.max(np.abs(phi_an(w) - np.unwrap(np.angle(H_s)))),
         np.max(np.abs(w_an(t) - h_s))))
t_max = np.log(p2 / p1) / (p1 - p2)
print('   максимум ИПФ при t = ln(p2/p1)/(p1-p2) = %.4f мс, w(tmax) = %.3f 1/c'
      % (t_max * 1e3, w_an(t_max)))

res['analog'] = dict(a2=a2, a1=a1, p1=p1, p2=p2, T1=T1, T2=T2, Ck1=Ck1, Ck2=Ck2,
                     k0=k0, w0=w0, dz=dz, w_c=w_c, w_m=w_m, t_max=t_max,
                     h_max=w_an(t_max))

# карта полюсов
fig = plt.figure(figsize=(7, 3.2))
plt.plot([p1, p2], [0, 0], 'rx', markersize=11, markeredgewidth=2, label='полюса')
for p in (p1, p2):
    plt.annotate('%.1f' % p, (p, 0), textcoords='offset points', xytext=(-14, 10))
plt.axhline(0, color='k', linewidth=0.7)
plt.axvline(0, color='k', linewidth=0.7)
plt.xlim(-1200, 200)
plt.ylim(-300, 300)
plt.title('Карта нулей и полюсов аналогового прототипа (нулей нет)')
plt.xlabel('Re p, 1/c')
plt.ylabel('Im p, 1/c')
plt.grid(True)
plt.legend()
save(fig, 'fig02_analog_pz.png')

# АЧХ, ФЧХ, ИПФ - аналитика и встроенные функции
fig, ax = plt.subplots(2, 1, figsize=(8, 6.5))
ax[0].plot(w, A_an(w), 'b', linewidth=2.5, label='аналитическое выражение')
ax[0].plot(w, np.abs(H_s), 'y--', linewidth=1.2, label='scipy.signal.freqs')
ax[0].axhline(1 / np.sqrt(2), color='gray', linestyle=':', linewidth=1)
ax[0].plot(w_c, 1 / np.sqrt(2), 'ko', markersize=4)
ax[0].annotate('w_c = %.0f рад/с' % w_c, (w_c, 0.707), xytext=(10, 5),
               textcoords='offset points')
ax[0].set_title('АЧХ аналогового прототипа A(w) = |W(jw)|')
ax[0].set_xlabel('w, рад/с')
ax[0].set_ylabel('A(w)')
ax[0].grid(True)
ax[0].legend()
wl = np.logspace(0, 5, 2000)
ax[1].semilogx(wl, db(A_an(wl)), 'b')
ax[1].set_title('АЧХ в логарифмическом масштабе (ЛАЧХ)')
ax[1].set_xlabel('w, рад/с')
ax[1].set_ylabel('L(w), дБ')
ax[1].set_ylim(-100, 5)
ax[1].grid(True, which='both')
save(fig, 'fig03_analog_afc.png')

fig = plt.figure(figsize=(8, 3.8))
plt.plot(w, np.degrees(phi_an(w)), 'b', linewidth=2.5, label='аналитическое выражение')
plt.plot(w, np.degrees(np.unwrap(np.angle(H_s))), 'y--', linewidth=1.2,
         label='scipy.signal.freqs')
plt.title('ФЧХ аналогового прототипа phi(w) = arg W(jw)')
plt.xlabel('w, рад/с')
plt.ylabel('phi(w), град')
plt.yticks(np.arange(-180, 1, 30))
plt.grid(True)
plt.legend()
save(fig, 'fig04_analog_pfc.png')

fig = plt.figure(figsize=(8, 3.8))
plt.plot(t * 1e3, w_an(t), 'b', linewidth=2.5, label='аналитическое выражение')
plt.plot(t * 1e3, h_s, 'y--', linewidth=1.2, label='scipy.signal.impulse')
plt.plot(t_max * 1e3, w_an(t_max), 'ko', markersize=4)
plt.title('ИПФ аналогового прототипа w(t)')
plt.xlabel('t, мс')
plt.ylabel('w(t), 1/c')
plt.grid(True)
plt.legend()
save(fig, 'fig05_analog_ipf.png')


# ======================= 2. Синтез цифровых фильтров =======================
# Td1 выбираю по рекомендации методички fd = (5...10)*fm,
# Td2 - заметно больше, чтобы различия были хорошо видны
f_m = w_m / 2 / np.pi
Tds = [0.2e-3, 1e-3]
print('\n2) Выбор интервала дискретизации: fm = %.1f Гц, 5*fm...10*fm = %.0f...%.0f Гц'
      % (f_m, 5 * f_m, 10 * f_m))
for Td in Tds:
    print('   Td = %.1f мс: fd = %.0f Гц = %.1f*fm, частота Найквиста w_N = pi/Td = %.1f рад/с'
          % (Td * 1e3, 1 / Td, 1 / Td / f_m, np.pi / Td))


def iih(Td):
    # метод инвариантной ИПФ: Wd(z) = Td * sum Ck/(1 - exp(pk*Td) z^-1)
    z1, z2 = np.exp(p1 * Td), np.exp(p2 * Td)
    b = np.array([0.0, Td * Ck1 * (z1 - z2)])   # Ck1 + Ck2 = 0, поэтому b0 = 0
    a = np.array([1.0, -(z1 + z2), z1 * z2])
    return b, a, (z1, z2)


def bil(Td):
    # метод билинейного преобразования p = 2/Td * (1 - z^-1)/(1 + z^-1)
    K = 2 / Td
    B0 = a2 * K ** 2 + a1 * K + 1
    B1 = 2 - 2 * a2 * K ** 2
    B2 = a2 * K ** 2 - a1 * K + 1
    b = np.array([1.0, 2.0, 1.0]) / B0
    a = np.array([B0, B1, B2]) / B0
    return b, a, (B0, B1, B2)


metody = {'ИИХ': iih, 'БП': bil}
cvet = {'ИИХ': 'tab:red', 'БП': 'tab:green'}
full = {'ИИХ': 'метод ИИХ', 'БП': 'билинейное преобразование'}
filt = {}           # filt[(метод, Td)] = (b, a)
res['digital'] = {}

for Td in Tds:
    for m, f in metody.items():
        b, a, extra = f(Td)
        filt[(m, Td)] = (b, a)
        zeros = np.roots(b[np.argmax(b != 0):]) if np.count_nonzero(b) > 1 else np.array([])
        if m == 'ИИХ':
            zeros = np.array([0.0])          # b1*z^-1 = b1*z/z^2 -> ноль в z = 0
        poles = np.roots(a)
        K0 = np.sum(b) / np.sum(a)
        print('\n   %s, Td = %.1f мс:' % (full[m], Td * 1e3))
        if m == 'ИИХ':
            print('     z1 = exp(p1*Td) = %.6f, z2 = exp(p2*Td) = %.6f' % extra)
        else:
            print('     B0 = %.6f, B1 = %.6f, B2 = %.6f (до нормировки)' % extra)
            bb, aa = signal.bilinear(num_a, den_a, fs=1 / Td)
            print('     проверка scipy.signal.bilinear: b =', np.round(bb, 8), 'a =', np.round(aa, 8))
        print('     b =', np.array2string(b, precision=8), ' a =', np.array2string(a, precision=8))
        print('     нули:', np.round(zeros, 6), ' полюса:', np.round(poles, 6),
              ' |z| полюсов:', np.round(np.abs(poles), 6))
        print('     коэффициент передачи на нулевой частоте Wd(1) = %.6f' % K0)
        res['digital']['%s_%g' % (m, Td)] = dict(b=b.tolist(), a=a.tolist(),
                                                  zeros=np.real(zeros).tolist(),
                                                  poles=np.real(poles).tolist(), K0=K0)

# ---- карты нулей и полюсов ----
for i, Td in enumerate(Tds):
    fig, ax = plt.subplots(1, 2, figsize=(9, 4.4))
    for j, m in enumerate(metody):
        b, a = filt[(m, Td)]
        z = np.array(res['digital']['%s_%g' % (m, Td)]['zeros'])
        p = np.roots(a)
        q = np.linspace(0, 2 * np.pi, 400)
        ax[j].plot(np.cos(q), np.sin(q), 'k', linewidth=0.7)
        ax[j].plot(np.real(p), np.imag(p), 'x', color=cvet[m], markersize=10,
                   markeredgewidth=2, label='полюса')
        ax[j].plot(np.real(z), np.imag(z), 'o', mfc='none', color='b', markersize=9,
                   markeredgewidth=1.5, label='нули' + (' (двукратный)' if m == 'БП' else ''))
        ax[j].axhline(0, color='k', linewidth=0.5)
        ax[j].axvline(0, color='k', linewidth=0.5)
        ax[j].set_aspect('equal')
        ax[j].set_xlim(-1.3, 1.3)
        ax[j].set_ylim(-1.3, 1.3)
        ax[j].set_title('%s, Td = %.1f мс' % (full[m], Td * 1e3))
        ax[j].set_xlabel('Re z')
        ax[j].set_ylabel('Im z')
        ax[j].grid(True)
        ax[j].legend(loc='upper left', fontsize=8)
        for pk in p:
            ax[j].annotate('%.4f' % np.real(pk), (np.real(pk), 0),
                           textcoords='offset points', xytext=(-18, -16 if pk == p[0] else 10),
                           fontsize=8)
    save(fig, 'fig%02d_pz_Td%d.png' % (6 + i, i + 1))


# ---- АЧХ, ФЧХ, ИПФ цифровых фильтров в сравнении с аналоговым ----
def freq_d(b, a, Td, w):
    _, H = signal.freqz(b, a, worN=w * Td)
    return H


figno = 8
for i, Td in enumerate(Tds):
    wN = np.pi / Td
    wd = np.linspace(1e-6, 0.998 * wN, 3000)   # в самой точке pi/Td у БП ноль z = -1, фаза не определена
    fig, ax = plt.subplots(2, 1, figsize=(8, 7))
    ax[0].plot(wd, A_an(wd), 'b', linewidth=2, label='аналоговый прототип')
    for m in metody:
        b, a = filt[(m, Td)]
        ax[0].plot(wd, np.abs(freq_d(b, a, Td, wd)), '--', color=cvet[m], linewidth=1.6,
                   label=full[m])
    ax[0].set_title('АЧХ, Td = %.1f мс (до частоты Найквиста %.0f рад/с)' % (Td * 1e3, wN))
    ax[0].set_xlabel('w, рад/с')
    ax[0].set_ylabel('A(w)')
    ax[0].grid(True)
    ax[0].legend()
    wl = np.logspace(1, np.log10(wN), 2000)
    ax[1].semilogx(wl, db(A_an(wl)), 'b', linewidth=2, label='аналоговый прототип')
    for m in metody:
        b, a = filt[(m, Td)]
        ax[1].semilogx(wl, db(freq_d(b, a, Td, wl)), '--', color=cvet[m], linewidth=1.6,
                       label=full[m])
    ax[1].set_title('ЛАЧХ, Td = %.1f мс' % (Td * 1e3))
    ax[1].set_xlabel('w, рад/с')
    ax[1].set_ylabel('L(w), дБ')
    ax[1].set_ylim(-100 if i == 0 else -60, 5)
    ax[1].grid(True, which='both')
    ax[1].legend(loc='lower left')
    save(fig, 'fig%02d_afc_Td%d.png' % (figno, i + 1))
    figno += 1

    fig = plt.figure(figsize=(8, 4))
    plt.plot(wd, np.degrees(phi_an(wd)), 'b', linewidth=2, label='аналоговый прототип')
    for m in metody:
        b, a = filt[(m, Td)]
        plt.plot(wd, np.degrees(np.unwrap(np.angle(freq_d(b, a, Td, wd)))), '--',
                 color=cvet[m], linewidth=1.6, label=full[m])
    plt.title('ФЧХ, Td = %.1f мс' % (Td * 1e3))
    plt.xlabel('w, рад/с')
    plt.ylabel('phi(w), град')
    plt.grid(True)
    plt.legend()
    save(fig, 'fig%02d_pfc_Td%d.png' % (figno, i + 1))
    figno += 1

    # ИПФ: у ИИХ wd(n) = Td*w(n*Td), поэтому сравниваю wd(n)/Td с w(t)
    n_len = int(round(0.015 / Td)) + 1
    fig = plt.figure(figsize=(8, 4))
    plt.plot(t * 1e3, w_an(t), 'b', linewidth=2, label='аналоговый прототип w(t)')
    for m, mk in zip(metody, ('o', 's')):
        b, a = filt[(m, Td)]
        imp = np.zeros(n_len)
        imp[0] = 1
        hd = signal.lfilter(b, a, imp)
        nn = np.arange(n_len)
        ml, sl, bl = plt.stem(nn * Td * 1e3, hd / Td, linefmt='-', markerfmt=mk,
                              basefmt=' ', label='%s: wd(n)/Td' % full[m])
        plt.setp(sl, color=cvet[m], linewidth=0.8)
        plt.setp(ml, color=cvet[m], markersize=4 if i == 0 else 6, mfc='none')
        res['digital']['%s_%g' % (m, Td)]['ipf_first'] = hd[:6].tolist()
    plt.title('ИПФ цифровых фильтров и аналогового прототипа, Td = %.1f мс' % (Td * 1e3))
    plt.xlabel('t = n·Td, мс')
    plt.ylabel('w(t), wd(n)/Td, 1/c')
    plt.xlim(0, 15)
    plt.grid(True)
    plt.legend()
    save(fig, 'fig%02d_ipf_Td%d.png' % (figno, i + 1))
    figno += 1

# числовое сравнение характеристик на контрольных частотах
w_ctrl = np.array([0, 100, 300, 628.3, 1000, 2000, 3000])
print('\n   Сравнение АЧХ и ФЧХ на контрольных частотах:')
table = []
for Td in Tds:
    for m in metody:
        b, a = filt[(m, Td)]
        H = freq_d(b, a, Td, np.maximum(w_ctrl, 1e-9))
        print('   %-26s Td = %.1f мс  A:' % (full[m], Td * 1e3),
              np.round(np.abs(H), 4), ' phi:', np.round(np.degrees(np.unwrap(np.angle(H))), 1))
print('   %-26s               A:' % 'аналоговый', np.round(A_an(w_ctrl), 4), ' phi:',
      np.round(np.degrees(phi_an(w_ctrl)), 1))
ctrl = {'w': w_ctrl.tolist(), 'analog_A': A_an(w_ctrl).tolist(),
        'analog_phi': np.degrees(phi_an(w_ctrl)).tolist()}
for Td in Tds:
    for m in metody:
        b, a = filt[(m, Td)]
        H = freq_d(b, a, Td, np.maximum(w_ctrl, 1e-9))
        ctrl['%s_%g_A' % (m, Td)] = np.abs(H).tolist()
        ctrl['%s_%g_phi' % (m, Td)] = np.degrees(np.unwrap(np.angle(H))).tolist()
res['ctrl'] = ctrl

# ---- сравнение двух интервалов дискретизации для каждого метода ----
wd = np.linspace(1e-6, 0.998 * np.pi / Tds[1], 3000)
fig, ax = plt.subplots(2, 2, figsize=(10, 7))
for j, m in enumerate(metody):
    ax[0, j].plot(wd, A_an(wd), 'b', linewidth=2, label='аналоговый')
    ax[1, j].plot(wd, np.degrees(phi_an(wd)), 'b', linewidth=2, label='аналоговый')
    for Td, ls in zip(Tds, ('--', '-.')):
        b, a = filt[(m, Td)]
        H = freq_d(b, a, Td, wd)
        ax[0, j].plot(wd, np.abs(H), ls, color=cvet[m] if Td == Tds[0] else 'k',
                      linewidth=1.6, label='Td = %.1f мс' % (Td * 1e3))
        ax[1, j].plot(wd, np.degrees(np.unwrap(np.angle(H))), ls,
                      color=cvet[m] if Td == Tds[0] else 'k', linewidth=1.6,
                      label='Td = %.1f мс' % (Td * 1e3))
    ax[0, j].set_title('АЧХ, %s' % full[m])
    ax[1, j].set_title('ФЧХ, %s' % full[m])
    for k in range(2):
        ax[k, j].set_xlabel('w, рад/с')
        ax[k, j].grid(True)
        ax[k, j].legend(fontsize=8)
    ax[0, j].set_ylabel('A(w)')
    ax[1, j].set_ylabel('phi(w), град')
save(fig, 'fig%02d_compare_Td.png' % figno)
figno += 1

# частотное искажение (warping) билинейного преобразования
print('\n   Деформация частоты при БП: w_a = 2/Td*tg(w*Td/2)')
for Td in Tds:
    for wx in (628.3, 2000):
        print('     Td = %.1f мс: цифровой частоте %.0f рад/с соответствует аналоговая %.1f рад/с'
              % (Td * 1e3, wx, 2 / Td * np.tan(wx * Td / 2)))


# ======================= 3. Алгоритм цифровой фильтрации =======================
# разностное уравнение в прямой форме (формула (3) лаб. работы 2):
#   v(n) = sum_q (Aq/B0) u(n-q) - sum_{q>=1} (Bq/B0) v(n-q)
def filtr(b, a, u):
    # прямая реализация алгоритма, как он будет работать в вычислителе
    v = np.zeros(len(u))
    u1 = u2 = v1 = v2 = 0.0     # ячейки памяти (элементы задержки z^-1)
    b = list(b) + [0.0] * (3 - len(b))
    for n in range(len(u)):
        v[n] = b[0] * u[n] + b[1] * u1 + b[2] * u2 - a[1] * v1 - a[2] * v2
        u2, u1 = u1, u[n]
        v2, v1 = v1, v[n]
    return v


# структурная схема прямой формы: слева линия задержек входа,
# справа линия задержек выхода, в середине сумматор
def draw_structure(b, a, title, name):
    b = list(b) + [0.0] * (3 - len(b))
    kmax = max(k for k in range(3) if b[k] != 0)     # сколько задержек по входу нужно
    fig, ax = plt.subplots(figsize=(8.5, 5.2))
    ax.set_xlim(-0.2, 9.6)
    ax.set_ylim(-0.9, 4.9)
    ax.axis('off')
    ys = [4.0, 2.0, 0.0]

    def box(x, y, txt):
        ax.add_patch(plt.Rectangle((x - 0.4, y - 0.3), 0.8, 0.6, fill=False, linewidth=1.3))
        ax.text(x, y, txt, ha='center', va='center', fontsize=11)

    def tri(x, y, txt, left=False):       # усилитель (умножитель на коэффициент)
        s = -1 if left else 1
        ax.add_patch(plt.Polygon([[x - s * 0.3, y + 0.3], [x - s * 0.3, y - 0.3], [x + s * 0.3, y]],
                                 fill=False, linewidth=1.3, closed=True))
        ax.text(x, y + 0.45, txt, ha='center', va='bottom', fontsize=9)

    def line(xs_, ys_):
        ax.plot(xs_, ys_, 'k', linewidth=1.1)

    def arr(x0, y0, x1, y1):
        ax.annotate('', xy=(x1, y1), xytext=(x0, y0),
                    arrowprops=dict(arrowstyle='-|>', linewidth=1.1, color='k'))

    def dot(x, y):
        ax.plot(x, y, 'ko', markersize=4)

    # сумматор
    ax.add_patch(plt.Rectangle((4.5, -0.4), 0.7, 4.8, fill=False, linewidth=1.5))
    ax.text(4.85, 2.0, 'Σ', ha='center', va='center', fontsize=18)
    # вход
    ax.text(-0.15, 4.0, 'u(n)', fontsize=11, va='center')
    line([0.45, 1.3], [4.0, 4.0])
    dot(1.3, 4.0)
    for k in range(kmax + 1):
        y = ys[k]
        if k > 0:
            line([1.3, 1.3], [ys[k - 1], ys[k - 1] - 0.7])
            box(1.3, ys[k - 1] - 1.0, 'z$^{-1}$')
            line([1.3, 1.3], [ys[k - 1] - 1.3, y])
            ax.text(0.15, y, 'u(n-%d)' % k, fontsize=9, va='center')
            if k < kmax:
                dot(1.3, y)
        if b[k] != 0:
            line([1.3, 2.45], [y, y])
            tri(2.75, y, 'b%d = %.6g' % (k, b[k]))
            arr(3.05, y, 4.5, y)
    # выход и обратная связь
    arr(5.2, 4.0, 9.0, 4.0)
    ax.text(9.05, 4.0, 'v(n)', fontsize=11, va='center')
    dot(8.2, 4.0)
    for k in (1, 2):
        y = ys[k]
        line([8.2, 8.2], [ys[k - 1], ys[k - 1] - 0.7])
        box(8.2, ys[k - 1] - 1.0, 'z$^{-1}$')
        line([8.2, 8.2], [ys[k - 1] - 1.3, y])
        ax.text(8.35, y - 0.35, 'v(n-%d)' % k, fontsize=9, va='center')
        if k == 1:
            dot(8.2, y)
        line([8.2, 7.0], [y, y])
        tri(6.7, y, '-a%d = %.6g' % (k, -a[k]), left=True)
        arr(6.4, y, 5.2, y)
    ax.set_title(title, fontsize=11)
    save(fig, name)


Td0 = Tds[0]
for m in metody:
    b, a = filt[(m, Td0)]
    draw_structure(b, a, 'Структурная схема алгоритма (прямая форма), %s, Td = %.1f мс'
                   % (full[m], Td0 * 1e3), 'fig%02d_struct_%s.png' % (figno, 'iih' if m == 'ИИХ' else 'bil'))
    figno += 1


# ======================= 4. Имитационное моделирование =======================
Td = Td0
fd = 1 / Td
T_sim = 0.5
N = int(round(T_sim * fd))
n = np.arange(N)
tt = n * Td
f_test = [20, 100, 400]          # полоса пропускания, переходная зона, задерживание
print('\n4) Имитационное моделирование, Td = %.1f мс, fd = %.0f Гц, длительность %.1f с (N = %d)'
      % (Td * 1e3, fd, T_sim, N))

# проверка своего алгоритма на совпадение с lfilter
u_chk = np.random.default_rng(1).standard_normal(500)
for m in metody:
    b, a = filt[(m, Td)]
    print('   %s: расхождение своего алгоритма и lfilter = %.2e'
          % (full[m], np.max(np.abs(filtr(b, a, u_chk) - signal.lfilter(b, a, u_chk)))))

N_ss = int(round(0.4 * fd))          # установившийся режим - последние 0.4 с
sim = {}
for f0 in f_test:
    u = np.sin(2 * np.pi * f0 * tt)
    for m in metody:
        b, a = filt[(m, Td)]
        v = filtr(b, a, u)
        # амплитуда и фаза "по графику": максимум на установившемся участке
        # и сдвиг между переходами через ноль снизу вверх
        us, vs, ts = u[-N_ss:], v[-N_ss:], tt[-N_ss:]
        Av = (vs.max() - vs.min()) / 2

        def zc(x, tx):           # моменты перехода через 0 снизу вверх (с интерполяцией)
            k = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
            return tx[k] - x[k] * (tx[k + 1] - tx[k]) / (x[k + 1] - x[k])
        tu, tv = zc(us, ts), zc(vs, ts)
        dts = []
        for t0 in tu[:-1]:
            later = tv[tv >= t0 - 1e-12]
            if len(later):
                dts.append(later[0] - t0)
        dt = np.mean(dts)
        dphi = -360 * f0 * dt
        # точное значение по частотной характеристике цифрового фильтра
        H = freq_d(b, a, Td, np.array([2 * np.pi * f0]))[0]
        ph_th = np.degrees(np.angle(H))
        dphi_w = (dphi - ph_th + 180) % 360 - 180 + ph_th     # тот же оборот, что и у теории
        sim[(f0, m)] = dict(u=u, v=v, Av=Av, dt=dt, dphi=dphi_w, A_th=abs(H), ph_th=ph_th,
                            A_an=A_an(2 * np.pi * f0), ph_an=np.degrees(phi_an(2 * np.pi * f0)))
        print('   f = %3d Гц, %-26s: Aвых/Aвх = %.4f (теор. |Wd| = %.4f, аналог %.4f), '
              'dt = %.3f мс, dphi = %.1f град (теор. %.1f, аналог %.1f)'
              % (f0, full[m], Av, abs(H), A_an(2 * np.pi * f0), dt * 1e3, dphi_w, ph_th,
                 np.degrees(phi_an(2 * np.pi * f0))))
res['sim'] = {'%d_%s' % k: {kk: float(vv) for kk, vv in d.items() if not isinstance(vv, np.ndarray)}
              for k, d in sim.items()}
res['sim_param'] = dict(Td=Td, fd=fd, T_sim=T_sim, N=N, f_test=f_test)

# временные диаграммы
for f0 in f_test:
    per = 1 / f0
    t_show = min(T_sim, max(6 * per, 0.03))
    k = tt <= t_show
    fig, ax = plt.subplots(2, 1, figsize=(8, 6))
    ax[0].plot(tt[k] * 1e3, sim[(f0, 'ИИХ')]['u'][k], 'b', linewidth=1.2, label='вход u(n)')
    for m in metody:
        ax[0].plot(tt[k] * 1e3, sim[(f0, m)]['v'][k], color=cvet[m], linewidth=1.2,
                   linestyle='-' if m == 'ИИХ' else '--', label='выход v(n), %s' % full[m])
    ax[0].set_title('Синусоида f = %d Гц: вход и выход фильтров (начало, переходный процесс)' % f0)
    ax[0].set_xlabel('t, мс')
    ax[0].grid(True)
    ax[0].legend(fontsize=8, loc='upper right')
    # установившийся участок - 2 периода в конце
    k2 = tt >= T_sim - 2 * per - Td / 2
    m = 'БП'
    ax[1].plot(tt[k2] * 1e3, sim[(f0, m)]['u'][k2], 'b.-', markersize=3, linewidth=1,
               label='вход u(n)')
    Av = sim[(f0, m)]['Av']
    # если выход маленький - рисую его по отдельной оси справа
    axv = ax[1].twinx() if Av < 0.3 else ax[1]
    axv.plot(tt[k2] * 1e3, sim[(f0, 'ИИХ')]['v'][k2], '.-', color=cvet['ИИХ'], markersize=3,
             linewidth=1, label='выход, метод ИИХ')
    axv.plot(tt[k2] * 1e3, sim[(f0, m)]['v'][k2], '.--', color=cvet[m], markersize=3,
             linewidth=1, label='выход, билинейное преобр.')
    axv.axhline(Av, color=cvet[m], linestyle=':', linewidth=0.8)
    axv.axhline(-Av, color=cvet[m], linestyle=':', linewidth=0.8)
    if axv is not ax[1]:
        axv.set_ylim(-1.1 * Av / 0.9 * 1.0, 1.1 * Av / 0.9)
        axv.set_ylabel('v(n) (правая ось)', color=cvet[m])
        axv.tick_params(axis='y', colors=cvet[m])
        ax[1].set_ylabel('u(n) (левая ось)')
    ax[1].set_title('Установившийся режим (последние 2 периода): Aвых(БП) = %.3f, '
                    'Δt(БП) = %.2f мс' % (Av, sim[(f0, m)]['dt'] * 1e3))
    ax[1].set_xlabel('t, мс')
    ax[1].grid(True)
    h1, l1 = ax[1].get_legend_handles_labels()
    h2, l2 = (axv.get_legend_handles_labels() if axv is not ax[1] else ([], []))
    ax[1].legend(h1 + h2, l1 + l2, fontsize=8, loc='upper right')
    save(fig, 'fig%02d_sin_%dHz.png' % (figno, f0))
    figno += 1


# спектры (односторонний амплитудный спектр по установившемуся участку,
# 0.4 с - целое число периодов для 20, 100 и 400 Гц, поэтому без утечки)
def spectrum(x, fs):
    Nx = len(x)
    X = np.abs(np.fft.rfft(x)) / Nx
    X[1:-1] = 2 * X[1:-1]
    return np.fft.rfftfreq(Nx, 1 / fs), X


fig, ax = plt.subplots(3, 1, figsize=(8, 8.5))
for i, f0 in enumerate(f_test):
    fu, U = spectrum(sim[(f0, 'ИИХ')]['u'][-N_ss:], fd)
    ku = U > 1e-4                   # нулевые бины не рисую
    ax[i].stem(fu[ku], U[ku], linefmt='b-', markerfmt='bo', basefmt=' ', label='|U(f)| вход')
    for m, mk in zip(metody, ('s', 'D')):
        fv, V = spectrum(sim[(f0, m)]['v'][-N_ss:], fd)
        kv = V > 1e-4
        ml, sl, bl = ax[i].stem(fv[kv], V[kv], linefmt='-', markerfmt=mk, basefmt=' ',
                                label='|V(f)| %s' % full[m])
        plt.setp(sl, color=cvet[m])
        plt.setp(ml, color=cvet[m], mfc='none')
    ax[i].set_xlim(0, 600)
    ax[i].axhline(0, color='k', linewidth=0.8)
    ax[i].set_title('Амплитудные спектры, синусоида %d Гц' % f0)
    ax[i].set_xlabel('f, Гц')
    ax[i].grid(True)
    ax[i].legend(fontsize=8)
save(fig, 'fig%02d_sin_spectra.png' % figno)
figno += 1

# белый нормальный шум
rng = np.random.default_rng(19)
Nn = 2 ** 15
un = rng.standard_normal(Nn)
tn = np.arange(Nn) * Td
vn = {m: filtr(*filt[(m, Td)], un) for m in metody}
print('\n   Белый шум: N = %d, СКО входа = %.4f' % (Nn, un.std()))
for m in metody:
    b, a = filt[(m, Td)]
    imp = np.zeros(4000)
    imp[0] = 1
    hd = signal.lfilter(b, a, imp)
    print('   %s: СКО выхода = %.4f, теория sqrt(sum wd^2) = %.4f'
          % (full[m], vn[m][200:].std(), np.sqrt(np.sum(hd ** 2))))
    res['noise_%s' % m] = dict(std_out=float(vn[m][200:].std()),
                               std_th=float(np.sqrt(np.sum(hd ** 2))))
res['noise_std_in'] = float(un.std())

fig, ax = plt.subplots(2, 1, figsize=(8, 6))
k = tn <= 0.05
ax[0].plot(tn[k] * 1e3, un[k], 'b', linewidth=0.8, label='вход: белый шум')
ax[0].set_title('Белый нормальный шум на входе (первые 50 мс)')
ax[0].set_xlabel('t, мс')
ax[0].grid(True)
ax[0].legend(fontsize=8)
for m in metody:
    ax[1].plot(tn[k] * 1e3, vn[m][k], color=cvet[m], linewidth=1.2,
               linestyle='-' if m == 'ИИХ' else '--', label='выход, %s' % full[m])
ax[1].set_title('Выходной сигнал фильтров')
ax[1].set_xlabel('t, мс')
ax[1].grid(True)
ax[1].legend(fontsize=8)
save(fig, 'fig%02d_noise_time.png' % figno)
figno += 1

# спектр шума: один БПФ (шумный) + оценка Уэлча (усреднение по сегментам)
fig, ax = plt.subplots(2, 1, figsize=(8, 7))
fu, U = spectrum(un, fd)
ax[0].plot(fu, db(U), color='lightsteelblue', linewidth=0.5, label='|U(f)| вход')
for m in metody:
    fv, V = spectrum(vn[m], fd)
    ax[0].plot(fv, db(V), color=cvet[m], linewidth=0.5, alpha=0.8, label='|V(f)| %s' % full[m])
ax[0].set_title('Амплитудные спектры шума (одно БПФ, N = %d)' % Nn)
ax[0].set_xlabel('f, Гц')
ax[0].set_ylabel('дБ')
ax[0].set_xlim(0, fd / 2)
ax[0].set_ylim(-140, -10)
ax[0].grid(True)
ax[0].legend(fontsize=8)
fw, Puu = signal.welch(un, fd, nperseg=1024)
fw_l = np.logspace(0, np.log10(fd / 2), 1000)
for m in metody:
    fw, Pvv = signal.welch(vn[m], fd, nperseg=1024)
    ax[1].semilogx(fw[1:], 10 * np.log10(Pvv[1:] / Puu[1:]), color=cvet[m], linewidth=1,
                   label='Pvv/Puu, %s' % full[m])
for m in metody:
    b, a = filt[(m, Td)]
    ax[1].semilogx(fw_l, db(freq_d(b, a, Td, 2 * np.pi * fw_l)), 'k--' if m == 'ИИХ' else 'k:',
                   linewidth=1.2, label='|Wd|^2, %s' % full[m])
ax[1].set_title('Отношение спектральных плотностей выхода и входа (метод Уэлча)')
ax[1].set_xlabel('f, Гц')
ax[1].set_ylabel('дБ')
ax[1].set_ylim(-80, 5)
ax[1].grid(True, which='both')
ax[1].legend(fontsize=8, loc='lower left')
save(fig, 'fig%02d_noise_spectra.png' % figno)
figno += 1


# ======================= 5. Результаты моделирования в SimInTech =======================
# данные сохранены из блока "Временной график" командой "Сохранить в текстовый файл":
# столбцы t, u, t, v_БП, t, v_ИИХ
sit = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'SimInTech')


def zero_cross(x, tx):           # моменты перехода через 0 снизу вверх
    k = np.where((x[:-1] < 0) & (x[1:] >= 0))[0]
    return tx[k] - x[k] * (tx[k + 1] - tx[k]) / (x[k + 1] - x[k])


def load_sit(name):
    d = np.loadtxt(os.path.join(sit, name), encoding='utf-8-sig')
    return d[:, 0], d[:, 1], {'БП': d[:, 3], 'ИИХ': d[:, 5]}


if os.path.isdir(sit):
    print('\n5) Результаты SimInTech (Td = 0.2 мс)')
    res['sit'] = {}
    for f0, name, t_ss in ((20, 'sin_20Hz.txt', 0.4), (100, 'sin_100Hz.txt', 0.03),
                           (400, 'sin_400Hz.txt', 0.01)):
        ts, us, vs = load_sit(name)
        print('   %s: %d отсчётов, t = 0...%.3f c, |u - sin| <= %.1e'
              % (name, len(ts), ts[-1], np.abs(us - np.sin(2 * np.pi * f0 * ts)).max()))
        k = ts >= ts[-1] - t_ss
        for m in metody:
            b, a = filt[(m, Td0)]
            err = np.abs(vs[m] - signal.lfilter(b, a, us)).max()
            Av = (vs[m][k].max() - vs[m][k].min()) / 2
            tu, tv = zero_cross(us[k], ts[k]), zero_cross(vs[m][k], ts[k])
            dts = [tv[tv >= t0][0] - t0 for t0 in tu if np.any(tv >= t0)]
            H = freq_d(b, a, Td0, np.array([2 * np.pi * f0]))[0]
            ph_th = np.degrees(np.angle(H))
            dphi = -360 * f0 * np.mean(dts)
            dphi = (dphi - ph_th + 180) % 360 - 180 + ph_th
            print('     %-26s отличие от Python %.1e; Aвых/Aвх = %.4f (|Wd| = %.4f), '
                  'dt = %.3f мс, dphi = %.1f град (теор. %.1f)'
                  % (full[m], err, Av, abs(H), np.mean(dts) * 1e3, dphi, ph_th))
            res['sit']['%d_%s' % (f0, m)] = dict(err=err, Av=Av, A_th=abs(H), dt=np.mean(dts),
                                                 dphi=dphi, ph_th=ph_th)

    # шум из SimInTech: проверка и спектры
    ts, us, vs = load_sit('noise.txt')
    print('   noise.txt: %d отсчётов, среднее входа %.4f, СКО входа %.4f'
          % (len(ts), us.mean(), us.std()))
    res['sit']['noise'] = dict(N=len(ts), mean_in=us.mean(), std_in=us.std())
    # блок "Запаздывание на период квантования" в SimInTech в момент t = 0 не
    # запоминает входное значение (на шагах n = 0 и n = 1 выдаёт начальное 0),
    # поэтому отсчёт u(0) в цепочку задержек не попадает. Для синуса u(0) = 0 и
    # это незаметно, для шума даёт короткое расхождение в начале
    def filtr_sit(b, a, u):
        v = np.zeros(len(u))
        u1 = u2 = v1 = v2 = 0.0
        b = list(b) + [0.0] * (3 - len(b))
        for n in range(len(u)):
            v[n] = b[0] * u[n] + b[1] * u1 + b[2] * u2 - a[1] * v1 - a[2] * v2
            un, vn = (0.0, 0.0) if n == 0 else (u[n], v[n])
            u2, u1 = u1, un
            v2, v1 = v1, vn
        return v

    for m in metody:
        b, a = filt[(m, Td0)]
        e = np.abs(vs[m] - signal.lfilter(b, a, us))
        err2 = np.abs(vs[m] - filtr_sit(b, a, us)).max()
        print('     %-26s отличие от Python: макс %.1e (только в начале), при t > 20 мс %.1e; '
              'с учётом инициализации задержек %.1e; СКО выхода %.4f'
              % (full[m], e.max(), e[ts > 0.02].max(), err2, vs[m][100:].std()))
        res['sit']['noise'][m] = dict(err=e.max(), err_after=e[ts > 0.02].max(), err_init=err2,
                                      std_out=vs[m][100:].std())

    fig, ax = plt.subplots(2, 1, figsize=(8, 7))
    fu, U = spectrum(us, fd)
    ax[0].plot(fu, db(U), color='lightsteelblue', linewidth=0.5, label='|U(f)| вход')
    for m in metody:
        fv, V = spectrum(vs[m], fd)
        ax[0].plot(fv, db(V), color=cvet[m], linewidth=0.5, alpha=0.8,
                   label='|V(f)| %s' % full[m])
    ax[0].set_title('Амплитудные спектры сигналов SimInTech (шум, N = %d)' % len(ts))
    ax[0].set_xlabel('f, Гц')
    ax[0].set_ylabel('дБ')
    ax[0].set_xlim(0, fd / 2)
    ax[0].set_ylim(-140, -10)
    ax[0].grid(True)
    ax[0].legend(fontsize=8)
    fw, Puu = signal.welch(us, fd, nperseg=512)
    for m in metody:
        fw, Pvv = signal.welch(vs[m], fd, nperseg=512)
        ax[1].semilogx(fw[1:], 10 * np.log10(Pvv[1:] / Puu[1:]), color=cvet[m], linewidth=1,
                       label='Pvv/Puu, %s' % full[m])
    for m in metody:
        b, a = filt[(m, Td0)]
        ax[1].semilogx(fw_l, db(freq_d(b, a, Td0, 2 * np.pi * fw_l)),
                       'k--' if m == 'ИИХ' else 'k:', linewidth=1.2, label='|Wd|^2, %s' % full[m])
    ax[1].set_title('Отношение спектральных плотностей выхода и входа (данные SimInTech)')
    ax[1].set_xlabel('f, Гц')
    ax[1].set_ylabel('дБ')
    ax[1].set_ylim(-80, 5)
    ax[1].grid(True, which='both')
    ax[1].legend(fontsize=8, loc='lower left')
    save(fig, 'fig%02d_sit_noise_spectra.png' % figno)
    figno += 1

    # спектры синусоид из SimInTech (по установившемуся участку)
    fig, ax = plt.subplots(3, 1, figsize=(8, 8.5))
    for i, (f0, name, t_ss) in enumerate(((20, 'sin_20Hz.txt', 0.4), (100, 'sin_100Hz.txt', 0.03),
                                          (400, 'sin_400Hz.txt', 0.01))):
        ts, us, vs = load_sit(name)
        n_ss = int(round(t_ss / Td0))
        fu, U = spectrum(us[-n_ss:], fd)
        ku = U > 1e-3
        ax[i].stem(fu[ku], U[ku], linefmt='b-', markerfmt='bo', basefmt=' ', label='|U(f)| вход')
        for m, mk in zip(metody, ('s', 'D')):
            fv, V = spectrum(vs[m][-n_ss:], fd)
            kv = V > 1e-3
            ml, sl, bl = ax[i].stem(fv[kv], V[kv], linefmt='-', markerfmt=mk, basefmt=' ',
                                    label='|V(f)| %s' % full[m])
            plt.setp(sl, color=cvet[m])
            plt.setp(ml, color=cvet[m], mfc='none')
        ax[i].axhline(0, color='k', linewidth=0.8)
        ax[i].set_xlim(0, 600)
        ax[i].set_title('Спектры сигналов SimInTech, синусоида %d Гц (участок %.2f с)' % (f0, t_ss))
        ax[i].set_xlabel('f, Гц')
        ax[i].grid(True)
        ax[i].legend(fontsize=8)
    save(fig, 'fig%02d_sit_sin_spectra.png' % figno)
    figno += 1


# сохраняю числа для отчёта
def conv(o):
    if isinstance(o, (np.floating, np.integer)):
        return o.item()
    if isinstance(o, np.ndarray):
        return o.tolist()
    raise TypeError(type(o))


with open(os.path.join(os.path.dirname(os.path.abspath(__file__)), 'results.json'), 'w',
          encoding='utf8') as fjs:
    json.dump(res, fjs, ensure_ascii=False, indent=1, default=conv)
print('\nГрафики сохранены в папку', papka)
