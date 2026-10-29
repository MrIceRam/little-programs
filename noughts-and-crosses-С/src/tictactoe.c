#include <stdio.h>
#include <stdlib.h>
#include <time.h>

#include "game.h"

void print_board(void) {
    printf("\n");
    for (int r = 0; r < 3; r++) {
        printf(" %c | %c | %c\n", board[r * 3], board[r * 3 + 1], board[r * 3 + 2]);
        if (r < 2) printf("---+---+---\n");
    }
    printf("\n");
}

int main(void) {
    srand((unsigned)time(NULL));

    board_reset();

    printf("Tic-tac-toe. You are X, computer is O. You move first.\n");

    while (1) {
        print_board();

        /* Player's move */
        int pos;
        while (1) {
            printf("Your move (1-9): ");
            if (scanf("%d", &pos) != 1) {
                if (feof(stdin)) return 0;
                while (getchar() != '\n');
                continue;
            }
            pos--;
            if (make_move(pos, 'X')) break;
            printf("Invalid cell, try again.\n");
        }

        if (check_winner() == 'X') { print_board(); printf("You win!\n"); break; }
        if (board_full())          { print_board(); printf("Draw!\n");    break; }

        /* Computer's random move */
        int choice = computer_move();
        printf("Computer plays cell %d\n", choice + 1);

        if (check_winner() == 'O') { print_board(); printf("Computer wins!\n"); break; }
        if (board_full())          { print_board(); printf("Draw!\n");          break; }
    }

    return 0;
}
