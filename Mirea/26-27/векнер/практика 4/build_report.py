"""Сборка отчёта ТСАУ ПР4 (вариант 13) в .docx по образцу отчёта ПР3.
Формулы — родные формулы Word (LaTeX -> MathML -> OMML через MML2OMML.XSL)."""
import copy
import os
import re

import docx
import numpy as np
import sympy as sp
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Cm, Pt
from latex2mathml.converter import convert as l2m
from lxml import etree
from scipy import signal

HERE = os.path.dirname(os.path.abspath(__file__))
FIG = os.path.join(HERE, 'Рисунки')
SIT = os.path.join(HERE, 'SimInTech')
TEMPLATE = os.path.join(HERE, '..', 'практика 3', 'ТСАУ_ПР3_вариант13.docx')
OUT = os.path.join(HERE, 'ТСАУ_ПР4_вариант13.docx')
XSL = etree.XSLT(etree.parse(r'C:\Program Files\Microsoft Office\root\Office16\MML2OMML.XSL'))

s = sp.symbols('s')


# ============================================================== числа
def n(x, d=4):
    """число с десятичной запятой для текста"""
    if isinstance(x, (int, np.integer)) or (float(x) == int(float(x)) and abs(float(x)) < 1e9 and d is None):
        return str(int(x))
    v = f'{float(x):.{d}f}'.rstrip('0').rstrip('.') if d is not None else str(x)
    return v.replace('-', '−').replace('.', ',')


def sci(x, d=1):
    e = int(np.floor(np.log10(abs(x))))
    m = x / 10 ** e
    sup = str(e).replace('-', '⁻').translate(str.maketrans('0123456789', '⁰¹²³⁴⁵⁶⁷⁸⁹'))
    return f'{m:.{d}f}'.replace('.', ',') + '·10' + sup


def nl(x, d=4):
    """число для LaTeX"""
    v = f'{float(x):.{d}f}'.rstrip('0').rstrip('.')
    return v.replace('.', '{,}')


def poly_tex(coefs, var='s'):
    """коэффициенты по убыванию степеней -> LaTeX"""
    deg = len(coefs) - 1
    out = ''
    for k, c in enumerate(coefs):
        p = deg - k
        if isinstance(c, float) and abs(c - round(c)) > 1e-9:
            if c == 0:
                continue
            sign = '-' if c < 0 else '+'
            term = nl(abs(c), 6) + (f'{var}^{{{p}}}' if p > 1 else (var if p == 1 else ''))
            out = (('-' if sign == '-' else '') + term) if out == '' else out + f' {sign} {term}'
            continue
        c = sp.nsimplify(c)
        if c == 0:
            continue
        sign = '-' if c < 0 else '+'
        a = abs(c)
        if a == 1 and p > 0:
            cs = ''
        else:
            cs = sp.latex(a)
        term = cs + (f'{var}^{{{p}}}' if p > 1 else (var if p == 1 else ''))
        if out == '':
            out = ('-' if sign == '-' else '') + term
        else:
            out += f' {sign} {term}'
    return out or '0'


def mat_tex(M, d=4):
    rows = []
    for i in range(M.shape[0]):
        row = []
        for j in range(M.shape[1]):
            v = M[i, j]
            if isinstance(v, sp.Basic):
                row.append(sp.latex(v))
            else:
                v = float(v)
                row.append(str(int(v)) if abs(v - round(v)) < 1e-12 else nl(v, d))
        rows.append(' & '.join(row))
    return r'\begin{bmatrix}' + r' \\ '.join(rows) + r'\end{bmatrix}'


def h_exact(num, den, t):
    """h(t) = W(0) + sum r_i/lambda_i e^(lambda_i t) для строго правильной W(s)"""
    r, p, _ = signal.residue(num, np.polymul(den, [1, 0]))
    return np.real(sum(ri * np.exp(pi * t) for ri, pi in zip(r, p)))


# ============================================================== документ
doc = docx.Document(TEMPLATE)
body = doc.element.body
# оставить титульный лист (до «Москва 2026» включительно)
els = list(body)
cut = None
for i, el in enumerate(els):
    if el.tag == qn('w:p'):
        txt = ''.join(t.text or '' for t in el.iter(qn('w:t')))
        if txt.strip() == 'Москва 2026':
            cut = i
            break
for el in els[cut + 1:]:
    if el.tag != qn('w:sectPr'):
        body.remove(el)
for p in doc.paragraphs:
    for r in p.runs:
        if 'РАБОТА №3' in r.text:
            r.text = r.text.replace('№3', '№4')
sectPr = body.find(qn('w:sectPr'))


def _append(el):
    sectPr.addprevious(el)
    return el


def omml(latex, display=False):
    mml = l2m(latex)
    tree = etree.fromstring(mml.encode('utf-8'))
    # точки/тильда над буквой — акцент (иначе Word рисует надстрочный предел)
    MM = '{http://www.w3.org/1998/Math/MathML}'
    acc = {'˙': '̇', '¨': '̈', '⃛': '⃛', '~': '̃', '˜': '̃'}
    for mo in tree.iter(MM + 'mover'):
        ch = mo[1] if len(mo) > 1 else None
        if ch is not None and (ch.text or '') in acc:
            mo.set('accent', 'true')
            ch.text = acc[ch.text]
    om = XSL(tree).getroot()
    M = 'http://schemas.openxmlformats.org/officeDocument/2006/math'
    for mm in list(om.iter('{%s}m' % M)) + list(om.iter('{%s}eqArr' % M)):
        prev, nxt = mm.getprevious(), mm.getnext()
        if prev is None or nxt is None or prev.tag != '{%s}r' % M or nxt.tag != '{%s}r' % M:
            continue
        tp, tn = prev.find('{%s}t' % M), nxt.find('{%s}t' % M)
        if tp is None or tn is None or not tp.text or not tn.text:
            continue
        if tp.text[-1] in '[(' and tn.text[0] in '])':
            beg, end = tp.text[-1], tn.text[0]
            dd = etree.Element('{%s}d' % M)
            dpr = etree.SubElement(dd, '{%s}dPr' % M)
            etree.SubElement(dpr, '{%s}begChr' % M).set('{%s}val' % M, beg)
            etree.SubElement(dpr, '{%s}endChr' % M).set('{%s}val' % M, end)
            e = etree.SubElement(dd, '{%s}e' % M)
            mm.addprevious(dd)
            e.append(mm)
            tp.text = tp.text[:-1]
            tn.text = tn.text[1:]
            for r in (prev, nxt):
                if not r.find('{%s}t' % M).text:
                    r.getparent().remove(r)
    return om


def new_par(style):
    p = OxmlElement('w:p')
    pPr = OxmlElement('w:pPr')
    ps = OxmlElement('w:pStyle')
    ps.set(qn('w:val'), style)
    pPr.append(ps)
    p.append(pPr)
    _append(p)
    return docx.text.paragraph.Paragraph(p, doc._body)


def add_runs(par, text):
    """text с $...$ — встроенные формулы"""
    parts = re.split(r'(\$[^$]+\$)', text)
    for part in parts:
        if not part:
            continue
        if part.startswith('$'):
            par._p.append(omml(part[1:-1]))
        else:
            # **жирный**
            for k, seg in enumerate(re.split(r'\*\*', part)):
                if seg:
                    r = par.add_run(seg)
                    if k % 2 == 1:
                        r.bold = True


FIRST = [True]


def H(text):
    p = new_par('1')
    p.add_run(text)
    FIRST[0] = True
    return p


def H2(text):
    p = new_par('a0')
    r = p.add_run(text)
    r.bold = True
    p.paragraph_format.keep_with_next = True
    FIRST[0] = True
    return p


def P(text):
    p = new_par('FirstParagraph' if FIRST[0] else 'a0')
    if FIRST[0]:
        p.paragraph_format.first_line_indent = Cm(1.25)
        p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.line_spacing = 1.5
        for_font(p)
    FIRST[0] = False
    add_runs(p, text)
    return p


def for_font(p):
    pass


def EQ(latex, label=None):
    p = new_par('a0')
    p.paragraph_format.first_line_indent = Cm(0)
    p.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
    mp = OxmlElement('m:oMathPara')
    mp.append(omml(latex))
    p._p.append(mp)
    return p


FIGN = [0]
TABN = [0]


def FIGURE(path, caption, width_cm=16.0):
    FIGN[0] += 1
    p = new_par('CaptionedFigure')
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(path, width=Cm(width_cm))
    c = new_par('ImageCaption')
    c.add_run(f'Рисунок {FIGN[0]} — {caption}')
    FIRST[0] = True
    return FIGN[0]


def set_cell_border(cell):
    tcPr = cell._tc.get_or_add_tcPr()
    b = OxmlElement('w:tcBorders')
    for edge in ('top', 'left', 'bottom', 'right'):
        e = OxmlElement(f'w:{edge}')
        e.set(qn('w:val'), 'single'); e.set(qn('w:sz'), '4'); e.set(qn('w:color'), '000000')
        b.append(e)
    tcPr.append(b)


def TABLE(caption, header, rows, widths=None, fs=12):
    TABN[0] += 1
    c = new_par('a0')
    c.paragraph_format.first_line_indent = Cm(0)
    c.paragraph_format.keep_with_next = True
    c.add_run(f'Таблица {TABN[0]} — {caption}')
    t = doc.add_table(rows=1 + len(rows), cols=len(header))
    t.alignment = WD_TABLE_ALIGNMENT.CENTER
    _append(t._tbl)
    for i, row in enumerate([header] + rows):
        for j, val in enumerate(row):
            cell = t.cell(i, j)
            set_cell_border(cell)
            cp = cell.paragraphs[0]
            cp.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
            cp.paragraph_format.first_line_indent = Cm(0)
            cp.paragraph_format.line_spacing = 1.0
            cp.paragraph_format.space_after = Pt(0)
            parts = re.split(r'(\$[^$]+\$)', str(val))
            for part in parts:
                if not part:
                    continue
                if part.startswith('$'):
                    cp._p.append(omml(part[1:-1]))
                else:
                    r = cp.add_run(part)
                    r.font.size = Pt(fs)
                    r.font.name = 'Times New Roman'
                    if i == 0:
                        r.bold = True
    if widths:
        for j, w in enumerate(widths):
            for row in t.rows:
                row.cells[j].width = Cm(w)
    sp_ = new_par('a0')
    FIRST[0] = True
    return TABN[0]


def PAGEBREAK():
    p = new_par('a0')
    p.add_run().add_break(WD_BREAK.PAGE)


# ============================================================== расчёты 4.1
a = [3, 6, 9, 3]
b = [1, 3, 6]
W = sp.Poly(b, s).as_expr() / sp.Poly(a, s).as_expr()
an = [sp.Rational(x, a[0]) for x in a]
bn = [sp.Rational(x, a[0]) for x in b]
# beta-метод: y''' + a1 y'' + a2 y' + a3 y = b0' u''' + b1' u'' + b2' u' + b3' u
B4 = [0] + bn
beta = [B4[0]]
for k in range(1, 4):
    beta.append(B4[k] - sum(an[j] * beta[k - j] for j in range(1, k + 1)))
A0 = sp.Matrix([[0, 1, 0], [0, 0, 1], [-an[3], -an[2], -an[1]]])
B0 = sp.Matrix(beta[1:])
C0 = sp.Matrix([[1, 0, 0]])
D0 = beta[0]
AF = A0
BF = sp.Matrix([0, 0, 1])
CF = sp.Matrix([[bn[2], bn[1], bn[0]]])


def tf(A, B, C, D=0):
    return sp.factor(sp.simplify((C * (s * sp.eye(A.shape[0]) - A).inv() * B)[0, 0] + D))


W0 = tf(A0, B0, C0, D0)
WFr = tf(AF, BF, CF)
num_n = [float(x) for x in bn]
den_n = [float(x) for x in an]
r_, p_, _ = signal.residue(num_n, den_n)
i1 = int(np.argmin(abs(p_.imag)))
ic = [k for k in range(3) if p_[k].imag > 1e-9][0]
lam1, sig, om = p_[i1].real, p_[ic].real, p_[ic].imag
r1, alf, bet = r_[i1].real, r_[ic].real, r_[ic].imag
c2, c3 = -2 * bet, 2 * alf
AJr = np.array([[lam1, 0, 0], [0, sig, om], [0, -om, sig]])
BJr = np.array([[1], [0], [1]])
CJr = np.array([[r1, c2, c3]])
nJ, dJ = signal.ss2tf(AJr, BJr, CJr, np.zeros((1, 1)))
# комплексная диагональная форма
lams = [lam1, complex(sig, om), complex(sig, -om)]
res = [r1, complex(alf, bet), complex(alf, -bet)]
nJc, dJc = signal.invres(res, lams, [])
# Вандермонд
V = np.array([[1, 1, 1], lams, [l ** 2 for l in lams]], dtype=complex)
AJc = np.linalg.inv(V) @ np.array(AF.evalf(), dtype=complex) @ V
# Мейсон
# SimInTech
d1 = np.loadtxt(os.path.join(SIT, 'pr4_1.dat'))
h1 = h_exact(b, a, d1[:, 0])
err1 = np.max(abs(d1[:, 2:] - h1[:, None]))

# ============================================================== расчёты 4.2
AFm = sp.Matrix([[3, 2], [1, 1]]); BFm = sp.Matrix([1, 2]); CFm = sp.Matrix([[1, 1]])
AGm = sp.Matrix([[3, 1], [1, 2]]); BGm = sp.Matrix([2, 1]); CGm = sp.Matrix([[0, 1]])


def closed(AF_, AG_):
    WF_ = tf(AF_, BFm, CFm)
    WG_ = tf(AG_, BGm, CGm)
    Phi = sp.cancel(WF_ ** 2 / (1 + WF_ ** 2 * WG_))
    nu, de = sp.fraction(Phi)
    nu, de = sp.Poly(nu, s), sp.Poly(de, s)
    lc = de.LC()
    return WF_, WG_, [x / lc for x in nu.all_coeffs()], [x / lc for x in de.all_coeffs()]


WF1, WG1, num1, den1 = closed(AFm, AGm)
WF2, WG2, num2, den2 = closed(-AFm, -AGm)
poles1 = np.roots([float(x) for x in den1])
poles2 = np.roots([float(x) for x in den2])
# Гурвиц
dd = [float(x) for x in den2]
nH = len(dd) - 1


def hurwitz(c):
    m = len(c) - 1
    Hm = np.zeros((m, m))
    for i in range(m):
        for j in range(m):
            k = 2 * j - i + 1
            if 0 <= k <= m:
                Hm[i, j] = c[k]
    return [np.linalg.det(Hm[:k, :k]) for k in range(1, m + 1)]


hur = hurwitz(dd)
aa = [x for x in den2[1:]]          # a1..a6
bb = [0] * (6 - len(num2)) + list(num2)
AL = sp.zeros(6, 6)
for i in range(6):
    AL[i, 0] = -aa[i]
    if i < 5:
        AL[i, i + 1] = 1
BL = sp.Matrix(bb)
CL = sp.Matrix([[1, 0, 0, 0, 0, 0]])
AK = sp.zeros(6, 6)
for i in range(5):
    AK[i, i + 1] = 1
for j in range(6):
    AK[5, j] = -aa[5 - j]
BK = sp.Matrix([0, 0, 0, 0, 0, 1])
CK = sp.Matrix([[bb[5 - j] for j in range(6)]])
WL = tf(AL, BL, CL)
WK = tf(AK, BK, CK)
# внутренняя модель соединения FFG (проверка)
A1, A2 = -AFm, -AGm
Acl = sp.zeros(6, 6)
Acl[0:2, 0:2] = A1
Acl[0:2, 4:6] = -BFm * CGm
Acl[2:4, 0:2] = BFm * CFm
Acl[2:4, 2:4] = A1
Acl[4:6, 2:4] = BGm * CFm
Acl[4:6, 4:6] = A2
eig_cl = np.sort_complex(np.linalg.eigvals(np.array(Acl.evalf(), dtype=float)))
d2 = np.loadtxt(os.path.join(SIT, 'pr4_2.dat'))
h2 = h_exact([float(x) for x in num2], [float(x) for x in den2], d2[:, 0])
err2 = np.max(abs(d2[:, 2:] - h2[:, None]))


def frac_tex(nu, de):
    return r'\frac{' + poly_tex(nu) + '}{' + poly_tex(de) + '}'


def W_tex(expr):
    nu, de = sp.fraction(sp.together(expr))
    return r'\frac{' + sp.latex(sp.expand(nu)) + '}{' + sp.latex(sp.expand(de)) + '}'


# ============================================================== текст
H('Цель работы')
P('Освоить переход от дифференциального уравнения и от внутренних моделей подсистем к внешним '
  'моделям (передаточным функциям) и обратно, к каноническим формам уравнений состояния; '
  'построить сигнальные графы и структурные схемы канонических форм и убедиться в их '
  'эквивалентности моделированием в SimInTech.')

# ------------------------------------------------------------------ 4.1
H('Часть 4.1. Канонические формы уравнений состояния')
H2('1. Исходные данные')
P('Вариант 13. Объект описывается дифференциальным уравнением')
EQ(r'a_0\frac{d^3 y}{dt^3}+a_1\frac{d^2 y}{dt^2}+a_2\frac{dy}{dt}+a_3 y='
   r'b_0\frac{d^2 u}{dt^2}+b_1\frac{du}{dt}+b_2 u,')
P('где $y=x_{вых}$, $u=x_{вх}$. Коэффициенты варианта 13 приведены в таблице 1.')
TABLE('Исходные данные варианта 13 (часть 4.1)',
      ['$a_0$', '$a_1$', '$a_2$', '$a_3$', '$b_0$', '$b_1$', '$b_2$'],
      [[str(x) for x in a + b]])
P('Уравнение варианта:')
EQ(r"3\dddot y+6\ddot y+9\dot y+3y=\ddot u+3\dot u+6u.")

H2('2. Передаточная функция и матрицы состояния, полученные из уравнения')
P('Применив преобразование Лапласа при нулевых начальных условиях, получим передаточную функцию')
EQ(r'W(s)=\frac{Y(s)}{U(s)}=\frac{s^2+3s+6}{3s^3+6s^2+9s+3}='
   r'\frac{\frac{1}{3}s^2+s+2}{s^3+2s^2+3s+1}.')
P('Порядок системы $n=3$, степень числителя $m=2<n$, поэтому система строго правильная ($D=0$). '
  'Коэффициент передачи $W(0)=6/3=2$.')
P('Для получения уравнений состояния непосредственно из уравнения с производными входа '
  'нормируем его ($a_0=1$): $\\dddot y+2\\ddot y+3\\dot y+y=\\tfrac13\\ddot u+\\dot u+2u$, и '
  'введём переменные состояния $x_1=y-\\beta_0u$, $x_2=\\dot x_1-\\beta_1u$, $x_3=\\dot x_2-\\beta_2u$. '
  'Коэффициенты $\\beta_k$ находятся из рекуррентного соотношения')
EQ(r'\beta_0=b_0^{*},\quad \beta_k=b_k^{*}-\sum_{j=1}^{k}{a_j^{*}\beta_{k-j}},\quad k=1,2,3,')
P(f'где $b^{{*}}=(0;\\,\\tfrac13;\\,1;\\,2)$, $a^{{*}}=(1;\\,2;\\,3;\\,1)$. Получаем '
  f'$\\beta_0={sp.latex(beta[0])}$, $\\beta_1={sp.latex(beta[1])}$, '
  f'$\\beta_2=1-2\\cdot\\tfrac13={sp.latex(beta[2])}$, '
  f'$\\beta_3=2-2\\cdot\\tfrac13-3\\cdot\\tfrac13={sp.latex(beta[3])}$. '
  'Уравнения состояния $\\dot x=Ax+Bu$, $y=Cx+Du$ имеют матрицы')
EQ(r'A=' + mat_tex(A0) + r',\quad B=' + mat_tex(B0) + r',\quad C=' + mat_tex(C0) + r',\quad D=0.')
P(f'Проверка: $W(s)=C(sI-A)^{{-1}}B+D={W_tex(W0)}$ — совпадает с передаточной функцией, '
  'полученной из уравнения.')

H2('3. Фробениусова строчно-управляемая каноническая форма')
P('Введём вспомогательную переменную $z$: $\\dddot z+2\\ddot z+3\\dot z+z=u$, тогда '
  '$y=\\tfrac13\\ddot z+\\dot z+2z$. Переменные состояния $x_1=z$, $x_2=\\dot z$, $x_3=\\ddot z$ дают '
  'фробениусову (сопровождающую) матрицу, у которой последняя строка состоит из коэффициентов '
  'характеристического полинома с обратным знаком, а вход действует только на последнее уравнение:')
EQ(r'A_Ф=' + mat_tex(AF) + r',\quad B_Ф=' + mat_tex(BF) + r',\quad C_Ф=' + mat_tex(CF) + r',\quad D_Ф=0.')
P('В скалярной записи: $\\dot x_1=x_2$, $\\dot x_2=x_3$, $\\dot x_3=-x_1-3x_2-2x_3+u$, '
  '$y=2x_1+x_2+\\tfrac13x_3$.')

H2('4. Жорданова каноническая форма')
P('Характеристическое уравнение $\\mathrm{det}(sI-A_Ф)=s^3+2s^2+3s+1=0$ имеет один вещественный и '
  'пару комплексно-сопряжённых корней:')
EQ(rf'\lambda_1={nl(lam1)},\qquad \lambda_{{2,3}}=\sigma\pm j\omega={nl(sig)}\pm j\,{nl(om)}.')
P('Все корни простые и лежат в левой полуплоскости — система устойчива. Разложим передаточную '
  'функцию на простые дроби:')
EQ(r'W(s)=\sum_{i=1}^{3}{\frac{r_i}{s-\lambda_i}},\quad r_i=\left.\frac{\frac13s^2+s+2}'
   r'{\frac{d}{ds}(s^3+2s^2+3s+1)}\right|_{s=\lambda_i},')
EQ(rf'r_1={nl(r1)},\qquad r_{{2,3}}=\alpha\pm j\beta={nl(alf)}\pm j\,({nl(bet)}).')
P('При простых корнях жорданова форма диагональна: каждая координата — отдельное апериодическое '
  'звено, вход подаётся на все координаты с единичным весом, а выход — сумма координат с весами-вычетами:')
EQ(r'A_J=\mathrm{diag}(\lambda_1,\lambda_2,\lambda_3),\quad B_J=\begin{bmatrix}1\\1\\1\end{bmatrix},\quad '
   r'C_J=\begin{bmatrix}r_1 & r_2 & r_3\end{bmatrix}.')
P('Переход от фробениусовой формы к жордановой выполняется преобразованием подобия $x=Vx_J$ с '
  'матрицей Вандермонда $V$, столбцы которой — собственные векторы $(1;\\,\\lambda_i;\\,\\lambda_i^2)^T$ '
  'матрицы $A_Ф$; численно $V^{-1}A_ФV$ действительно диагональна с элементами $\\lambda_i$ '
  f'(наибольший внедиагональный элемент по модулю {sci(np.max(abs(AJc - np.diag(np.diag(AJc)))))} — ошибка округления).')
P('Комплексные коэффициенты неудобны для моделирования, поэтому для пары $\\lambda_{2,3}$ '
  'используем вещественную жорданову клетку $\\begin{bmatrix}\\sigma & \\omega\\\\ -\\omega & \\sigma\\end{bmatrix}$. '
  'Для неё $C(sI-A)^{-1}B$ с $B=(0;\\,1)^T$, $C=(c_2;\\,c_3)$ равна '
  '$\\dfrac{c_2\\omega+c_3(s-\\sigma)}{(s-\\sigma)^2+\\omega^2}$, а сумма двух сопряжённых дробей равна '
  '$\\dfrac{2\\alpha(s-\\sigma)-2\\beta\\omega}{(s-\\sigma)^2+\\omega^2}$. Отсюда $c_2=-2\\beta$, $c_3=2\\alpha$ и')
EQ(r'A_J^{вещ}=' + mat_tex(AJr) + r',\quad B_J^{вещ}=\begin{bmatrix}1\\0\\1\end{bmatrix},')
EQ(r'C_J^{вещ}=' + mat_tex(CJr) + r'.')

H2('5. Передаточные функции по матрицам канонических форм')
P('Фробениусова форма:')
EQ(r'W_Ф(s)=C_Ф(sI-A_Ф)^{-1}B_Ф=\frac{\frac13s^2+s+2}{s^3+2s^2+3s+1}=' + W_tex(WFr) + '.')
P('Для фробениусовой формы это видно и без обращения матрицы: $(sI-A_Ф)^{-1}B_Ф=(1;\\,s;\\,s^2)^T/\\Delta(s)$, '
  'где $\\Delta(s)=s^3+2s^2+3s+1$, поэтому числитель равен $C_Ф(1;\\,s;\\,s^2)^T=2+s+\\tfrac13s^2$.')
P('Жорданова форма (диагональная, комплексная):')
EQ(r'W_J(s)=\sum_{i=1}^{3}{\frac{r_i}{s-\lambda_i}}=\frac{' + poly_tex([round(float(np.real(x)), 6) for x in nJc]).replace('.', '{,}') +
   '}{' + poly_tex([round(float(np.real(x)), 6) for x in dJc]).replace('.', '{,}') + '}.')
P('Жорданова форма (вещественная), численно по матрицам:')
EQ(r'W_J^{вещ}(s)=\frac{' + poly_tex([round(float(x), 6) for x in nJ[0][1:]]).replace('.', '{,}') +
   '}{' + poly_tex([round(float(x), 6) for x in dJ]).replace('.', '{,}') + '}.')
TABLE('Сравнение коэффициентов передаточных функций (нормированный знаменатель)',
      ['Модель', '$s^2$', '$s^1$', '$s^0$', 'знаменатель'],
      [['ДУ, $W(s)$', '0,333333', '1', '2', '$s^3+2s^2+3s+1$'],
       ['матрицы из ДУ ($\\beta$-метод)', '0,333333', '1', '2', '$s^3+2s^2+3s+1$'],
       ['фробениусова форма', '0,333333', '1', '2', '$s^3+2s^2+3s+1$'],
       ['жорданова форма', n(nJ[0][1], 6), n(nJ[0][2], 6), n(nJ[0][3], 6), '$s^3+2s^2+3s+1$']],
      widths=[5.5, 2.2, 2.2, 2.2, 4.2])
P('Все передаточные функции совпадают с передаточной функцией, полученной из дифференциального '
  'уравнения (у жордановой формы — с точностью до округления вычетов, порядка $10^{-12}$). Так и должно '
  'быть: канонические формы получаются друг из друга неособым преобразованием подобия '
  '$\\tilde A=T^{-1}AT$, $\\tilde B=T^{-1}B$, $\\tilde C=CT$, а передаточная функция к нему инвариантна: '
  '$\\tilde C(sI-\\tilde A)^{-1}\\tilde B=CT\\,T^{-1}(sI-A)^{-1}T\\,T^{-1}B=C(sI-A)^{-1}B$.')

H2('6. Сигнальные графы канонических форм')
P('Узлы графа — сигналы $u$, $\\dot x_i$, $x_i$, $y$; ветви $s^{-1}$ — интеграторы, остальные ветви — '
  'постоянные коэффициенты матриц $A$, $B$, $C$.')
FIGURE(os.path.join(FIG, 'sfg_frob_41.png'), 'Сигнальный граф фробениусовой (управляемой) канонической формы', 15.5)
P('Проверим граф по формуле Мейсона. Все три контура $L_1=-2s^{-1}$, $L_2=-3s^{-2}$, $L_3=-s^{-3}$ '
  'проходят через узел $\\dot x_3$, т. е. попарно касаются, поэтому $\\Delta=1+2s^{-1}+3s^{-2}+s^{-3}$. '
  'Прямые пути $P_1=2s^{-3}$, $P_2=s^{-2}$, $P_3=\\tfrac13s^{-1}$ касаются всех контуров ($\\Delta_k=1$):')
EQ(r'W(s)=\frac{\sum{P_k\Delta_k}}{\Delta}=\frac{2s^{-3}+s^{-2}+\frac13s^{-1}}{1+2s^{-1}+3s^{-2}+s^{-3}}'
   r'=\frac{\frac13s^2+s+2}{s^3+2s^2+3s+1}.')
FIGURE(os.path.join(FIG, 'sfg_jordan_41.png'), 'Сигнальный граф жордановой канонической формы (вещественная клетка для пары λ₂,₃)', 15.5)
P('Граф жордановой формы распадается на независимую ветвь вещественного корня $\\lambda_1$ (контур '
  '$\\lambda_1s^{-1}$) и подграф комплексной пары, в котором две координаты связаны перекрёстными '
  'ветвями $\\pm\\omega$. В комплексной диагональной форме перекрёстных ветвей нет: граф — три '
  'параллельные ветви $u\\to\\dot x_i\\to x_i\\to y$ с петлями $\\lambda_is^{-1}$ и весами выхода $r_i$.')

H2('7. Моделирование в SimInTech')
P('В проекте SimInTech/ПР4_1.xprt собраны три схемы с общим входом — ступенькой $u(t)=1(t)$ '
  '(рисунок 3): блок «Передаточная функция общего вида» с $W(s)$; фробениусова форма из трёх '
  'интеграторов и двух сумматоров с весами $(1;\\,-1;\\,-3;\\,-2)$ и $(2;\\,1;\\,\\tfrac13)$; '
  'жорданова форма из трёх интеграторов и сумматоров с весами $\\lambda_1$, $\\sigma$, $\\pm\\omega$ и '
  '$c_1$, $c_2$, $c_3$. Выходы подключены к временному графику и к блоку «В файл» (pr4_1.dat). '
  'Метод интегрирования — Рунге–Кутты 4(5), максимальный шаг 0,01 с, время 20 с.')
FIGURE(os.path.join(FIG, 'sit_4_1_scheme.jpg'), 'Схема моделирования в SimInTech (часть 4.1): W(s), фробениусова и жорданова формы', 16.5)
FIGURE(os.path.join(FIG, 'step_41.png'), 'Реакции трёх моделей на ступенчатый сигнал (данные SimInTech) и их отклонение от точной переходной функции', 15.5)
rows = []
for q in (0.5, 1, 2, 3, 5, 10, 20):
    i = int(np.argmin(abs(d1[:, 0] - q)))
    rows.append([n(d1[i, 0], 2), n(d1[i, 2], 6), n(d1[i, 3], 6), n(d1[i, 4], 6), n(h1[i], 6)])
TABLE('Значения переходных процессов (SimInTech) и точной переходной функции',
      ['t, с', 'W(s)', 'фробениусова', 'жорданова', 'точно h(t)'], rows, widths=[2.0, 3.3, 3.3, 3.3, 3.3])
P(f'Три кривые на рисунке 4 совпадают. Наибольшее отклонение любой модели от точной переходной '
  f'функции за 20 с равно {sci(err1)}, т. е. на уровне погрешности вычислений с плавающей точкой; '
  'установившееся значение $h(\\infty)=W(0)=2$. Процесс апериодический: доминирует медленный корень '
  f'$\\lambda_1={nl(lam1)}$ (постоянная времени ≈ {n(-1 / lam1, 2)} с), колебательная составляющая пары '
  f'$\\lambda_{{2,3}}$ затухает быстрее ($|\\sigma|={nl(-sig)}$). Структуры эквивалентны.')

# ------------------------------------------------------------------ 4.2
PAGEBREAK()
H('Часть 4.2. Внешняя модель соединения подсистем и её канонические формы')
H2('1. Исходные данные')
P('Варианту 13 соответствует комбинация FFG (столбец «13-14»): подсистема F задаётся матрицами '
  'варианта 13, подсистема G — матрицами варианта 14. Две подсистемы F, включённые последовательно, '
  'образуют прямой тракт, подсистема G — отрицательную обратную связь.')
EQ(r'F:\ A_F=' + mat_tex(AFm) + r',\ B_F=' + mat_tex(BFm) + r',\ C_F=' + mat_tex(CFm) + r';\qquad '
   r'G:\ A_G=' + mat_tex(AGm) + r',\ B_G=' + mat_tex(BGm) + r',\ C_G=' + mat_tex(CGm) + r'.')

H2('2. Внешние модели подсистем')
P('Передаточная функция подсистемы $W(s)=C(sI-A)^{-1}B$, $(sI-A)^{-1}=\\mathrm{adj}(sI-A)/\\mathrm{det}(sI-A)$:')
EQ(r'(sI-A_F)^{-1}B_F=\frac{1}{s^2-4s+1}\begin{bmatrix}s-1 & 2\\1 & s-3\end{bmatrix}'
   r'\begin{bmatrix}1\\2\end{bmatrix}=\frac{1}{s^2-4s+1}\begin{bmatrix}s+3\\2s-5\end{bmatrix},\quad '
   r'W_F(s)=' + W_tex(WF1) + ',')
EQ(r'(sI-A_G)^{-1}B_G=\frac{1}{s^2-5s+5}\begin{bmatrix}s-2 & 1\\1 & s-3\end{bmatrix}'
   r'\begin{bmatrix}2\\1\end{bmatrix}=\frac{1}{s^2-5s+5}\begin{bmatrix}2s-3\\s-1\end{bmatrix},\quad '
   r'W_G(s)=' + W_tex(WG1) + '.')
P('Собственные значения $A_F$: $2\\pm\\sqrt3$ ($3{,}732$ и $0{,}268$), $A_G$: $(5\\pm\\sqrt5)/2$ '
  '($3{,}618$ и $1{,}382$) — обе подсистемы неустойчивы.')

H2('3. Внешняя модель замкнутой системы и обеспечение устойчивости')
P('Для соединения FFG с отрицательной обратной связью')
EQ(r'\Phi(s)=\frac{W_F^2(s)}{1+W_F^2(s)W_G(s)}=\frac{N_F^2D_G}{D_F^2D_G+N_F^2N_G},')
P('где $W_F=N_F/D_F$, $W_G=N_G/D_G$. Для исходных матриц')
EQ(r'\Phi(s)=' + frac_tex(num1, den1) + '.')
P('Коэффициенты знаменателя знакопеременные — не выполняется даже необходимое условие устойчивости. '
  'Полюсы: ' + '; '.join(n(x.real, 3) + (f' ± j{n(abs(x.imag), 3)}' if abs(x.imag) > 1e-9 else '')
                          for x in sorted(poles1, key=lambda z: -z.real) if x.imag >= -1e-9) +
  ' — все в правой полуплоскости, замкнутая система неустойчива.')
P('По заданию изменим знаки перед коэффициентами матриц $A$. Сменим знаки всех элементов $A_F$ и '
  '$A_G$ ($A\\to-A$): собственные значения подсистем отражаются в левую полуплоскость, обе подсистемы '
  'становятся устойчивыми. Матрицы $B$ и $C$ не меняются:')
EQ(r'A_F^{*}=' + mat_tex(-AFm) + r',\quad A_G^{*}=' + mat_tex(-AGm) + r',\quad '
   r'W_F(s)=' + W_tex(WF2) + r',\quad W_G(s)=' + W_tex(WG2) + '.')
P('Внешняя модель замкнутой системы:')
EQ(r'\Phi(s)=\frac{(3s+2)^2(s^2+5s+5)}{(s^2+4s+1)^2(s^2+5s+5)+(3s+2)^2(s+1)}=' + frac_tex(num2, den2) + '.')
P('Все коэффициенты знаменателя положительны. Определители Гурвица: ' +
  ', '.join(f'$\\Delta_{k + 1}={nl(h, 0) if abs(h) > 100 else nl(h, 2)}$' for k, h in enumerate(hur)) +
  ' — все положительны, замкнутая система устойчива. Её полюсы:')
pl = sorted(poles2, key=lambda z: -z.real)
EQ(', \\ '.join(nl(x.real, 4) + (rf'\pm j\,{nl(abs(x.imag), 4)}' if abs(x.imag) > 1e-9 else '')
                for x in pl if x.imag >= -1e-9) + '.')
FIGURE(os.path.join(FIG, 'ffg_scheme.png'), 'Структурная схема замкнутой системы FFG после смены знаков в матрицах A', 15.0)
FIGURE(os.path.join(FIG, 'poles_42.png'), 'Полюсы замкнутой системы до и после смены знаков', 13.0)
P('Проверка через внутреннюю модель. Если сложить уравнения состояния подсистем ($x_a$ — первая F, '
  '$x_b$ — вторая F, $x_c$ — G; $u_a=u-C_Gx_c$, $u_b=C_Fx_a$, $u_c=C_Fx_b$), получим матрицу шестого порядка')
EQ(r'A_{зам}=\begin{bmatrix}A_F^{*} & 0 & -B_FC_G\\ B_FC_F & A_F^{*} & 0\\ 0 & B_GC_F & A_G^{*}\end{bmatrix},')
P('собственные значения которой совпадают с полюсами $\\Phi(s)$ (расхождение ' +
  sci(np.max(abs(np.sort_complex(pl) - eig_cl))) + '). Сокращений нулей и полюсов нет: '
  'порядок внешней модели равен шести — суммарному порядку подсистем.')

H2('4. Каноническая форма Люенбергера')
P('Для одномерной системы каноническая форма Люенбергера совпадает с наблюдаемой канонической формой. '
  'Запишем $\\Phi(s)=\\dfrac{b_1s^5+\\dots+b_6}{s^6+a_1s^5+\\dots+a_6}$, где '
  f'$a=({"; ".join(str(int(x)) for x in aa)})$, $b=({"; ".join(str(int(x)) for x in bb)})$. Матрица '
  'состояния содержит коэффициенты знаменателя в первом столбце, вход входит в каждое уравнение '
  'с весом $b_i$, выход — первая координата:')
EQ(r'\dot x_i=x_{i+1}-a_ix_1+b_iu\ (i=1,\dots,5),\quad \dot x_6=-a_6x_1+b_6u,\quad y=x_1,')
EQ(r'A_Л=' + mat_tex(AL) + r',\ B_Л=' + mat_tex(BL) + r',')
EQ(r'C_Л=' + mat_tex(CL) + r',\quad D_Л=0.')
FIGURE(os.path.join(FIG, 'luenberger_scheme.png'), 'Структурная схема модели в канонической форме Люенбергера', 16.5)

H2('5. Внутренняя модель в канонической форме Коши–Фробениуса')
P('Управляемая каноническая форма: координаты — вспомогательная переменная и её производные, '
  '$\\dot x_i=x_{i+1}$ ($i=1,\\dots,5$), $\\dot x_6=u-\\sum a_{7-j}x_j$, $y=\\sum b_{7-j}x_j$:')
EQ(r'A_К=' + mat_tex(AK) + r',\ B_К=' + mat_tex(BK) + r',')
EQ(r'C_К=' + mat_tex(CK) + r',\quad D_К=0.')
P('Форма Коши–Фробениуса дуальна форме Люенбергера: $A_К=A_Л^T$ с точностью до перенумерации '
  'координат, $B_К\\leftrightarrow C_Л^T$, $C_К\\leftrightarrow B_Л^T$.')
FIGURE(os.path.join(FIG, 'frob_scheme_42.png'), 'Структурная схема модели в канонической форме Коши–Фробениуса', 16.5)
P('Передаточные функции, вычисленные по матрицам обеих форм, совпадают с $\\Phi(s)$:')
EQ(r'C_Л(sI-A_Л)^{-1}B_Л=C_К(sI-A_К)^{-1}B_К=' + W_tex(WK) + '.')
assert sp.simplify(WL - WK) == 0

H2('6. Моделирование в SimInTech')
P('Проект SimInTech/ПР4_2.xprt (рисунок 9) содержит три схемы с общей ступенькой на входе: блок '
  '«Передаточная функция общего вида» с $\\Phi(s)$; форму Люенбергера — цепочку из шести сумматоров '
  'и шести интеграторов, где на каждый сумматор подаются $x_{i+1}$, $-a_ix_1$ и $b_iu$; форму '
  'Коши–Фробениуса — цепочку из шести интеграторов, сумматор на входе с весами $(1;\\,-9;\\,-61;\\,'
  '-152;\\,-147;\\,-63;\\,-13)$ и выходной сумматор с весами $(20;\\,80;\\,109;\\,57;\\,9)$. '
  'Время моделирования 40 с, метод Рунге–Кутты 4(5), максимальный шаг 0,01 с.')
FIGURE(os.path.join(FIG, 'sit_4_2_scheme.jpg'), 'Схема моделирования в SimInTech (часть 4.2): Φ(s), формы Люенбергера и Коши–Фробениуса', 16.5)
FIGURE(os.path.join(FIG, 'step_42.png'), 'Реакции трёх моделей замкнутой системы на ступенчатый сигнал (данные SimInTech) и отклонение от точной переходной функции', 15.5)
rows = []
for q in (0.5, 1, 2, 5, 10, 20, 40):
    i = int(np.argmin(abs(d2[:, 0] - q)))
    rows.append([n(d2[i, 0], 2), n(d2[i, 2], 6), n(d2[i, 3], 6), n(d2[i, 4], 6),
                 n(h2[i], 6)])
TABLE('Значения переходных процессов замкнутой системы (SimInTech) и точной переходной функции',
      ['t, с', 'Φ(s)', 'Люенбергер', 'Коши–Фробениус', 'точно h(t)'], rows, widths=[2.0, 3.3, 3.3, 3.3, 3.3])
ymax = float(np.max(d2[:, 2]))
P(f'Кривые всех трёх моделей совпадают; наибольшее отклонение от точного решения {sci(err2)} '
  f'(точное решение вычислено аналитически через вычеты $W(s)/s$). Установившееся значение '
  f'$h(\\infty)=\\Phi(0)=20/9={nl(20 / 9, 4)}$; максимум {n(ymax, 4)} превышает его на '
  f'{n((ymax / (20 / 9) - 1) * 100, 2)} % — переходный процесс практически монотонный, длительность '
  f'определяется медленной парой полюсов ${nl(pl[0].real, 4)}\\pm j\\,{nl(abs(pl[0].imag), 4)}$. '
  'Структуры эквивалентны.')

H('Выводы')
P('1. Для уравнения варианта 13 получена передаточная функция $W(s)=(s^2+3s+6)/(3s^3+6s^2+9s+3)$ и '
  'матрицы состояния ($\\beta$-методом), сформированы фробениусова (управляемая) и жорданова формы. '
  f'Корни характеристического уравнения ${nl(lam1)}$ и ${nl(sig)}\\pm j\\,{nl(om)}$ — объект устойчив.')
P('2. Передаточные функции, вычисленные по матрицам всех форм, совпадают с исходной: передаточная '
  'функция инвариантна к преобразованию подобия координат. Это подтверждено и формулой Мейсона '
  'по сигнальному графу фробениусовой формы.')
P('3. Подсистемы F и G и замкнутая система FFG с исходными матрицами неустойчивы. Смена знаков всех '
  'элементов матриц $A$ сделала устойчивыми и подсистемы, и замкнутую систему шестого порядка с '
  '$\\Phi(s)=(9s^4+57s^3+109s^2+80s+20)/(s^6+13s^5+63s^4+147s^3+152s^2+61s+9)$.')
P('4. Для $\\Phi(s)$ построены каноническая форма Люенбергера (наблюдаемая) и форма Коши–Фробениуса '
  '(управляемая), изображены их структурные схемы.')
P(f'5. В SimInTech реакции передаточной функции и двух канонических форм на единичную ступеньку '
  f'совпали в обеих частях работы (расхождение не более {sci(err1)} и {sci(err2)}), '
  'что подтверждает эквивалентность структур.')

doc.save(OUT)
print('saved', OUT, 'figs', FIGN[0], 'tables', TABN[0])
print('beta', beta, 'W0', W0, 'WFr', WFr)
print('hur', hur)
print('nJ', nJ, 'nJc', nJc)
