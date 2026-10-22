# ===================== Makefile для "Крестики-нолики" =====================
#
#   make          собрать программу (то же, что make all)
#   make run      собрать и запустить
#   make debug    собрать с отладочной информацией (для gdb)
#   make clean    удалить всё собранное (папку build)
#
# Правило в Makefile выглядит так:
#
#   цель: зависимости
#   <TAB>команда
#
# make запускает команду, только если цели ещё нет или какая-то
# зависимость новее неё. Отступ перед командой — обязательно TAB, не пробелы.

# ----------------------------- Настройки ---------------------------------

CC      = gcc
CFLAGS  = -Wall -Wextra -std=c11 -O2
LDFLAGS =

SRC_DIR   = src
BUILD_DIR = build
NAME      = tictactoe

# ------------------------- Различия Windows / Linux ----------------------
# Под MSYS2 make использует свою оболочку sh, поэтому команды и так Unix-вида.
# SHELL = cmd.exe здесь ставить НЕЛЬЗЯ.

ifeq ($(OS),Windows_NT)
    EXE = .exe
else
    EXE =
endif

MKDIR   = mkdir -p $(BUILD_DIR)
RMDIR   = rm -rf $(BUILD_DIR)
FIXPATH = $1

# ----------------------------- Файлы -------------------------------------

# Все .c из src/ (новый файл в src/ подхватится сам)
SRCS   = $(wildcard $(SRC_DIR)/*.c)
# src/foo.c -> build/foo.o
OBJS   = $(patsubst $(SRC_DIR)/%.c,$(BUILD_DIR)/%.o,$(SRCS))
# build/foo.d — списки .h, от которых зависит каждый .o (создаёт gcc)
DEPS   = $(OBJS:.o=.d)
TARGET = $(BUILD_DIR)/$(NAME)$(EXE)

# ----------------------------- Правила -----------------------------------

# Первая цель в файле — цель по умолчанию (просто "make")
all: $(TARGET)

# Компоновка: все .o -> один .exe
#   $@ = имя цели, $^ = все зависимости
$(TARGET): $(OBJS)
	$(CC) $^ -o $@ $(LDFLAGS)

# Компиляция: каждый src/X.c -> build/X.o
#   $< = первая зависимость
#   "| $(BUILD_DIR)" — папка должна существовать, но её дата не важна
#   -MMD -MP — gcc заодно пишет build/X.d с зависимостями от .h
$(BUILD_DIR)/%.o: $(SRC_DIR)/%.c | $(BUILD_DIR)
	$(CC) $(CFLAGS) -MMD -MP -c $< -o $@

$(BUILD_DIR):
	$(MKDIR)

run: all
	$(call FIXPATH,$(TARGET))

# Пересобрать с -g (отладка) и без оптимизаций
debug: CFLAGS = -Wall -Wextra -std=c11 -g -O0
debug: clean all

clean:
	$(RMDIR)

# Эти цели — не файлы, а просто имена команд
.PHONY: all run debug clean

# Подключить .d-файлы (минус = не ругаться, если их ещё нет)
-include $(DEPS)
