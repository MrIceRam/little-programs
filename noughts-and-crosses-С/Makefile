# ===================== Makefile для "Крестики-нолики" =====================
#
#   make          собрать программу (то же, что make all)
#   make run      собрать и запустить
#   make debug    собрать с отладочной информацией (для gdb)
#   make test     собрать и запустить тесты (фреймворк Unity)
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
TEST_DIR  = test
UNITY_DIR = $(TEST_DIR)/unity
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

# Для тестов нужны все .o, кроме того, где лежит main() программы
GAME_OBJS   = $(filter-out $(BUILD_DIR)/$(NAME).o,$(OBJS))
TEST_SRCS   = $(wildcard $(TEST_DIR)/*.c)
TEST_OBJS   = $(patsubst $(TEST_DIR)/%.c,$(BUILD_DIR)/test/%.o,$(TEST_SRCS))               $(BUILD_DIR)/test/unity.o
TEST_TARGET = $(BUILD_DIR)/test_$(NAME)$(EXE)
DEPS       += $(TEST_OBJS:.o=.d)

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

# ----------------------------- Тесты -------------------------------------

# Тесты: test/X.c и unity.c -> build/test/X.o, затем вместе с логикой игры
# в один build/test_tictactoe.exe. -I — где искать game.h и unity.h
$(TEST_TARGET): $(TEST_OBJS) $(GAME_OBJS)
	$(CC) $^ -o $@ $(LDFLAGS)

$(BUILD_DIR)/test/%.o: $(TEST_DIR)/%.c | $(BUILD_DIR)/test
	$(CC) $(CFLAGS) -I$(SRC_DIR) -I$(UNITY_DIR) -MMD -MP -c $< -o $@

$(BUILD_DIR)/test/unity.o: $(UNITY_DIR)/unity.c | $(BUILD_DIR)/test
	$(CC) $(CFLAGS) -I$(UNITY_DIR) -MMD -MP -c $< -o $@

$(BUILD_DIR)/test:
	mkdir -p $@

# Exe возвращает число упавших тестов, поэтому make сам сообщит об ошибке
test: $(TEST_TARGET)
	$(call FIXPATH,$(TEST_TARGET))

run: all
	$(call FIXPATH,$(TARGET))

# Пересобрать с -g (отладка) и без оптимизаций
debug: CFLAGS = -Wall -Wextra -std=c11 -g -O0
debug: clean all

clean:
	$(RMDIR)

# Эти цели — не файлы, а просто имена команд
.PHONY: all run debug clean test

# Подключить .d-файлы (минус = не ругаться, если их ещё нет)
-include $(DEPS)
