#ifndef GAME_H
#define GAME_H

/* Game logic without input/output, so it can be tested separately */

extern char board[9];

/* Fills the board with spaces */
void board_reset(void);

/* Returns 'X' or 'O' if someone has won, otherwise 0 */
char check_winner(void);

/* Returns 1 if there are no empty cells left */
int board_full(void);

/* Returns 1 if pos is 0..8 and the cell is empty */
int is_valid_move(int pos);

/* Puts mark into cell pos. Returns 1 on success, 0 if the move is invalid */
int make_move(int pos, char mark);

/* Puts 'O' into a random empty cell. Returns the cell index or -1 if full */
int computer_move(void);

#endif
