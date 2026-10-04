import pyautogui
import time
import random

print("Скрипт запущен. Переключитесь на окно с игрой!")
print("Для остановки нажмите Ctrl + C в терминале.")

# Пауза 5 секунд, чтобы вы успели открыть окно игры
time.sleep(10)


try:
    while True:
        # Нажимаем 'w'
        pyautogui.keyDown('w')
        time.sleep(0.1)
        pyautogui.keyUp('w')
        
        # Небольшая пауза между нажатиями
        time.sleep(1)
        
        # Нажимаем 's'
        pyautogui.keyDown('s')
        time.sleep(9999)
        pyautogui.keyUp('s')
        
        # Ждем от 25 до 40 секунд перед следующим циклом
        sleep_time = random.randint(2, 4)
        time.sleep(sleep_time)
        
except KeyboardInterrupt:
    print("\nСкрипт успешно остановлен.")
