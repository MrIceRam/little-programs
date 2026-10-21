#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include "board.h"

#define HUMAN_MARK    'X'
#define COMPUTER_MARK 'O'

/* Рисует поле. Пустые клетки показываются их номерами 1..9. */
static void print_board(const Board *b) {
    printf("\n");
    for (int row = 0; row < 3; row++) {
        for (int col = 0; col < 3; col++) {
            int pos = row * 3 + col;
            char cell = b->cells[pos];
            if (cell == EMPTY_CELL) {
                cell = (char)('1' + pos);
            }
            printf(" %c ", cell);
            if (col < 2) {
                printf("|");
            }
        }
        printf("\n");
        if (row < 2) {
            printf("---+---+---\n");
        }
    }
    printf("\n");
}

static bool game_over(const Board *b) {
    return board_winner(b) != EMPTY_CELL || board_is_full(b);
}

/* Спрашивает ход у человека, пока он не введёт свободную клетку.
 * Возвращает индекс 0..8, или -1 если ввод закончился (Ctrl+D). */
static int read_human_move(const Board *b) {
    char line[64];

    for (;;) {
        printf("Твой ход (1-9): ");
        if (fgets(line, sizeof line, stdin) == NULL) {
            return -1;
        }

        char *end = NULL;
        long number = strtol(line, &end, 10);
        if (end == line || (*end != '\n' && *end != '\0')) {
            printf("Введи число от 1 до 9.\n");
            continue;
        }

        int pos = (int)number - 1;
        if (!board_is_free(b, pos)) {
            printf("Эта клетка недоступна, выбери другую.\n");
            continue;
        }
        return pos;
    }
}

static void print_result(const Board *b) {
    char winner = board_winner(b);
    if (winner == HUMAN_MARK) {
        printf("Ты победил!\n");
    } else if (winner == COMPUTER_MARK) {
        printf("Победил компьютер.\n");
    } else {
        printf("Ничья.\n");
    }
}

int main(void) {
    Board board;
    board_init(&board);
    print_board(&board);

    while (!game_over(&board)) {
        int move = read_human_move(&board);
        if (move < 0) {
            printf("\nВыход из игры.\n");
            return 0;
        }
        board_place(&board, move, HUMAN_MARK);
        print_board(&board);
        if (game_over(&board)) {
            break;
        }

        int ai_move = board_best_move(&board, COMPUTER_MARK, HUMAN_MARK);
        board_place(&board, ai_move, COMPUTER_MARK);
        printf("Компьютер ходит в клетку %d.\n", ai_move + 1);
        print_board(&board);
    }

    print_result(&board);
    return 0;
}
