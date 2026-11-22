import fs from "node:fs";
import path from "node:path";
import {
  AlignmentType, Document, Footer, HeadingLevel, ImageRun,
  Math as MathEq, MathFraction, MathRadical, MathRoundBrackets, MathRun,
  MathSquareBrackets, MathSubScript, MathSubSuperScript, MathSuperScript,
  Packer, PageBreak, PageNumber, Paragraph, ShadingType, Tab, TabStopType,
  Table, TableCell, TableRow, TextRun, WidthType,
} from "docx";

const outputPath = process.argv[2];
if (!outputPath) throw new Error("Usage: node create.js /abs/out.docx");
const outputDir = path.dirname(outputPath);
const imgDir = path.join(outputDir, "img");

const T = String.raw;
const font = { ascii: "Times New Roman", hAnsi: "Times New Roman", cs: "Times New Roman", eastAsia: "SimSun" };
const run = (text, options = {}) => new TextRun({ text, font, size: 28, ...options });
const para = (children, options = {}) => new Paragraph({
  spacing: { after: 160, line: 360 },
  ...options,
  children: Array.isArray(children) ? children : [children],
});
const body = (text, options = {}) =>
  para(run(text), { indent: { firstLine: 709 }, alignment: AlignmentType.JUSTIFIED, ...options });
const h1 = (text) => para(run(text, { bold: true, color: "000000" }), {
  heading: HeadingLevel.HEADING_1,
  alignment: AlignmentType.CENTER,
  spacing: { before: 280, after: 160, line: 360 },
});
const bodyM = (parts, options = {}) =>
  para(parts.map(([t, o]) => run(t, o || {})), { indent: { firstLine: 709 }, alignment: AlignmentType.JUSTIFIED, ...options });
const center = (text, options = {}) =>
  para(run(text, options), { alignment: AlignmentType.CENTER });

/* ---------- math helpers ---------- */
const mr = (t) => new MathRun(t);
const fr = (n, d) => new MathFraction({ numerator: n, denominator: d });
const sp = (b, s) => new MathSuperScript({ children: b, superScript: s });
const sb = (b, s) => new MathSubScript({ children: b, subScript: s });
const ssb = (b, s, p2) => new MathSubSuperScript({ children: b, subScript: s, superScript: p2 });
const sq = (c) => new MathRadical({ children: c });
const rb = (c) => new MathRoundBrackets({ children: c });
const sbk = (c) => new MathSquareBrackets({ children: c });
const E = (mant, exp) => sp([mr(`${mant}·10`)], [mr(exp)]);

const I1 = () => sb([mr("I")], [mr("1")]);
const I2 = () => sb([mr("I")], [mr("2")]);
const R1 = () => sb([mr("R")], [mr("1")]);
const R2 = () => sb([mr("R")], [mr("2")]);
const C1 = () => sb([mr("C")], [mr("1")]);
const C2 = () => sb([mr("C")], [mr("2")]);
const XC1 = () => sb([mr("X")], [mr("C1")]);
const XC2 = () => sb([mr("X")], [mr("C2")]);
const XV = () => sb([mr("x")], [mr("вых")]);
const XH = () => sb([mr("x")], [mr("вх")]);

const TEXTW = 9355;
const eq = (mathChildren, num) => new Paragraph({
  tabStops: [
    { type: TabStopType.CENTER, position: 4677 },
    { type: TabStopType.RIGHT, position: TEXTW },
  ],
  spacing: { before: 80, after: 80, line: 360 },
  children: [
    new TextRun({ children: [new Tab()] }),
    new MathEq({ children: mathChildren }),
    ...(num ? [new TextRun({ children: [new Tab()], }), run(`(${num})`)] : []),
  ],
});

/* ---------- figures ---------- */
const fig = (file, widthPx, natW, natH, caption) => [
  new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { before: 120, after: 60 },
    children: [new ImageRun({
      type: "png",
      data: fs.readFileSync(path.join(imgDir, file)),
      transformation: { width: widthPx, height: Math.round(widthPx * natH / natW) },
    })],
  }),
  para(run(caption, { size: 24 }), { alignment: AlignmentType.CENTER, spacing: { after: 200 } }),
];

/* ---------- cover ---------- */
const coverLine = (left, right) => new Paragraph({
  tabStops: [{ type: TabStopType.RIGHT, position: TEXTW }],
  spacing: { after: 120, line: 360 },
  children: [run(left), new TextRun({ children: [new Tab()] }), run(right)],
});
const gap = (n = 1) => Array.from({ length: n }, () => para(run(""), { spacing: { after: 200 } }));

const cover = [
  center("МИНОБРНАУКИ РОССИИ", { size: 24 }),
  center("Федеральное государственное бюджетное образовательное учреждение", { size: 24 }),
  center("высшего образования", { size: 24 }),
  center("«МИРЭА – Российский технологический университет»", { size: 24 }),
  center("РТУ МИРЭА", { bold: true, size: 32 }),
  ...gap(1),
  center("Институт искусственного интеллекта", { size: 24 }),
  center("(наименование института, филиала)", { size: 20, italics: true }),
  center("Кафедра автоматических систем", { size: 24 }),
  center("(наименование кафедры)", { size: 20, italics: true }),
  ...gap(4),
  center("ПРАКТИЧЕСКОЕ ЗАДАНИЕ № 1", { bold: true, size: 32 }),
  center("по дисциплине «Основы цифровой фильтрации в автоматических системах»", { size: 24 }),
  center("Вариант № 19", { size: 24 }),
  ...gap(4),
  coverLine("Выполнил:", "Оськин Владислав Андреевич"),
  coverLine("Группа:", "КВБО-11-24"),
  coverLine("Проверил:", "Гурьянова Е.О.   ___________"),
  para(run("Работа представлена к защите   «____»___________ 2026 г.")),
  para(run("Работа сдана   «____»___________ 2026 г.")),
  ...gap(3),
  center("Москва 2026", { size: 24 }),
  new Paragraph({ children: [new PageBreak()] }),
];

/* ---------- intro ---------- */
const widths = [1871, 1871, 1871, 1871, 1871];
const tcell = (children, options = {}) => new TableCell({
  children: [new Paragraph({
    alignment: AlignmentType.CENTER,
    spacing: { after: 0 },
    children: Array.isArray(children) ? children : [children],
  })],
  margins: { top: 60, bottom: 60, left: 80, right: 80 },
  width: { size: widths[0], type: WidthType.DXA },
  ...options,
});
const th = (main, sub, unit) => tcell(
  [run(main), ...(main ? [new TextRun({ text: sub, font, size: 28, subScript: true })] : []), run(", " + unit)],
  { shading: { type: ShadingType.CLEAR, fill: "F2F2F2" } },
);
const paramTable = new Table({
  width: { size: widths.reduce((a, b) => a + b, 0), type: WidthType.DXA },
  columnWidths: widths,
  rows: [
    new TableRow({ children: [
      tcell(run("Параметр"), { shading: { type: ShadingType.CLEAR, fill: "F2F2F2" } }),
      th("R", "1", "Ом"), th("R", "2", "Ом"), th("C", "1", "мкФ"), th("C", "2", "мкФ"),
    ] }),
    new TableRow({ children: [
      tcell(run("Значение")),
      tcell(run("900")), tcell(run("4900")), tcell(run("1,59")), tcell(run("0,36")),
    ] }),
  ],
});

const intro = [
  body("Согласно варианту № 19 задания на курсовую работу расчёту подлежит схема 1 — пассивная RC-цепь (двухзвенная RC-цепочка). Исходная схема приведена на рис. 1, номиналы элементов — в таблице 1."),
  ...fig("scheme1_orig.png", 430, 800, 370, "Рис. 1. Заданная аналоговая пассивная цепь (схема 1)"),
  para(run("Таблица 1 — Параметры элементов схемы 1 (вариант 19)", { size: 24 }), { alignment: AlignmentType.CENTER, spacing: { after: 80 } }),
  paramTable,
  para(run(""), { spacing: { after: 80 } }),
  bodyM([
    ["Условия расчёта: нагрузка и внутреннее сопротивление генератора не учитываются (режим холостого хода, идеальный источник напряжения U). Выходное напряжение V снимается с конденсатора C"],
    ["2", { subScript: true }],
    ["."],
  ]),
];

/* ---------- 1.1 transfer function ---------- */
const s11 = [
  h1("1.1. НАХОЖДЕНИЕ ПЕРЕДАТОЧНОЙ ФУНКЦИИ"),
  bodyM([
    ["Для нахождения передаточной функции воспользуемся методом контурных токов. Выберем независимые контуры и направим контурные токи I"],
    ["1", { subScript: true }],
    [" и I"],
    ["2", { subScript: true }],
    [" по часовой стрелке (рис. 2). Сопротивления конденсаторов в операторной форме:"],
  ]),
  eq([XC1(), mr(" = "), fr([mr("1")], [C1(), mr("·p")])], "1.1"),
  eq([XC2(), mr(" = "), fr([mr("1")], [C2(), mr("·p")])], "1.2"),
  ...fig("scheme.png", 470, 1659, 881, "Рис. 2. Схема цепи с контурными токами"),
  bodyM([
    ["По второму закону Кирхгофа составим систему уравнений для контурных токов. Выходное напряжение равно напряжению на конденсаторе C"],
    ["2", { subScript: true }],
    [":"],
  ]),
  eq([mr("U = "), I1(), mr("·"), R1(), mr(" + "), rb([I1(), mr(" − "), I2()]), mr("·"), XC1()], "1.3"),
  eq([mr("0 = "), I2(), mr("·"), R2(), mr(" + "), I2(), mr("·"), XC2(), mr(" + "), rb([I2(), mr(" − "), I1()]), mr("·"), XC1()], "1.4"),
  eq([mr("V = "), I2(), mr("·"), XC2()], "1.5"),
  bodyM([["Из уравнения (1.4) выразим контурный ток I"], ["1", { subScript: true }], [":"]]),
  eq([I1(), mr(" = "), I2(), mr("·"), fr([R2(), mr(" + "), XC1(), mr(" + "), XC2()], [XC1()]), mr(" = "), I2(), mr("·"), rb([mr("1 + "), fr([C1()], [C2()]), mr(" + p·"), C1(), mr("·"), R2()])], "1.6"),
  bodyM([
    ["Подставим (1.6) в (1.3) и учтём, что по (1.5) ток I"],
    ["2", { subScript: true }],
    [" = V·p·C"],
    ["2", { subScript: true }],
    [". Тогда:"],
  ]),
  eq([mr("U = "), I2(), mr("·"), sbk([R1(), mr("·"), rb([mr("1 + "), fr([C1()], [C2()]), mr(" + p·"), C1(), mr("·"), R2()]), mr(" + "), R2(), mr(" + "), fr([mr("1")], [C2(), mr("·p")])]), mr(" =")], null),
  eq([mr("= V·"), sbk([mr("1 + p·"), rb([R1(), mr("·"), C1(), mr(" + "), rb([R1(), mr(" + "), R2()]), mr("·"), C2()]), mr(" + "), sp([mr("p")], [mr("2")]), mr("·"), R1(), mr("·"), R2(), mr("·"), C1(), mr("·"), C2()])], "1.7"),
  body("Отсюда передаточная функция цепи:"),
  eq([mr("W(p) = "), fr([mr("V(p)")], [mr("U(p)")]), mr(" = "), fr([mr("1")], [sp([mr("p")], [mr("2")]), mr("·"), R1(), mr("·"), R2(), mr("·"), C1(), mr("·"), C2(), mr(" + p·"), rb([R1(), mr("·"), C1(), mr(" + "), rb([R1(), mr(" + "), R2()]), mr("·"), C2()]), mr(" + 1")])], "1.8"),
  bodyM([
    ["Подставим номиналы элементов варианта: R"], ["1", { subScript: true }],
    ["·R"], ["2", { subScript: true }],
    ["·C"], ["1", { subScript: true }],
    ["·C"], ["2", { subScript: true }],
    [" = 900·4900·1,59·10⁻⁶·0,36·10⁻⁶ = 2,5243·10⁻⁶ с²; R"], ["1", { subScript: true }],
    ["·C"], ["1", { subScript: true }],
    [" + (R"], ["1", { subScript: true }],
    [" + R"], ["2", { subScript: true }],
    [")·C"], ["2", { subScript: true }],
    [" = 900·1,59·10⁻⁶ + 5800·0,36·10⁻⁶ = 1,431·10⁻³ + 2,088·10⁻³ = 3,519·10⁻³ с. Получаем:"],
  ]),
  eq([mr("W(p) = "), fr([mr("1")], [E("2,5243", "−6"), mr("·"), sp([mr("p")], [mr("2")]), mr(" + "), E("3,519", "−3"), mr("·p + 1")])], "1.9"),
];

/* ---------- 1.2 diff equation ---------- */
const s12 = [
  h1("1.2. ЗАПИСЬ ДИФФЕРЕНЦИАЛЬНОГО УРАВНЕНИЯ"),
  bodyM([
    ["По определению передаточной функции W(p) = x"],
    ["вых", { subScript: true }],
    ["/x"],
    ["вх", { subScript: true }],
    [". Выразим выходной сигнал и умножим обе части на знаменатель:"],
  ]),
  eq([rb([E("2,5243", "−6"), mr("·"), sp([mr("p")], [mr("2")]), mr(" + "), E("3,519", "−3"), mr("·p + 1")]), mr("·"), XV(), mr(" = "), XH()], "1.10"),
  body("Осуществим замену p = d/dt и получим дифференциальное уравнение цепи:"),
  eq([E("2,5243", "−6"), mr("·"), fr([sp([mr("d")], [mr("2")]), XV()], [mr("d"), sp([mr("t")], [mr("2")])]), mr(" + "), E("3,519", "−3"), mr("·"), fr([mr("d"), XV()], [mr("dt")]), mr(" + "), XV(), mr("(t) = "), XH(), mr("(t)")], "1.11"),
];

/* ---------- 1.3 poles ---------- */
const s13 = [
  h1("1.3. НАХОЖДЕНИЕ ПОЛЮСОВ ПЕРЕДАТОЧНОЙ ФУНКЦИИ"),
  body("Для нахождения полюсов приравняем знаменатель передаточной функции к нулю: 2,5243·10⁻⁶·p² + 3,519·10⁻³·p + 1 = 0. Дискриминант:"),
  eq([mr("D = "), sp([rb([E("3,519", "−3")])], [mr("2")]), mr(" − 4·"), E("2,5243", "−6"), mr(" = "), E("2,2862", "−6")], "1.12"),
  body("Тогда √D = 1,5120·10⁻³, и корни характеристического уравнения (полюсы):"),
  eq([sb([mr("p")], [mr("1,2")]), mr(" = "), fr([mr("−"), E("3,519", "−3"), mr(" ± "), E("1,5120", "−3")], [mr("2·"), E("2,5243", "−6")])], "1.13"),
  eq([sb([mr("p")], [mr("1")]), mr(" ≈ −397,53 "), sp([mr("с")], [mr("−1")]), mr(";   "), sb([mr("p")], [mr("2")]), mr(" ≈ −996,53 "), sp([mr("с")], [mr("−1")])], "1.14"),
  bodyM([
    ["Оба полюса вещественные, отрицательные и лежат в левой полуплоскости комплексной плоскости (p"],
    ["1", { subScript: true }],
    [" ≈ −397,53 с⁻¹, p"],
    ["2", { subScript: true }],
    [" ≈ −996,53 с⁻¹), поэтому цепь асимптотически устойчива, а переходный процесс в ней апериодический. Нулей передаточная функция не имеет (числитель постоянен). Карта нулей и полюсов приведена на рис. 3."],
  ]),
  ...fig("pzmap.png", 420, 1254, 654, "Рис. 3. Карта нулей и полюсов передаточной функции"),
];

/* ---------- 1.4 AFC, PFC, IRF ---------- */
const DW = () => [sp([rb([mr("1 − "), E("2,5243", "−6"), mr("·"), sp([mr("ω")], [mr("2")])])], [mr("2")]), mr(" + "), sp([rb([E("3,519", "−3"), mr("·ω")])], [mr("2")])];
const s14 = [
  h1("1.4. РАСЧЁТ АЧХ, ФЧХ И ИПФ"),
  body("Для получения комплексной частотной характеристики (КЧХ) подставим p = jω в выражение (1.9):"),
  eq([mr("W(jω) = "), fr([mr("1")], [rb([mr("1 − "), E("2,5243", "−6"), mr("·"), sp([mr("ω")], [mr("2")])]), mr(" + j·"), E("3,519", "−3"), mr("·ω")])], "1.15"),
  body("Домножив числитель и знаменатель на комплексно-сопряжённое знаменателю выражение, получим вещественную (ВЧХ) и мнимую (МЧХ) части КЧХ:"),
  eq([mr("P(ω) = Re W(jω) = "), fr([mr("1 − "), E("2,5243", "−6"), mr("·"), sp([mr("ω")], [mr("2")])], [mr("Δ(ω)")])], "1.16"),
  eq([mr("Q(ω) = Im W(jω) = "), fr([mr("−"), E("3,519", "−3"), mr("·ω")], [mr("Δ(ω)")])], "1.17"),
  body("где Δ(ω) — квадрат модуля знаменателя:"),
  eq([mr("Δ(ω) = "), ...DW()], "1.18"),
  body("Амплитудно-частотная характеристика (АЧХ):"),
  eq([mr("A(ω) = |W(jω)| = "), sq([sp([mr("P")], [mr("2")]), mr("(ω) + "), sp([mr("Q")], [mr("2")]), mr("(ω)")]), mr(" = "), fr([mr("1")], [sq(DW())])], "1.19"),
  body("Фазочастотная характеристика (ФЧХ):"),
  eq([mr("φ(ω) = arctg "), fr([mr("Q(ω)")], [mr("P(ω)")]), mr(" = −arctg "), rb([fr([E("3,519", "−3"), mr("·ω")], [mr("1 − "), E("2,5243", "−6"), mr("·"), sp([mr("ω")], [mr("2")])])])], "1.20"),
  body("причём при переходе частоты через значение ω = 1/√(2,5243·10⁻⁶) ≈ 629,4 рад/с, при котором вещественная часть меняет знак, учитывается квадрант аргумента (фаза монотонно изменяется от 0° до −180°)."),
  bodyM([
    ["Для нахождения импульсной переходной функции разложим W(p) на простые дроби, используя полюсы p"],
    ["1", { subScript: true }],
    [" = −397,53 с⁻¹ и p"],
    ["2", { subScript: true }],
    [" = −996,53 с⁻¹:"],
  ]),
  eq([mr("W(p) = "), fr([mr("1")], [E("2,5243", "−6"), rb([mr("p + 397,53")]), rb([mr("p + 996,53")])]), mr(" = 396152·"), rb([fr([mr("A")], [mr("p + 397,53")]), mr(" + "), fr([mr("B")], [mr("p + 996,53")])])], "1.21"),
  body("Из равенства 1 = A·(p + 996,53) + B·(p + 397,53): при p = −397,53 получаем A = 1/599,00 = 1,6694·10⁻³; при p = −996,53 получаем B = −1,6694·10⁻³. Тогда:"),
  eq([mr("W(p) = "), fr([mr("661,36")], [mr("p + 397,53")]), mr(" − "), fr([mr("661,36")], [mr("p + 996,53")])], "1.22"),
  body("Обратное преобразование Лапласа даёт импульсную переходную функцию (ИПФ):"),
  eq([mr("h(t) = 661,36·"), sp([mr("e")], [mr("−397,53·t")]), mr(" − 661,36·"), sp([mr("e")], [mr("−996,53·t")]), mr(",  t ≥ 0")], "1.23"),
];

/* ---------- 1.5 plots ---------- */
const s15 = [
  h1("1.5. ПОСТРОЕНИЕ ГРАФИКОВ АЧХ, ФЧХ И ИПФ"),
  body("По аналитическим выражениям (1.19), (1.20) и (1.23) построены графики АЧХ, ФЧХ и ИПФ; для проверки те же характеристики рассчитаны встроенными функциями bode и impulse."),
  ...fig("achh.png", 620, 2173, 694, "Рис. 4. Графики АЧХ, построенные по аналитическому выражению и с помощью встроенной функции"),
  ...fig("fchh.png", 620, 2173, 694, "Рис. 5. Графики ФЧХ, построенные по аналитическому выражению и с помощью встроенной функции"),
  ...fig("ipf.png", 620, 2173, 694, "Рис. 6. Графики ИПФ, построенные по аналитическому выражению и с помощью встроенной функции"),
  body("Как показывают результаты, графики, полученные на основе аналитических выражений, полностью совпадают с графиками, построенными с использованием встроенных функций, что подтверждает корректность выполненных вычислений."),
];

/* ---------- 1.6 filter type ---------- */
const s16 = [
  h1("1.6. ОПРЕДЕЛЕНИЕ ТИПА ФИЛЬТРА ПО ЧАСТОТНОЙ ИЗБИРАТЕЛЬНОСТИ"),
  body("АЧХ цепи максимальна на нулевой частоте: A(0) = 1 (постоянная составляющая проходит без ослабления) и монотонно убывает с ростом частоты: A(ω) → 0 при ω → ∞, причём в области высоких частот спад составляет −40 дБ/дек, что соответствует второму порядку знаменателя. Фазовый сдвиг при этом изменяется от 0° до −180°."),
  body("Следовательно, заданная цепь является фильтром нижних частот (ФНЧ) второго порядка апериодического типа. Частота среза по уровню 1/√2 ≈ 0,707 составляет ωс ≈ 351 рад/с (fс ≈ 56 Гц)."),
];

/* ---------- listing ---------- */
const codeLines = T`clear; clc; close all;
pkg load control

% Исходные данные (вариант 19, схема 1)
R1 = 900;       % Ом
R2 = 4900;      % Ом
C1 = 1.59e-6;   % Ф
C2 = 0.36e-6;   % Ф

% Передаточная функция W(p) = 1 / (a2*p^2 + a1*p + 1)
a2 = R1*R2*C1*C2;          % 2.5243e-06 с^2
a1 = R1*C1 + (R1+R2)*C2;   % 3.5190e-03 с
num = [1];
den = [a2, a1, 1];
sys = tf(num, den);

% Полюсы передаточной функции
poles = roots(den)   % p1 = -397.53; p2 = -996.53

% Карта нулей и полюсов
figure;
plot(real(poles), imag(poles), 'rx', 'MarkerSize', 12, 'LineWidth', 2);
grid on; xlabel('Re(p)'); ylabel('Im(p)');
title('Карта нулей и полюсов');

% АЧХ и ФЧХ
w = logspace(0, 5, 1000);   % диапазон частот от 1 до 100000 рад/с

% Аналитические выражения
A_analit = 1 ./ sqrt((1 - a2*w.^2).^2 + (a1*w).^2);
phi_analit = -atan2(a1*w, 1 - a2*w.^2) * 180/pi;

% Расчёт встроенными функциями
[mag_sys, phase_sys, w_sys] = bode(sys, w);
mag_sys = squeeze(mag_sys);
phase_sys = squeeze(phase_sys);

figure('Name', 'АЧХ');
subplot(1, 2, 1);
semilogx(w, A_analit, 'b-', 'LineWidth', 2);
grid on; title('АЧХ (аналитически)');
xlabel('\\omega, рад/с'); ylabel('A(\\omega)');

subplot(1, 2, 2);
semilogx(w_sys, mag_sys, 'r-', 'LineWidth', 2);
grid on; title('АЧХ (встроенная функция bode)');
xlabel('\\omega, рад/с'); ylabel('A(\\omega)');

figure('Name', 'ФЧХ');
subplot(1, 2, 1);
semilogx(w, phi_analit, 'b-', 'LineWidth', 2);
grid on; title('ФЧХ (аналитически)');
xlabel('\\omega, рад/с'); ylabel('\\phi(\\omega), град');

subplot(1, 2, 2);
semilogx(w_sys, phase_sys, 'r-', 'LineWidth', 2);
grid on; title('ФЧХ (встроенная функция bode)');
xlabel('\\omega, рад/с'); ylabel('\\phi(\\omega), град');

% ИПФ: h(t) = K*(exp(p1*t) - exp(p2*t))
t = linspace(0, 0.012, 1000);
p1 = -397.53; p2 = -996.53; K = 661.36;
h_analit = K*(exp(p1*t) - exp(p2*t));

[y_sys, t_sys] = impulse(sys, t);

figure('Name', 'ИПФ');
subplot(1, 2, 1);
plot(t, h_analit, 'b-', 'LineWidth', 2);
grid on; title('ИПФ (аналитически)'); xlabel('t, с'); ylabel('h(t)');

subplot(1, 2, 2);
plot(t_sys, y_sys, 'r-', 'LineWidth', 2);
grid on; title('ИПФ (встроенная функция impulse)');
xlabel('t, с'); ylabel('h(t)');`.split("\n");

const codeFont = { ascii: "Courier New", hAnsi: "Courier New", cs: "Courier New", eastAsia: "SimSun" };
const listing = [
  h1("ЛИСТИНГ КОДА"),
  ...codeLines.map((line) => new Paragraph({
    spacing: { after: 0, line: 240 },
    children: [new TextRun({ text: line === "" ? " " : line, font: codeFont, size: 20 })],
  })),
];

/* ---------- sources ---------- */
const sources = [
  h1("СПИСОК ИСПОЛЬЗОВАННЫХ ИСТОЧНИКОВ"),
  body("Основы компьютерного моделирования радиоэлектронных систем и сигналов : учебное пособие / С. А. Кудряков, Е. В. Соболев, Е. А. Рубцов [и др.]. — Санкт-Петербург : СПБГУ ГА им. А.А. Новикова, 2020. — 301 с. — ISBN 978-5-6043133-2-9. — Текст : электронный // Лань : электронно-библиотечная система. — URL: https://e.lanbook.com/book/179209 (дата обращения: 22.11.2026). — Режим доступа: для авториз. пользователей.", { indent: { firstLine: 0 } }),
];

/* ---------- document ---------- */
const doc = new Document({
  features: { updateFields: false },
  sections: [{
    properties: {
      titlePage: true,
      page: {
        margin: { top: 1134, bottom: 1134, left: 1701, right: 850 },
      },
    },
    footers: {
      default: new Footer({
        children: [new Paragraph({
          alignment: AlignmentType.CENTER,
          children: [new TextRun({ children: [PageNumber.CURRENT], font, size: 24 })],
        })],
      }),
      first: new Footer({ children: [para(run(""))] }),
    },
    children: [
      ...cover,
      ...intro,
      ...s11, ...s12, ...s13, ...s14, ...s15, ...s16,
      ...listing,
      ...sources,
    ],
  }],
});

fs.writeFileSync(outputPath, await Packer.toBuffer(doc));
