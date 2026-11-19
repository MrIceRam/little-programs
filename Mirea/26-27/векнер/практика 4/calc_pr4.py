"""ТСАУ ПР4, вариант 13 — расчёты для частей 4.1 и 4.2."""
import numpy as np
import sympy as sp
from scipy import signal

s = sp.symbols('s')
np.set_printoptions(precision=5, suppress=True)


def tf_from_ss(A, B, C, D=0):
    A, B, C = sp.Matrix(A), sp.Matrix(B), sp.Matrix(C)
    W = (C * (s * sp.eye(A.shape[0]) - A).inv() * B)[0, 0] + D
    return sp.factor(sp.simplify(W))


print("=" * 70, "\nЧасть 4.1")
a = [3, 6, 9, 3]
b = [1, 3, 6]
W = sp.Poly(b, s).as_expr() / sp.Poly(a, s).as_expr()
print("W(s) =", W, "=", sp.simplify(W))
an = [x / a[0] for x in a]           # нормированные
bn = [x / a[0] for x in b]
print("нормированные a:", an, " b:", bn)

# Фробениусова (управляемая) форма: x1=..., последняя строка -a
n = 3
Af = np.zeros((n, n)); Af[:-1, 1:] = np.eye(n - 1)
Af[-1, :] = [-an[3], -an[2], -an[1]]
Bf = np.array([[0], [0], [1]])
Cf = np.array([[bn[2], bn[1], bn[0]]])
print("Af=\n", Af, "\nBf=", Bf.T, "\nCf=", Cf)
print("W_Ф(s) =", tf_from_ss(sp.Matrix(Af).applyfunc(sp.nsimplify), Bf, sp.Matrix(Cf).applyfunc(sp.nsimplify)))

# Жорданова форма
num = np.array(bn); den = np.array(an)
r, p, k = signal.residue(num, den)
print("полюсы:", p, "\nвычеты:", r)
# точные корни
den_s = sp.Poly([1, 2, 3, 1], s)
print("корни точно:", [sp.N(x, 8) for x in sp.solve(den_s.as_expr(), s)])
# вещественная жорданова форма
lam1 = p[np.argmin(abs(p.imag))].real
pc = p[p.imag > 1e-9][0]
sig, om = pc.real, pc.imag
r1 = r[np.argmin(abs(p.imag))].real
rc = r[np.argmin(abs(p - pc))]
print(f"λ1={lam1:.6f}, σ={sig:.6f}, ω={om:.6f}, r1={r1:.6f}, rc={rc:.6f}")

print("\nЧасть 4.2  (FFG: F — вар.13, G — вар.14)")
AF = sp.Matrix([[3, 2], [1, 1]]); BF = sp.Matrix([1, 2]); CF = sp.Matrix([[1, 1]])
AG = sp.Matrix([[3, 1], [1, 2]]); BG = sp.Matrix([2, 1]); CG = sp.Matrix([[0, 1]])
for nm, A_, B_, C_ in [("F", AF, BF, CF), ("G", AG, BG, CG)]:
    print(nm, "W=", tf_from_ss(A_, B_, C_), " eig", A_.eigenvals())


def closed(AF, AG, sign=-1):
    WF = tf_from_ss(AF, BF, CF); WG = tf_from_ss(AG, BG, CG)
    Wc = sp.simplify(WF * WF / (1 - sign * WF * WF * WG))
    nu, de = sp.fraction(sp.together(Wc))
    nu, de = sp.Poly(sp.expand(nu), s), sp.Poly(sp.expand(de), s)
    return WF, WG, nu, de


WF, WG, nu, de = closed(AF, AG)
print("Исходная замкнутая: num", nu.all_coeffs(), "den", de.all_coeffs())
print("корни", np.roots([float(c) for c in de.all_coeffs()]))

# перебор знаков элементов A: ищем устойчивую замкнутую систему
import itertools
cands = []
for sf in itertools.product([1, -1], repeat=4):
    for sg in itertools.product([1, -1], repeat=4):
        AF2 = sp.Matrix(2, 2, [x * y for x, y in zip(sf, [3, 2, 1, 1])])
        AG2 = sp.Matrix(2, 2, [x * y for x, y in zip(sg, [3, 1, 1, 2])])
        _, _, nu2, de2 = closed(AF2, AG2)
        rr = np.roots([float(c) for c in de2.all_coeffs()])
        if np.all(rr.real < 0):
            cands.append((sum(x < 0 for x in sf) + sum(x < 0 for x in sg), sf, sg, max(rr.real)))
cands.sort()
print("устойчивых вариантов:", len(cands))
for c in cands[:12]:
    print(c)
