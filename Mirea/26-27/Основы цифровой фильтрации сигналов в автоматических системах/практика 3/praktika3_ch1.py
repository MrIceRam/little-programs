# Практическая работа 3, часть 1. БПФ и оконные преобразования
# Оськин В.А., КВБО-11-24, вариант 19
# Вариант 19: синусоида + окно Гаусса, сравнение sigma
# fs = 4000 Гц, f0 = 500 Гц, N = 512, A = 1.0, sigma = 0.1, 0.2, 0.4
# (в методичке код на Octave, здесь то же самое на Python: numpy + scipy)

import os
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq
from scipy.signal import stft

fs = 4000
f0 = 500
N = 512
A = 1.0
sigmas = (0.1, 0.2, 0.4)
colors = {0.1: 'tab:blue', 0.2: 'tab:green', 0.4: 'tab:red'}
print('Вариант 19: fs = %d Гц, f0 = %d Гц, N = %d, A = %.1f' % (fs, f0, N, A))

papka = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'скриншоты')
os.makedirs(papka, exist_ok=True)


def save(fig, name):
    fig.tight_layout()
    fig.savefig(os.path.join(papka, name), dpi=130)


# окно Гаусса из сводки окон в методичке:
# w[n] = exp(-1/2 * ((n - (N-1)/2) / (sigma*(N-1)/2))^2)
def gauss_win(N, sigma):
    n = np.arange(N)
    return np.exp(-0.5 * ((n - (N - 1) / 2) / (sigma * (N - 1) / 2)) ** 2)


# односторонний амплитудный спектр, нормировка на сумму окна
# (для прямоугольного окна sum(w) = N, как в методичке)
def spectrum(x, w, fs):
    N = len(x)
    X = np.abs(np.fft.fft(x * w)) / np.sum(w)
    X = X[:N // 2 + 1]
    X[1:-1] = 2 * X[1:-1]
    f = np.arange(N // 2 + 1) * fs / N
    return f, X


def db(x):
    return 20 * np.log10(np.abs(x) + 1e-300)


# ================ 1. Тестовый сигнал ================
n = np.arange(N)
t = n / fs
x = A * np.sin(2 * np.pi * f0 * n / fs)

print('\n1) Тестовый сигнал x[n] = A*sin(2*pi*f0*n/fs)')
print('   длительность записи T = N/fs = %.4f c' % (N / fs))
print('   отсчётов на период fs/f0 = %.1f' % (fs / f0))
print('   первые 9 отсчётов:', np.round(x[:9], 4))

fig = plt.figure(figsize=(8, 4))
fig.canvas.manager.set_window_title('Тестовый сигнал')
plt.plot(t * 1000, x, 'b-', linewidth=0.8)
plt.plot(t[:40] * 1000, x[:40], 'ro', markersize=3)
plt.xlim(0, 10)
plt.title('Тестовый сигнал x[n], f0 = %d Гц, fs = %d Гц (первые 10 мс)' % (f0, fs))
plt.xlabel('t, мс')
plt.ylabel('x[n]')
plt.grid(True)
save(fig, 'ch1_fig1_signal.png')


# ================ 2-3. БПФ и проверка когерентности ================
df = fs / N
k0 = f0 * N / fs
print('\n2-3) Проверка когерентности:')
print('   f0*N/fs = %d*%d/%d = %.4f' % (f0, N, fs, k0))
print('   целое число -> когерентная выборка:', k0 == int(k0))
print('   разрешение по частоте df = fs/N = %.4f Гц' % df)
print('   пик должен быть в бине k = %d, f = %.2f Гц' % (k0, k0 * df))

w_rect = np.ones(N)
f, X_rect = spectrum(x, w_rect, fs)
k_max = np.argmax(X_rect)
X_other = np.delete(X_rect, k_max)
print('   БПФ (прямоугольное окно): макс. в бине %d, f = %.2f Гц, |X| = %.6f'
      % (k_max, f[k_max], X_rect[k_max]))
print('   наибольший уровень в остальных бинах: %.1f дБ' % db(X_other.max()))


fig, ax = plt.subplots(2, 1, figsize=(8, 6))
fig.canvas.manager.set_window_title('Спектр, прямоугольное окно')
ax[0].stem(f, X_rect, basefmt='k-', markerfmt='b.')
ax[0].set_title('Амплитудный спектр, прямоугольное окно (линейный масштаб)')
ax[0].set_xlabel('f, Гц')
ax[0].set_ylabel('|X(f)|')
ax[0].set_xlim(0, fs / 2)
ax[0].grid(True)
ax[1].plot(f, db(X_rect), 'r.-', markersize=3, linewidth=0.7)
ax[1].set_title('Тот же спектр в дБ')
ax[1].set_xlabel('f, Гц')
ax[1].set_ylabel('|X(f)|, дБ')
ax[1].set_xlim(0, fs / 2)
ax[1].set_ylim(-340, 20)
ax[1].grid(True)
save(fig, 'ch1_fig2_fft_rect.png')


# ================ 6. Окно Гаусса, sigma = 0.1, 0.2, 0.4 ================
# частотная характеристика окна с дополнением нулями (в 64 раза),
# чтобы увидеть форму главного и боковых лепестков
P = 64


def window_props(w):
    M = P * len(w)
    W = np.abs(np.fft.fft(w, M))
    W = W / W[0]
    h = db(W[:M // 2])
    bins = np.arange(M // 2) / P              # смещение в бинах БПФ
    bw3 = 2 * bins[np.argmax(h < -3)]          # ширина ГЛ по -3 дБ
    bw6 = 2 * bins[np.argmax(h < -6)]
    i_min = None                               # первый минимум = край ГЛ
    for i in range(1, len(h) - 1):
        if h[i] < h[i - 1] and h[i] <= h[i + 1]:
            i_min = i
            break
    if i_min is not None and h[i_min:].max() > -280:
        gl = 2 * bins[i_min]                   # ширина ГЛ между нулями
        psl = h[i_min:].max()                  # уровень наибольшего БЛ
    else:
        gl, psl = np.nan, np.nan               # БЛ ниже точности double
    cg = np.sum(w) / len(w)                    # когерентное усиление
    enbw = len(w) * np.sum(w ** 2) / np.sum(w) ** 2
    nn = np.arange(len(w))
    scal = db(np.abs(np.sum(w * np.exp(-1j * np.pi * nn / len(w)))) / np.sum(w))
    return dict(bw3=bw3, bw6=bw6, gl=gl, psl=psl, cg=cg, enbw=enbw,
                scal=scal, edge=w[0], bins=bins, h=h)


print('\n6) Окно Гаусса, характеристики (ширины в бинах, 1 бин = %.4f Гц):' % df)
print('   sigma  край w[0]   CG      ENBW   -3дБ   -6дБ   ГЛ(нули)  БЛ,дБ   '
      'потери м/у бинами')
wp = {}
for s in sigmas:
    wp[s] = window_props(gauss_win(N, s))
    p = wp[s]
    gl = '   ---  ' if np.isnan(p['gl']) else '%7.2f ' % p['gl']
    psl = '  <-300' if np.isnan(p['psl']) else '%7.1f' % p['psl']
    print('   %.1f   %9.2e  %.4f  %5.3f  %5.2f  %5.2f   %s  %s   %6.2f дБ'
          % (s, p['edge'], p['cg'], p['enbw'], p['bw3'], p['bw6'], gl, psl,
             p['scal']))
pr = window_props(w_rect)
print('   rect   %9.2e  %.4f  %5.3f  %5.2f  %5.2f   %7.2f  %7.1f   %6.2f дБ'
      % (pr['edge'], pr['cg'], pr['enbw'], pr['bw3'], pr['bw6'], pr['gl'],
         pr['psl'], pr['scal']))

# спектры сигнала с окнами Гаусса (обычное БПФ, N = 512)
X_g = {}
for s in sigmas:
    f, X_g[s] = spectrum(x, gauss_win(N, s), fs)
print('\n   Спектр сигнала (БПФ N = 512) с нормировкой на sum(w):')
for s in sigmas:
    k = np.argmax(X_g[s])
    print('   sigma = %.1f: пик %.2f Гц, |X| = %.6f; бины k0+-1: %.1f дБ, '
          'k0+-3: %.1f дБ, k0+-10: %.1f дБ'
          % (s, f[k], X_g[s][k], db(X_g[s][k + 1]), db(X_g[s][k + 3]),
             db(X_g[s][k + 10])))
    # без нормировки на sum(w) (делим на N) амплитуда занижается в CG раз
    X_bad = 2 * np.abs(np.fft.fft(x * gauss_win(N, s))) / N
    print('      если делить на N, а не на sum(w): |X| = %.4f (= CG)'
          % X_bad.max())

fig, ax = plt.subplots(2, 1, figsize=(8, 6))
fig.canvas.manager.set_window_title('Окна Гаусса')
for s in sigmas:
    ax[0].plot(n, gauss_win(N, s), color=colors[s], label='sigma = %.1f' % s)
ax[0].plot(n, w_rect, 'k--', linewidth=0.8, label='прямоугольное')
ax[0].set_title('Окна Гаусса во временной области, N = %d' % N)
ax[0].set_xlabel('n')
ax[0].set_ylabel('w[n]')
ax[0].grid(True)
ax[0].legend(loc='upper right', fontsize=8)
for s in sigmas:
    ax[1].plot(n, x * gauss_win(N, s), color=colors[s], linewidth=0.6,
               label='sigma = %.1f' % s)
ax[1].set_title('Сигнал после умножения на окно x[n]·w[n]')
ax[1].set_xlabel('n')
ax[1].set_ylabel('x[n]·w[n]')
ax[1].grid(True)
ax[1].legend(loc='upper right', fontsize=8)
save(fig, 'ch1_fig3_windows.png')

# три спектра на одном графике (главное требование варианта)
fig, ax = plt.subplots(2, 1, figsize=(8, 7))
fig.canvas.manager.set_window_title('Три спектра, окно Гаусса')
for s in sigmas:
    ax[0].plot(f, db(X_g[s]), '.-', color=colors[s], markersize=3,
               linewidth=0.8, label='sigma = %.1f' % s)
ax[0].plot(f, db(X_rect), 'k.', markersize=3, label='прямоугольное')
ax[0].set_title('Спектр сигнала с окном Гаусса (БПФ, N = 512), весь диапазон')
ax[0].set_xlabel('f, Гц')
ax[0].set_ylabel('|X(f)|, дБ')
ax[0].set_xlim(0, fs / 2)
ax[0].set_ylim(-340, 20)
ax[0].grid(True)
ax[0].legend(fontsize=8)
for s in sigmas:
    ax[1].plot(f, db(X_g[s]), 'o-', color=colors[s], markersize=4,
               linewidth=1, label='sigma = %.1f' % s)
ax[1].plot(f, db(X_rect), 'ks', markersize=4, label='прямоугольное')
ax[1].set_title('То же, область 500 Гц (точки - бины БПФ через 7.8125 Гц)')
ax[1].set_xlabel('f, Гц')
ax[1].set_ylabel('|X(f)|, дБ')
ax[1].set_xlim(350, 650)
ax[1].set_ylim(-200, 10)
ax[1].grid(True)
ax[1].legend(fontsize=8)
save(fig, 'ch1_fig4_three_spectra.png')

# форма спектра окна (дополнение нулями) - ширина ГЛ и уровень БЛ
fig = plt.figure(figsize=(8, 4.5))
fig.canvas.manager.set_window_title('Спектр окна Гаусса')
for s in sigmas:
    b, h = wp[s]['bins'], wp[s]['h']
    m = b <= 60
    plt.plot(b[m], h[m], color=colors[s], label='sigma = %.1f' % s)
m = pr['bins'] <= 60
plt.plot(pr['bins'][m], pr['h'][m], 'k', linewidth=0.5, label='прямоугольное')
plt.title('Частотная характеристика окон (дополнение нулями в %d раз)' % P)
plt.xlabel('смещение от f0, бины БПФ')
plt.ylabel('|W|, дБ')
plt.ylim(-320, 5)
plt.xlim(0, 60)
plt.grid(True)
plt.legend()
save(fig, 'ch1_fig5_window_response.png')


# ================ Сравнение с окном Кайзера ================
# при больших beta: I0(beta*sqrt(1-u^2))/I0(beta) ~ exp(-beta*u^2/2),
# то есть окно Кайзера близко к гауссову с sigma = 1/sqrt(beta)
# эквивалентное окно Кайзера подбираю так, чтобы совпала ENBW (ширина ГЛ)
def enbw_of(w):
    return len(w) * np.sum(w ** 2) / np.sum(w) ** 2


print('\n   Сравнение с окном Кайзера при той же ENBW (той же ширине ГЛ):')
print('   sigma  beta=1/s^2  beta(ENBW)  Кайзер: -3дБ  ГЛ(нули)  БЛ,дБ  |'
      '  Гаусс: -3дБ  ГЛ(нули)  БЛ,дБ')
kp, betas = {}, {}
for s in sigmas:
    target = wp[s]['enbw']
    beta = brentq(lambda bb: enbw_of(np.kaiser(N, bb)) - target, 0.5, 300)
    betas[s] = beta
    kp[s] = window_props(np.kaiser(N, beta))
    g, k = wp[s], kp[s]

    def fmt(v, form):
        return '  ---  ' if np.isnan(v) else form % v
    print('   %.1f   %8.1f   %9.2f     %5.2f     %s  %s  |     %5.2f     %s  %s'
          % (s, 1 / s ** 2, beta, k['bw3'], fmt(k['gl'], '%7.2f'),
             fmt(k['psl'], '%7.1f'), g['bw3'], fmt(g['gl'], '%7.2f'),
             fmt(g['psl'], '%7.1f')))

fig, ax = plt.subplots(3, 1, figsize=(8, 9))
fig.canvas.manager.set_window_title('Гаусс и Кайзер')
for i, s in enumerate(sigmas):
    b = wp[s]['bins']
    m = b <= 60
    ax[i].plot(b[m], wp[s]['h'][m], color=colors[s],
               label='Гаусс, sigma = %.1f' % s)
    ax[i].plot(b[m], kp[s]['h'][m], 'k--',
               label='Кайзер, beta = %.1f' % betas[s])
    ax[i].set_ylim(-320, 5)
    ax[i].set_xlim(0, 60)
    ax[i].set_ylabel('|W|, дБ')
    ax[i].grid(True)
    ax[i].legend(loc='upper right', fontsize=8)
ax[0].set_title('Окно Гаусса и окно Кайзера с той же ENBW')
ax[2].set_xlabel('смещение от f0, бины БПФ')
save(fig, 'ch1_fig6_gauss_kaiser.png')


# ================ 7. Свои преобразования: некогерентный случай ================
# при когерентной выборке прямоугольное окно уже идеально (утечки нет),
# окно Гаусса здесь только расширяет пик. Пользу окна видно, когда
# f0 попадает между бинами: беру f0 = 503.90625 Гц = 64.5 бина
f1 = (k0 + 0.5) * df
x1 = A * np.sin(2 * np.pi * f1 * n / fs)
print('\n7) Некогерентный случай f0 = %.5f Гц, f0*N/fs = %.1f' % (f1, f1 * N / fs))
f, X1r = spectrum(x1, w_rect, fs)
X1g = {}
print('   окно          пик |X|   ошибка ампл.   уровень на 1000 Гц')
print('   прямоуг.     %.4f    %6.2f дБ      %7.1f дБ'
      % (X1r.max(), db(X1r.max()), db(X1r[np.argmin(abs(f - 1000))])))
for s in sigmas:
    f, X1g[s] = spectrum(x1, gauss_win(N, s), fs)
    print('   Гаусс %.1f    %.4f    %6.2f дБ      %7.1f дБ'
          % (s, X1g[s].max(), db(X1g[s].max()),
             db(X1g[s][np.argmin(abs(f - 1000))])))

fig = plt.figure(figsize=(8, 4.5))
fig.canvas.manager.set_window_title('Некогерентный случай')
plt.plot(f, db(X1r), 'k', linewidth=0.8, label='прямоугольное')
for s in sigmas:
    plt.plot(f, db(X1g[s]), color=colors[s], linewidth=0.9,
             label='Гаусс, sigma = %.1f' % s)
plt.title('Некогерентный сигнал f0 = %.3f Гц (64.5 бина)' % f1)
plt.xlabel('f, Гц')
plt.ylabel('|X(f)|, дБ')
plt.xlim(0, fs / 2)
plt.ylim(-200, 5)
plt.grid(True)
plt.legend(fontsize=8)
save(fig, 'ch1_fig7_noncoherent.png')


# ================ Шум в спектре (контрольный вопрос 4) ================
rng = np.random.default_rng(19)
sn = 0.01
xn = x1 + sn * rng.standard_normal(N)
f, Xn = spectrum(xn, gauss_win(N, 0.2), fs)
w2 = gauss_win(N, 0.2)
# теоретический уровень белого шума в одностороннем спектре
floor = 2 * sn * np.sqrt(np.sum(w2 ** 2)) / np.sum(w2)
lo = (f > 50) & (f < 400)
hi = (f > 1500) & (f < 1950)
# усредняю мощность шума по 200 реализациям
Pn = np.zeros(len(f))
for i in range(200):
    _, Xi = spectrum(sn * rng.standard_normal(N), w2, fs)
    Pn = Pn + Xi ** 2 / 200
print('\n   Белый шум sigma_n = %.2f, окно Гаусса 0.2, среднее по 200 реализациям:'
      % sn)
print('   средний уровень шума 50-400 Гц: %.1f дБ, 1500-1950 Гц: %.1f дБ'
      % (db(np.sqrt(np.mean(Pn[lo]))), db(np.sqrt(np.mean(Pn[hi])))))
print('   теоретический уровень 2*sn*sqrt(sum w^2)/sum w = %.1f дБ' % db(floor))

fig = plt.figure(figsize=(8, 4))
fig.canvas.manager.set_window_title('Шум')
plt.plot(f, db(Xn), 'g', linewidth=0.8, label='сигнал + белый шум')
plt.plot(f, db(np.sqrt(Pn)), 'm', linewidth=1, label='шум, среднее по 200 реализациям')
plt.axhline(db(floor), color='k', linestyle='--', label='теоретический уровень шума')
plt.title('Спектр сигнала с белым шумом (sigma_n = %.2f), окно Гаусса 0.2' % sn)
plt.xlabel('f, Гц')
plt.ylabel('|X(f)|, дБ')
plt.xlim(0, fs / 2)
plt.ylim(-100, 5)
plt.grid(True)
plt.legend(fontsize=8)
save(fig, 'ch1_fig8_noise.png')


# ================ Спектрограмма с окнами Гаусса ================
# тестовый сигнал 1 с: 500 Гц, с t = 0.5 с частота 560 Гц,
# плюс короткая вспышка 1200 Гц длительностью 10 мс при t = 0.25 с
T2 = 1.0
t2 = np.arange(int(T2 * fs)) / fs
xs = np.where(t2 < 0.5, np.sin(2 * np.pi * 500 * t2), np.sin(2 * np.pi * 560 * t2))
burst = (t2 >= 0.25) & (t2 < 0.26)
xs = xs + burst * np.sin(2 * np.pi * 1200 * t2)

print('\n   Спектрограмма (окно %d отсчётов = %.0f мс, шаг 16 отсчётов):'
      % (N, N / fs * 1000))
print('   sigma  эфф.длит. sigma_t, мс  эфф.полоса sigma_f, Гц  sigma_t*sigma_f'
      '  (предел Габора 1/(4pi) = %.4f)' % (1 / (4 * np.pi)))
fig, ax = plt.subplots(3, 1, figsize=(8, 9))
fig.canvas.manager.set_window_title('Спектрограммы')
for i, s in enumerate(sigmas):
    w = gauss_win(N, s)
    # эффективная (среднеквадратичная) длительность и полоса окна
    tc = (n - (N - 1) / 2) / fs
    st = np.sqrt(np.sum(tc ** 2 * w ** 2) / np.sum(w ** 2))
    M = P * N
    Wf = np.abs(np.fft.fft(w, M)) ** 2
    ff = np.fft.fftfreq(M, 1 / fs)
    sf = np.sqrt(np.sum(ff ** 2 * Wf) / np.sum(Wf))
    print('   %.1f        %6.2f                %6.2f             %.4f'
          % (s, st * 1000, sf, st * sf))
    fS, tS, Z = stft(xs, fs, window=w, nperseg=N, noverlap=N - 16,
                     boundary=None, padded=False)
    S = db(np.abs(Z) / np.abs(Z).max())
    im = ax[i].pcolormesh(tS, fS, S, vmin=-120, vmax=0, shading='auto',
                          cmap='jet')
    ax[i].set_ylim(300, 1400)
    ax[i].set_ylabel('f, Гц')
    ax[i].set_title('Спектрограмма, окно Гаусса sigma = %.1f' % s)
    fig.colorbar(im, ax=ax[i], label='дБ')
ax[2].set_xlabel('t, c')
save(fig, 'ch1_fig9_spectrogram.png')

plt.show()
