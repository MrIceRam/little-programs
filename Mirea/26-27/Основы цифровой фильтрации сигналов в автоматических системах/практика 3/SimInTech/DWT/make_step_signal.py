# Практическая работа 3, часть 2, задание 4.2, вариант 19
# Ступенчатая функция (единичный скачок): x(t) = 0 при t < t0, x(t) = A при t >= t0
# A = 1, t0 = 0.5 с, N = 128 (длительность 1 с, шаг 1/128 с)
# Формат файла как у демо-примера data\signal.dat: в каждой строке
# время и N значений сигнала через табуляцию (блок "Из файла" выдаёт вектор)
import os
import numpy as np

A = 1.0
t0 = 0.5
N = 128
t = np.arange(N) / N
x = np.where(t >= t0, A, 0.0)

papka = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'data')
os.makedirs(papka, exist_ok=True)
stroka = '\t'.join('%g' % v for v in x)
with open(os.path.join(papka, 'signal.dat'), 'w', newline='\n') as f:
    for k in range(11):                  # время 0..10 с, сигнал один и тот же
        f.write('%d\t%s\n' % (k, stroka))
print('N = %d, нулей: %d, единиц: %d, скачок на отсчёте %d (t = %.3f c)'
      % (N, np.sum(x == 0), np.sum(x == 1), np.argmax(x) + 1, t[np.argmax(x)]))
