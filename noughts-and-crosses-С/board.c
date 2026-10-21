#include <limits.h>
#include "board.h"

/* Все выигрышные линии: три строки, три столбца и две диагонали. */
static const int WIN_LINES[8][3] = {
    {0, 1, 2}, {3, 4, 5}, {6, 7, 8},
    {0, 3, 6}, {1, 4, 7}, {2, 5, 8},
    {0, 4, 8}, {2, 4, 6},
};

static const int WIN_LINES_COUNT = 8;

void board_init(Board *b) {
    for (int i = 0; i < BOARD_SIZE; i++) {
        b->cells[i] = EMPTY_CELL;
    }
}

bool board_is_free(const Board *b, int pos) {
    return pos >= 0 && pos < BOARD_SIZE && b->cells[pos] == EMPTY_CELL;
}

bool board_place(Board *b, int pos, char player) {
    if (!board_is_free(b, pos)) {
        return false;
    }
    b->cells[pos] = player;
    return true;
}

char board_winner(const Board *b) {
    for (int i = 0; i < WIN_LINES_COUNT; i++) {
        char first = b->cells[WIN_LINES[i][0]];
        if (first != EMPTY_CELL &&
            first == b->cells[WIN_LINES[i][1]] &&
            first == b->cells[WIN_LINES[i][2]]) {
            return first;
        }
    }
    return EMPTY_CELL;
}

bool board_is_full(const Board *b) {
    for (int i = 0; i < BOARD_SIZE; i++) {
        if (b->cells[i] == EMPTY_CELL) {
            return false;
        }
    }
    return true;
}

static char opponent_of(char player, char computer, char human) {
    return player == computer ? human : computer;
}

/* Оценка позиции с точки зрения компьютера (алгоритм минимакс).
 *  +10 - победа компьютера, -10 - победа человека, 0 - ничья.
 * Вычитание глубины заставляет компьютера выбирать быструю победу
 * и затягивать поражение. */
static int minimax(const Board *b, char turn, char computer, char human, int depth) {
    char winner = board_winner(b);
    if (winner == computer) {
        return 10 - depth;
    }
    if (winner == human) {
        return depth - 10;
    }
    if (board_is_full(b)) {
        return 0;
    }

    bool computer_turn = (turn == computer);
    int best = computer_turn ? INT_MIN : INT_MAX;

    for (int pos = 0; pos < BOARD_SIZE; pos++) {
        if (!board_is_free(b, pos)) {
            continue;
        }
        Board next = *b;
        board_place(&next, pos, turn);

        int score = minimax(&next, opponent_of(turn, computer, human),
                            computer, human, depth + 1);
        if (computer_turn && score > best) {
            best = score;
        } else if (!computer_turn && score < best) {
            best = score;
        }
    }
    return best;
}

int board_best_move(const Board *b, char computer, char human) {
    int best_pos = -1;
    int best_score = INT_MIN;

    for (int pos = 0; pos < BOARD_SIZE; pos++) {
        if (!board_is_free(b, pos)) {
            continue;
        }
        Board next = *b;
        board_place(&next, pos, computer);

        int score = minimax(&next, human, computer, human, 1);
        if (score > best_score) {
            best_score = score;
            best_pos = pos;
        }
    }
    return best_pos;
}
