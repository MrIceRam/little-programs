import matplotlib.pyplot as plt
import numpy as np

# Данные из таблицы (запятые заменены на точки для Python)
I_vh = np.array([0.05, 0.1, 0.15, 0.2, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6])

U_vyh_dc = np.array([0.05, 0.1, 0.15, 0.19, 0.25, 0.3, 0.35, 0.4, 0.45, 0.5, 0.55, 0.6]) # постоянный
U_vyh_ac = np.array([0.05, 0.1, 0.149, 0.198, 0.251, 0.299, 0.35, 0.401, 0.449, 0.5, 0.551, 0.6]) # переменный

# Настройка размера графика
plt.figure(figsize=(10, 7))

# Построение графиков
# Кривая 1: Постоянный ток (DC) - синяя линия с кружками
plt.plot(I_vh, U_vyh_dc, marker='o', linestyle='-', color='blue', linewidth=2, 
         label='1 — постоянный ток (DC, f = 0 Гц)')

# Кривая 2: Переменный ток (AC) - красная пунктирная линия с квадратиками
plt.plot(I_vh, U_vyh_ac, marker='s', linestyle='--', color='red', linewidth=2, 
         label='2 — переменный ток (AC, f = 50 Гц)')

# Добавление заголовка и подписей осей
plt.title('График 1. Статическая характеристика измерительного шунта \(U_{вых} = f(I_{вх})\)', 
          fontsize=14, fontweight='bold', pad=15)
plt.xlabel('Входной ток \(I_{вх}\), [мА]', fontsize=12)
plt.ylabel('Выходное напряжение \(U_{вых}\), [В]', fontsize=12)

# Настройка сетки (имитация миллиметровой бумаги)
# Основная сетка
plt.grid(which='major', color='black', linestyle='-', linewidth=0.7, alpha=0.6)
# Дополнительная (минорная) сетка
plt.minorticks_on()
plt.grid(which='minor', color='gray', linestyle=':', linewidth=0.5, alpha=0.5)

# Настройка шага сетки (чтобы было похоже на миллиметровку)
plt.xticks(np.arange(0, 0.7, 0.05))
plt.yticks(np.arange(0, 0.7, 0.05))

# Ограничение осей (чтобы график начинался от 0)
plt.xlim(0, 0.65)
plt.ylim(0, 0.65)

# Расположение легенды
plt.legend(loc='upper left', fontsize=11)

# Показать график
plt.tight_layout()
plt.show()

# Если нужно сохранить график в картинку, раскомментируйте строку ниже:
# plt.savefig('shunt_characteristic.png', dpi=300)