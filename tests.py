#! /usr/bin/env python
# -*- coding: utf-8 -*-
# vim:fenc=utf-8
#
# Copyright © 2015 Danny Tamez <zematynnad@gmail.com>
#
# Distributed under terms of the MIT license.

"""Tests for mastermind module."""

from unittest import TestCase

from mock import (
    call,
    MagicMock,
    patch,
)

from mastermind import (
    Guess,
    MasterMind,
)


class GuessTests(TestCase):

    """Test the guess class logic."""

    def test_str(self):
        """Test the colors and format of a printed guess."""
        guess = Guess('rgby', 2, 0)

        repr = str(guess)

        expected = ('\x1b[31mr\x1b[0m, \x1b[32mg\x1b[0m, \x1b[34mb\x1b[0m, '
                    '\x1b[33my\x1b[0m,     W:0, B:2')
        self.assertEqual(expected, repr)


class MasterMindTests(TestCase):

    """Test the main game logic."""

    def test_num_colors_good(self):
        """Test a happy case for number of colors."""
        mm = MasterMind(4)

        self.assertEqual(4, len(mm.colors))
        self.assertEqual(('r', 'G', 'y', 'g'), mm.colors)

    def test_num_colors_too_small(self):
        """Test input of fewer colors than allowed."""
        mm = MasterMind(0)

        self.assertEqual(3, len(mm.colors))
        self.assertEqual(('r', 'G', 'y'), mm.colors)

    def test_num_colors_too_big(self):
        """Test input of more colors than allowed."""
        mm = MasterMind(20)

        self.assertEqual(8, len(mm.colors))
        self.assertEqual(('r', 'G', 'y', 'g', 'b', 'm', 'c', 'w'), mm.colors)

    def test_play(self):
        """Test that the  game continues when game_over is False."""
        mm = MasterMind(3)
        mm.display_game = MagicMock()
        mm.get_next_guess = MagicMock()
        mm.evaluate_guess = MagicMock()
        mm.update_points = MagicMock()
        mm.game_over = False

        def side_effect():
            mm.game_over = True
        mm.evaluate_guess.side_effect = side_effect

        mm.play()

        self.assertEqual(1, mm.display_game.call_count)
        self.assertEqual(1, mm.get_next_guess.call_count)
        self.assertEqual(1, mm.evaluate_guess.call_count)
        self.assertEqual(1, mm.update_points.call_count)

    def test_play_game_over(self):
        """Test that the game ends  when game_over is False."""
        mm = MasterMind(3)
        mm.display_game = MagicMock()
        mm.get_next_guess = MagicMock()
        mm.evaluate_guess = MagicMock()
        mm.update_points = MagicMock()
        mm.game_over = True

        mm.play()

        self.assertEqual(0, mm.display_game.call_count)
        self.assertEqual(0, mm.get_next_guess.call_count)
        self.assertEqual(0, mm.evaluate_guess.call_count)
        self.assertEqual(0, mm.update_points.call_count)

    def test_evaluate_guess_0_0(self):
        """Test no matches at all."""
        guess = Guess('rgby')
        mm = MasterMind(8)
        mm.secret = 'Gmcw'
        mm.guesses.append(guess)

        mm.evaluate_guess()

        self.assertEqual(0, mm.guesses[0].black)
        self.assertEqual(0, mm.guesses[0].white)

    def test_evaluate_guess_4_0(self):
        """Test 4 matches in wrong spots."""
        guess = Guess('rgby')
        mm = MasterMind(8)
        mm.secret = 'gbyr'
        mm.guesses.append(guess)

        mm.evaluate_guess()

        self.assertEqual(4, mm.guesses[0].black)
        self.assertEqual(0, mm.guesses[0].white)

    def test_evaluate_guess_win(self):
        """Test 4 matches in wrong spots."""
        guess = Guess('rgby')
        mm = MasterMind(8)
        mm.secret = 'rgby'
        mm.guesses.append(guess)
        mm.display_game_over = MagicMock()

        mm.evaluate_guess()

        self.assertTrue(mm.game_over)
        self.assertTrue(mm.winner)

    def test_evaluate_double_color_secret(self):
        """Test that a double color in the secret only counts once."""
        guess = Guess('grgy')
        mm = MasterMind(8)
        mm.secret = 'rbwr'
        mm.guesses.append(guess)

        mm.evaluate_guess()

        self.assertEqual(1, mm.guesses[0].black)
        self.assertEqual(0, mm.guesses[0].white)

    def test_evaluate_double_color_guess(self):
        """Test that a double color in the guess only counts once."""
        guess = Guess('rbwr')
        mm = MasterMind(8)
        mm.secret = 'grgy'
        mm.guesses.append(guess)

        mm.evaluate_guess()

        self.assertEqual(1, mm.guesses[0].black)
        self.assertEqual(0, mm.guesses[0].white)

    @patch('__builtin__.print')
    def test_display_game(self, mock_print):
        """Test that the output of display game matches history."""
        mm = MasterMind(8)
        mm.secret = 'ywwr'
        guess_1 = Guess('rbwr')
        mm.guesses.append(guess_1)
        mm.evaluate_guess()
        guess_2 = Guess('wwrr')
        mm.guesses.append(guess_2)
        mm.evaluate_guess()
        guess_3 = Guess('ywrr')
        mm.guesses.append(guess_3)
        mm.evaluate_guess()

        mm.display_game()

        self.assertEqual(5, mock_print.call_count)
        expected = [call('------------------------'),
                    call(guess_1),
                    call(guess_2),
                    call(guess_3),
                    call('------------------------'),
                    ]
        mock_print.assert_has_calls(expected)

    @patch('__builtin__.raw_input')
    def test_display_game_over_win(self, mock_raw_input):
        """Test that the right message is displayed on a win."""
        mm = MasterMind(4)
        mm.winner = True
        mm.save_score = MagicMock()

        mm.display_game_over()

        expected = [call('enter your initials:\n'),
                    call('Would you like to see the high scores? [y/N]\n'),
                    call().__eq__('y')]

        mock_raw_input.assert_called_with(expected)

    @patch('__builtin__.raw_input')
    def test_display_game_over_loss(self, mock_raw_input):
        """Test that the right message is displayed on a loss."""

    def test_update_points(self):
        pass

    def test_save_score(self):
        pass

    def test_display_high_score(self):
        pass

    def test_get_next_guess(self):
        pass
