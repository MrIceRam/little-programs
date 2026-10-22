#include <stdio.h>
#include <stdlib.h>
#include <time.h>

char board[9];

void print_board(void) {
    printf("\n");
    for (int r = 0; r < 3; r++) {
        printf(" %c | %c | %c\n", board[r * 3], board[r * 3 + 1], board[r * 3 + 2]);
        if (r < 2) printf("---+---+---\n");
    }
    printf("\n");
}

/* Returns 'X' or 'O' if someone has won, otherwise 0 */
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

int main(void) {
    srand((unsigned)time(NULL));

    for (int i = 0; i < 9; i++) board[i] = ' ';

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
            if (pos >= 0 && pos < 9 && board[pos] == ' ') break;
            printf("Invalid cell, try again.\n");
        }
        board[pos] = 'X';

        if (check_winner() == 'X') { print_board(); printf("You win!\n"); break; }
        if (board_full())          { print_board(); printf("Draw!\n");    break; }

        /* Computer's random move */
        int free_cells[9], count = 0;
        for (int i = 0; i < 9; i++)
            if (board[i] == ' ') free_cells[count++] = i;

        int choice = free_cells[rand() % count];
        board[choice] = 'O';
        printf("Computer plays cell %d\n", choice + 1);

        if (check_winner() == 'O') { print_board(); printf("Computer wins!\n"); break; }
        if (board_full())          { print_board(); printf("Draw!\n");          break; }
    }

    return 0;
}