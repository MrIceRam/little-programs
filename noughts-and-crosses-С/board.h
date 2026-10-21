#ifndef BOARD_H
#define BOARD_H

#include <stdbool.h>

#define BOARD_SIZE 9
#define EMPTY_CELL ' '

/* Игровое поле 3x3, хранится как одномерный массив из 9 клеток.
 * Индексы клеток:
 *   0 | 1 | 2
 *   3 | 4 | 5
 *   6 | 7 | 8
 */
typedef struct {
    char cells[BOARD_SIZE];
} Board;

/* Делает все клетки пустыми. */
void board_init(Board *b);

/* true, если клетка pos (0..8) существует и пуста. */
bool board_is_free(const Board *b, int pos);

/* Ставит фишку player ('X' или 'O') в клетку pos.
 * Возвращает false, если ход невозможен. */
bool board_place(Board *b, int pos, char player);

/* Возвращает 'X' или 'O', если есть три в ряд, иначе EMPTY_CELL. */
char board_winner(const Board *b);

/* true, если свободных клеток не осталось. */
bool board_is_full(const Board *b);

/* Лучший ход для компьютера (индекс 0..8).
 * Возвращает -1, если ходов нет. */
int board_best_move(const Board *b, char computer, char human);

#endif /* BOARD_H */
