#include <stdlib.h>
#include <string.h>

#include "unity.h"
#include "game.h"

/* Fills the board from a 9-character string, e.g. "XXXOO    " */
static void set_board(const char *cells) {
    memcpy(board, cells, 9);
}

/* Unity calls these before and after every test */
void setUp(void) {
    board_reset();
}

void tearDown(void) {
}

/* ----------------------------- board_reset ------------------------------ */

static void test_board_reset_makes_all_cells_empty(void) {
    set_board("XOXOXOXOX");
    board_reset();
    for (int i = 0; i < 9; i++)
        TEST_ASSERT_EQUAL_CHAR(' ', board[i]);
}

/* ----------------------------- check_winner ----------------------------- */

static void test_no_winner_on_empty_board(void) {
    TEST_ASSERT_EQUAL_CHAR(0, check_winner());
}

static void test_x_wins_every_row(void) {
    set_board("XXX      "); TEST_ASSERT_EQUAL_CHAR('X', check_winner());
    set_board("   XXX   "); TEST_ASSERT_EQUAL_CHAR('X', check_winner());
    set_board("      XXX"); TEST_ASSERT_EQUAL_CHAR('X', check_winner());
}

static void test_o_wins_every_column(void) {
    set_board("O  O  O  "); TEST_ASSERT_EQUAL_CHAR('O', check_winner());
    set_board(" O  O  O "); TEST_ASSERT_EQUAL_CHAR('O', check_winner());
    set_board("  O  O  O"); TEST_ASSERT_EQUAL_CHAR('O', check_winner());
}

static void test_wins_on_diagonals(void) {
    set_board("X   X   X"); TEST_ASSERT_EQUAL_CHAR('X', check_winner());
    set_board("  O O O  "); TEST_ASSERT_EQUAL_CHAR('O', check_winner());
}

static void test_no_winner_with_mixed_line(void) {
    set_board("XXO      ");
    TEST_ASSERT_EQUAL_CHAR(0, check_winner());
}

static void test_no_winner_on_drawn_board(void) {
    /* X O X
       X O O
       O X X */
    set_board("XOXXOOOXX");
    TEST_ASSERT_EQUAL_CHAR(0, check_winner());
}

static void test_winner_on_full_board(void) {
    /* Last move fills the board and wins at the same time */
    set_board("XOXOXOOXX");
    TEST_ASSERT_EQUAL_CHAR('X', check_winner());
}

/* ------------------------------ board_full ------------------------------ */

static void test_empty_board_is_not_full(void) {
    TEST_ASSERT_FALSE(board_full());
}

static void test_board_with_one_empty_cell_is_not_full(void) {
    set_board("XOXOXOXO ");
    TEST_ASSERT_FALSE(board_full());
}

static void test_filled_board_is_full(void) {
    set_board("XOXXOOOXX");
    TEST_ASSERT_TRUE(board_full());
}

/* ---------------------------- is_valid_move ----------------------------- */

static void test_every_cell_valid_on_empty_board(void) {
    for (int i = 0; i < 9; i++)
        TEST_ASSERT_TRUE(is_valid_move(i));
}

static void test_out_of_range_moves_are_invalid(void) {
    TEST_ASSERT_FALSE(is_valid_move(-1));
    TEST_ASSERT_FALSE(is_valid_move(9));
    TEST_ASSERT_FALSE(is_valid_move(100));
}

static void test_occupied_cell_is_invalid(void) {
    board[4] = 'O';
    TEST_ASSERT_FALSE(is_valid_move(4));
}

/* ------------------------------ make_move ------------------------------- */

static void test_make_move_places_mark(void) {
    TEST_ASSERT_TRUE(make_move(0, 'X'));
    TEST_ASSERT_EQUAL_CHAR('X', board[0]);
}

static void test_make_move_does_not_overwrite(void) {
    make_move(4, 'X');
    TEST_ASSERT_FALSE(make_move(4, 'O'));
    TEST_ASSERT_EQUAL_CHAR('X', board[4]);
}

static void test_make_move_out_of_range_changes_nothing(void) {
    TEST_ASSERT_FALSE(make_move(-1, 'X'));
    TEST_ASSERT_FALSE(make_move(9, 'X'));
    for (int i = 0; i < 9; i++)
        TEST_ASSERT_EQUAL_CHAR(' ', board[i]);
}

/* ---------------------------- computer_move ----------------------------- */

static void test_computer_moves_into_empty_cell(void) {
    /* rand() is random, so repeat many times */
    for (int run = 0; run < 200; run++) {
        set_board("XX XO X  ");
        int cell = computer_move();
        TEST_ASSERT_TRUE(cell == 2 || cell == 5 || cell == 7 || cell == 8);
        TEST_ASSERT_EQUAL_CHAR('O', board[cell]);
    }
}

static void test_computer_takes_last_empty_cell(void) {
    set_board("XOXOX XOX");
    TEST_ASSERT_EQUAL_INT(5, computer_move());
    TEST_ASSERT_EQUAL_CHAR('O', board[5]);
}

static void test_computer_move_on_full_board(void) {
    set_board("XOXXOOOXX");
    TEST_ASSERT_EQUAL_INT(-1, computer_move());
    TEST_ASSERT_EQUAL_STRING_LEN("XOXXOOOXX", board, 9);
}

/* ------------------------------ full game ------------------------------- */

static void test_full_game_x_wins(void) {
    TEST_ASSERT_TRUE(make_move(0, 'X'));
    TEST_ASSERT_TRUE(make_move(3, 'O'));
    TEST_ASSERT_TRUE(make_move(1, 'X'));
    TEST_ASSERT_TRUE(make_move(4, 'O'));
    TEST_ASSERT_EQUAL_CHAR(0, check_winner());
    TEST_ASSERT_TRUE(make_move(2, 'X'));
    TEST_ASSERT_EQUAL_CHAR('X', check_winner());
    TEST_ASSERT_FALSE(board_full());
}

int main(void) {
    srand(12345);

    UNITY_BEGIN();

    RUN_TEST(test_board_reset_makes_all_cells_empty);

    RUN_TEST(test_no_winner_on_empty_board);
    RUN_TEST(test_x_wins_every_row);
    RUN_TEST(test_o_wins_every_column);
    RUN_TEST(test_wins_on_diagonals);
    RUN_TEST(test_no_winner_with_mixed_line);
    RUN_TEST(test_no_winner_on_drawn_board);
    RUN_TEST(test_winner_on_full_board);

    RUN_TEST(test_empty_board_is_not_full);
    RUN_TEST(test_board_with_one_empty_cell_is_not_full);
    RUN_TEST(test_filled_board_is_full);

    RUN_TEST(test_every_cell_valid_on_empty_board);
    RUN_TEST(test_out_of_range_moves_are_invalid);
    RUN_TEST(test_occupied_cell_is_invalid);

    RUN_TEST(test_make_move_places_mark);
    RUN_TEST(test_make_move_does_not_overwrite);
    RUN_TEST(test_make_move_out_of_range_changes_nothing);

    RUN_TEST(test_computer_moves_into_empty_cell);
    RUN_TEST(test_computer_takes_last_empty_cell);
    RUN_TEST(test_computer_move_on_full_board);

    RUN_TEST(test_full_game_x_wins);

    return UNITY_END();
}
