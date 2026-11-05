clear; clc; close all;

% папка для графиков (рядом с этим файлом)
OUT = fullfile(fileparts(mfilename('fullpath')), 'скриншоты');
if ~exist(OUT, 'dir'), mkdir(OUT); end
% размер картинки задаётся через PaperPosition (в дюймах, 100 пикселей = 1 дюйм)
savefig = @(name) print(gcf, fullfile(OUT, name), '-dpng', '-r150');
newfig  = @(w, h) figure('Visible', 'off', 'PaperUnits', 'inches', 'PaperPosition', [0 0 w/100 h/100]);
set(0, 'DefaultAxesFontSize', 10, 'DefaultTextFontSize', 10);

T  = 10; % период, мс
W0 = 2*pi/T; % основная круговая частота, рад/мс

% одиночный импульс: на каждом участке своя формула, вне импульса ноль
pulse = @(t) 2*(t+1).*(t >= -1 & t < 0) + 1.*(t >= 0 & t < 0.5);
% периодический сигнал: mod приводит любое t в базовый период [-1; 9)
s_per = @(t) pulse(mod(t+1, T) - 1);

t_r = linspace(-1, 0, 20001); % рампа
t_p = linspace(0, 0.5, 20001); % полка
x_r = 2*(t_r + 1); % значения сигнала на рампе (в t = 0 берём 2 В, предел слева)
x_p = ones(size(t_p)); % значения сигнала на полке

%%Задание 1.1
% коэффициенты ряда Фурье численно (метод трапеций), n = 0..10
NMAX = 10;
a = zeros(1, NMAX+1);  b = zeros(1, NMAX+1);
for n = 0:NMAX
    a(n+1) = 2/T*(trapz(t_r, x_r.*cos(n*W0*t_r)) + trapz(t_p, x_p.*cos(n*W0*t_p)));
    b(n+1) = 2/T*(trapz(t_r, x_r.*sin(n*W0*t_r)) + trapz(t_p, x_p.*sin(n*W0*t_p)));
end
A   = sqrt(a.^2 + b.^2);  A(1) = abs(a(1))/2; % для n = 0 - постоянная составляющая a0/2
phi = atan2(-b, a);       phi(1) = 0; % s(t) = a0/2 + sum A_n cos(n W0 t + phi_n)
A(abs(A) < 1e-9) = 0;     phi(A == 0) = 0; % у нулевой гармоники фаза не определена
a(abs(a) < 1e-9) = 0;     b(abs(b) < 1e-9) = 0; % убираем «-0.00000» в таблице

% те же коэффициенты по выведенным формулам (для проверки)
n  = 1:NMAX;  th = n*W0;                        % theta_n = n*pi/5
a_an = 2/T*(2*(1 - cos(th))./th.^2 + sin(th/2)./th);
b_an = 2/T*(2*(sin(th) - th)./th.^2 + (1 - cos(th/2))./th);
err_coef = max(abs([a_an - a(2:end), b_an - b(2:end), a(1) - 0.3]));

fprintf('Задание 1.1. Коэффициенты ряда Фурье (T = 10 мс)\n');
fprintf('  n      a_n       b_n       A_n   phi_n,рад  phi_n,град\n');
for k = 0:NMAX
    fprintf('%3d %9.5f %9.5f %9.5f %9.4f %9.2f\n', k, a(k+1), b(k+1), A(k+1), phi(k+1), phi(k+1)*180/pi);
end
fprintf('Расхождение численного расчёта с формулами: %.2e\n', err_coef);

% --- п.1: график периодического сигнала (три периода)
t = linspace(-12, 22, 34001);
s = s_per(t);
newfig(1000, 360); plot(t, s, 'b', 'LineWidth', 1.2); grid on;
xlim([-12 22]); xlabel('t, мс'); ylabel('s(t), В'); title('Периодический сигнал s(t), вариант 19 (T = 10 мс)');
savefig('fig01_signal.png');

% --- п.3: амплитудная и фазовая спектральные диаграммы
newfig(700, 380); stem(0:NMAX, A, 'filled'); grid on; xlim([-0.5 NMAX+0.5]);
xlabel('n'); ylabel('A_n, В'); title('Амплитудный спектр A_n');
savefig('fig02_amp_spectrum.png');
newfig(700, 380); stem(0:NMAX, phi, 'filled'); grid on; xlim([-0.5 NMAX+0.5]);
xlabel('n'); ylabel('\phi_n, рад'); title('Фазовый спектр \phi_n');
savefig('fig03_phase_spectrum.png');

% --- п.4, п.5: аппроксимация N гармониками и сигнал ошибки
P = (trapz(t_r, x_r.^2) + trapz(t_p, x_p.^2))/T; % средняя мощность сигнала
Ns = [5 10 20];
clr = {[0.85 0.33 0.10], [0.13 0.55 0.13], [0.80 0.10 0.10]};
in_period = (t >= -1 & t < 9);
xz = linspace(-2, 1.5, 4001);  sz = s_per(xz); % окно для крупного плана
xN_zoom = zeros(numel(Ns), numel(xz));
for i = 1:numel(Ns)
    N = Ns(i);
    aN = zeros(1, N+1);  bN = zeros(1, N+1);
    for k = 0:N
        aN(k+1) = 2/T*(trapz(t_r, x_r.*cos(k*W0*t_r)) + trapz(t_p, x_p.*cos(k*W0*t_p)));
        bN(k+1) = 2/T*(trapz(t_r, x_r.*sin(k*W0*t_r)) + trapz(t_p, x_p.*sin(k*W0*t_p)));
    end
    % частичная сумма ряда: постоянная составляющая + N гармоник
    xN = aN(1)/2*ones(size(t));
    xN_zoom(i, :) = aN(1)/2;
    for k = 1:N
        xN = xN + aN(k+1)*cos(k*W0*t) + bN(k+1)*sin(k*W0*t);
        xN_zoom(i, :) = xN_zoom(i, :) + aN(k+1)*cos(k*W0*xz) + bN(k+1)*sin(k*W0*xz);
    end
    eps_N = s - xN;% сигнал ошибки
    PN = aN(1)^2/4 + 0.5*sum(aN(2:end).^2 + bN(2:end).^2);   % мощность N гармоник (Парсеваль)
    fprintf('N = %2d: СКО ошибки = %.4f В, max|eps| = %.4f В, P_N/P = %.1f %%\n', N, sqrt(mean(eps_N(in_period).^2)), max(abs(eps_N)), 100*PN/P);

    newfig(1000, 380); plot(t, s, 'b', t, xN, 'Color', clr{i}, 'LineWidth', 1.2); grid on;
    xlim([-12 22]); ylim([-0.5 2.6]); xlabel('t, мс'); ylabel('В');
    legend('исходный s(t)', sprintf('s^*_{%d}(t)', N), 'Location', 'north', 'Orientation', 'horizontal');
    title(sprintf('Аппроксимация рядом Фурье, N = %d', N));
    savefig(sprintf('fig%02d_approx_N%d.png', 3 + i, N));

    newfig(1000, 340); plot(t, eps_N, 'Color', clr{i}, 'LineWidth', 1.1); grid on;
    xlim([-12 22]); xlabel('t, мс'); ylabel('\epsilon(t), В');
    title(sprintf('Сигнал ошибки \\epsilon(t) = s(t) - s^*_{%d}(t)', N));
    savefig(sprintf('fig%02d_error_N%d.png', 6 + i, N));
end
fprintf('Мощность сигнала P = %.5f В^2\n', P);

% крупный план одного импульса: все три аппроксимации на одном графике
newfig(900, 400); plot(xz, sz, 'b', 'LineWidth', 2); hold on;
for i = 1:numel(Ns), plot(xz, xN_zoom(i, :), 'Color', clr{i}, 'LineWidth', 1.2); end
hold off; grid on; xlabel('t, мс'); ylabel('В');
legend('s(t)', 'N = 5', 'N = 10', 'N = 20', 'Location', 'northwest'); title('Сравнение аппроксимаций на одном импульсе');
savefig('fig10_approx_zoom.png');

%%Задание 1.2
% --- п.1: одиночный импульс
tp = linspace(-4, 4, 8001);
newfig(900, 360); plot(tp, pulse(tp), 'b', 'LineWidth', 1.2); grid on;
xlabel('t, мс'); ylabel('x(t), В'); title('Одиночный импульс x(t), вариант 19');
savefig('fig11_pulse.png');

% --- п.2: спектральная характеристика X(jw) по формуле прямого преобразования Фурье
t_r2 = linspace(-1, 0, 3001);   t_p2 = linspace(0, 0.5, 3001);
x_r2 = 2*(t_r2 + 1);
WC = 20; % интервал [0, wc], рад/мс
w  = linspace(0, WC, 4001);
X  = zeros(size(w));
for k = 1:numel(w)
    X(k) = trapz(t_r2, x_r2.*exp(-1i*w(k)*t_r2)) + trapz(t_p2, exp(-1i*w(k)*t_p2));
end
% та же характеристика по аналитической формуле (для проверки и для восстановления)
X_an = @(ww) (ww == 0)*1.5 + (ww ~= 0).*( ...
        2*(1 + 1i*ww - exp(1i*ww))./(ww.^2 + (ww == 0)) + (1 - exp(-0.5i*ww))./(1i*ww + (ww == 0)) );
fprintf('\nЗадание 1.2. X(0) = %.4f В мс, расхождение с формулой: %.2e\n', real(X(1)), max(abs(X - X_an(w))));

newfig(900, 380); plot(w, abs(X), 'b', 'LineWidth', 1.2); grid on;
xlabel('\omega, 10^3 рад/с'); ylabel('X(\omega), В мс');
title('Амплитудная спектральная характеристика X(\omega)');
savefig('fig12_X_amp.png');
newfig(900, 380); plot(w, angle(X), 'r', 'LineWidth', 1.2); grid on;
xlabel('\omega, 10^3 рад/с'); ylabel('\phi(\omega), рад');
title('Фазовая спектральная характеристика \phi(\omega)');
savefig('fig13_X_phase.png');
newfig(800, 400); plot(real(X), -imag(X), 'b', real(X(1)), -imag(X(1)), 'ko', 'LineWidth', 1.2, 'MarkerFaceColor', 'k'); grid on;
text(real(X(1)) - 0.2, -imag(X(1)) + 0.04, '\omega = 0');
xlabel('a(\omega), В мс'); ylabel('-b(\omega), В мс');
title('Годограф X(j\omega), \omega = 0...20 10^3 рад/с');
savefig('fig14_hodograph.png');

% восстановление по обратному преобразованию (формула 2.15)
% x(t) = 1/pi * int_0^wc [a(w) cos(wt) + b(w) sin(wt)] dw
tr = linspace(-3, 3, 1201);
x_true = pulse(tr);
wcs = [20 5 100];
for i = 1:numel(wcs)
    wc = wcs(i);
    ww = 0:0.002:wc; % мелкий шаг по частоте
    Xw = X_an(ww);
    aw = real(Xw);  bw = -imag(Xw);  % X(jw) = a(w) - j b(w)
    xr = zeros(size(tr));
    for k = 1:numel(tr)
        xr(k) = trapz(ww, aw.*cos(ww*tr(k)) + bw.*sin(ww*tr(k)))/pi;
    end
    fprintf('wc = %3g 10^3 рад/с: СКО = %.4f В, max x_в = %.3f В\n', wc, sqrt(mean((xr - x_true).^2)), max(xr));
    newfig(900, 380); plot(tr, x_true, 'b', tr, xr, 'r', 'LineWidth', 1.2); grid on;
    xlabel('t, мс'); ylabel('В'); legend('исходный x(t)', 'восстановленный x_{в}(t)');
    title(sprintf('Восстановление сигнала, интервал [0; %g 10^3] рад/с', wc));
    savefig(sprintf('fig%d_restore_wc%d.png', 14 + i, wc));
end

% --- дополнительные проверки
E_t = trapz(t_r, x_r.^2) + trapz(t_p, x_p.^2); % энергия импульса во времени
wE  = linspace(1e-6, 2000, 2000001);
E_w = trapz(wE, abs(X_an(wE)).^2)/pi; % энергия по спектру (теорема Рэлея)
link = max(abs((a(2:end) - 1i*b(2:end)) - 2*X_an(n*W0)/T));   % a_n - j b_n = 2X(jnW0)/T
fprintf('Энергия: по времени %.4f, по спектру %.4f В^2 мс\n', E_t, E_w);
fprintf('Проверка a_n - j b_n = 2X(jnW0)/T: расхождение %.2e\n', link);
