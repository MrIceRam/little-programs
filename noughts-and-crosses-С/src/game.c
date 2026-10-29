#include <stdlib.h>

#include "game.h"

char board[9];

void board_reset(void) {
    for (int i = 0; i < 9; i++) board[i] = ' ';
}

char check_winner(void) {
    int lines[8][3] = {
        {0, 1, 2}, {3, 4, 5}, {6, 7, 8},
        {0, 3, 6}, {1, 4, 7}, {2, 5, 8},
        {0, 4, 8}, {2, 4, 6}
    };
    for (int i = 0; i < 8; i++) {
        int a = lines[i][0], b = lines[i][1], c = lines[i][2];
        if (board[a] != ' ' && board[a] == board[b] && board[a] == board[c])
            return board[a];
    }
    return 0;
}

int board_full(void) {
    for (int i = 0; i < 9; i++)
        if (board[i] == ' ') return 0;
    return 1;
}

int is_valid_move(int pos) {
    return pos >= 0 && pos < 9 && board[pos] == ' ';
}

int make_move(int pos, char mark) {
    if (!is_valid_move(pos)) return 0;
    board[pos] = mark;
    return 1;
}

int computer_move(void) {
    int free_cells[9], count = 0;
    for (int i = 0; i < 9; i++)
        if (board[i] == ' ') free_cells[count++] = i;

    if (count == 0) return -1;

    int choice = free_cells[rand() % count];
    board[choice] = 'O';
    return choice;
}
