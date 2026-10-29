Unable to start debugging. Unexpected GDB output from command "-environment-cd D:\Programs\IT\little-programs\noughts-and-crosses-C\.vscode".
D:\Programs\IT\little-programs\noughts-and-crosses-C\.vscode: No such file or directory.
\



pacman -Syu
Шаг 3. Установите инструменты
Теперь в том же терминале установите нужные компоненты:
Компилятор GCC:
pacman -S mingw-w64-ucrt-x86_64-gcc
. coddy.tech (https://coddy.tech/docs/ru/c/install-c)metanit.com (https://metanit.com/c/tutorial/1.2.php)
Отладчик GDB:
pacman -S mingw-w64-ucrt-x86_64-gdb
. coddy.tech (https://coddy.tech/docs/ru/c/install-c)bytegoblin.io (https://bytegoblin.io/blog/how-to-install-gcc-and-gdb-on-windows-using-msys2-tutorial)
Утилита
make
:
pacman -S make
. coddy.tech (https://coddy.tech/docs/ru/c/install-c)
После установки в папке
C:\msys64\ucrt64\bin
будут лежать все нужные исполняемые файлы (включая
gcc.exe
,
gdb.exe
и