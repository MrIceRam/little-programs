# Вариант 19
import os
import numpy as np
import matplotlib.pyplot as plt
from scipy import signal, optimize
from scipy.special import comb

n = 3
wc = 2200.0 # рад/с
fs = 15000.0 # Гц (нужна для ч.2, тут только проверка)

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "графики")
os.makedirs(OUT, exist_ok=True)

def tf_str(b, a):
    return f"num = {np.array2string(np.asarray(b), precision=6)}\nden = {np.array2string(np.asarray(a), precision=6)}"

def mag(b, a, w):
    _, h = signal.freqs(b, a, worN=w)
    return np.abs(h)

def cutoff(b, a, lo, hi):
    # частота, где |H| = 1/sqrt(2) (-3 дБ)
    return optimize.brentq(lambda x: mag(b, a, [x])[0] - 1 / np.sqrt(2), lo, hi)

#  1. прототип ФНЧ, wc = 1 рад/с 
# биномиальный: (s+1)^n, коэффициенты = C(n,k)
b0 = [1.0]
a0 = np.array([comb(n, k) for k in range(n + 1)])
print("1) прототип H0(s) = 1/(s+1)^3")
print(tf_str(b0, a0))
print("полюсы:", np.roots(a0))

#  2. масштабирование s -> s/wc 
# вручную: a_k * wc^k
a_lp_hand = a0 * wc ** np.arange(n + 1)
b_lp_hand = [wc ** n]
# встроенным методом
b_lp, a_lp = signal.lp2lp(b0, a0, wo=wc)
print("\n2) ФНЧ wc = 2200")
print("вручную:\n" + tf_str(b_lp_hand, a_lp_hand))
print("lp2lp:\n" + tf_str(b_lp, a_lp))
print("совпадает:", np.allclose(a_lp, a_lp_hand) and np.allclose(b_lp, b_lp_hand))
print("полюсы:", np.roots(a_lp))

# 3 АЧХ
w = np.logspace(1, 6, 20000)
H_lp = mag(b_lp, a_lp, w)
H_lp_db = 20 * np.log10(H_lp)

w3_lp = cutoff(b_lp, a_lp, 1, wc)
w3_lp_formula = wc * np.sqrt(2 ** (1 / n) - 1)
H_at_wc_db = 20 * np.log10(mag(b_lp, a_lp, [wc])[0])
print("\n3) АЧХ ФНЧ")
print(f"w(-3дБ) численно  = {w3_lp:.2f} рад/с")
print(f"w(-3дБ) формулой  = {w3_lp_formula:.2f} рад/с  (wc*sqrt(2^(1/n)-1))")
print(f"|H(j*wc)| = {H_at_wc_db:.2f} дБ")

def db_at(b, a, x):
    return 20 * np.log10(mag(b, a, [x])[0])

slope_far = db_at(b_lp, a_lp, 100 * wc) - db_at(b_lp, a_lp, 10 * wc)
slope_oct = db_at(b_lp, a_lp, 200 * wc) - db_at(b_lp, a_lp, 100 * wc)
slope_near = db_at(b_lp, a_lp, 10 * w3_lp) - db_at(b_lp, a_lp, w3_lp)
print(f"крутизна (10wc..100wc) = {slope_far:.2f} дБ/дек, {slope_oct:.2f} дБ/окт")
print(f"крутизна (w3..10*w3)   = {slope_near:.2f} дБ/дек")

pb = w <= w3_lp
monot = np.all(np.diff(H_lp) <= 1e-12)
nerav = H_lp_db[pb].max() - H_lp_db[pb].min()
print(f"АЧХ монотонная: {monot}, макс. = {H_lp_db.max():.4f} дБ (перерегулирования нет)")
print(f"неравномерность в полосе 0..w3: {nerav:.2f} дБ")

#  4. инверсия ФНЧ -> ФВЧ, s -> wc/s 
# вручную: 1/((wc/s)+1)^3 = s^3/(s+wc)^3
b_hp_hand = np.r_[1.0, np.zeros(n)]
a_hp_hand = a0[::-1] * wc ** np.arange(n + 1)   # полином симметричный
b_hp, a_hp = signal.lp2hp(b0, a0, wo=wc)
print("\n4) ФВЧ, s -> wc/s")
print("вручную:\n" + tf_str(b_hp_hand, a_hp_hand))
print("lp2hp:\n" + tf_str(b_hp, a_hp))
print("совпадает:", np.allclose(a_hp, a_hp_hand) and np.allclose(b_hp, b_hp_hand))
print("нули:", np.roots(b_hp), " полюсы:", np.roots(a_hp))

H_hp = mag(b_hp, a_hp, w)
H_hp_db = 20 * np.log10(H_hp)
w3_hp = cutoff(b_hp, a_hp, wc, 100 * wc)
print(f"w(-3дБ) ФВЧ = {w3_hp:.2f} рад/с  (wc/sqrt(2^(1/n)-1) = {wc / np.sqrt(2 ** (1 / n) - 1):.2f})")
slope_hp = db_at(b_hp, a_hp, wc / 10) - db_at(b_hp, a_hp, wc / 100)
print(f"крутизна ФВЧ (wc/100..wc/10) = {slope_hp:.2f} дБ/дек")
print(f"w*w = w3_lp*w3_hp = {w3_lp * w3_hp:.1f},  wc^2 = {wc ** 2:.1f}")

#  уточнение: -3 дБ ровно на 2200 рад/с 
k = np.sqrt(2 ** (1 / n) - 1)
b_lp2, a_lp2 = signal.lp2lp(b0, a0, wo=wc / k)
b_hp2, a_hp2 = signal.lp2hp(b0, a0, wo=wc * k)
print(f"\nуточнение: k = sqrt(2^(1/3)-1) = {k:.4f}")
print("ФНЧ (-3дБ на 2200):\n" + tf_str(b_lp2, a_lp2), " w3 =", round(cutoff(b_lp2, a_lp2, 1, 10 * wc), 2))
print("ФВЧ (-3дБ на 2200):\n" + tf_str(b_hp2, a_hp2), " w3 =", round(cutoff(b_hp2, a_hp2, 10, 10 * wc), 2))

print(f"\nпроверка fs: fs/2 = {fs / 2:.0f} Гц = {np.pi * fs:.0f} рад/с, wc = {wc / 2 / np.pi:.1f} Гц -> fs подходит")

#  графики 
plt.rcParams.update({"font.size": 10})

# рис 1 прототип
wn = np.logspace(-2, 2, 4000)
H0 = mag(b0, a0, wn)
w3_0 = np.sqrt(2 ** (1 / n) - 1)
plt.figure(figsize=(7, 4))
plt.semilogx(wn, H0)
plt.axhline(1 / np.sqrt(2), ls="--", c="gray", lw=0.8)
plt.axvline(1, ls=":", c="r", lw=0.8)
plt.plot(w3_0, 1 / np.sqrt(2), "ro")
plt.text(w3_0 * 1.1, 0.74, f"0.707 при ω={w3_0:.3f}")
plt.title("АЧХ прототипа ФНЧ 1/(s+1)³")
plt.xlabel("ω, рад/с"); plt.ylabel("|H|")
plt.grid(True, which="both", alpha=0.4)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "1_prototype.png"), dpi=150)

# рис 2 ФНЧ 2200
plt.figure(figsize=(7, 4))
plt.semilogx(w, H_lp_db, label="ФНЧ, ωc=2200")
plt.semilogx(w, 20 * np.log10(mag(b_lp2, a_lp2, w)), "--", lw=0.9, label="уточн. (-3 дБ на 2200)")
wa = w[w > wc]
plt.semilogx(wa, -60 * np.log10(wa / wc), ":", c="k", lw=0.8, label="асимптота -60 дБ/дек")
plt.axhline(-3, ls="--", c="gray", lw=0.8)
plt.axvline(wc, ls=":", c="r", lw=0.8)
plt.plot(w3_lp, -3, "ro")
plt.text(w3_lp * 0.25, -12, f"-3 дБ: {w3_lp:.0f} рад/с")
plt.ylim(-120, 5)
plt.title("АЧХ ФНЧ после масштабирования")
plt.xlabel("ω, рад/с"); plt.ylabel("|H|, дБ")
plt.grid(True, which="both", alpha=0.4); plt.legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "2_lpf.png"), dpi=150)

# рис 3 ФВЧ
plt.figure(figsize=(7, 4))
plt.semilogx(w, H_hp_db, label="ФВЧ, s→ωc/s")
plt.semilogx(w, 20 * np.log10(mag(b_hp2, a_hp2, w)), "--", lw=0.9, label="уточн. (-3 дБ на 2200)")
plt.semilogx(w, H_lp_db, c="gray", lw=0.7, alpha=0.6, label="ФНЧ (для сравнения)")
plt.axhline(-3, ls="--", c="gray", lw=0.8)
plt.axvline(wc, ls=":", c="r", lw=0.8)
plt.plot(w3_hp, -3, "ro")
plt.text(w3_hp * 1.3, -12, f"-3 дБ: {w3_hp:.0f} рад/с")
plt.ylim(-120, 5)
plt.title("АЧХ ФВЧ (инверсия ФНЧ)")
plt.xlabel("ω, рад/с"); plt.ylabel("|H|, дБ")
plt.grid(True, which="both", alpha=0.4); plt.legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "3_hpf.png"), dpi=150)

# рис 4 нули/полюсы
fig, ax = plt.subplots(1, 2, figsize=(8, 3.5))
for a_, (b, a, t) in zip(ax, [(b_lp, a_lp, "ФНЧ"), (b_hp, a_hp, "ФВЧ")]):
    p = np.roots(a)
    a_.plot(p.real, p.imag, "x", ms=10, mew=2, label="полюсы (×3)")
    if len(b) > 1:
        z = np.roots(b)
        a_.plot(z.real, z.imag, "o", mfc="none", ms=10, mew=2, label="нули (×3)")
    a_.axhline(0, c="k", lw=0.5); a_.axvline(0, c="k", lw=0.5)
    a_.set_xlim(-3000, 500); a_.set_ylim(-1500, 1500)
    a_.set_xticks([-3000, -2000, -1000, 0])
    a_.set_title(t); a_.set_xlabel("Re"); a_.set_ylabel("Im")
    a_.grid(alpha=0.4); a_.legend(fontsize=8)
plt.tight_layout(); plt.savefig(os.path.join(OUT, "4_pz.png"), dpi=150)

print("\nграфики сохранены в", OUT)
plt.show()