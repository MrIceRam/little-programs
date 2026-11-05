import numpy as np
import matplotlib.pyplot as plt
from scipy import signal

# 1. Ваш аналитический результат (по формуле)
def w_analytical(t):
    return 5 * np.exp(-t) - 5 * np.exp(-2*t)

num = [5]
den = [1, 3, 2]

# Создаем модель системы из передаточной функции
system = signal.TransferFunction(num, den)

# Задаем временной интервал (от 0 до 5 секунд, 500 точек)
t_values = np.linspace(0, 5, 500)

# Получаем численную реакцию системы на импульс (это и есть обратное преобразование Лапласа)
# Функция возвращает время и значения амплитуды
t_num, y_numerical = signal.impulse(system, T=t_values)

# Считаем значения по вашей формуле
y_analytical = w_analytical(t_values)

# 3. Построение графика
plt.figure(figsize=(10, 6))

# Синяя жирная линия - ваш ответ по формуле
plt.plot(t_values, y_analytical, label='Аналитический оригинал: \(5e^{-t} - 5e^{-2t}\)', 
         color='blue', linewidth=4, alpha=0.6)

# Красная пунктирная линия - машинный расчет из исходной дроби W(s)
plt.plot(t_num, y_numerical, label='Точный расчет Python (через scipy.signal)', 
         color='red', linestyle='--', linewidth=2)

plt.title('Проверка обратного преобразования Лапласа (Идеальное совпадение)')
plt.xlabel('Время t (сек)')
plt.ylabel('Амплитуда w(t)')
plt.legend()
plt.grid(True)
plt.show()